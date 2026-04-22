---
title: HyProNet Installation Guide
sidebar_position: 2
description: Detailed Windows and macOS installation, environment setup, workbook import, and real solver connectivity guide for the current HyProNet application.
---

## Overview

This guide explains how to install the required environment and run the current HyProNet application from the `Plant-Modelling` / `capstone` repository.

The current workflow is:

1. Clone the repository.
2. Install the local development environment.
3. Prepare the `.env` file.
4. Install Node.js dependencies for the backend and frontend.
5. Import a system Excel workbook into PostgreSQL and MongoDB.
6. Start the web application.
7. Use the GUI to create, edit, verify, and run diagrams.

## Repository and Branch

The current repository used by this guide is:

```text
https://github.com/bluehydrogenplant123/Plant-Modelling.git
```

For this setup, users should work on the following branch:

```text
stable-version6.1-apr-6
```

In the current remote, that branch is available as:

```text
origin/feature/stable-version6.1-apr-6
```

Clone the repository first, then switch to the required working branch.

## Recommended Local Location

The examples in this guide use the following local paths:

- Windows (PowerShell): `$HOME\Projects\capstone`
- Windows (Git Bash): `~/Projects/capstone`
- macOS: `~/Projects/capstone`

The main application directory is:

- Windows (PowerShell): `$HOME\Projects\capstone\src`
- Windows (Git Bash): `~/Projects/capstone/src`
- macOS: `~/Projects/capstone/src`

## Software Required on Both Systems

HyProNet currently requires:

- Git
- Node.js
- npm
- Docker Desktop
- Bash

The repository scripts use `.sh` files, so a Bash-compatible shell is required.

Where a command must be run in a specific terminal, this guide labels it explicitly as one of the following:

- `PowerShell`
- `PowerShell (Administrator)`
- `Git Bash`
- `macOS Terminal`

## Windows Installation

### Windows Requirements

Before installing the project dependencies, confirm the following:

- You are using a Docker Desktop-supported Windows version.
- Docker Desktop will use `WSL 2`.
- You can run PowerShell as Administrator.
- Hardware virtualization is enabled in BIOS/UEFI.
- The machine has enough RAM for Docker Desktop, the databases, and the import process.

Docker's current Windows guidance requires a recent Windows version and WSL 2 support.
Docker's Windows requirements also depend on hardware virtualization being enabled and sufficient system memory being available.

### Step 1: Install Git, Node.js LTS, WSL, and Docker Desktop with Package Managers

Open **PowerShell as Administrator** and run:

Terminal: **PowerShell (Administrator)**

```powershell
winget install --id Git.Git -e --source winget
winget install --id OpenJS.NodeJS.LTS -e --source winget
wsl --install
wsl --update
winget install --id Docker.DockerDesktop -e --source winget
```

Notes:

- `Git.Git`, `OpenJS.NodeJS.LTS`, and `Docker.DockerDesktop` were verified from `winget` on April 21, 2026.
- `wsl --install` may require a restart.
- If WSL is already installed, `wsl --install` may report that no action is needed.
- Installing `Git.Git` installs **Git for Windows**, which includes **Git Bash**.

### Step 1A: Install Git Bash with `winget`

If you want the shortest Windows setup, install Git for Windows from **PowerShell as Administrator**:

Terminal: **PowerShell (Administrator)**

```powershell
winget install --id Git.Git -e --source winget
```

After installation, Git Bash is usually available from the Start menu as:

```text
Git Bash
```

You can verify the installation from PowerShell:

Terminal: **PowerShell**

```powershell
git --version
```

### Step 1B: Install Git Bash Manually from the Official Installer

If you prefer the normal graphical installer, download **Git for Windows** from the official Git download page:

```text
https://git-scm.com/download/win
```

That download redirects to the official **Git for Windows** installer, which includes **Git Bash**.

Then:

1. Run the downloaded installer.
2. Keep the default install location unless your lab or company requires another path.
3. On the component selection screen, leave **Git Bash Here** enabled.
4. On the PATH screen, the default recommended option is usually the safest choice.
5. Finish the installation.

After installation, open **Start** and search for:

