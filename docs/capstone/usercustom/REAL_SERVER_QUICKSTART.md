# Real Server Quickstart

This note gives the minimal steps to run the app and connect to the real solver server.

## 1. Go to source folder

```bash
cd src
```

## 2. Install dependencies

```bash
npm install
```

## 3. Prepare local services (Mongo/Postgres/Redis)

```bash
docker compose up -d mongo-single postgres redis
npm run migrate:postgres
npm run migrate:mongodb
```

## 4. Configure real server endpoints in `.env`

Set these values in `src/.env`:

```env
BASE_SOLVER_ENGINE_URL=https://<real-solver-host>/api
BASE_EXTERNAL_URL=https://<your-public-backend-host>/api/external
SAVE_JSON_FILES=true
```

Notes:
- `BASE_EXTERNAL_URL` must be publicly reachable by the real solver (for callback).
- Do not include `/compute/callback/` in `BASE_EXTERNAL_URL`; backend appends it automatically.
- Keep URLs without trailing slash if possible.

## 5. Start the app

```bash
npm run dev
```

This starts backend and frontend together.

## 6. Quick connection check

- Trigger one compute from the UI.
- Confirm request file is generated: `src/src/backend/services/solve_request.json`.
- Confirm callback file is updated: `src/src/backend/routes/external/callback_response.json`.
- Backend logs should show:
  - solver request URL (`.../api/solve/`)
  - callback status (`success` or `failed`)
