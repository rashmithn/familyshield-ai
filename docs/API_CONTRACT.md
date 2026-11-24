# FamilyShield AI — Internal API Contract

Both frontend and backend must follow this contract exactly. All dates are ISO-8601 strings.
All protected endpoints require `Authorization: Bearer <jwt>`.

## Common types

### UserOut
```json
{
  "id": "uuid-string",
  "email": "user@example.com",
  "full_name": "Ravi Kumar",
  "created_at": "2026-01-01T10:00:00Z",
  "families": [
    { "id": "uuid", "name": "Kumar Family", "role": "admin", "member_count": 4 }
  ]
}
```

### FamilyOut
```json
{
  "id": "uuid",
  "name": "Kumar Family",
  "description": "Family safety group",
  "invite_code": "FS-ABCD12EF",
  "created_at": "2026-01-01T10:00:00Z",
  "my_role": "admin",
  "members": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "full_name": "Ravi Kumar",
      "email": "user@example.com",
      "role": "admin",
      "joined_at": "2026-01-01T10:00:00Z"
    }
  ]
}
```

### IndicatorOut
```json
{
  "code": "otp_request",
  "label": "OTP request",
  "severity": "high",
  "phrase": "share your OTP",
  "description": "Banks and legitimate services never ask for your OTP."
}
```
`severity` is one of `low`, `medium`, `high`.

### ScanOut
```json
{
  "id": "uuid",
  "scan_type": "message",
  "risk_score": 87,
  "risk_level": "high_risk",
  "category": "OTP / credential phishing",
  "confidence_score": 0.91,
  "summary": "This message has several traits of an OTP phishing attempt.",
  "explanation": "Human friendly explanation. Always includes a no-guarantee caveat.",
  "indicators": [],
  "recommended_actions": ["Do not share your OTP with anyone."],
  "details": {},
  "engine": "rules+ml",
  "content_excerpt": "Redacted excerpt, never raw secrets.",
  "created_at": "2026-01-01T10:00:00Z",
  "family_id": "uuid-or-null",
  "is_shared": false
}
```
`risk_level` is exactly `safe`, `suspicious`, or `high_risk`.
`scan_type` is exactly `message` or `url`.

### AlertOut
```json
{
  "id": "uuid",
  "family_id": "uuid",
  "family_name": "Kumar Family",
  "scan_id": "uuid",
  "title": "High-risk message detected",
  "severity": "high",
  "risk_level": "high_risk",
  "summary": "Short family-safe summary.",
  "status": "unread",
  "created_at": "2026-01-01T10:00:00Z",
  "reviewed_at": null,
  "reviewed_by": null,
  "scan": { "...": "ScanOut or null" }
}
```

## Endpoints

### Auth
- `POST /auth/register` body `{email, password, full_name}` -> `{access_token, token_type:"bearer", user: UserOut}`
- `POST /auth/login` body `{email, password}` -> same
- `GET /auth/me` -> `UserOut`
- `PATCH /auth/me` body `{full_name?, email?}` -> `UserOut`

### Families
- `POST /families` body `{name, description?}` -> `FamilyOut` (creator is admin)
- `GET /families` -> `FamilyOut[]`
- `GET /families/{family_id}` -> `FamilyOut`
- `POST /families/join` body `{invite_code}` -> `FamilyOut` (member role)
- `PATCH /families/{family_id}/members/{member_id}` body `{role:"admin"|"member"}` -> member object (admin only)
- `POST /families/{family_id}/invites` -> `{invite_code, invite_url}`

### Scanning
- `POST /scan/message` body `{text: string (max 20000), family_id?: uuid}` -> `ScanOut`
- `POST /scan/url` body `{url: string (max 2048), family_id?: uuid}` -> `ScanOut`
- `GET /scans?risk_level=&scan_type=&search=&limit=50&offset=0` -> `{items: ScanOut[], total: int, limit: int, offset: int}`
- `GET /scans/{scan_id}` -> `ScanOut`
- `DELETE /scans/{scan_id}` -> `{message: "Scan deleted"}`
- `POST /scans/{scan_id}/share` body `{family_id?: uuid}` -> `{alert: AlertOut}`

### Alerts
- `GET /alerts?status=all|unread|reviewed` -> `AlertOut[]`
- `POST /alerts/{alert_id}/review` -> `AlertOut`

### Analytics
- `GET /analytics/overview` -> 
```json
{
  "total_scans": 12,
  "high_risk": 3,
  "suspicious": 4,
  "safe": 5,
  "shared_alerts": 3,
  "unread_alerts": 1,
  "average_risk_score": 46,
  "weekly_trend": [{"date":"2026-11-18","label":"Wed","scans":2,"high_risk":1}],
  "categories": [{"name":"UPI payment scam","count":2}],
  "risk_distribution": [{"name":"Safe","value":5},{"name":"Suspicious","value":4},{"name":"High Risk","value":3}],
  "family_activity": [{"family_name":"Kumar Family","scans":12,"high_risk":3,"members":4}],
  "recent_scans": ["ScanOut"],
  "scope": "family and personal scans"
}
```
All values must come from the database. Weekly trend must cover the last 7 days including days with zero scans.

### Awareness
- `GET /awareness` ->
```json
{
  "categories": [
    {
      "id": "upi-scams",
      "title": "Common Indian UPI scams",
      "description": "How payment request fraud works.",
      "articles": [
        {
          "id": "upi-collect-request",
          "title": "Fake UPI collect request",
          "summary": "One-line summary.",
          "content": ["Paragraph 1.", "Paragraph 2."],
          "checklist": ["Do ...", "Do not ..."]
        }
      ]
    }
  ]
}
```

## Behavior rules

1. Never imply a message is guaranteed safe. Even `safe` results must carry a caveat such as "No obvious scam indicators were detected; this is not a guarantee of safety."
2. Redact OTPs, long digit strings, card numbers, and email addresses from stored excerpts and displayed indicator phrases.
3. Family data is visible only to members of that family. A scan may be filed under a family only if the user is a member.
4. Auto-create a family alert when a scan submitted with `family_id` has `risk_level` of `suspicious` or `high_risk`.
5. `engine` must honestly report which components ran: `rules`, `rules+ml`, `rules+ml+groq`, etc. If Groq key missing, fallback explanation engine is used and must be labeled.
6. Rate limit scan endpoints per authenticated user (default 20 requests/minute, configurable).