```text
Git Bash
```

You can also right-click in a folder in File Explorer and use:

```text
Open Git Bash here
```

If `winget` cannot be used and you already downloaded `Docker Desktop Installer.exe`, install Docker Desktop from that local installer with:

Terminal: **PowerShell (Administrator)**

```powershell
Start-Process 'Docker Desktop Installer.exe' -Wait install
```

After the installation, restart Windows if prompted.

### Step 2: Add Your User to the `docker-users` Group If Needed

This is required when:

- your administrator account is different from your normal user account, or
- your setup needs Docker Desktop features that require higher privileges

If that applies, run this in **PowerShell as Administrator**:

Terminal: **PowerShell (Administrator)**

```powershell
net localgroup docker-users $env:USERNAME /add
```

Then sign out and sign back in.

### Step 3: Start Docker Desktop

Start Docker Desktop from the Start menu and wait until it shows that Docker is running.

You can also launch it from PowerShell:

Terminal: **PowerShell**

```powershell
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
```

That path assumes Docker Desktop was installed in the default location.

### Step 4: Verify the Installation

Open a new **PowerShell** window and run:

Terminal: **PowerShell**

```powershell
git --version
node --version
npm --version
wsl --version
docker --version
docker compose version
docker info
```

If `docker info` fails, Docker Desktop is not ready yet.

If Docker Desktop does not start at all on Windows, the most common causes are:

- WSL 2 is not installed correctly
- hardware virtualization is disabled in BIOS/UEFI
- the Windows hypervisor is disabled at startup
- the machine does not have enough available memory

### Step 5: Choose the Shell for Running the Repository Scripts

For the HyProNet repository itself, use one of these:

- `Git Bash` (recommended)
- `WSL`

The remaining Windows commands below assume you are using **Git Bash**.

If you just installed Git Bash and want to open it immediately from PowerShell, try:

Terminal: **PowerShell**

```powershell
Start-Process "$env:ProgramFiles\Git\git-bash.exe"
```

### Step 5A: Prevent Git Bash from Rewriting Docker Path Arguments

If you run this project from **Git Bash on Windows**, it is recommended to disable Git Bash path conversion for the current shell session before running the project scripts.

Why this matters:

- This repository uses Docker commands inside shell scripts.
- Git Bash can sometimes rewrite Linux-style path arguments automatically.
- That can interfere with Docker commands that expect container paths such as `/app/...`.

This setting is recommended for:

- Windows + `Git Bash`

This setting is usually **not** needed for:

- Windows + `WSL`
- macOS

To set it for the current Git Bash session only, run:

Terminal: **Git Bash**

```bash
export MSYS_NO_PATHCONV=1
```

Then continue with the normal project commands in the same Git Bash window.

If you want to make it persistent for future Git Bash sessions, run:

Terminal: **Git Bash**

```bash
echo 'export MSYS_NO_PATHCONV=1' >> ~/.bashrc
source ~/.bashrc
```

If you later want to remove it from your Git Bash startup file, open `~/.bashrc` and delete that line.

### Step 6: Create a Working Folder and Clone the Repository

Open **PowerShell** and run:

Terminal: **PowerShell**

```powershell
New-Item -ItemType Directory -Force -Path "$HOME\Projects"
Set-Location "$HOME\Projects"
git clone https://github.com/bluehydrogenplant123/Plant-Modelling.git capstone
Set-Location .\capstone
```

To move onto the required working branch, run:

Terminal: **PowerShell**

```powershell
git switch -c stable-version6.1-apr-6 --track origin/feature/stable-version6.1-apr-6
```

To update an existing local copy later, use:

Terminal: **PowerShell**

```powershell
Set-Location "$HOME\Projects\capstone"
git switch stable-version6.1-apr-6
git pull
```

### Step 7: Go to the Repository in Bash

In **Git Bash**, run:

Terminal: **Git Bash**

```bash
cd ~/Projects/capstone
```

If you cloned the repository into another folder, replace the path accordingly.

### Step 8: Create the Environment File

If `src/.env` does not exist, create it from the example:

Terminal: **Git Bash**

