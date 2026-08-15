---
title: System and User Table Reference
sidebar_position: 18
description: Complete current catalog of PostgreSQL system tables and MongoDB user-data collections, with representative structures and ownership.
---

# System and User Table Reference

## Purpose and Scope

HyProNet keeps reusable, imported system knowledge in PostgreSQL and user-created, diagram-specific state in MongoDB. This page is the current catalog of both stores. It documents the Prisma schemas, not a promise that every field is returned by every API.

The authoritative definitions are `src/src/backend/prisma/postgres/schema.prisma` and `src/src/backend/prisma/mongodb/schema.prisma`. `id` is the primary key of every PostgreSQL table. MongoDB document ids are ObjectIds unless noted otherwise.

## System Tables (PostgreSQL)

These tables are shared catalog/configuration data. Most are populated by the system workbook import; normal diagram editing reads them but does not modify them.

| Table | Representative structure | Purpose |
| --- | --- | --- |
| `Domain` | `{ id, name }` | A named process domain. |
| `Models` | `{ id, model_name, shape, icon_width, icon_height }` | Reusable node-model definitions. |
| `ModelVersion` | `{ id, model_id, model_version_name, default, version_date, author }` | Versioned model metadata and phase settings. |
| `Ports` | `{ id, model_version_id, port_name, port_type, port_class_id, port_var_name, send_to_calc }` | Ports exposed by a model version. |
| `SystemVariables` | `{ id, domain_id, port_var_name, dimension, type, lower_bound, upper_bound }` | Domain-wide variable dictionary and default metadata. |
| `PortClass` | `{ id, name, description, color }` | First-class classification for material ports. |
| `PortClassVariable` | `{ id, port_class_id, system_variable_id, hidden_by_default, send_to_calc, is_parameter }` | Membership and display/solver flags for a variable in a port class. |
| `ModelVarMapping` | `{ id, model_version_id, port_id, system_variable_id, port_class_variable_id, internal_var_name }` | Maps a system variable to a model port's internal variable name. |
| `PortVariable` | `{ id, port_id, name, variable_name, unit, type, lower_bound, upper_bound }` | Per-port variables for INFO ports; they are not in `SystemVariables`. |
| `VarNames` | `{ id, ports_id, model_version_id, name, simulation, optimization, param_updt, data_rec }` | Legacy per-port variable mapping retained for compatibility. |
| `DomainModelMapping` | `{ id, domain_id, model_id }` | Many-to-many mapping between domains and models. |
| `DomainStreamsMapping` | `{ id, domain_id, stream_id }` | Many-to-many mapping between domains and streams. |
| `Streams` | `{ id, domain, stream_database_id, content, instance, stream_fractions, properties, port_class_id }` | System material/stream records and their composition/property JSON. |
| `PortClassDatabaseMapping` | `{ id, domain_id, port_class_id, properties_database_name, fractions_database_name, user_properties_database_name }` | Resolves material databases for a domain and port class. |
| `PortClassesDatabaseMappingRaw` | `{ id, domain, port_class, properties_database, composition_database }` | Raw imported mapping retained for compatibility with workbook column names. |
| `UnitConversion` | `{ id, dimension, base_unit, target_unit, multiplier, formula_offset, formula_note }` | One target-unit conversion within a dimension. |
| `Colors` | `{ id, port_class, color }` | Legacy port-class color lookup. |
| `CompTaskTypes` | `{ id, task_name, default }` | Available computation task types. |
| `CompStepTypes` | `{ id, step_name, default, description }` | Available computation step types. |
| `RunConfigs` | `{ id, run_config_type, attribute_name, label_text, data_type, default_value, options }` | Solver/run configuration fields and defaults. |
| `SolutionAlgoLibrary` | `{ id, domain, algorithm_name, phase_name, max_phase_iter, tolerance_percent, solver }` | System defaults for SoluAlgoLib phases. |
| `EqTypeConfig` | `{ id, domain, eq_type, description }` | Equation-type choices by domain. |
| `CostEntitiesConfig` | `{ id, entity_key, entity_name, default_value, default_unit, default_dimension }` | System defaults for economic cost entities. |
| `ComputationResults` | `{ id, diagram_id, run_name, node_id, port_name, port_var_name, from_tp, to_tp, value, unit }` | Persisted solver result rows; operational rather than workbook catalog data. |
| `DashboardBindings` | `{ id, diagram_id, network_name, metabase_dashboard_id, metabase_dashboard_name }` | Links a HyProNet network to a Metabase dashboard. |
| `DashboardPanelConfigs` | `{ id, dashboard_binding_id, metabase_card_id, panel_name, chart_type, source_mode, config }` | Per-panel dashboard display configuration. |

