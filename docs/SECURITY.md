# Security notes

## Credentials and tokens

- Passwords are hashed with bcrypt. Plaintext passwords are never stored or logged.
- Authentication uses signed JWT bearer tokens with an expiry configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`.
- `SECRET_KEY` must be replaced in production. API keys are read only by the backend and are never sent to the browser.

## Input handling

- All request bodies are validated with Pydantic. Message text is limited to 20,000 characters; URLs to 2,048.
- Database access uses SQLAlchemy ORM constructs. No user input is interpolated into raw SQL.
- React escapes displayed user text by default. The frontend avoids `dangerouslySetInnerHTML` for scan content.

## Sensitive data

- Before persistence, long digit sequences, OTP-like codes, card-like numbers, and email addresses in message excerpts and indicator phrases are redacted.
- The system does not ask for or store OTPs, passwords, PINs, or banking credentials. Users are instructed never to share them.
- Application logs avoid message bodies and URL query credentials.

## Authorization

- Every family-scoped read/write verifies that the authenticated user is a member of that family.
- Role changes require the `admin` role.
- Scan deletion is restricted to the scan owner (and, where implemented, family admins for family scans).

## Scanning safety

- Scan endpoints are rate limited per authenticated user (default 20/minute; configurable).
- Submitted URLs are not opened in a browser. Page content and scripts are not fetched or executed by default.
- TLS certificate checks are socket-level only. Optional redirect probing is disabled by default, uses short timeouts and disables redirects, and reports its status.
- Threat-intelligence lookups occur only when an API key is configured; otherwise the result is labeled unavailable.

## Honesty safeguards

- Risk levels are advisory. Every explanation includes a caveat that detection is not a guarantee.
- The `engine` field reports exactly which components ran (rules, ML, Groq, threat intel).
- If Groq, Safe Browsing, or ML artifacts are unavailable, the application reports the fallback explicitly instead of simulating those features.
