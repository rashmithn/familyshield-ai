# Deploying FamilyShield AI to Render

## Why the first deploy failed

The log showed:

```
Running 'npm start'
Could not read package.json: /opt/render/project/src/package.json
```

That means the Render service was created as a **Node service** with the default start command `npm start`. The repository root contains the Python backend, not a `package.json`. The fix is to set the service runtime to **Python** and use a Uvicorn start command.

A ready-made blueprint is included at `render.yaml`, and `.python-version` pins Python 3.13 (the version tested locally).

## Option A — Deploy with the blueprint (recommended)

1. Push the latest commit (including `render.yaml` and `.python-version`).
2. In Render, choose **New → Blueprint**.
3. Connect the GitHub repository `rashmithn/familyshield-ai`.
4. Render will create:
   - `familyshield-db` — managed PostgreSQL
   - `familyshield-api` — Python web service
   - `familyshield-frontend` — static site
5. Deploy. The API runs `alembic upgrade head` before starting.

The blueprint sets `CORS_ORIGINS` and `VITE_API_URL` using the assumed service names above. If Render gives your services different URLs, update both environment variables and redeploy.

## Option B — Fix the existing API service manually

In your Render web service settings:

| Setting | Value |
| --- | --- |
| Runtime | **Python 3** |
| Root Directory | leave empty (repository root) |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn backend.main:app --host 0.0.0.0 --port $PORT` |
| Health Check Path | `/health` |
| Pre-Deploy Command | `alembic -c backend/alembic.ini upgrade head` |

Do not put `alembic` or `uvicorn` in the build command. The build command only installs dependencies; `alembic` does not exist until that step finishes. Migrations belong in the pre-deploy command, and Uvicorn belongs in the start command.

Environment variables:

| Key | Value |
| --- | --- |
| `DATABASE_URL` | Connection string from a Render PostgreSQL database (not SQLite) |
| `SECRET_KEY` | Long random value |
| `DEV_AUTO_CREATE_TABLES` | `false` |
| `CORS_ORIGINS` | Your frontend URL, e.g. `https://familyshield-frontend.onrender.com` |
| `FRONTEND_BASE_URL` | Same frontend URL |
| `RATE_LIMIT_PER_MINUTE` | `20` |
| `SAFE_URL_PROBE` | `false` |

Optional keys: `GROQ_API_KEY`, `GOOGLE_SAFE_BROWSING_API_KEY`.

After setting these, create a **Shell** tab in Render and run:

```bash
alembic -c backend/alembic.ini upgrade head
```

Or add that command as a **Pre-Deploy Command** in the service settings.

## Deploy the frontend

Create a separate **Static Site**:

| Setting | Value |
| --- | --- |
| Root Directory | `frontend` |
| Build Command | `npm install && npm run build` |
| Publish Directory | `dist` |
| Environment Variable | `VITE_API_URL=https://your-api-url.onrender.com` |

The frontend has no API keys. All keys stay on the backend.

## Important notes

- Do **not** use SQLite on Render. The filesystem is ephemeral; data can disappear on restart. Use the managed PostgreSQL database.
- Set `DEV_AUTO_CREATE_TABLES=false` in production and apply migrations with Alembic.
- Change `CORS_ORIGINS` and `VITE_API_URL` to your real Render URLs after the first deploy.
- If only the API is needed, skip the static site and keep the frontend running locally.
- Without `GROQ_API_KEY` or `GOOGLE_SAFE_BROWSING_API_KEY`, the app uses and labels its documented fallbacks.
