---
title: Calculation Server Payload Reference
sidebar_position: 20
description: Canonical source-backed reference for the complete request assembled and posted to the external calculation server.
---

# Calculation Server Payload Reference

## Overview

The computation worker calls `buildSolveRequest(...)`, then posts the result to `${BASE_SOLVER_ENGINE_URL}/solve/`. This page describes that final request—not the frontend compute-start request and not the optional generated `solve_request.json` debug file.

The request always has three top-level fields:

```ts
{
  callback_url: `${BASE_EXTERNAL_URL}/compute/callback/`,
  configuration: { /* run configuration */ },
  parameters: { /* translated diagram data and selected solve inputs */ }
}
```

## Complete Request Shape

The following is a representative complete Optimization request. Fields marked optional are included only when the source data exists. IDs are illustrative.

```json
{
  "callback_url": "https://public-host.example/api/external/compute/callback/",
  "configuration": {
    "max_computation_time": 3600,
    "solver": {
      "solver_name": "IPOPT",
      "attributes": [{ "attribute_name": "tol", "value": "0.0001" }]
    },
    "algorithm": "SoluAlgoLib",
    "solution_algo_library": [
      {
        "id": "phase-1",
        "algorithmName": "Main algorithm",
        "phaseName": "P1",
        "maxPhaseIter": 100,
        "tolerancePercent": 0.1,
        "stepReduction": 0.5,
        "ifConvergenceFailGoto": "END",
        "ifConvergencePassGoto": "P2",
        "updateVar": "x",
        "convergenceVar": "residual",
        "runType": "OPT",
        "solver": "IPOPT",
        "collection": "collection-1",
        "set": "objective-set-1"
      }
    ],
    "Log_level": "development"
  },
  "parameters": {
    "global_params": {},
    "models": [],
    "nodes": [],
    "tps_specs": [],
    "stream_connectivity": [],
    "material_properties": [],
    "material_fractions": [],
    "costs": {
      "entities": [],
      "mappings": [],
      "duration": []
    },
    "solve_inputs": {
      "calculation_type": "Optimization",
      "optimization": {
        "mode": "deterministic",
        "wasserstein_radius": null,
        "objective_functions": [{ "set_id": "objective-set-1", "name": "Objective", "equations": ["eq-1"] }],
        "additional_constraints": [{ "set_id": "constraint-set-1", "name": "Limits", "equations": ["eq-2"] }]
      }
    },
    "equations": [
      {
        "id": "eq-1",
        "name": "Minimize energy",
        "belong_to": "Network A",
        "equation_type": "Objective Function",
        "eq_type": "linear",
        "expression": "x[t]",
        "tokens": [{ "token_type": "variable", "type": "pyo.NonNegativeReals", "name": "x[t]", "network": "Network A", "node": "N1", "port": "Output", "variable": "x", "tp": "t", "path": "Network A.N1.Output.x[t]", "lb": 0, "ub": 1000, "units": "kg/h" }]
      }
    ],
    "equation_collections": [{ "id": "collection-1", "name": "Operating limits", "sets": ["constraint-set-1"] }]
  }
}
```

## Field Ownership and Inclusion Rules

| Field | Source | Inclusion rule |
| --- | --- | --- |
| `callback_url` | `BASE_EXTERNAL_URL` | Always present; dispatch fails if the environment variable is missing. |
| `configuration.max_computation_time`, `solver`, `Log_level` | Compute start and saved run configuration | Always present in the configuration object; individual values may be `null`. |
| `configuration.algorithm` | Requested algorithm/current compatibility rule | Defaults to `SoluAlgoLib` when the stored value is null. |
| `configuration.solution_algo_library` | `diagram.solualgolib` | Always an array. Nested set/collection objects are reduced to ids. |
| Core translated parameters | `diagram.parameters`, created by `translation(...)` | Passed through after legacy independent solve-input fields are removed. The common sections are `global_params`, `models`, `nodes`, `tps_specs`, `stream_connectivity`, `material_properties`, `material_fractions`, and optional `costs`. |
| `parameters.solve_inputs` | Queued task `configuration.selected_inputs` | Present when a run has selected Optimization or Data Reconciliation inputs. |
| `parameters.equations` | `diagram.equations` | Present only if at least one saved equation normalizes successfully. |
| `parameters.equation_collections` | `diagram.collections` | Present only if at least one collection exists. |

## Translated Diagram Sections

`translation(...)` always creates the following `parameters` keys before the final builder adds the conditional sections above. Their arrays can be empty for a valid diagram.

| Key | Element shape / data carried |
| --- | --- |
| `global_params` | Network-wide calculation metadata assembled by translation. |
| `models` | Model definitions required by the solver for the saved network. |
| `nodes` | Saved node instances and their model/version context. |
| `tps_specs` | One variable specification per active node/port variable/range: `{ from_tp, to_tp, task, network, node_name, model_name, model_version, port, port_var_name, value, spec, unit, var_type, lower_bound, upper_bound, is_human_input }`. |
| `stream_connectivity` | Stream connection records resolved from saved canvas edges. |
| `material_properties` | Material property rows formatted for calculation. |
| `material_fractions` | Material composition/fraction rows formatted for calculation. |
| `costs` (optional) | Economic `entities`, `mappings`, and `duration` rows; present only when compute start supplies economic data. |

The nested `models`, `nodes`, stream, and material shapes are derived from the current domain snapshot and saved canvas. Their full content varies by domain and diagram; no client-supplied fields are added after `translation(...)` except the solve-input/equation fields documented on this page.

For Data Reconciliation, `solve_inputs` has this alternate shape:

```json
{
  "calculation_type": "Data Reconciliation",
  "data_reconciliation": {
    "instrument_set": "instrument-set-id",
    "instruments": ["instrument-id"],
    "measurements": ["measurement-id"],
    "objective_functions": [{ "set_id": "objective-set-id", "name": "Objective", "equations": ["eq-id"] }]
  }
}
```

## Normalization Before Dispatch

- `selected_inputs` is removed from `configuration`; its solver form is `parameters.solve_inputs`.
- Stale legacy solve-input keys such as `sets`, `collections`, `equation_sets`, `constraints`, and old data-reconciliation keys are removed from `diagram.parameters` before the final merge.
- Equation variable bounds are converted from the saved display unit into the dimension base unit. Structured tokens retain their path fields; manually defined paths have null structured fields and units.
- Equations, collections, selected sets, and SoluAlgoLib references use ids where references are needed, avoiding ambiguity from duplicate display names.
- Empty normalized equation and collection arrays are omitted from `parameters`; `configuration.solution_algo_library` remains an empty array when none is saved.

## Related Pages

- [Compute, Solver Callback, and Results Code Explanation](./compute-solver-callback-and-results.md)
- [Translation and Reverse Translation Code Explanation](./translation-and-reverse-translation.md)
- [Equation Writing Module Code Explanation](./equation-writing-module.md)
- [Constraint Module Code Explanation](./constraint-module.md)
- [Solution Algorithm Library Module Code Explanation](./solution-algo-library-module.md)
