---
title: Excel Import Pipeline Code Explanation
sidebar_position: 32
description: Explains how HyProNet imports system Excel workbooks, normalizes workbook sheets into legacy CSV contracts, runs Prisma database setup, and writes imported reference data.
---

## Overview

The Excel import pipeline prepares HyProNet's local databases and loads system reference data from a workbook in `src/excel-sheets/`. The normal entry point is `src/run-all.sh`, which starts Docker services, runs Prisma schema setup, and then launches the Python importer inside the `python-runner` container.

The Python importer converts workbook sheets to normalized CSV files, then reads those CSV files into PostgreSQL catalog tables. It does not write user diagrams, runtime computation tasks, or solver request artifacts.

## Source Files

- `src/run-all.sh`: orchestration entry point for Docker services, Prisma setup, and workbook import.
- `src/docker-compose.yml`: defines `mongo-single`, `postgres`, `redis`, and the build/runtime configuration for `python-runner`.
- `src/package.json`: defines `migrate:postgres` and `migrate:mongodb`, which are called by `run-all.sh`.
- `src/excel-migration/Dockerfile`: builds the Python container image by copying the importer scripts into `/app`.
- `src/excel-migration/run_python_import.sh`: container-side import script that converts the workbook, redirects `migrate.py` output to a timestamped log, and removes temporary CSV output after success.
- `src/excel-migration/excel_to_csv.py`: converts workbook sheets into legacy CSV filenames and headers expected by the importer.
- `src/excel-migration/migration_normalization.py`: shared cleanup helpers for model rows, unit rows, cost rows, and stream property aliases.
- `src/excel-migration/migrate.py`: reads `csv_outputs/*.csv` and writes imported reference/configuration data into PostgreSQL.
- `src/excel-migration/requirements.txt`: Python package versions used by the importer container.
- `src/src/backend/prisma/postgres/schema.prisma`: PostgreSQL schema that receives imported catalog/configuration rows.
- `src/src/backend/prisma/mongodb/schema.prisma`: MongoDB application schema prepared before startup, but not written by the Python importer.
- `src/excel-sheets/`: workbook input directory mounted into the Python container as `/app/excel-sheets`.

## Purpose and Responsibility

This pipeline owns initial database preparation and workbook-to-database import for system metadata. It is responsible for:

- starting the required local database services;
- applying the current Prisma schemas;
- converting accepted workbook sheet names and headers into the legacy CSV contract;
- importing domain, stream, model, port, variable, unit, run configuration, color, task type, and cost configuration data into PostgreSQL;
- writing importer logs for migration failures.

It does not own frontend startup, user authentication data, saved diagrams, computation queue state, solver execution, or callback result storage. Those areas use MongoDB, Redis, and PostgreSQL at runtime after the imported catalog is available.

## Inputs and Outputs

| Input | Source | Used For |
| --- | --- | --- |
| Excel filename argument | `bash run-all.sh <workbook>.xlsx` from `src/` | Selects `/app/excel-sheets/<workbook>.xlsx` inside the Python container. |
| Workbook file | `src/excel-sheets/*.xlsx` | Source sheets for system catalog data. |
| `icons.csv` | `src/excel-sheets/icons.csv` | Replaces model `Shape` values with SVG/icon data during conversion. |
| PostgreSQL connection URL | `DATABASE_URL_POSTGRES` from Compose service environment for `python-runner` | Lets `migrate.py` connect to the `postgres` Docker service. |
| Node/Prisma environment | `src/.env` and Prisma schema files | Used by `npm run migrate:postgres` and `npm run migrate:mongodb`. |

| Output | Destination | Notes |
| --- | --- | --- |
| Docker containers | `mongo-single`, `postgres`, `redis` | Started before Prisma and import steps. |
| PostgreSQL schema and data | `postgres` database `capstone` | Prisma creates/updates schema, then `migrate.py` upserts imported catalog rows. |
| MongoDB schema | `mongo-single` database | Prepared by Prisma `db push`; Python import does not write MongoDB rows. |
| Temporary CSV files | container-local `/app/csv_outputs/` | Created by `excel_to_csv.py` and deleted after successful import. |
| Import log | host `src/excel-migration/logs/log_<timestamp>.log` | Contains redirected `migrate.py` output and traceback details. |
| Python runner image | local Docker image `python-runner:latest` | Built from `src/excel-migration/Dockerfile`; rebuild after Python importer source changes. |