```bash
cp src/.env.example src/.env
```

If you prefer PowerShell, the equivalent command is:

Terminal: **PowerShell**

```powershell
Copy-Item .\src\.env.example .\src\.env
```

### Step 9: Review the Main Environment Variables

Open `src/.env` and verify the important values:

```env
PORT=3000
DATABASE_URL_POSTGRES="postgresql://capstone:capstone@localhost:5434/capstone"
DATABASE_URL_MONGO="mongodb://localhost:27017/capstone?replicaSet=rs0"
REDIS_HOST=127.0.0.1
REDIS_PORT=6380
REDIS_PASSWORD=capstone
BASE_SOLVER_ENGINE_URL=http://127.0.0.1:8000/api
ALLOWED_ORIGINS=http://localhost:5173
```

Important:

- `BASE_SOLVER_ENGINE_URL` must point to a reachable solver engine if you want actual computations to run.
- If you only want to start the GUI and backend locally, the solver engine can be configured later.

### Step 10: Install Project Dependencies

From **Git Bash**, install backend dependencies:

Terminal: **Git Bash**

```bash
cd ~/Projects/capstone/src
npm install
```

Then install frontend dependencies:

Terminal: **Git Bash**

```bash
cd ~/Projects/capstone/src/src/frontend
npm install
```

### Step 11: Put the Workbook into `src/excel-sheets`

Copy the workbook you want to import into:

```text
~/Projects/capstone/src/excel-sheets/
```

Example workbook names already present in the repository may include:

- `nov-19-2024.xlsx`
- `jan-30-2026.xlsx`
- `mar-18-2026.xlsx`
- `apr-6-2026.xlsx`

### Step 12: Initialize the Databases and Import the Workbook

Return to the `src` directory:

Terminal: **Git Bash**

```bash
cd ~/Projects/capstone/src
```

Run the import script:

Terminal: **Git Bash**

```bash
bash run-all.sh apr-6-2026.xlsx
```

This script will:

1. Start MongoDB, PostgreSQL, and Redis through Docker Compose.
2. Wait for the databases to become available.
3. Run Prisma migrations for PostgreSQL and MongoDB.
4. Start the Python import container.
5. Convert the workbook into normalized CSV files.
6. Import the workbook data into the databases.

If you want a single bootstrap command from the repository root instead, run:

Terminal: **Git Bash**

```bash
cd ~/Projects/capstone
bash init.sh apr-6-2026.xlsx
```

`init.sh` will:

- create `src/.env` if needed
- run `npm install` in `src`
- run `npm install` in `src/src/frontend`
- call `run-all.sh`

After `init.sh` finishes, you still need to start the application manually.

### Step 13: Start the Application

From `src`, run:

Terminal: **Git Bash**

```bash
cd ~/Projects/capstone/src
npm run dev
```

This starts both:

- the backend server
- the frontend development server

### Step 14: Open the Application

Open these URLs in your browser:

- Frontend GUI: `http://localhost:5173`
- Backend API: `http://localhost:3000/api`
- Swagger docs: `http://localhost:3000/api-docs`
- Queue admin UI: `http://localhost:3000/admin/queues`

### Windows Quick Start From a Fresh Machine

If you are starting from a machine that does not yet have the repository locally, use:

Terminal: **Git Bash**

```bash
mkdir -p ~/Projects
cd ~/Projects
git clone https://github.com/bluehydrogenplant123/Plant-Modelling.git capstone
cd ~/Projects/capstone
git switch -c stable-version6.1-apr-6 --track origin/feature/stable-version6.1-apr-6
cp src/.env.example src/.env
cd ~/Projects/capstone/src
npm install
cd ~/Projects/capstone/src/src/frontend
npm install
cd ~/Projects/capstone/src
export MSYS_NO_PATHCONV=1
bash run-all.sh apr-6-2026.xlsx
npm run dev
```

## macOS Installation

### macOS Requirements

Before installing the environment, confirm the following:

- You have administrator access on the Mac.
- You can use Terminal.
- Docker Desktop is supported on your macOS version.