## User Tables (MongoDB)

These collections contain authenticated-user state, diagram edits, runtime tasks, and per-diagram time-period data. A user should access them only through the application API; diagram ownership is enforced by `Diagram.userId` and related route checks.

| Collection | Representative structure | Purpose |
| --- | --- | --- |
| `users` | `{ _id, email, password, firstName, lastName, role }` | Account identity and authorization role. |
| `refreshTokens` | `{ _id, token, userId, expiresAt }` | Refresh-token session persistence. |
| `diagrams` | `{ _id, userId, name, canvas, parameters, equations, sets, collections, solualgolib, duration, tpMode }` | Main user-owned diagram, including saved equation/constraint/SoluAlgoLib data. |
| `nodes` | `{ _id, diagramId, nodeId, modelVersion, position }` | Cached persisted node model-version state for a diagram. |
| `domainSnapshots` | `{ _id, userId, data }` | Frozen system-domain data used by a saved diagram/run. |
| `computationTasks` | `{ _id, userId, diagramId, configuration, status, taskId, runName }` | Queued and dispatched calculation task state. |
| `subnetworkBlueprints` | `{ _id, userId, diagramId, name, portsMapping }` | Reusable subnetwork-blueprint metadata. |
| `tpNodeVers` | `{ _id, diagramId, nodeId, tp, modelVersion }` | Node model versions scoped to time periods. |
| `tpChanges` | `{ _id, diagramId, nodeId, fromTp, toTp, changes }` | Sparse user/computed per-port time-period overrides. |
| `tpSpecVersionSets` | `{ _id, diagramId, scope, calculationType, name, active }` | Named TP specification version sets. |
| `tpSpecVersionTables` | `{ _id, versionSetId, tableName, version }` | Tables belonging to a TP specification version set. |
| `tpSpecBaseChanges` | `{ _id, diagramId, versionSetId, nodeId, changes }` | Sparse base-TP specification patches. |
| `instrumentSets` | `{ _id, userId, diagramId, network, instrSet }` | User-defined data-reconciliation instrument-set headers. |
| `variableInstrumentMappings` | `{ _id, instrumentSetId, modelPath, instrument, units, lowerBound, upperBound }` | Maps model variables to instruments and measurement limits. |
| `plantMeasurements` | `{ _id, instrumentSetId, mappingId, instrumentName, value, units, measuredAt }` | Imported/manual plant measurement rows. |

## Important Ownership Rules

- `UnitConversion`, `SystemVariables`, port/model tables, and SoluAlgoLib base rows are system data. Diagram-specific copies or selections belong in MongoDB, not back in these tables.
- `Diagram.parameters` is a generated solver-facing snapshot. Edit through the UI/source fields; do not use it as the user-facing source of truth.
- `Diagram.equations`, `sets`, `collections`, and `solualgolib` are JSON fields because they are diagram-specific structures with nested references.
- `ComputationResults` is PostgreSQL because it is queried as result rows, even though its data originates from a user's diagram/run.

## Related Pages

- [Unit Conversion and Administration](./unit-conversion-and-administration.md)
- [Calculation Server Payload Reference](./calculation-server-payload-reference.md)
- [Backend Data Routes and Persistence Code Explanation](./backend-data-routes-and-persistence.md)
