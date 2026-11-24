# Deployment notes

FamilyShield AI can run locally with SQLite or with PostgreSQL. PostgreSQL is recommended for anything beyond a single-machine demo.

## Production checklist

1. Set a strong random `SECRET_KEY`.
2. Set `DATABASE_URL` to a PostgreSQL URL using the `psycopg` driver.
3. Run `alembic upgrade head` before starting the API.
4. Set `CORS_ORIGINS` to the exact frontend origin(s), not `*`.
5. Keep `GROQ_API_KEY` and `GOOGLE_SAFE_BROWSING_API_KEY` in backend environment only.
6. Keep `SAFE_URL_PROBE=false` unless you have a reason to enable limited redirect inspection.
7. Build the frontend with `npm run build` and serve `frontend/dist` behind a static web server or reverse proxy.
8. Terminate TLS at a reverse proxy and serve the API over HTTPS in production.
9. Add persistent, rate-limited logging at the proxy in addition to the app-level scan limiter.
10. Back up the database regularly and test restoration.

## Suggested process layout

```
reverse proxy (HTTPS)
  ├── /            -> static frontend/dist
  └── /api/*       -> uvicorn backend.main:app
```

If the frontend is served from a different origin, set `VITE_API_URL` at build time to the full API URL and include that frontend origin in `CORS_ORIGINS`.

## Health checks

- `GET /health` — lightweight API liveness check.
- Database connectivity is exercised by authenticated endpoints and migrations.

## Operational limits

- Scan endpoints are rate limited per authenticated user (configurable).
- Message text is capped at 20,000 characters; URLs at 2,048.
- Optional external services degrade gracefully: Groq, Safe Browsing, and ML artifacts are reported as unavailable/fallback rather than simulated.
- The URL analyzer does not fetch page content by default and never executes page scripts or downloaded files.

## Updating

1. Pull changes.
2. Install updated Python and npm dependencies.
3. Run `alembic upgrade head`.
4. Retrain ML artifacts if `ml/` changed: `python -m ml.train_model`.
5. Rebuild the frontend: `npm run build`.
6. Restart the API and proxy.
