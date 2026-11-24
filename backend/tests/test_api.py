"""End-to-end API tests against an isolated temporary SQLite database."""

from __future__ import annotations

import pytest

from backend.config import settings
from backend.rate_limit import reset_rate_limits

PASSWORD = "TestPass123"


def register(client, email: str, name: str = "Test User") -> dict:
    response = client.post(
        "/auth/register", json={"email": email, "password": PASSWORD, "full_name": name}
    )
    assert response.status_code == 201, response.text
    return response.json()


def headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def create_family(client, token: str, name: str = "Kumar Family") -> dict:
    response = client.post("/families", json={"name": name, "description": "Family safety group"}, headers=headers(token))
    assert response.status_code == 201, response.text
    return response.json()


# ------------------------------------------------------------------------- auth
def test_register_login_me_and_validation(client):
    data = register(client, "ravi@example.com", "Ravi Kumar")
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["user"]["email"] == "ravi@example.com"
    assert data["user"]["full_name"] == "Ravi Kumar"
    assert data["user"]["families"] == []
    assert "created_at" in data["user"]

    assert client.get("/auth/me", headers=headers(data["access_token"])).status_code == 200
    login = client.post("/auth/login", json={"email": "ravi@example.com", "password": PASSWORD})
    assert login.status_code == 200
    assert login.json()["user"]["email"] == "ravi@example.com"

    bad = client.post("/auth/login", json={"email": "ravi@example.com", "password": "WrongPass123"})
    assert bad.status_code == 401
    duplicate = client.post(
        "/auth/register", json={"email": "RAVI@example.com", "password": PASSWORD, "full_name": "Other"}
    )
    assert duplicate.status_code == 409
    assert client.post("/auth/register", json={"email": "bad", "password": PASSWORD, "full_name": "X"}).status_code == 422
    assert client.post(
        "/auth/register", json={"email": "a@b.com", "password": "short", "full_name": "X"}
    ).status_code == 422
    assert client.get("/auth/me").status_code == 401

    patched = client.patch(
        "/auth/me", json={"full_name": "Ravi K."}, headers=headers(data["access_token"])
    )
    assert patched.status_code == 200
    assert patched.json()["full_name"] == "Ravi K."


# ---------------------------------------------------------------------- families
def test_family_create_join_and_authorization(client):
    owner = register(client, "owner@example.com", "Owner")
    member = register(client, "member@example.com", "Member")
    outsider = register(client, "outsider@example.com", "Outsider")

    family = create_family(client, owner["access_token"])
    assert family["my_role"] == "admin"
    assert len(family["members"]) == 1
    assert family["invite_code"].startswith("FS-")

    listed = client.get("/families", headers=headers(owner["access_token"]))
    assert listed.status_code == 200 and len(listed.json()) == 1

    joined = client.post(
        "/families/join", json={"invite_code": family["invite_code"]}, headers=headers(member["access_token"])
    )
    assert joined.status_code == 200, joined.text
    assert joined.json()["my_role"] == "member"
    assert len(joined.json()["members"]) == 2
    member_id = next(m["id"] for m in joined.json()["members"] if m["email"] == "member@example.com")

    assert client.post(
        "/families/join", json={"invite_code": family["invite_code"]}, headers=headers(member["access_token"])
    ).status_code == 409

    assert client.post(
        f"/families/{family['id']}/invites", headers=headers(member["access_token"])
    ).status_code == 403
    assert client.patch(
        f"/families/{family['id']}/members/{member_id}",
        json={"role": "admin"},
        headers=headers(member["access_token"]),
    ).status_code == 403

    promoted = client.patch(
        f"/families/{family['id']}/members/{member_id}",
        json={"role": "admin"},
        headers=headers(owner["access_token"]),
    )
    assert promoted.status_code == 200 and promoted.json()["role"] == "admin"

    assert client.get(f"/families/{family['id']}", headers=headers(outsider["access_token"])).status_code == 404
    assert client.post(
        "/scan/message",
        json={"text": "Urgent! Share your OTP to avoid block.", "family_id": family["id"]},
        headers=headers(outsider["access_token"]),
    ).status_code == 404

    invites = client.post(f"/families/{family['id']}/invites", headers=headers(owner["access_token"]))
    assert invites.status_code == 200
    assert invites.json()["invite_code"].startswith("FS-")
    assert "invite_code=" in invites.json()["invite_url"]


