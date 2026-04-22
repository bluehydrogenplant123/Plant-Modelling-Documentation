---
title: HyProNet Streamlined Guide
sidebar_position: 3
description: Short setup path for the current HyProNet application, from clone to first launch.
---

This is the short version of the setup guide for the current HyProNet application.

If you need the full Windows/macOS walkthrough, use [HYPRONET_INSTALLATION_GUIDE](./HYPRONET_INSTALLATION_GUIDE.md).

## 1. Prerequisites

Install these first:

- Git
- Node.js LTS
- Docker Desktop
- Bash

Platform notes:

- On Windows, use **Git Bash** or **WSL** for repository scripts.
- On macOS, the normal Terminal is fine.
- If you use **Git Bash on Windows**, run this before the repository scripts:

```bash
export MSYS_NO_PATHCONV=1
```

## 2. Clone the Repository and Switch to the Working Branch

Terminal: **Git Bash** or **macOS Terminal**

```bash
git clone https://github.com/bluehydrogenplant123/Plant-Modelling.git capstone
cd capstone
git fetch origin
git switch -c stable-version6.1-apr-6 --track origin/feature/stable-version6.1-apr-6
```

If you already have the repository:

```bash
git switch stable-version6.1-apr-6
git pull
```

## 3. Pick the Workbook You Want to Import

Workbooks are stored in:

```text
src/excel-sheets/
```

For a first local run, you can use the repository example:

```text
apr-6-2026.xlsx
```

## 4. Run the Fastest Setup Path

From the repository root:

Terminal: **Git Bash** or **macOS Terminal**

```bash
bash init.sh apr-6-2026.xlsx
```

This script does the following:

- creates `src/.env` from `src/.env.example` if needed
- installs dependencies in `src`
- installs dependencies in `src/src/frontend`
- starts MongoDB, PostgreSQL, and Redis with Docker
- runs Prisma migrations
- imports the Excel workbook into the databases

Then start the app:

Terminal: **Git Bash** or **macOS Terminal**

```bash
cd src
npm run dev
```

## 5. Open the Application

After `npm run dev` starts successfully, open:

- GUI: `http://localhost:5173`
- Swagger/API docs: `http://localhost:3000/api-docs`
- Queue admin: `http://localhost:3000/admin/queues`

## 6. Real Solver Setup

If you want actual computations, check these two values in `src/.env`:

```env
BASE_SOLVER_ENGINE_URL=http://127.0.0.1:8000/api
BASE_EXTERNAL_URL=http://localhost:3000/api/external
```

What they mean:

- `BASE_SOLVER_ENGINE_URL` is the solver engine API endpoint
- `BASE_EXTERNAL_URL` is the public callback base URL for the HyProNet backend

If you are using a real remote solver:

- replace `BASE_SOLVER_ENGINE_URL` with the real solver API URL
- if the solver needs to call back into your local backend, expose backend port `3000`
- write the resulting public `3000` URL into `BASE_EXTERNAL_URL`
- do not append `/compute/callback/`; the backend builds that path automatically

Example:

```env
BASE_SOLVER_ENGINE_URL=https://<real-solver-host>/api
BASE_EXTERNAL_URL=https://<public-3000-host>/api/external
```

If you need the full callback and port-forwarding explanation, use [REAL_SERVER_QUICKSTART](./REAL_SERVER_QUICKSTART.md) and [HYPRONET_INSTALLATION_GUIDE](./HYPRONET_INSTALLATION_GUIDE.md).

## 7. Quick Troubleshooting

- If `bash init.sh ...` fails immediately, make sure Docker Desktop is open and fully started.
- If Docker will not start on Windows, check WSL 2, hardware virtualization, and Docker Desktop memory settings.
- If Git Bash rewrites Docker path arguments on Windows, set `MSYS_NO_PATHCONV=1`.
- If the GUI opens but computations fail, check both `BASE_SOLVER_ENGINE_URL` and `BASE_EXTERNAL_URL`.
- If workbook import fails, review the logs under `src/excel-migration/logs/`.

## 8. Related Pages

- [HYPRONET_INSTALLATION_GUIDE](./HYPRONET_INSTALLATION_GUIDE.md)
- [DUMMY_SERVER_QUICKSTART](./DUMMY_SERVER_QUICKSTART.md)
- [REAL_SERVER_QUICKSTART](./REAL_SERVER_QUICKSTART.md)
