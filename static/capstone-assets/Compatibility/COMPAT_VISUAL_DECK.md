---
marp: true
paginate: true
theme: default
title: Plant-GUI Compatibility Walkthrough
description: Slide-style walkthrough of compatibility workflow, versioning, and decision boundaries.
---

# Plant-GUI Compatibility Walkthrough

### Purpose

- explain what compatibility work is responsible for
- separate persisted-structure drift from Excel/runtime-library drift
- show where human decisions are required
- give the team a 5-minute overview before diving into code

---

# 1. Why This Exists

Compatibility is not only about JSON shape.

We have two independent sources of risk:

1. persisted structure changed
2. Excel/runtime-library contract changed

Both can break saved diagrams.

```mermaid
flowchart LR
    A[Developer changes code] --> B[Persisted shape may change]
    A --> C[Excel or runtime library may change]
    B --> D[Old saved diagrams may drift]
    C --> D
    D --> E[Need compat check]
```

---

# 2. Document Roles

```mermaid
flowchart TD
    A[COMPAT_CHECK.md] --> A1[Operational workflow]
    B[SCHEMA_SNAPSHOT.md] --> B1[Current persisted baseline]
    C[SCHEMA_HISTORY.md] --> C1[Version map + decision summary]
    D[COMPAT_VISUAL_DECK.md] --> D1[Team walkthrough]
    E[archive/] --> E1[Historical assessments]
```

Rules:

- `SCHEMA_SNAPSHOT.md` answers: "What is the baseline now?"
- `SCHEMA_HISTORY.md` answers: "What changed between versions, and what did we decide?"
- `COMPAT_CHECK.md` answers: "How do we run the review?"

---

# 3. Data Flow View

```mermaid
flowchart LR
    A[Frontend save payload] --> B[Backend save route]
    B --> C[Mongo Diagram.canvas]
    B --> D[Mongo Node / TpNodeVers / TpChanges]
    B --> E[DomainSnapshot]
    C --> F[Load / Upgrade / Library Refresh]
    D --> F
    E --> F
    F --> G[Translation]
    G --> H[Solver / Compute]
```

Questions to ask:

- did the persisted shape change?
- did the runtime model contract change?
- can old data be refreshed automatically?

---

# 4. Execution Flow View

```mermaid
flowchart TD
    A[Change detected] --> B[Choose mode 1N / 1Y / 2N / 2Y]
    B --> C[Determine unreleased compatibility scope]
    C --> D[Classify change]
    D --> E[Compare against SCHEMA_SNAPSHOT]
    E --> F[Inspect runtime library impact]
    F --> G[Produce decision summary]
    G --> H{Ready for full patch?}
    H -- No --> I[Report drift and required later patch]
    H -- Yes --> J[Bump version + update snapshot/history/tests]
```

---

# 5. Classification Matrix

| Classification | What changed | Typical handling |
|----------------|--------------|------------------|
| `schema-only` | persisted shape only | migration-driven |
| `library-additive` | new runtime items | additive refresh if clearly safe |
| `library-rename` | same concept, new identifier/name | explicit mapping required |
| `library-delete` | runtime item removed | warn + unverify + manual reselection by default |
| `mixed` | both shape and runtime changed | combine schema patch with strictest library rule |

Important:

- this repo uses **one compatibility version axis**
- but review still distinguishes schema vs library semantics internally

---

# 6. Decision Boundary

```mermaid
flowchart TD
    A[Excel/runtime change found] --> B{Clearly additive and low-risk?}
    B -- Yes --> C[auto-safe additive refresh]
    B -- No --> D{Delete or rename?}
    D -- Yes --> E[manual-review-required]
    D -- No --> F{Semantic/default change?}
    F -- Yes --> G[domain-owner-decision-required]
    F -- No --> H[manual-review-required]
```

Team rule:

- tooling may detect
- tooling may refresh low-risk additive data
- tooling must not invent chemical-engineering meaning

---

# 7. Why History Must Include Decisions

Only recording "which Excel file was used" is **not enough**.

We also need to know:

- was the change `add`, `delete`, `rename`, or `mixed`?
- did we auto-refresh, warn, unverify, or require manual remap?
- who decided that this behavior was acceptable?

Example history row content:

```text
Version: 6.0.0
Runtime baseline: src/excel-sheets/mar-18-2026.xlsx
Classification: library-additive
Decision summary:
- additive refresh allowed
- rename/delete not auto-resolved
```

---

# 8. Recommended Team Workflow

```mermaid
sequenceDiagram
    participant MW as Model Writer
    participant Dev as Developer / Codex
    participant Docs as History + Snapshot
    MW->>Dev: Change Excel / runtime definition
    Dev->>Dev: Run compat-check
    Dev->>Dev: Classify add / delete / rename / mixed
    Dev->>MW: Ask only for domain decisions that are not safe to infer
    Dev->>Docs: Record version bump + decision summary
    Dev->>Team: Present workflow and impact
```

What the team should expect from each release:

- one compatibility version bump
- one snapshot update
- one history row with the decision summary

---

# 9. What To Present In A Team Meeting

Minimum walkthrough:

1. what changed
2. what class of compatibility change it is
3. what was handled automatically
4. what required human judgment
5. what was recorded in history

That is enough for a short PPT or slide-driven Markdown walkthrough.
