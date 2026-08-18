---
title: Diagram Verification Lifecycle
---

# Diagram Verification Lifecycle

This page documents the canonical verification state for normal root diagrams, the compatible API surface, and the Full Data transfer contract. The editable source for the companion diagram is [`images/diagram-verification-lifecycle.drawio`](./images/diagram-verification-lifecycle.drawio).

![Verification lifecycle and Full Data transfer flow](./images/diagram-verification-lifecycle.svg)

## State Ownership

`Diagram.isVerified` in MongoDB is authoritative. The Redux `canvas.verified` value is a UI projection of the state returned by the server; a speaker label, TP row, export option, or client-side assumption must not manufacture a verified state.

The Model-menu toggle is available only for a saved diagram with `type === 0`. It is one switch-like button with `role="switch"`: the visible text reports the canonical current state, **Unverified** or **Verified**, while a click requests the opposite state. Existing disable guards remain in force. Subnetwork blueprint/instance semantics are outside this lifecycle change. A normal root diagram can still be verified before entering Multi-TP, preserving the existing verified-then-Multi-TP flow.

## Desired-State API

`PATCH /api/data/diagrams/:diagramId/verification` accepts exactly:

```json
{ "isVerified": true }
```

or the same object with `false`. The route:

1. loads the diagram;
2. checks that the authenticated user owns it before disclosing same-state information;
3. updates the Boolean only when it differs; and
4. returns HTTP `200` with `changed`, top-level `isVerified`, and the saved `diagram`.

The operation is idempotent. A repeated desired state returns `changed: false` and the canonical state. Missing diagrams return `404`, non-owners receive `403`, and a non-Boolean body receives `400`.

The historical `PATCH /api/data/diagrams/:diagramId/verify` endpoint remains a compatible desired-`true` wrapper. New clients should use `/verification` for both directions.

## UI Flow

`verify-button.tsx` derives the next desired state from Redux, sends it to `/verification`, and disables duplicate clicks while the request is pending. It updates Redux only from the canonical Boolean in a successful response. A failed or malformed response leaves the current UI state unchanged.

The TP-row settings loader no longer dispatches verification when rows exist. TP data and diagram verification are independent persisted facts.

## Full Data Export

Header and Dashboard use `utils/diagramTransfer.ts` for the same request and download behavior:

```text
GET /api/data/diagrams/:diagramId/export?verification=preserve
GET /api/data/diagrams/:diagramId/export?verification=unverified
```

`preserve` is the default and retains the stored root status. `unverified` changes only `snapshot.metadata.isVerified` in the response to `false`. Neither mode updates the source database, and the override does not change nested subnetwork instance semantics. Invalid values return `400`.

The extra choice is presented only for a verified source and only for Full Data. Solver and Algorithm exports are unchanged.

## Current-Format Import

`utils/diagramTransfer.ts` also owns recognition and import of supported Full Data versions. Header and Dashboard send one `POST /api/data/diagrams/import` request. The backend creates the root diagram with the snapshot's exact `metadata.isVerified` value and returns that value in the canonical response.

Current-format callers must not send a follow-up `/verify` request. The legacy-format import path may still call the legacy compatibility wrapper when its payload requests verification.

## Compatibility Decision

Classification: **SCHEMA_CONTRACT_NO_CHANGE**.

This change reuses the existing required `Diagram.isVerified` Boolean and existing Full Data `metadata.isVerified` field. It adds an optional export query and a desired-state endpoint without changing Prisma models, workbook schemas, snapshot versions, callback contracts, or nested records. Therefore it requires no schema version bump, migration handler, or database backfill.

## Verification Matrix

| Surface | Required check | Acceptance signal |
| --- | --- | --- |
| API lifecycle | `false -> true -> false -> true`, plus repeated states | `200`; canonical state matches request; repeated call has `changed: false` |
| Authorization | non-owner requests either desired state | `403` before same-state disclosure; no update |
| Legacy API | call `/verify` twice | both succeed; final state is `true` |
| Root UI | toggle both directions on type `0` | label/state change only after successful response |
| Existing guards | disabled control; subnetwork blueprint/instance | no new mutation path; prior semantics remain |
| Multi-TP continuity | normal type-`0` root before and after entering Multi-TP | toggle remains available subject to existing guards; verified-then-Multi-TP behavior is unchanged |
| Header export | verified source, both choices | downloaded root metadata matches choice; source remains verified |
| Dashboard export | verified and unverified rows | same request contract as Header |
| Nested export | forced-unverified root with nested instances | nested records are byte-for-byte unchanged by the override |
| Current import | preserved and forced-unverified files | one import POST; created state matches file; correct Dashboard group |
| Legacy import | verified legacy file | compatibility wrapper still reaches verified state |

Real-server evidence should repeat the API and transfer rows against a disposable owner diagram and query the source after export. Browser evidence should cover Header and Dashboard choices, failure rollback, refresh persistence, and verified/unverified grouping.
