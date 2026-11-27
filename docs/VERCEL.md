# Deploying the frontend to Vercel

Vercel is a good host for the **React frontend**. Keep the FastAPI backend on Render (or another Python host) because it needs a long-running Python process, PostgreSQL migrations, and in-memory rate limiting that does not work reliably in a serverless environment.

## Architecture

```
Vercel (React/Vite)  ->  Render (FastAPI)  ->  Render PostgreSQL
```

## Steps

1. Deploy the backend first using `docs/RENDER.md` or `render.yaml`.
2. In Vercel, choose **Add New → Project** and import:
   `https://github.com/rashmithn/familyshield-ai`
3. Set **Root Directory** to `frontend`.
4. Framework preset: **Vite**.
5. Build command: `npm run build`.
6. Output directory: `dist` (the included `frontend/vercel.json` sets this).
7. Add environment variable:

   ```text
   VITE_API_URL=https://your-familyshield-api.onrender.com
   ```

8. Deploy. VITE variables are baked at build time, so redeploy after changing this value.
9. On Render, update the backend environment variables:

   ```text
   CORS_ORIGINS=https://your-vercel-app.vercel.app
   FRONTEND_BASE_URL=https://your-vercel-app.vercel.app
   ```

10. Redeploy the Render API after changing CORS.

## SPA routing

`frontend/vercel.json` rewrites unknown paths to `/index.html`, so React Router routes such as `/app/scanner` work on refresh.

## Security notes

- Never add `GROQ_API_KEY`, `GOOGLE_SAFE_BROWSING_API_KEY`, `SECRET_KEY`, or `DATABASE_URL` to Vercel.
- The frontend only receives the public API URL.
- If the browser shows CORS errors, the Render `CORS_ORIGINS` value does not exactly match your Vercel domain.

## Can the backend also go on Vercel?

Not recommended for this project. Vercel serverless functions are short-lived and stateless, which conflicts with:

- FastAPI lifespan startup and table initialization
- Alembic migrations
- In-memory per-user rate limiting
- Long-lived database sessions
- Local SQLite fallback

Use Render, Railway, Fly.io, or a container host for the API. If you want everything on one platform, the included `render.yaml` can host both the API and frontend on Render.