## Core Data Structures and Contracts

### Workbook Sheet Contract

`excel_to_csv.py` accepts current workbook sheet names and maps them back to legacy CSV output names:

| Workbook sheet | CSV output |
| --- | --- |
| `Units` | `SYS Units.csv` |
| `Comp Task Types` | `CompTaskTypes.csv` |
| `System Variables` | `SYS System Variables.csv` |
| `Domains` | `SYSDomains.csv` |
| `Stream Properties` | `SYS Stream Properties.csv` |
| `Stream Fractions` | `SYS Stream Fractions.csv` |
| `Node Variables` | `SYSNodeVariables.csv` |
| `Node Model Library` or `SYS Node Model Library` | `SYSNodeModelLibrary.csv` |
| `Port Classes and Vars` | `SYSPortClassesandVars.csv` |
| `Run Configs` | `SYS Run Configs.csv` |
| `Node Ports Model Library` | `SYSNodePortsModelLibrary.csv` |
| `Entity Specs` | `SYS Costs.csv` |

The current `jun-16-2026.xlsx` workbook also contains sheets such as `EQ type` and `SYS Node Variable Spec`. `excel_to_csv.py` will export unmapped sheets using their original names, but `migrate.py` ignores them unless a current `process_*` function reads that CSV.

### Header and Row Normalization

`excel_to_csv.py` normalizes selected headers before writing CSV files. Important examples include:

- `Base Unit` to `BaseUnit`
- `Target Unit` to `TargetUnit`
- `Task Name` to `TaskName`
- `Port Var Name` to `PortVar Name`
- `Stream Database ID` to `StreamDatabaseId`
- `Stream Content` to `StreamContent`
- `Model Version` to `ModelVersion`
- `Hidden By Default` to `HiddenByDefault`
- `Send to Calc` to `SendtoCalc`
- `Entity` to `Entity Name`
- `Default Value` to `Cost`

For `SYS Costs.csv`, the converter also inserts a missing `Generated by` column and orders the core columns as:

```text
Generated by, Entity Name, Cost, Unit, Type
```

`migration_normalization.py` adds cleanup at import time:

- `sanitize_model_library_df(...)` drops model library rows with missing `ModelName` or `ModelVersion`.
- `sanitize_unit_conversion_df(...)` trims unit text, coerces multipliers and offsets, and drops incomplete conversion rows.
- `normalize_cost_rows(...)` trims cost config text and drops empty entity rows.
- `expand_stream_property_aliases(...)` copies stream property values from keys such as `T0`, `P0`, `H0`, and `MF0` to accepted aliases such as `T`, `TZ`, `P`, `PZ`, `H`, `HZ`, `MF`, and `MFZ` when those aliases are missing.

## Main Functions and Scripts

- `run-all.sh`: starts `mongo-single`, `postgres`, and `redis`; waits briefly; runs `npm run migrate:postgres`; runs `npm run migrate:mongodb`; then starts the `python-runner` container with the selected workbook path.
- `run_python_import.sh`: checks the workbook file, runs `python excel_to_csv.py "$EXCEL_FILE" csv_outputs`, redirects `python migrate.py` output to `logs/log_<timestamp>.log`, deletes `csv_outputs`, and prints `Process completed successfully.` on success.
- `export_excel_to_csv(...)`: iterates workbook sheets, normalizes sheet names and headers, applies icon replacement for `SYSNodeModelLibrary`, and writes CSV files.
- `load_icons_df(...)`: reads `icons.csv` from `/app/excel-sheets/icons.csv` in Docker or from the repo-local `src/excel-sheets/icons.csv` fallback for direct local runs.
- `get_db_connection()`: connects `migrate.py` to PostgreSQL using `DATABASE_URL_POSTGRES`.
- `process_streams(...)`: reads stream properties and stream fraction CSVs, builds JSON for `stream_fractions` and `properties`, upserts `Streams`, and links `DomainStreamsMapping`.
- `process_models(...)`: imports `Models` and `ModelVersion` rows, including icon/shape data and phase metadata.
- `process_ports(...)`: imports `Ports` from node variables, node-port mappings, and port class definitions.
- `process_varnames(...)`: imports `VarNames` and attaches them to matching port/model-version rows.
- `process_run_configs(...)`: imports solver and algorithm configuration rows from `SYS Run Configs.csv`.
- `process_costs(...)`: imports Economic defaults into `CostEntitiesConfig` from `SYS Costs.csv`.
- `main()` in `migrate.py`: runs the import stages in dependency order.

