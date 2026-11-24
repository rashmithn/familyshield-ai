# Test plan

## Automated checks

| Check | Command | Pass condition |
| --- | --- | --- |
| Backend API tests | `python -m pytest backend/tests -q` | All tests pass against temporary SQLite DB |
| ML training | `python -m ml.train_model` | Artifacts written to `ml/artifacts/` without error |
| ML evaluation | `python -m ml.evaluate` | Metrics printed; no exceptions |
| Frontend build | `cd frontend && npm run build` | Vite production build succeeds |
| Live smoke test | `python scripts/smoke_api.py` with API running | Register → family → scans → alerts → analytics → delete succeeds |

Run everything with `powershell -File scripts/verify.ps1` from the repository root, then start the API and run the smoke test.

## Manual workflow checks

1. Register two accounts in two browsers.
2. Create a family with account A; copy the invite code.
3. Join the family with account B.
4. Run a high-risk message scan as A; confirm B sees the family alert.
5. As B, mark the alert reviewed; confirm A sees the updated status.
6. Filter history by risk level, search by keyword, open details, delete a scan.
7. Confirm dashboard numbers change after scanning/deleting.
8. Confirm no OTP-like value entered in a message appears in history or indicator text.
9. Disable `GROQ_API_KEY` and confirm explanations still appear with a fallback label.
10. Remove ML artifacts and confirm scans still work with `engine: rules`.

## Security checks

- Attempt to read another family's scans or alerts with a non-member token → 403/404.
- Attempt role change as a member → 403.
- Submit an oversized message/URL → 422.
- Send more than the configured number of scans per minute → 429.
- Inspect frontend bundle → no API keys present.
- Submit an IP-based URL → flagged, and no browser navigation occurs.