If you install Docker Desktop with Homebrew, note that the current Homebrew `docker-desktop` cask targets recent macOS releases. If that cask is unavailable on your machine, install Docker Desktop from the official `.dmg` instead.

### Step 1: Install Xcode Command Line Tools

Open **Terminal** and run:

Terminal: **macOS Terminal**

```bash
xcode-select --install
```

If the tools are already installed, macOS will tell you.

### Step 2: Install Homebrew

Run the official Homebrew install command:

Terminal: **macOS Terminal**

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Then load Homebrew into your shell.

For **Apple Silicon Macs**:

Terminal: **macOS Terminal**

```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

For **Intel Macs**:

Terminal: **macOS Terminal**

```bash
echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/usr/local/bin/brew shellenv)"
```

### Step 3: Install Git, Node.js, and Docker Desktop with Homebrew

Run:

Terminal: **macOS Terminal**

```bash
brew update
brew install git
brew install node
brew install --cask docker-desktop
```

If you need to install Docker Desktop from the official `.dmg` instead, first download `Docker.dmg`, then install from that local disk image:

Terminal: **macOS Terminal**

```bash
sudo hdiutil attach Docker.dmg
sudo /Volumes/Docker/Docker.app/Contents/MacOS/install
sudo hdiutil detach /Volumes/Docker
```

### Step 4: Start Docker Desktop

Launch Docker Desktop:

Terminal: **macOS Terminal**

```bash
open -a Docker
```

Wait until Docker Desktop shows that Docker is running.

If you expect to run larger imports or multiple containers, also review Docker Desktop resource settings after startup:

- Docker Desktop `Settings`
- `Resources`
- `Advanced` where available on your platform

If the environment feels slow or containers stop unexpectedly, Docker's documentation recommends increasing memory and disk allocation for heavier workloads.

### Step 5: Verify the Installation

Run:

Terminal: **macOS Terminal**

```bash
git --version
node --version
npm --version
docker --version
docker compose version
docker info
```

If `docker info` fails, Docker Desktop is not ready yet.

### Step 6: Create a Working Folder and Clone the Repository

Run:

Terminal: **macOS Terminal**

```bash
mkdir -p ~/Projects
cd ~/Projects
git clone https://github.com/bluehydrogenplant123/Plant-Modelling.git capstone
cd capstone
```

To move onto the required working branch, run:

Terminal: **macOS Terminal**

```bash
git switch -c stable-version6.1-apr-6 --track origin/feature/stable-version6.1-apr-6
```

To update an existing local copy later, use:

Terminal: **macOS Terminal**

```bash
cd ~/Projects/capstone
git switch stable-version6.1-apr-6
git pull
```

### Step 7: Create the Environment File

If `src/.env` does not exist, create it:

Terminal: **macOS Terminal**

```bash
cp src/.env.example src/.env
```

### Step 8: Review the Main Environment Variables

Open `src/.env` and check:

```env
PORT=3000
DATABASE_URL_POSTGRES="postgresql://capstone:capstone@localhost:5434/capstone"
DATABASE_URL_MONGO="mongodb://localhost:27017/capstone?replicaSet=rs0"
REDIS_HOST=127.0.0.1
REDIS_PORT=6380
REDIS_PASSWORD=capstone
BASE_SOLVER_ENGINE_URL=http://127.0.0.1:8000/api
ALLOWED_ORIGINS=http://localhost:5173
```

If your solver engine is running on another machine or port, update `BASE_SOLVER_ENGINE_URL`.

### Step 9: Install Project Dependencies

Install backend dependencies:

Terminal: **macOS Terminal**

```bash
cd ~/Projects/capstone/src
npm install
```

Install frontend dependencies:

Terminal: **macOS Terminal**

```bash
cd ~/Projects/capstone/src/src/frontend
npm install
```

### Step 10: Put the Workbook into `src/excel-sheets`

Place the workbook file into:

```text
~/Projects/capstone/src/excel-sheets/
```

### Step 11: Initialize the Databases and Import the Workbook

Run:

Terminal: **macOS Terminal**

```bash
cd ~/Projects/capstone/src
bash run-all.sh apr-6-2026.xlsx
```

This starts MongoDB, PostgreSQL, and Redis, runs Prisma migrations, and imports the workbook into the databases.

If you want to use the helper script from the repository root instead:

Terminal: **macOS Terminal**

```bash
cd ~/Projects/capstone
bash init.sh apr-6-2026.xlsx
```

### Step 12: Start the Application

Run:

Terminal: **macOS Terminal**

```bash
cd ~/Projects/capstone/src
npm run dev
```

### Step 13: Open the Application

Open:

- Frontend GUI: `http://localhost:5173`
- Backend API: `http://localhost:3000/api`
- Swagger docs: `http://localhost:3000/api-docs`
- Queue admin UI: `http://localhost:3000/admin/queues`

