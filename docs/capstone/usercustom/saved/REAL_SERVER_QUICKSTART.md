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

## 7. Docker cleanup (between test runs)

Use these commands when you want a clean local environment for real-server testing.

### 7.1 Standard cleanup (recommended)

From `src`:

```bash
docker compose down
docker compose up -d mongo-single postgres redis
```

This recreates project containers without deleting volumes.

### 7.2 Reset with fresh database volumes

From `src`:

```bash
docker compose down -v
docker compose up -d mongo-single postgres redis
npm run migrate:postgres
npm run migrate:mongodb
```

Use this when local DB state is corrupted or test data must be fully reset.

After `down -v`, domain/model seed data is empty. Re-import Excel data:

```bash
docker compose run --rm python-runner /app/run_python_import.sh "/app/excel-sheets/<excel-file>.xlsx"
```

Example:

```bash
docker compose run --rm python-runner /app/run_python_import.sh "/app/excel-sheets/jan-30-2026.xlsx"
```

Quick verify after import:
- Reopen dashboard and check `Select Domain` is no longer empty.
- If still empty, check import logs under `src/excel-migration/logs/`.

### 7.3 Optional global Docker cache cleanup

```bash
docker system prune -f
```

This removes unused containers/networks/images.  
Avoid `-a` unless you intentionally want to remove all unused images.