## Data Flow

1. A contributor places the workbook in `src/excel-sheets/`.
2. From `src/`, the contributor runs `bash run-all.sh jun-16-2026.xlsx`.
3. `run-all.sh` starts `mongo-single`, `postgres`, and `redis` through Docker Compose.
4. `npm run migrate:postgres` applies `src/src/backend/prisma/postgres/schema.prisma`.
5. `npm run migrate:mongodb` applies `src/src/backend/prisma/mongodb/schema.prisma`.
6. `docker compose run --rm python-runner /app/run_python_import.sh "/app/excel-sheets/<workbook>"` starts the importer container.
7. `run_python_import.sh` calls `excel_to_csv.py`, which writes normalized CSV files into container-local `csv_outputs/`.
8. `run_python_import.sh` calls `migrate.py` and redirects its output to `logs/log_<timestamp>.log`.
9. `migrate.py` reads known CSV files, applies normalization helpers, and writes PostgreSQL rows.
10. After success, `run_python_import.sh` deletes `csv_outputs/`, prints `Process completed successfully.`, and `run-all.sh` prints `All steps done!`.

## Database Boundaries

The Python importer writes PostgreSQL only. `migrate.py` connects through `psycopg2` and `DATABASE_URL_POSTGRES`; it does not create a MongoDB or Redis client.

PostgreSQL import targets include:

- `CompTaskTypes`
- `Domain`
- `Streams`
- `DomainStreamsMapping`
- `Models`
- `ModelVersion`
- `DomainModelMapping`
- `Colors`
- `Ports`
- `VarNames`
- `SystemVariables`
- `UnitConversion`
- `RunConfigs`
- `CostEntitiesConfig`

`ComputationResults` is also in the PostgreSQL schema, but it is runtime compute-result storage. It is not populated by the workbook importer.

MongoDB is prepared by `npm run migrate:mongodb`, which runs Prisma `db push` against `src/src/backend/prisma/mongodb/schema.prisma`. User-owned collections such as `diagrams`, `nodes`, `tp_changes`, and `computation_tasks` are written by runtime API routes, not by `migrate.py`.

Redis is started because the application uses it for queues and cache state, but the workbook import does not enqueue compute jobs or write Bull queue records.

## Import and Setup Commands

Routine import from Git Bash, WSL, or macOS Terminal:

```bash
cd src
bash run-all.sh jun-16-2026.xlsx
```

The setup guides also allow `./run-all.sh jun-16-2026.xlsx` when the script is executable.

If Python importer source files changed, rebuild the container image before rerunning the import:

```bash
cd src
docker compose build python-runner
bash run-all.sh jun-16-2026.xlsx
```

Inspect the newest migration log from PowerShell:

```powershell
Get-ChildItem .\src\excel-migration\logs\log_*.log | Sort-Object LastWriteTime -Descending | Select-Object -First 1
```

Inspect logs from Git Bash, WSL, or macOS Terminal:

```bash
ls -t src/excel-migration/logs/log_*.log
```

The first path printed by `ls -t` is the newest log.

Run only Prisma setup from `src/` when debugging schema setup without importing a workbook:

```bash
npm run migrate:postgres
npm run migrate:mongodb
```

## Error Handling and Failure Boundaries

