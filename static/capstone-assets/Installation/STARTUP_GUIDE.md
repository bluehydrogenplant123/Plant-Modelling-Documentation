---
title: HyProNet Streamlined Guide
sidebar_position: 3
description: Concise installation, first-time setup, startup, shutdown, and update guide for the current HyProNet application.
---

This page is the streamlined setup and startup guide for the current HyProNet application.

If you need the full Windows/macOS walkthrough with more background and troubleshooting, use [HYPRONET_INSTALLATION_GUIDE](./HYPRONET_INSTALLATION_GUIDE.md).

## 1. Prerequisites

Install the following before setting up the repository:

- Git Bash
- Visual Studio Code
- Node.js LTS (20.1 or newer)
- Docker Desktop

Git Bash:

- Windows: [Git for Windows download](https://git-scm.com/downloads/win)
- macOS: Git is usually already installed, but installing the latest Git is still recommended if your local version is outdated

Visual Studio Code:

- [VS Code download](https://code.visualstudio.com/)

Node.js:

- [Node.js download](https://nodejs.org/en/download)

Docker Desktop:

- Windows: [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/)
- macOS: [Docker Desktop for Mac](https://docs.docker.com/desktop/setup/install/mac-install/)

Optional:

- A database viewer such as DBGate can be useful if you want to inspect PostgreSQL or MongoDB manually.

### Windows Git Bash Setup

If you are using **Git Bash on Windows**, run these commands one at a time in **Git Bash**:

Terminal: **Git Bash**

```bash
echo 'export MSYS_NO_PATHCONV=1' >> ~/.bashrc
source ~/.bashrc
```

This prevents Git Bash from rewriting Linux-style Docker path arguments used by the repository scripts.

## 2. Clone the Repository

Choose the drive or folder where you want to keep the project, then open **Git Bash** or **macOS Terminal** there.

Run:

```bash
git clone --branch feature/stable-version7.0-Aug-11 --single-branch https://github.com/bluehydrogenplant123/HYPRONET-GUI.git HypronetGUI
cd HypronetGUI
```

If GitHub asks you to log in, make sure you sign in with an account that has access to the repository.

## 3. Automated Windows Installer

Windows users can run the installer by double-clicking:

```text
install-hypronet.bat
```

The installer checks the Windows and virtualization requirements, installs
missing Git Bash, Node.js LTS 20.1 or newer, Docker Desktop, and WSL 2, prepares the project,
and optionally starts the application. It uses `winget`, requires internet
access, and may request administrator approval when enabling or updating WSL.

If WSL installation requires a Windows restart, restart the computer and run
`install-hypronet.bat` again. The installer is resumable and skips prerequisites
that are already available.

Before changing Docker resources, the installer offers these modes:

- **Preserve** is the default. It keeps existing labelled HyProNet database
  volumes and adopts their Docker Compose project name. Migrations and the
  selected system-workbook import still run against the preserved databases.
- **Clean** displays the exact HyProNet containers and volumes it found and
  requires typing `RESET` before deletion. This permanently removes locally
  stored diagrams and database records in those volumes.

The installer never runs a global Docker prune and does not remove shared
MongoDB, PostgreSQL, Redis, or Metabase images. Fixed-name containers that are
unlabelled or have unexpected Compose ownership or images cause a safe stop for
manual review.

Command-line usage is also supported:

```powershell
.\install-hypronet.bat `
  -CleanupMode Prompt `
  -Workbook Aug-24-2026.xlsx `
  -CertificateMode Prompt `
  -LaunchMode Prompt
```

Valid modes are:

- `-CleanupMode Prompt|Preserve|Clean`
- `-CertificateMode Prompt|Default|WindowsStore`
- `-LaunchMode Prompt|Launch|Skip`
- `-Workbook <filename>` for a file directly inside `src/excel-sheets`
- `-DryRun` to inspect and report planned actions without installing packages,
  writing project configuration, changing Docker resources, importing data, or
  launching the application

When `-CertificateMode Prompt` is used, the installer asks whether npm needs
company network certificate support. Choose **Yes** if npm previously reported
`UNABLE_TO_GET_ISSUER_CERT_LOCALLY`. The `WindowsStore` mode makes Node.js use
certificate authorities trusted by Windows for that installer process and
tests `npm ping` with strict SSL verification before dependency installation.
It does not set `strict-ssl=false`, does not use
`NODE_TLS_REJECT_UNAUTHORIZED=0`, and does not persistently change npm or Node
configuration. `Default` uses Node.js certificate handling without this option.

If `WindowsStore` is selected but the certificate check still fails, company
IT must install the HTTPS-inspection certificate in Windows Trusted Root
Certification Authorities or provide a PEM certificate that can be configured
with npm's `cafile` setting. Older Node.js versions that do not support the
Windows certificate store must be upgraded to the current LTS release.

Installer logs are written to:

```text
%LOCALAPPDATA%\HyProNet\logs
```

After a completed system-workbook import, the installer reviews the generated
`src/excel-migration/logs/log_<timestamp>.log`. Logged row-level data issues are
shown as prominent warnings, including a preview and the complete log path, but
they do not prevent Metabase setup or optional application launch. The final
installer status says **completed with workbook import warnings** because
affected workbook data or models may be incomplete. A missing import log, a
Python traceback, or a nonzero migration/import command still stops the
installer with a nonzero exit code.

Database initialization polls PostgreSQL and MongoDB readiness instead of
assuming they are ready after a fixed delay. If Docker Desktop briefly exposes
PostgreSQL's host port before Prisma can use it, the PostgreSQL migration is
retried for `P1001` connectivity failures. Other Prisma errors are not retried
and still stop the installer.

If Docker BuildKit reports a missing parent or extraction snapshot while
exporting `python-runner:latest`, the installer retries that image build once
with `--no-cache`. This recovery is scoped to the HyProNet image build and does
not prune global Docker build cache, images, containers, or volumes. If the
retry also fails, restart Docker Desktop and rerun the installer.

The installer does not install the calculation solver. The GUI can run without
it, but calculations require the solver configured by `BASE_SOLVER_ENGINE_URL`
in `src/.env`.

During backend and frontend dependency installation, npm HTTP fetch messages
are displayed in the installer window and copied to the installer log. A
periodic message confirms that `npm ci` is still running when a slow company
proxy delays output. The installer disables npm audit and funding notices for
these deterministic installation steps, reducing unnecessary network requests;
package versions still come from the committed lockfiles.

The remaining sections document the manual fallback procedure.

## 4. Create the `.env` File Manually

From the repository root, create `src/.env` by copying `src/.env.example`.

Terminal: **Git Bash** or **macOS Terminal**

```bash
cp src/.env.example src/.env
```

Review `src/.env` before running the app, especially if you are using a real solver engine instead of the default local setup.

## 5. Manual First-Time Setup

### Step 1: Open the Repository in VS Code

Open VS Code and open the cloned `HypronetGUI` repository folder.

### Step 2: Start Docker Desktop

Open Docker Desktop and wait until it reports that Docker is running.

### Step 3: Install Backend Dependencies

From the repository root:

```bash
cd src
npm ci
```

### Step 4: Install Frontend Dependencies

Still in the repository terminal:

```bash
cd src/frontend
npm ci
```

### Step 5: Return to `src`

```bash
cd ..
cd ..
```

### Step 6: Import the Latest System Workbook and Prepare the Databases

Run:

Terminal: **Git Bash** or **macOS Terminal**

```bash
./run-all.sh Aug-24-2026.xlsx
```

If there are import errors, check:

```text
src/excel-migration/logs/
```

### Step 7: Start the Application

From `src`, run:

```bash
npm run dev
```

When the command finishes starting, open:

```text
http://localhost:5173
```

## 6. Stopping the Application

To stop the app:

1. In the terminal running `npm run dev`, press `Ctrl + C`.
2. Open Docker Desktop and stop the containers if you do not want to keep the databases running.

## 7. Running the Application Again

On an already-installed Windows checkout, double-click:

```text
start-hypronet.bat
```

This starts Docker Desktop when needed, starts the existing HyProNet database
and Metabase containers without rerunning migrations or workbook imports,
launches `npm run dev` in a separate command window, waits for ports `3000` and
`5173`, and opens `http://localhost:5173`. If HyProNet is already listening on
both ports, it reuses that server instead of starting a duplicate. Startup logs
are stored alongside installer logs under `%LOCALAPPDATA%\HyProNet\logs`. If
only the backend or frontend survived from an earlier run, the starter waits
briefly and then starts only the missing half after verifying that the existing
Node process belongs to the current HyProNet checkout. It never kills the
existing process, and an unrelated or unverifiable port owner still causes a
safe stop.

To start without opening a browser, run from PowerShell:

```powershell
.\start-hypronet.bat -NoBrowser
```

For a manual restart:

1. Open Docker Desktop and make sure the required containers are running.
2. Open the project in a terminal.
3. Go to `src`.
4. Start the app again.

```bash
cd src
npm run dev
```

## 8. Updating the Application from GitHub

Be careful when resetting or deleting containers: current diagrams and local runtime data may be lost if you remove the existing databases.

Recommended update flow:

### Step 1: Stop the Application

Stop `npm run dev` with `Ctrl + C`.

### Step 2: Pull the Latest Code

From the repository root:

```bash
git switch feature/stable-version7.0-Aug-11
git pull
```

### Step 3: Re-run the Workbook Import and Migrations

Go to `src`:

```bash
cd src
```

Then run:

Terminal: **Git Bash** or **macOS Terminal**

```bash
./run-all.sh Aug-24-2026.xlsx
```

Again, replace `Aug-24-2026.xlsx` with the latest workbook in `src/excel-sheets/` when a newer workbook is released.

Only remove containers first if you intentionally want a clean reset. If you do that, assume local diagrams and runtime data may be lost unless you have backed them up elsewhere.

### Step 4: Start the Server Again

```bash
npm run dev
```

## 9. Real Solver Notes

If you are using a real solver instead of the local default solver endpoint,
review these values in `src/.env`:

```env
BASE_SOLVER_ENGINE_URL=http://127.0.0.1:8000/api
BASE_EXTERNAL_URL=http://localhost:3000/api/external
```

Rules:

- `BASE_SOLVER_ENGINE_URL` should point to the actual solver API
- `BASE_EXTERNAL_URL` should point to the public callback base URL of the HyProNet backend
- the backend can be exposed directly with Microsoft Dev Tunnels CLI; VS Code is not required
- host the actual backend `PORT` (default `3000`) with `devtunnel host -p 3000 --allow-anonymous`
- write the temporary public tunnel URL into `BASE_EXTERNAL_URL`
- do not append `/compute/callback/`; the backend appends that automatically

For the complete installation, temporary-tunnel security boundary, route checks,
compute acceptance chain, and failure classification, see:

- [Real Solver Quickstart](./REAL_SERVER_QUICKSTART.md)

Example:

```env
BASE_SOLVER_ENGINE_URL=https://<real-solver-host>/api
BASE_EXTERNAL_URL=https://<public-3000-host>/api/external
```

For more detail, see [HYPRONET_INSTALLATION_GUIDE](./HYPRONET_INSTALLATION_GUIDE.md).

## 10. Related Pages

- [REAL_SERVER_QUICKSTART](./REAL_SERVER_QUICKSTART.md)
- [HYPRONET_INSTALLATION_GUIDE](./HYPRONET_INSTALLATION_GUIDE.md)