### macOS Quick Start From a Fresh Machine

If you are starting from a machine that does not yet have the repository locally, use:

Terminal: **macOS Terminal**

```bash
mkdir -p ~/Projects
cd ~/Projects
git clone https://github.com/bluehydrogenplant123/Plant-Modelling.git capstone
cd ~/Projects/capstone
git switch -c stable-version6.1-apr-6 --track origin/feature/stable-version6.1-apr-6
cp src/.env.example src/.env
cd ~/Projects/capstone/src
npm install
cd ~/Projects/capstone/src/src/frontend
npm install
cd ~/Projects/capstone/src
bash run-all.sh apr-6-2026.xlsx
npm run dev
```

## Using a Real Solver Engine with VS Code Port Forwarding

When HyProNet talks to a real computation / solver engine, there are **two different URLs** in `src/.env` that matter:

```env
BASE_SOLVER_ENGINE_URL=http://127.0.0.1:8000/api
BASE_EXTERNAL_URL=http://localhost:3000/api/external
```

They do different jobs:

- `BASE_SOLVER_ENGINE_URL`
  - where HyProNet sends computation requests
- `BASE_EXTERNAL_URL`
  - the public callback URL that the solver engine uses to send results back to HyProNet

For the VS Code **Ports** workflow shown in the screenshot, the relevant port is **3000**, not `8000`.

Why:

- HyProNet's backend runs on port `3000`
- the callback route is under `/api/external/compute/callback`
- the solver engine must be able to reach that callback URL from outside the local machine

So if you are using VS Code port forwarding, the port you need to forward and make public is the **backend port `3000`**, and the resulting public URL should be written into `BASE_EXTERNAL_URL`.

![VS Code Ports Example](./images/vscode-ports-example.svg)

### Example Procedure

Assume:

- HyProNet backend is running on port `3000`
- the real solver engine can already be reached separately
- you need to expose HyProNet's callback endpoint publicly

In VS Code:

1. Open the **Ports** panel.
2. Add port `3000` if it is not already listed.
3. Change **Visibility** to **Public**.
4. Copy the **Forwarded Address**.

If VS Code gives you a forwarded address such as:

```text
https://example-3000.use.devtunnels.ms/
```

then update `src/.env` to:

```env
BASE_EXTERNAL_URL=https://example-3000.use.devtunnels.ms/api/external
```

At the same time, keep `BASE_SOLVER_ENGINE_URL` pointed at the real solver engine API endpoint.

Example:

```env
BASE_SOLVER_ENGINE_URL=http://127.0.0.1:8000/api
BASE_EXTERNAL_URL=https://example-3000.use.devtunnels.ms/api/external
```

If your forwarded URL already ends with `/api/external`, use it directly and do not append `/api/external` a second time.

### Where to Change It

Open:

```text
src/.env
```

Then replace the external callback line with the forwarded public URL, for example:

```env
BASE_EXTERNAL_URL=https://example-3000.use.devtunnels.ms/api/external
```

### Why This Is Required

HyProNet sends computation requests to the solver engine through `BASE_SOLVER_ENGINE_URL`, but the solver engine sends the final callback back to HyProNet through `BASE_EXTERNAL_URL`.

If `BASE_EXTERNAL_URL` is wrong, private, or not publicly reachable, computations can fail even if:

- the GUI opens normally
- the backend starts correctly
- the workbook import succeeds

## How to Use the Application After Startup

Once the app is running, the normal workflow is:

