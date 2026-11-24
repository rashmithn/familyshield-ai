# Architecture

## Request flow

```
Browser (React/Vite)
  -> Axios client (JWT from localStorage)
  -> FastAPI routers (Pydantic validation)
  -> Services (analysis, explanation, alerting)
  -> SQLAlchemy models -> PostgreSQL (or SQLite fallback)
```

## Backend layers

- `app/routers` — HTTP boundary, authentication and authorization dependencies.
- `app/schemas` — Pydantic request/response models. No ORM objects are returned directly.
- `app/services` — detection, explanation, persistence and alert side effects.
- `app/models` — relational schema with UUID primary keys and timestamps.
- `ml/` — offline training/evaluation; artifacts are loaded at runtime if present.

## Relational model

- `users` — account credentials (bcrypt hash only), profile, timestamps.
- `families` — family group, invite code, creator.
- `family_members` — join table with `admin`/`member` role.
- `scans` — scan type, redacted excerpt, risk score/level, category, confidence, explanation, actions, details JSON, engine label.
- `scam_indicators` — one row per detected indicator, linked to a scan.
- `family_alerts` — alerts shared with a family, review status and reviewer.
- `notifications` — per-user notification inbox linked to alerts.

## Detection pipeline

1. Normalize and truncate input; redact OTPs, long numbers, card-like sequences, and emails.
2. Run deterministic rules to collect indicators and a category.
3. If ML artifacts exist, run TF-IDF + logistic regression and blend its probability with rule evidence.
4. Map combined evidence to a 0–100 risk score and one of `safe`, `suspicious`, `high_risk`.
5. Generate explanation via Groq (if configured) or the deterministic fallback, always with a no-guarantee caveat.
6. Persist scan and indicators; create family alerts/notifications when applicable.
7. Return a response whose `engine` field honestly lists the components used.

## URL safety posture

URLs are parsed and analyzed server-side. By default the backend does not fetch page content. Optional TLS probing uses a socket/TLS handshake to check certificate validity only; `SAFE_URL_PROBE` (default false) can perform a short, redirect-disabled probe for redirect metadata. No downloaded file is executed and no page script is run.

## Analytics

The overview endpoint computes counts, seven-day trends (including zero days), category counts, risk distribution, family activity, and recent scans from SQL queries scoped to the authenticated user's own scans and scans belonging to their families. There are no seeded or hardcoded dashboard statistics.
