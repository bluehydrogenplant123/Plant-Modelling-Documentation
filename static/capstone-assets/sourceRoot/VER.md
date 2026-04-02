# Version 6 Factory Test Preparation Schema

**Purpose:** Pre-release checklist for factory testing (not production optimization)  
**Timeline:** 1 week  
**Target:** Version 6.0 (feature/stable-version6.0)

---

## 1. Version Compatibility

| Area                     | Action                                                                                                                              | Priority |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------- | -------- |
| **Schema / Data Format** | Ensure save/load JSON schema is backward-compatible with older diagrams; add `modelVersion` or `schemaVersion` field if not present | High     |
| **API Contract**         | Document and freeze backend API endpoints; avoid breaking changes during test window                                                | High     |
| **Node.js**              | Pin Node.js version (e.g. 18.x or 20.x LTS) in docs and `.nvmrc`                                                                    | Medium   |
| **Database**             | Document Prisma schema version; provide migration scripts if schema changed                                                         | Medium   |
| **Browser**              | Specify supported browsers (Chrome, Edge, etc.) and minimum versions                                                                | Medium   |

**Suggested additions:**
- Add `VERSION` or `BUILD_ID` in UI footer or About dialog for quick identification
- Add `/api/health` or `/api/version` endpoint returning app version for factory verification

---

## 2. Installation Package

| Item | Action | Priority |
|------|--------|----------|
| **Build artifacts** | Create reproducible build: `npm run build` (backend) + `npm run build` (frontend) | High |
| **Single deliverable** | Package as one folder: `dist/` (backend) + `frontend/dist/` (static assets) | High |
| **Install script** | Provide `install.bat` / `install.sh` for: `npm install`, env setup, DB init | High |
| **Run script** | Provide `start.bat` / `start.sh` to start backend + serve frontend | High |
| **Environment** | Document `.env.example` with all required vars (DB, Redis, ports, etc.) | High |
| **Dependencies** | Use `npm ci` in install script for deterministic installs | Medium |

**Package structure suggestion:**
```
Plant-GUI-v6.0-factory/
├── backend/           # compiled backend + package.json
├── frontend/          # built static files (or bundled)
├── install.bat
├── start.bat
├── .env.example
├── README_FACTORY.md  # factory-specific quick start
└── VERSION.txt        # 6.0.0-factory
```

---

## 3. Additional Recommendations (1-Week Timeline)

### 3.1 Documentation

| Task | Description |
|------|-------------|
| **Factory Quick Start** | One-page README: prerequisites, install steps, start steps, how to verify it works |
| **Known Limitations** | List what is NOT tested/optimized (e.g. performance, scale, security) |
| **Troubleshooting** | Common errors (port in use, Redis down, DB connection) and fixes |

### 3.2 Stability & Observability

| Task | Description |
|------|-------------|
| **Error handling** | Ensure uncaught errors don’t crash the app; add basic try/catch where critical |
| **Logging** | Use Winston; ensure logs go to file and/or console for factory debugging |
| **Health check** | `/api/health` returning DB + Redis status for quick sanity checks |

### 3.3 Test Coverage

| Task | Description |
|------|-------------|
| **Smoke test** | Short checklist: app starts, login (if any), load diagram, run computation |
| **Regression** | Run existing Jest + Cypress tests before packaging |
| **Manual test script** | 1–2 page step-by-step for factory testers |

### 3.4 Configuration & Security

| Task | Description |
|------|-------------|
| **Config freeze** | Avoid changing ports, DB names, Redis config during test |
| **Secrets** | No hardcoded secrets; use `.env` and document in `.env.example` |
| **CORS** | Ensure CORS allows factory test URLs if different from dev |

### 3.5 Rollback & Support

| Task | Description |
|------|-------------|
| **Rollback plan** | Document how to revert to previous version if critical issues appear |
| **Contact / channel** | Provide contact or channel for factory feedback during test week |
| **Issue template** | Simple template: version, steps, expected vs actual, logs |

---

## 4. One-Week Schedule (Suggested)

| Day | Focus |
|-----|--------|
| **Day 1** | Version compatibility: schema versioning, API freeze, Node/DB/browser docs |
| **Day 2** | Build & package: reproducible build, folder structure, install/start scripts |
| **Day 3** | Env & config: `.env.example`, health endpoint, logging |
| **Day 4** | Docs: Factory Quick Start, troubleshooting, known limitations |
| **Day 5** | Testing: run full test suite, smoke test, manual test script |
| **Day 6** | Final package: create deliverable, verify on clean machine |
| **Day 7** | Buffer / handoff: support channel, issue template, rollback doc |

---

## 5. Checklist Before Handoff

- [ ] Version number visible in UI or API
- [ ] Schema/API backward compatibility documented
- [ ] Single installable package with install + start scripts
- [ ] `.env.example` complete and documented
- [ ] Health check endpoint working
- [ ] Factory Quick Start README written
- [ ] Known limitations documented
- [ ] Full test suite passing
- [ ] Smoke test verified on clean environment
- [ ] Support channel and issue template ready

---

## 6. Out of Scope (For Later Production)

- Performance optimization
- Security hardening (beyond basic secrets handling)
- Full i18n / localization
- Advanced monitoring (APM, metrics)
- Production deployment (Docker, K8s, etc.)

---

*Document created for Version 6 factory testing preparation. Update as needed.*
