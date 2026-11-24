"""End-to-end smoke test against a running FamilyShield API.

Usage:
    python scripts/smoke_api.py [http://127.0.0.1:8000]

This creates a temporary demo account and verifies the main authenticated workflows.
It requires `httpx` (already a backend dependency).
"""

from __future__ import annotations

import sys
import uuid
from typing import Any

import httpx

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
EMAIL = f"smoke-{uuid.uuid4().hex[:12]}@example.com"
PASSWORD = "SmokeTest!2345"


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)
    print(f"  ok: {message}")


def body(response: httpx.Response) -> dict[str, Any]:
    try:
        return response.json()
    except Exception as exc:  # pragma: no cover - diagnostic helper
        raise AssertionError(f"Non-JSON response ({response.status_code}): {response.text[:300]}") from exc


def main() -> None:
    with httpx.Client(base_url=BASE_URL, timeout=20.0) as client:
        health = client.get("/health")
        check(health.status_code == 200, "health endpoint")

        registration = client.post(
            "/auth/register",
            json={"email": EMAIL, "password": PASSWORD, "full_name": "Smoke Tester"},
        )
        check(registration.status_code in (200, 201), f"register ({registration.status_code})")
        token = body(registration)["access_token"]
        client.headers.update({"Authorization": f"Bearer {token}"})

        me = client.get("/auth/me")
        check(me.status_code == 200 and body(me)["email"] == EMAIL, "authenticated me")

        family = client.post("/families", json={"name": "Smoke Family", "description": "Temporary test group"})
        check(family.status_code in (200, 201), f"create family ({family.status_code})")
        family_data = body(family)
        family_id = family_data["id"]
        check(family_data["my_role"] == "admin", "creator is family admin")

        join_code = body(client.post(f"/families/{family_id}/invites"))["invite_code"]
        check(bool(join_code), "invite code issued")

        message_scan = client.post(
            "/scan/message",
            json={
                "text": "URGENT: Your bank account will be blocked today. Share your OTP and card number to avoid closure.",
                "family_id": family_id,
            },
        )
        check(message_scan.status_code in (200, 201), f"message scan ({message_scan.status_code})")
        message_data = body(message_scan)
        check(message_data["risk_level"] in {"suspicious", "high_risk"}, "message flagged as risky")
        check(message_data["risk_score"] >= 0 and message_data["risk_score"] <= 100, "risk score in range")
        check(bool(message_data["indicators"]), "indicators returned")
        check("not a guarantee" in message_data["explanation"].lower(), "explanation includes caveat")
        check(bool(message_data["engine"]), "engine honestly labeled")

        url_scan = client.post(
            "/scan/url",
            json={"url": "http://192.168.1.10/verify?account=update", "family_id": family_id},
        )
        check(url_scan.status_code in (200, 201), f"url scan ({url_scan.status_code})")
        url_data = body(url_scan)
        check(url_data["risk_level"] in {"suspicious", "high_risk"}, "IP-based URL flagged")
        check(isinstance(url_data["details"], dict), "URL details returned")

        scans = client.get("/scans", params={"limit": 20})
        check(scans.status_code == 200 and body(scans)["total"] >= 2, "scan history contains new scans")

        detail = client.get(f"/scans/{message_data['id']}")
        check(detail.status_code == 200 and body(detail)["id"] == message_data["id"], "scan detail")

        alerts = client.get("/alerts")
        check(alerts.status_code == 200 and len(body(alerts)) >= 2, "family alerts auto-created")
        alert = body(alerts)[0]
        reviewed = client.post(f"/alerts/{alert['id']}/review")
        check(reviewed.status_code == 200 and body(reviewed)["status"] == "reviewed", "alert review")

        analytics = client.get("/analytics/overview")
        check(analytics.status_code == 200, "analytics endpoint")
        analytics_data = body(analytics)
        check(analytics_data["total_scans"] >= 2, "analytics reflects real scans")
        check(len(analytics_data["weekly_trend"]) == 7, "seven-day trend")

        awareness = client.get("/awareness")
        check(awareness.status_code == 200 and len(body(awareness)["categories"]) >= 5, "awareness content")

        deletion = client.delete(f"/scans/{url_data['id']}")
        check(deletion.status_code in (200, 204), "scan deletion")

        print(f"\nSmoke test passed. Temporary account: {EMAIL}")


if __name__ == "__main__":
    main()
