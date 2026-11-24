# API examples

These examples use `curl` on Windows PowerShell. Replace the token with the one returned from register/login.

## Register

```powershell
curl -X POST http://localhost:8000/auth/register `
  -H "Content-Type: application/json" `
  -d '{"email":"parent@example.com","password":"StrongPass!123","full_name":"A Parent"}'
```

## Login

```powershell
curl -X POST http://localhost:8000/auth/login `
  -H "Content-Type: application/json" `
  -d '{"email":"parent@example.com","password":"StrongPass!123"}'
```

## Use the token

```powershell
$token = "PASTE_ACCESS_TOKEN_HERE"
$headers = @{ Authorization = "Bearer $token" }
```

## Create a family

```powershell
curl -X POST http://localhost:8000/families `
  -H "Content-Type: application/json" -H "Authorization: Bearer $token" `
  -d '{"name":"Sharma Family","description":"Family safety group"}'
```

## Join a family

```powershell
curl -X POST http://localhost:8000/families/join `
  -H "Content-Type: application/json" -H "Authorization: Bearer $token" `
  -d '{"invite_code":"FS-ABCDEF12"}'
```

## Scan a message

```powershell
curl -X POST http://localhost:8000/scan/message `
  -H "Content-Type: application/json" -H "Authorization: Bearer $token" `
  -d '{"text":"Urgent: share your OTP now or your account will be blocked","family_id":"PASTE_FAMILY_ID"}'
```

## Scan a URL

```powershell
curl -X POST http://localhost:8000/scan/url `
  -H "Content-Type: application/json" -H "Authorization: Bearer $token" `
  -d '{"url":"http://192.168.1.10/verify"}'
```

## History, alerts, analytics, awareness

```powershell
curl http://localhost:8000/scans?limit=20 -H "Authorization: Bearer $token"
curl http://localhost:8000/alerts?status=unread -H "Authorization: Bearer $token"
curl http://localhost:8000/analytics/overview -H "Authorization: Bearer $token"
curl http://localhost:8000/awareness -H "Authorization: Bearer $token"
```

## Review an alert

```powershell
curl -X POST http://localhost:8000/alerts/PASTE_ALERT_ID/review `
  -H "Authorization: Bearer $token"
```

The interactive OpenAPI documentation at `http://localhost:8000/docs` lets you try every endpoint in the browser.
