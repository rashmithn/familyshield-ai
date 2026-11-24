# FamilyShield AI

FamilyShield AI is a software-only full-stack application that helps families identify suspicious messages, payment requests, URLs, and impersonation attempts. It combines an explainable rule engine, an optional local scikit-learn classifier, optional Groq-generated explanations, family alerting, and a premium React dashboard.

> **Important:** Detection is advisory. A low risk score means "no obvious indicators were detected", never "this is definitely safe". The application does not open submitted links in a browser, does not execute downloaded content, and must not be used as a substitute for verifying payments through a trusted channel.

---

## Project structure

```
familyshield-ai/
├── backend/                 FastAPI application, routers, services, tests, Alembic migrations
│   ├── routers/             auth, families, scans, alerts, analytics, awareness, notifications
│   ├── services/            message analysis, URL analysis, ML classifier, explanation, scanning
│   ├── models.py            SQLAlchemy models
│   ├── schemas.py           Pydantic request/response schemas
│   ├── main.py              FastAPI entrypoint
│   ├── alembic/             Database migrations
│   └── tests/               API integration tests
├── frontend/                React + Vite + Tailwind application
│   ├── src/api/             Axios client and typed-in-name service wrappers
│   ├── src/components/      Reusable UI components and app shell
│   ├── src/context/         Auth provider and protected routes
│   └── src/pages/           Landing, auth, dashboard, scanners, alerts, history, awareness, settings
├── ml/                      Synthetic dataset, training and evaluation scripts, model artifacts
├── database/                Database initialization helpers
├── docs/                    API contract, architecture, security notes
├── docker-compose.yml       Optional local PostgreSQL
├── .env.example             Environment variable reference
└── README.md
```

---

## Quick start (local development, SQLite)

Requirements: Python 3.11+ (3.13 tested), Node 20+ (Node 26 tested). PostgreSQL is optional for local development; without a `DATABASE_URL` pointing to PostgreSQL the backend uses a local SQLite file, clearly labeled as a development fallback.

### 1. Backend

```bash
cd familyshield-ai
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env               # Windows; use cp on macOS/Linux
```

Review the root `.env`. It is read from the repository root when you start Uvicorn there. For development the defaults are usable. Change `SECRET_KEY` before any real deployment.

Train the optional local classifier (creates `ml/artifacts/`):

```bash
python -m ml.train_model
python -m ml.evaluate
```

Start the API from the repository root:

```bash
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### 2. Frontend

```bash
cd familyshield-ai/frontend
npm install
copy .env.example .env          # Windows; use cp on macOS/Linux
npm run dev
```

Open http://localhost:5173. Register an account, then use the dashboard.

Production build:

```bash
npm run build
npm run preview
```

---

## PostgreSQL setup

PostgreSQL is not required for the SQLite development fallback, but is the intended production database.

```bash
cd familyshield-ai
docker compose up -d postgres
```

Set `DATABASE_URL` in the root `.env`:

```
DATABASE_URL=postgresql+psycopg://familyshield:familyshield@localhost:5432/familyshield
```

Apply migrations:

```bash
cd familyshield-ai
alembic -c backend/alembic.ini upgrade head
```

Then start the API as above. In development the app may auto-create tables for SQLite; in production, use Alembic rather than auto-creation.

---

## Environment variables

| Variable | Purpose | Default |
| --- | --- | --- |
| `DATABASE_URL` | SQLAlchemy database URL | `sqlite:///./familyshield_dev.db` (development fallback) |
| `SECRET_KEY` | JWT signing key | Development-only value; change in production |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime | `60` |
| `GROQ_API_KEY` | Enables Groq explanations | unset → deterministic fallback |
| `GROQ_MODEL` | Groq chat model | `llama-3.3-70b-versatile` |
| `GOOGLE_SAFE_BROWSING_API_KEY` | Enables threat-intelligence lookups | unset → unavailable label |
| `SAFE_URL_PROBE` | Allow limited active URL probe | `false` |
| `TLS_PROBE_TIMEOUT_SECONDS` | TLS handshake timeout (no page download) | `1.5` |
| `CORS_ORIGINS` | Comma-separated allowed origins | localhost:5173 and localhost:3000 |
| `RATE_LIMIT_PER_MINUTE` | Scan requests per user per minute | `20` |
| `DEV_AUTO_CREATE_TABLES` | Auto-create tables on startup for SQLite dev | `true` (set `false` with PostgreSQL) |
| `FRONTEND_BASE_URL` | Base URL used in invite links | `http://localhost:3000` |
| `VITE_API_URL` (frontend) | Backend base URL | `http://localhost:8000` |

