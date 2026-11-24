# Troubleshooting

## Backend will not start

- Confirm Python 3.11+ and that `pip install -r requirements.txt` completed from the repository root.
- Check `root `.env`` exists. Copy `.env.example` if needed.
- If using SQLite, the default `DATABASE_URL=sqlite:///./familyshield_dev.db` works without extra services.
- If using PostgreSQL, confirm the container is running (`docker compose ps`) and run `alembic upgrade head` from `backend/`.
- A development-only default `SECRET_KEY` works locally; set a real one for any deployment.

## Frontend shows network errors

- Confirm the API is running on port 8000 and `http://localhost:8000/health` returns OK.
- If port 8000 is used by another local service, start the API on another port (for example 8010) and set `VITE_API_URL=http://localhost:8010` in `frontend/.env`, then rebuild or restart Vite.
- Confirm `frontend/.env` has `VITE_API_URL=http://localhost:8000` (or the alternate port you chose).
- Check CORS_ORIGINS in `root `.env`` includes `http://localhost:5173`.
- Restart the Vite dev server when changing `.env` files.

## ML classifier is not running

- Run `python -m ml.train_model` from the repository root.
- Confirm files exist under `ml/artifacts/`.
- Scans still work with the rule engine; the response `engine` field will say `rules` instead of `rules+ml`.

## Explanations look generic

- That is expected without `GROQ_API_KEY`. The deterministic fallback engine is used and labeled.
- Set the key in `root `.env`` and restart the API to enable Groq explanations.

## URL reputation says unavailable

- Set `GOOGLE_SAFE_BROWSING_API_KEY` in `root `.env`` and restart the API.
- Structural analysis still works without it.

## Rate limit errors (429)

- The default limit is 20 scan requests per user per minute.
- Increase `RATE_LIMIT_PER_MINUTE` in `root `.env`` if needed and restart.

## Tests fail on Windows

- Use `python -m pytest` rather than bare `pytest`.
- If `npm` is blocked by PowerShell execution policy, use `cmd /c "npm install"` and `cmd /c "npm run build"`.
