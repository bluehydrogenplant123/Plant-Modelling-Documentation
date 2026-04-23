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
- Node.js LTS
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
git clone https://github.com/bluehydrogenplant123/Plant-Modelling.git capstone
cd capstone
git fetch origin
git switch -c stable-version6.1-apr-6 --track origin/feature/stable-version6.1-apr-6
```

If GitHub asks you to log in, make sure you sign in with an account that has access to the repository.

## 3. Create the `.env` File

From the repository root, create `src/.env` by copying `src/.env.example`.

Terminal: **Git Bash** or **macOS Terminal**

```bash
cp src/.env.example src/.env
```

Review `src/.env` before running the app, especially if you are using a real solver engine instead of the default local setup.

## 4. First-Time Setup

### Step 1: Open the Repository in VS Code

Open VS Code and open the cloned `capstone` repository folder.

### Step 2: Start Docker Desktop

Open Docker Desktop and wait until it reports that Docker is running.

### Step 3: Install Backend Dependencies

From the repository root:

```bash
cd src
npm install
```

### Step 4: Install Frontend Dependencies

Still in the repository terminal:

```bash
cd src/frontend
npm install
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
./run-all.sh apr-6-2026.xlsx
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

## 5. Stopping the Application

To stop the app:

1. In the terminal running `npm run dev`, press `Ctrl + C`.
2. Open Docker Desktop and stop the containers if you do not want to keep the databases running.

## 6. Running the Application Again

For a normal restart:

1. Open Docker Desktop and make sure the required containers are running.
2. Open the project in a terminal.
3. Go to `src`.
4. Start the app again.

```bash
cd src
npm run dev
```

## 7. Updating the Application from GitHub

Be careful when resetting or deleting containers: current diagrams and local runtime data may be lost if you remove the existing databases.

Recommended update flow:

### Step 1: Stop the Application

Stop `npm run dev` with `Ctrl + C`.

### Step 2: Pull the Latest Code

From the repository root:

```bash
git switch stable-version6.1-apr-6
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
./run-all.sh apr-6-2026.xlsx
```

Again, replace `apr-6-2026.xlsx` with the latest workbook in `src/excel-sheets/`.

Only remove containers first if you intentionally want a clean reset. If you do that, assume local diagrams and runtime data may be lost unless you have backed them up elsewhere.

### Step 4: Start the Server Again

```bash
npm run dev
```

## 8. Real Solver Notes

If you are using a real solver instead of the local default solver endpoint, review these values in `src/.env`:

```env
BASE_SOLVER_ENGINE_URL=http://127.0.0.1:8000/api
BASE_EXTERNAL_URL=http://localhost:3000/api/external
```

Rules:

- `BASE_SOLVER_ENGINE_URL` should point to the actual solver API
- `BASE_EXTERNAL_URL` should point to the public callback base URL of the HyProNet backend
- if you expose the backend through VS Code port forwarding, the relevant backend port is `3000`
- write the public `3000` URL into `BASE_EXTERNAL_URL`
- do not append `/compute/callback/`; the backend appends that automatically

For the step-by-step VS Code **Ports** workflow, including how to add port `3000`, set visibility, and copy the forwarded URL, see:

- [HYPRONET_INSTALLATION_GUIDE - Example Procedure](./HYPRONET_INSTALLATION_GUIDE.md#example-procedure)

Example:

```env
BASE_SOLVER_ENGINE_URL=https://<real-solver-host>/api
BASE_EXTERNAL_URL=https://<public-3000-host>/api/external
```

For more detail, see [HYPRONET_INSTALLATION_GUIDE](./HYPRONET_INSTALLATION_GUIDE.md).

## 9. Related Pages

- [HYPRONET_INSTALLATION_GUIDE](./HYPRONET_INSTALLATION_GUIDE.md)