API keys are read only by the backend. Never put them in `frontend/` or any `VITE_*` variable.

---

## API overview

Interactive OpenAPI documentation is served at `/docs`.

| Method | Path | Description |
| --- | --- | --- |
| POST | `/auth/register` | Create account, returns JWT |
| POST | `/auth/login` | Authenticate, returns JWT |
| GET | `/auth/me` | Current user with family memberships |
| PATCH | `/auth/me` | Update profile |
| POST | `/families` | Create family group (creator becomes admin) |
| GET | `/families` | List current user's families |
| GET | `/families/{id}` | Family detail with members |
| POST | `/families/join` | Join with invite code |
| PATCH | `/families/{id}/members/{member_id}` | Change role (admin only) |
| POST | `/families/{id}/invites` | Return invite code/link |
| POST | `/scan/message` | Analyze pasted/uploaded message |
| POST | `/scan/url` | Analyze URL server-side |
| GET | `/scans` | Filtered scan history |
| GET | `/scans/{id}` | Single scan detail |
| DELETE | `/scans/{id}` | Delete scan |
| POST | `/scans/{id}/share` | Share a scan as a family alert |
| GET | `/alerts` | Family alerts |
| POST | `/alerts/{id}/review` | Mark alert reviewed |
| GET | `/analytics/overview` | Database-backed analytics |
| GET | `/awareness` | Educational content |
| GET | `/notifications` | Current user's notifications |
| GET | `/health` | Health check |

A detailed request/response contract is in `docs/API_CONTRACT.md`.

---

## Detection design

1. **Rule engine** — deterministic indicators for urgency, OTP/credential requests, UPI collect requests, impersonation, lottery/job/investment lures, delivery scams, digital arrest, and suspicious URL structure. Each indicator has a label, severity, and redacted phrase.
2. **Local ML classifier** — TF-IDF + logistic regression trained on a clearly synthetic dataset in `ml/`. It is optional at runtime; the response `engine` field reports whether it ran. Retrain with `python -m ml.train_model`.
3. **URL analysis** — structural/domain heuristics, brand typo detection, IP hosts, punycode, subdomain anomalies, optional TLS certificate inspection, and optional Google Safe Browsing. Submitted links are never fetched as pages by default and are never opened in a browser.
4. **Explanations** — Groq when configured; otherwise a deterministic explanation engine. Both include a no-guarantee caveat and concrete recommended actions.
5. **Family alerts** — suspicious/high-risk scans submitted with a family ID automatically create family alerts and notifications. Members can review alerts.
6. **Analytics** — all dashboard numbers are computed from stored scan/alert rows.

### Risk levels

- `safe`: no strong indicators detected (still not a guarantee)
- `suspicious`: one or more moderate indicators, or mixed signals
- `high_risk`: multiple strong indicators or a highly specific scam pattern

---

## Testing

```bash
# Backend API tests
cd familyshield-ai
python -m pytest backend/tests -q

# ML training/evaluation
python -m ml.train_model
python -m ml.evaluate

# Frontend production build
cd frontend
npm run build
```

---

## Security notes

See `docs/SECURITY.md`. Highlights: bcrypt password hashing, JWT bearer auth, ORM-only database access, member-scoped authorization, rate-limited scanning, input length limits, secret redaction before persistence/display, no client-side API keys, no browser navigation to submitted URLs, and no execution of downloaded content.

For Render deployment, see `docs/RENDER.md` and the ready-to-use `render.yaml` blueprint.

---

## Known configuration-dependent features

| Feature | Requirement |
| --- | --- |
| Groq natural-language explanations | `GROQ_API_KEY` (fallback engine works without it) |
| Google Safe Browsing reputation | `GOOGLE_SAFE_BROWSING_API_KEY` (reported unavailable without it) |
| ML classification | Run `python -m ml.train_model` to generate artifacts (rule engine works without it) |
| PostgreSQL | Docker Compose service or an external database plus `DATABASE_URL` and `alembic upgrade head` |
| Redirect probe | `SAFE_URL_PROBE=true` (off by default; limited, no page script execution) |

When these are not configured, the UI and API clearly label the fallback rather than pretending the feature is active.
