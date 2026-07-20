---
title: Selected Inputs in Solve Requests
sidebar_position: 15
description: Describes how Calc Type dropdown selections become authoritative solver inputs.
---

# Selected Inputs in Solve Requests

Optimization and DataRec inputs are controlled by the active Calc Type dropdown selections. Editor persistence alone does not add an Instrument, Plant Measurement, Objective Function, or Constraint to a Solve Request.

## Selection Boundary

The frontend sends identifiers only:

```json
{
  "optimizationOptions": {
    "mode": "deterministic",
    "objectiveFunctionSetIds": ["objective-set-1"],
    "additionalConstraintSetIds": ["constraint-set-1"]
  }
}
```

```json
{
  "dataRecOptions": {
    "instrumentSetId": "64b000000000000000000003",
    "measurementIds": ["64b000000000000000000005"],
    "objectiveFunctionSetIds": ["objective-set-1"]
  }
}
```

The backend treats these values only as selections. It reloads the current records owned by the user and network, rejects stale or mismatched IDs, and stores the translated values as a queued-task snapshot. This prevents edited names, equations, mapping details, or measurement values in the browser request from overriding persisted data.

## Solver Contract

Selected inputs are grouped under `parameters.solve_inputs`. Equations remain inside their selected Objective Function or Constraint Set; the request does not create a second flattened `parameters.equations` copy.

### Optimization

```json
{
  "parameters": {
    "solve_inputs": {
      "calculation_type": "Optimization",
      "optimization": {
        "mode": "deterministic",
        "wasserstein_radius": null,
        "objective_functions": [
          {
            "set_id": "objective-set-1",
            "name": "Fuel objective",
            "equations": [
              {
                "name": "Minimize fuel",
                "belong_to": "Main Network",
                "equation_type": "Objective Function",
                "eq_type": "Minimize",
                "expression": "Main Network.Heater.OUT.Duty[t]",
                "tokens": []
              }
            ]
          }
        ],
        "additional_constraints": [
          {
            "set_id": "constraint-set-1",
            "name": "Operating limits",
            "equations": []
          }
        ]
      }
    }
  }
}
```

### DataRec

```json
{
  "parameters": {
    "solve_inputs": {
      "calculation_type": "DataRec",
      "data_reconciliation": {
        "instrument_set": {
          "id": "64b000000000000000000003",
          "network": "Main Network",
          "instr_set": "VARINSTRMAP"
        },
        "instruments": [
          {
            "id": "64b000000000000000000004",
            "instrument_name": "TI-101",
            "units": "C",
            "weight": 2,
            "accuracy": {
              "absolute_accuracy": 0.5,
              "percent_accuracy": null
            },
            "bounds": {
              "lower_bound": 0,
              "upper_bound": 500
            },
            "model_path": {
              "network": "Main Network",
              "subnetwork": "none",
              "sub_subnetwork": "none",
              "node_id": "heater-node-1",
              "node_name": "Heater",
              "port": "OUT",
              "variable": "Temperature"
            }
          }
        ],
        "measurements": [
          {
            "id": "64b000000000000000000005",
            "mapping_id": "64b000000000000000000004",
            "instrument_name": "TI-101",
            "plant_value": 325.5,
            "units": "C",
            "date": "2026-07-20",
            "time": "10:30:00",
            "sample_number": "3",
            "measurement_weight": 1.5,
            "mapping_weight": 2,
            "accuracy": {
              "absolute_accuracy": 0.5,
              "percent_accuracy": null
            },
            "bounds": {
              "lower_bound": 0,
              "upper_bound": 500
            },
            "model_path": {
              "network": "Main Network",
              "subnetwork": "none",
              "sub_subnetwork": "none",
              "node_id": "heater-node-1",
              "node_name": "Heater",
              "port": "OUT",
              "variable": "Temperature"
            }
          }
        ],
        "objective_functions": []
      }
    }
  }
}
```

All normal translated model parameters remain alongside these fields. The examples show only the selected-input portion.

## Independent Inputs Removed

Before the selected snapshot is attached, the builder removes legacy or independently persisted equation, set, constraint, instrument, and measurement parameter keys. In particular:

- `diagram.equations` is no longer passed directly to `buildSolveRequest`.
- A legacy `parameters.equations` value is removed and is not recreated.
- A saved Objective Function or Constraint is sent only through a selected set.
- A saved Instrument Set is expanded only when that set is selected.
- A Plant Measurement is sent only when its measurement ID is selected. Its editor-level `include` value does not independently add or remove it from the request.
