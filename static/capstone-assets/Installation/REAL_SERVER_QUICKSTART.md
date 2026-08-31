# Real Solver Quickstart

Use this guide to connect HyProNet to a real solver without VS Code port
forwarding. The Microsoft Dev Tunnels CLI exposes the local HyProNet backend
temporarily so the remote solver can send its callback.

On an already-installed Windows checkout, `start-hypronetGUI-remote.bat`
automates the callback tunnel and application startup described below. It asks
for the solver Dev Tunnel URL and applies both remote URLs only to the launched
server process, leaving `src/.env` unchanged.

## 1. Start the local data services

From `src`:

```bash
docker compose up -d mongo-single postgres redis
npm run migrate:postgres
npm run migrate:mongodb
```

Import the accepted workbook before computing if the local PostgreSQL database
does not already contain the required runtime catalog.

## 2. Install the Dev Tunnels CLI

The CLI is independent of VS Code.

On Windows, install it with WinGet:

```powershell
winget install Microsoft.devtunnel
```

If WinGet is unavailable, download the official standalone executable:

```powershell
$hypronetToolDir = Join-Path $env:LOCALAPPDATA 'HyProNet\Tools'
New-Item -ItemType Directory -Force -Path $hypronetToolDir | Out-Null
Invoke-WebRequest `
  -Uri 'https://aka.ms/TunnelsCliDownload/win-x64' `
  -OutFile (Join-Path $hypronetToolDir 'devtunnel.exe')
& (Join-Path $hypronetToolDir 'devtunnel.exe') --version
```

On macOS:

```bash
brew install --cask devtunnel
```

Microsoft's current installation and command references are:

- [Create and host a tunnel](https://learn.microsoft.com/azure/developer/dev-tunnels/get-started)
- [Dev Tunnels CLI reference](https://learn.microsoft.com/azure/developer/dev-tunnels/cli-commands)

## 3. Sign in once

```powershell
devtunnel user login
devtunnel user show
```

For a standalone executable, replace `devtunnel` with its full path. A browser
may open during the first login. Hosting a tunnel does not require VS Code.

## 4. Host the callback tunnel

The default HyProNet backend port is `3000`. In a separate terminal, run:

```powershell
devtunnel host -p 3000 --allow-anonymous
```

For a custom backend port, replace `3000` with the actual `PORT` value.

The command prints a URL similar to:

```text
https://example-3000.use2.devtunnels.ms
```

`--allow-anonymous` is required because the remote solver cannot complete an
interactive Microsoft login when posting a callback. It also makes the entire
forwarded backend port publicly reachable. Use a temporary tunnel only, keep
it open only for the compute test, and press `Ctrl+C` immediately afterward.
Do not use anonymous temporary tunnels as a production deployment method.

## 5. Configure `src/.env`

Use the real solver API base and the public HyProNet callback base:

```env
BASE_SOLVER_ENGINE_URL=https://<real-solver-host>/api
BASE_EXTERNAL_URL=https://example-3000.use2.devtunnels.ms/api/external
SAVE_JSON_FILES=false
```

Rules:

- `BASE_SOLVER_ENGINE_URL` is where HyProNet posts `/solve/` and `/kill/`.
- `BASE_EXTERNAL_URL` is the public HyProNet backend URL, ending in
  `/api/external`.
- Do not append `/compute/callback/`; HyProNet appends it automatically.
- Avoid a trailing slash on either base URL.
- Restart the backend after changing `src/.env`.
- `SAVE_JSON_FILES` is not required for computation. Leave it `false` for a
  normal run because debug capture writes request, callback, and result JSON
  into repository paths. Enable it only in a disposable clean worktree when
  those local artifacts are intentionally required, and do not commit them.

## 6. Start HyProNet

From `src`:

```bash
npm run dev
```

Keep the Dev Tunnels CLI process running while the computation is active.

## 7. Verify the route before computing

Check the local backend:

```powershell
curl.exe http://127.0.0.1:3000/api
```

Check the same route through the public tunnel:

```powershell
curl.exe https://example-3000.use2.devtunnels.ms/api
```

Both requests should return:

```json
{"message":"API is working"}
```

If the solver provides a health route, check it separately. For the current
HyProNet solver contract, a typical route is:

```powershell
curl.exe -H "X-Tunnel-Skip-AntiPhishing-Page: true" `
  https://<real-solver-host>/api/health/
```

A health response proves only that the server is reachable. It does not prove
that the requested solver executable is installed or that callbacks work.

## 8. Run and classify one real computation

Use a fresh test diagram and select a solver and algorithm that exist in the
diagram snapshot's run configuration. Then start the computation from the UI.

The full acceptance chain is:

1. HyProNet accepts `/api/compute/start`.
2. The queue posts to `<BASE_SOLVER_ENGINE_URL>/solve/`.
3. The solver returns `processing` and a `task_id`.
4. The solver posts to `<BASE_EXTERNAL_URL>/compute/callback/`.
5. MongoDB records a terminal task status.
6. A successful run stores computation results and the UI/API reports
   `Diagram computed successfully`.

Classify failures by the furthest completed step:

| Evidence | Meaning | Action |
| --- | --- | --- |
| Solver health is unreachable | Solver host, tunnel, VPN, firewall, or URL problem | Restore solver connectivity before testing HyProNet computation. |
| `/compute/start` returns a diagram validation error | Diagram/runtime contract blocker before dispatch | Fix the named diagram issue; do not blame the solver. |
| `/solve/` is unreachable | Solver API infrastructure blocker | Verify `BASE_SOLVER_ENGINE_URL` and the remote service. |
| `/solve/` returns a task but no callback arrives | Public callback/tunnel blocker | Verify the Dev Tunnels process and `BASE_EXTERNAL_URL`. |
| Callback says `No executable found for solver '<name>'` | Remote solver installation/configuration blocker | Install that executable on the solver host or select a configured solver. |
| Callback status is `success` and results are stored | Real compute path passed for that exact diagram, solver, algorithm, and commit | Record the exact evidence; do not generalize it to every diagram or solver. |

## 9. Stop the public tunnel

After the computation reaches a terminal status, press `Ctrl+C` in the
Dev Tunnels terminal. A temporary tunnel created by `devtunnel host -p ...` is
deleted when the host process exits.

The local databases and HyProNet server can then be stopped using the normal
project shutdown procedure.