1. Open the GUI in the browser.
2. Create a new diagram or open an existing one.
3. Add nodes, ports, and connections.
4. Edit materials, run settings, and other runtime data.
5. Save the diagram.
6. Verify the diagram.
7. Select the calculation type, solver, and algorithm settings.
8. Run the computation.
9. Review the results and run history.

## Data Architecture Summary

The current system separates imported system definitions from user runtime data:

- PostgreSQL stores the imported system metadata.
- MongoDB stores runtime diagram and user session data.
- Redis supports queue handling and task dispatch.
- The external solver engine performs the actual optimization or computation.

## Troubleshooting

### `winget` is not available on Windows

Update App Installer from Microsoft Store, or install the tools manually from their official installers.

### Docker Desktop starts but `docker info` fails

Wait another minute and try again:

Terminal: **Git Bash**, **WSL**, or **macOS Terminal**

```bash
docker info
```

Docker Desktop may still be initializing in the background.

### Docker Desktop does not start because virtualization is not available

On Windows, Docker Desktop depends on WSL 2 and hardware virtualization.

Check:

- virtualization is enabled in BIOS/UEFI
- WSL 2 is installed and updated
- the Windows hypervisor is enabled at boot

Useful checks:

Terminal: **PowerShell**

```powershell
wsl --status
systeminfo
bcdedit /enum | findstr hypervisorlaunchtype
```

If the hypervisor is installed but disabled at startup, run this in **PowerShell as Administrator**:

Terminal: **PowerShell (Administrator)**

```powershell
bcdedit /set hypervisorlaunchtype auto
```

Then restart Windows.

### Docker Desktop runs, but memory is too low

If workbook import is very slow, containers exit unexpectedly, or Docker Desktop feels unstable, the machine may not have enough memory available for:

- Docker Desktop
- PostgreSQL
- MongoDB
- Redis
- the Python import container
- the frontend and backend dev servers

What to check:

- close other heavy applications
- confirm the host machine has enough free RAM
- review Docker Desktop resource settings

On platforms where Docker Desktop exposes resource limits in the UI, check:

- `Settings`
- `Resources`
- `Advanced`

If your platform exposes a memory limit there, increase it before rerunning:

Terminal: **Git Bash**, **WSL**, or **macOS Terminal**

```bash
bash run-all.sh apr-6-2026.xlsx
```

Docker Desktop also has a **Resource Saver** feature that reduces CPU and memory usage when Docker is idle. This is useful normally, but if Docker has just resumed from idle, give it a moment to become responsive before retrying commands.

### `bash run-all.sh ...` says the Excel file does not exist

Make sure the workbook is in:

- Windows: `~/Projects/capstone/src/excel-sheets`
- macOS: `~/Projects/capstone/src/excel-sheets`

and that the filename matches exactly.

### Prisma or database migration commands fail

Check:

- `src/.env`
- Docker container status
- whether ports `5434`, `27017`, and `6380` are already in use

You can inspect running containers with:

Terminal: **Git Bash**, **WSL**, or **macOS Terminal**

```bash
docker ps
```

### Workbook import fails

Check the import logs:

Terminal: **Git Bash** on Windows, or **macOS Terminal** on Mac

```bash
cd ~/Projects/capstone/src/excel-migration/logs
ls
```

### The GUI opens but computation does not run

Most often this means the solver engine is not reachable.

Check both `BASE_SOLVER_ENGINE_URL` and `BASE_EXTERNAL_URL` in `src/.env`.

Then verify:

- the solver engine is actually running at `BASE_SOLVER_ENGINE_URL`
- the backend callback URL in `BASE_EXTERNAL_URL` is reachable from the solver-engine side

If the solver engine is hosted through VS Code port forwarding, also verify:

- port `3000` was forwarded for the HyProNet backend callback
- the port visibility is set to **Public**
- the copied URL was written into `BASE_EXTERNAL_URL`
- `/api/external` was appended only when needed

### You want to check the available API routes

Open:

```text
http://localhost:3000/api-docs
```

### You want to inspect queue or task behavior

Open:

```text
http://localhost:3000/admin/queues
```