# ------------------------------------------------------------------------ scans
def test_message_scan_high_risk_and_redaction(client):
    user = register(client, "scan@example.com")
    text = (
        "URGENT: your SBI bank account will be blocked. Share your OTP 123456 and card number "
        "4111 1111 1111 1111 immediately. Email help@example.com or pay ravi@paytm to verify."
    )
    response = client.post("/scan/message", json={"text": text}, headers=headers(user["access_token"]))
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["scan_type"] == "message"
    assert body["risk_level"] == "high_risk"
    assert body["risk_score"] >= 60
    assert any(indicator["code"] == "otp_request" for indicator in body["indicators"])
    assert body["engine"] in {"rules", "rules+ml", "rules+groq", "rules+ml+groq"}
    assert "guarantee" in body["explanation"].lower()
    assert 0.0 <= body["confidence_score"] <= 1.0
    for secret in ("123456", "4111", "help@example.com", "ravi@paytm"):
        assert secret not in body["content_excerpt"], secret
        assert all(secret not in indicator["phrase"] for indicator in body["indicators"]), secret


def test_url_scan_ip_address(client):
    user = register(client, "url@example.com")
    response = client.post(
        "/scan/url",
        json={"url": "http://192.168.1.1:8080/verify?otp=123456"},
        headers=headers(user["access_token"]),
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["scan_type"] == "url"
    assert body["risk_level"] in {"suspicious", "high_risk"}
    assert any(indicator["code"] == "url_ip_host" for indicator in body["indicators"])
    assert "123456" not in body["content_excerpt"]


def test_safe_message_still_has_caveat(client):
    user = register(client, "safe@example.com")
    response = client.post(
        "/scan/message",
        json={"text": "Hi Ravi, are we still meeting for lunch tomorrow near the office?"},
        headers=headers(user["access_token"]),
    )
    assert response.status_code == 201
    body = response.json()
    assert body["risk_level"] == "safe"
    assert "not a guarantee" in body["explanation"].lower()


def test_scan_list_detail_delete_and_share(client):
    owner = register(client, "list-owner@example.com")
    member = register(client, "list-member@example.com")
    family = create_family(client, owner["access_token"])
    client.post(
        "/families/join", json={"invite_code": family["invite_code"]}, headers=headers(member["access_token"])
    )

    created = client.post(
        "/scan/message",
        json={"text": "URGENT: share your OTP and bank password immediately to avoid account block.", "family_id": family["id"]},
        headers=headers(owner["access_token"]),
    )
    assert created.status_code == 201
    scan = created.json()
    assert scan["family_id"] == family["id"]
    assert scan["is_shared"] is True  # auto-created family alert

    listed = client.get("/scans", headers=headers(owner["access_token"]))
    assert listed.status_code == 200
    assert listed.json()["total"] >= 1
    assert listed.json()["limit"] == 50 and listed.json()["offset"] == 0
    filtered = client.get("/scans?risk_level=high_risk&scan_type=message", headers=headers(owner["access_token"]))
    assert all(item["risk_level"] == "high_risk" for item in filtered.json()["items"])
    search = client.get(f"/scans?search={scan['id'][:5]}", headers=headers(owner["access_token"]))
    assert search.status_code == 200

    detail = client.get(f"/scans/{scan['id']}", headers=headers(member["access_token"]))
    assert detail.status_code == 200 and detail.json()["id"] == scan["id"]

    shared = client.post(
        f"/scans/{scan['id']}/share",
        json={"family_id": family["id"]},
        headers=headers(owner["access_token"]),
    )
    assert shared.status_code == 200
    assert shared.json()["alert"]["scan"]["id"] == scan["id"]

    forbidden = client.delete(f"/scans/{scan['id']}", headers=headers(member["access_token"]))
    assert forbidden.status_code == 403
    deleted = client.delete(f"/scans/{scan['id']}", headers=headers(owner["access_token"]))
    assert deleted.status_code == 200 and deleted.json()["message"] == "Scan deleted"
    assert client.get(f"/scans/{scan['id']}", headers=headers(owner["access_token"])).status_code == 404


# ------------------------------------------------------------------------ alerts
def test_alerts_review_and_notifications(client):
    owner = register(client, "alert-owner@example.com")
    member = register(client, "alert-member@example.com")
    family = create_family(client, owner["access_token"])
    client.post(
        "/families/join", json={"invite_code": family["invite_code"]}, headers=headers(member["access_token"])
    )
    scan = client.post(
        "/scan/url",
        json={"url": "http://192.168.1.1/verify", "family_id": family["id"]},
        headers=headers(owner["access_token"]),
    ).json()

    unread = client.get("/alerts?status=unread", headers=headers(member["access_token"]))
    assert unread.status_code == 200
    assert any(alert["scan_id"] == scan["id"] for alert in unread.json())
    alert = next(alert for alert in unread.json() if alert["scan_id"] == scan["id"])
    assert alert["family_name"] == family["name"]
    assert alert["status"] == "unread"

    reviewed = client.post(f"/alerts/{alert['id']}/review", headers=headers(member["access_token"]))
    assert reviewed.status_code == 200
    assert reviewed.json()["status"] == "reviewed"
    assert reviewed.json()["reviewed_at"]
    assert reviewed.json()["reviewed_by"] == member["user"]["id"]
    reviewed_list = client.get("/alerts?status=reviewed", headers=headers(owner["access_token"]))
    assert any(item["id"] == alert["id"] for item in reviewed_list.json())

    notifications = client.get("/notifications", headers=headers(member["access_token"]))
    assert notifications.status_code == 200 and len(notifications.json()) >= 1


# -------------------------------------------------------------------- analytics
def test_analytics_and_awareness_shapes(client):
    user = register(client, "analytics@example.com")
    family = create_family(client, user["access_token"])
    client.post(
        "/scan/message",
        json={"text": "You have won a lottery. Pay a fee to claim your prize.", "family_id": family["id"]},
        headers=headers(user["access_token"]),
    )
    client.post(
        "/scan/message",
        json={"text": "Family dinner is at 7 pm tonight."},
        headers=headers(user["access_token"]),
    )

    response = client.get("/analytics/overview", headers=headers(user["access_token"]))
    assert response.status_code == 200
    data = response.json()
    for key in (
        "total_scans", "high_risk", "suspicious", "safe", "shared_alerts", "unread_alerts",
        "average_risk_score", "weekly_trend", "categories", "risk_distribution",
        "family_activity", "recent_scans", "scope",
    ):
        assert key in data
    assert data["total_scans"] == data["high_risk"] + data["suspicious"] + data["safe"]
    assert len(data["weekly_trend"]) == 7
    assert sum(day["scans"] for day in data["weekly_trend"]) == data["total_scans"]
    assert all(set(day) == {"date", "label", "scans", "high_risk"} for day in data["weekly_trend"])
    assert len(data["risk_distribution"]) == 3
    assert data["family_activity"][0]["family_name"] == family["name"]
    assert data["family_activity"][0]["members"] == 1
    assert data["scope"] == "family and personal scans"
    assert isinstance(data["recent_scans"], list)

    awareness = client.get("/awareness")
    assert awareness.status_code == 200
    categories = awareness.json()["categories"]
    assert isinstance(categories, list) and len(categories) >= 7
    ids = {item["id"] for item in categories}
    assert {
        "upi-scams", "otp-fraud", "fake-customer-care", "digital-arrest",
        "fake-investments", "social-engineering", "parent-safety-checklist",
    } <= ids
    for category in categories:
        assert {"id", "title", "description", "articles"} <= set(category)
        for article in category["articles"]:
            assert {"id", "title", "summary", "content", "checklist"} <= set(article)
            assert isinstance(article["content"], list) and article["content"]
            assert isinstance(article["checklist"], list) and article["checklist"]


# ------------------------------------------------------------------ rate limits
def test_scan_rate_limit_returns_429(client, monkeypatch):
    user = register(client, "ratelimit@example.com")
    reset_rate_limits()
    monkeypatch.setattr(settings, "RATE_LIMIT_PER_MINUTE", 2)
    responses = [
        client.post("/scan/message", json={"text": f"Hello message number {i}."}, headers=headers(user["access_token"]))
        for i in range(3)
    ]
    assert [response.status_code for response in responses] == [201, 201, 429]
    assert "Rate limit" in responses[2].json()["detail"]
    reset_rate_limits()
