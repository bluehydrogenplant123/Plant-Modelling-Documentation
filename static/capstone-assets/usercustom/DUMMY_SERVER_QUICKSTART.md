# Dummy Server Quickstart

Simple steps to run the app with the local dummy solver.

## 1. Set dummy mode in `src/.env`

Use these values:

```env
REDIS_PORT=6380
BASE_SOLVER_ENGINE_URL=http://127.0.0.1:8000/api
BASE_EXTERNAL_URL=http://localhost:3000/api/external
SAVE_JSON_FILES=true
```

## 2. Start database + Redis

From `src`:

```bash
docker compose up -d mongo-single postgres redis
npm install
npm run migrate:postgres
npm run migrate:mongodb
```

## 3. Start dummy solver (2 terminals)

From `Computation-Dummy-Server`:

Terminal A:

```bash
python manage.py runserver 127.0.0.1:8000
```

Terminal B:

```bash
celery -A config worker --loglevel=info --pool=solo
```

## 4. Start backend + frontend

From `src`:

```bash
npm run dev
```

## 5. Quick check

- Run one compute from UI.
- Confirm backend log shows solver URL `http://127.0.0.1:8000/api/solve/`.
- Confirm `src/src/backend/services/solve_request.json` is updated.