- If `run-all.sh` receives no workbook argument, it prints `Please provide an Excel filename` and exits before starting the importer.
- If the workbook path does not exist inside the container, `run_python_import.sh` prints `Error: Excel file '<path>' not found.` and exits.
- If Docker Desktop is not running or a required port is unavailable, Docker Compose or Prisma fails before the Python import starts.
- If Prisma migration fails, `set -e` stops `run-all.sh` before the workbook conversion step.
- If `excel_to_csv.py` fails, the error appears in the terminal because logging redirection has not started yet.
- If `migrate.py` fails, the terminal may stop after `Running the data import Python script...`; the traceback is in `src/excel-migration/logs/log_<timestamp>.log`.
- If `migrate.py` fails before cleanup, `Process completed successfully.` and `All steps done!` will not print.
- `process_ports(...)` currently casts `HiddenByDefault` and `SendtoCalc` with `int(...)`, so those CSV values must be numeric-like, usually `0` or `1`. A workbook that uses `Y`, `N`, `Yes`, or `No` for those fields can fail during port import unless the converter is extended first.
- Import reruns use a mix of `ON CONFLICT DO UPDATE`, `ON CONFLICT DO NOTHING`, and targeted cleanup. Treat reruns as upsert/update behavior, not as a full database reset that removes rows missing from the workbook.
- Some process functions log an error and continue when a CSV is missing or malformed. Always inspect the latest log, not only the final terminal line, before trusting imported data.

## Extension Points

- Add support for a renamed workbook sheet in `SHEET_NAME_ALIASES` in `excel_to_csv.py`.
- Add support for renamed workbook columns in `HEADER_ALIASES` in `excel_to_csv.py`.
- Add workbook compatibility cleanup that belongs before CSV import in `excel_to_csv.py`, especially when the downstream `migrate.py` code expects legacy CSV values.
- Add row-level cleanup that belongs to importer semantics in `migration_normalization.py`, then call it from the relevant `process_*` function.
- Add a new imported PostgreSQL table by updating `schema.prisma`, adding or extending a `process_*` function in `migrate.py`, and checking the dependency order in `main()`.
- Do not add MongoDB writes to the Python importer without first defining the ownership boundary with runtime API routes and saved user data.

## Testing and Verification

For documentation-only edits to this page, run from the repository root:

```powershell
git diff --check -- docs/CodeExplanation/excel-import-pipeline.md
```

For importer source changes, use a source-level check first when possible, then run the import from `src/`:

```bash
docker compose build python-runner
bash run-all.sh jun-16-2026.xlsx
```

Expected terminal success markers:

```text
Process completed successfully.
All steps done!
```

After a full import, inspect the newest `src/excel-migration/logs/log_<timestamp>.log` as read-only confirmation. The generated log can confirm what happened in the latest run, but source files and database schemas remain the source of truth for documentation and code changes.

## Known Cautions

- `src/excel-migration/logs/` contains generated runtime logs. Do not commit new logs unless a task explicitly asks for diagnostic artifacts.
- `csv_outputs/` is a temporary generated import directory. Do not document behavior from generated CSV files without checking `excel_to_csv.py` and `migrate.py`.
- `python-runner:latest` can be stale after changing `src/excel-migration/*.py`. Rebuild the image before testing importer code changes.
- `src/generated/`, `src/node_modules/`, `src/dist/`, and `src/coverage/` are generated build or dependency artifacts and should not be used as import source documentation.
- `src/src/backend/services/solve_request.json` is a solver runtime diagnostic, not an import artifact. Do not edit it or use it to infer workbook import behavior.
- New workbook shape support should preserve the legacy CSV contract unless `migrate.py` and the database schema are intentionally updated together.
- The Python importer assumes PostgreSQL schema compatibility. If Prisma schema changes and importer SQL are not updated together, imports can fail at runtime even when workbook conversion succeeds.

## Related Pages

- `docs/Installation/STARTUP_GUIDE.md`
- `docs/Installation/HYPRONET_INSTALLATION_GUIDE.md`
- `docs/CodeExplanation/backend-data-routes-and-persistence.md`
- `docs/CodeExplanation/compute-solver-callback-and-results.md`
