---
title: Create and Save Equations
sidebar_position: 4
description: Use Equation Writing to build equations from network, node, port, variable, and time-period references.
---

# Create and Save Equations

Use this page when you need to create equations that reference variables from the current diagram.

## Before You Start

- Open a saved diagram.
- Make sure the nodes and ports referenced by the equation exist.
- Save the diagram before saving equations; the app requires a diagram id for equation persistence.

## Create an Equation

1. Click **Equation Writing** in the header toolbar.
2. In the **Equation Writing** dialog, click **New Equation**.
3. Edit the equation name in the left-side list.
4. Select the equation's target or ownership fields shown in the editor.
5. Build the expression by choosing the available network, node, port, variable, and time-period values.
6. Insert operators from the operator controls.
7. Review the expression text.
8. Click **Save**.

## Import Variables From CSV

1. Open **Equation Writing**.
2. Use the import control for variables.
3. Select a `.csv` file.
4. Make sure the file has these columns in order: **Node**, **Port**, **Variable**.
5. Review the imported variables before using them in equations.

## Delete an Equation

1. Open **Equation Writing**.
2. Select the equation in the left-side list.
3. Click **Delete**.
4. Save the remaining equations.

## Result

The diagram stores the current equation list. Equation variables can point to diagram nodes, subnetwork variables, imported variables, and selected time-period contexts.

## Troubleshooting

| Problem | What To Check |
| --- | --- |
| **Save** shows an error asking you to save the diagram first | Save the diagram from the main header, then reopen **Equation Writing**. |
| CSV import fails | Confirm the file is `.csv` and the headers are **Node**, **Port**, **Variable**. |
| A node or port is not available | Confirm the node exists on the canvas and its model data is loaded. |
| The expression references the wrong TP | Check the selected time-period value before inserting the variable. |

## Related Pages

- [Edit node settings, streams, variables, and specs](./edit-node-variables)
- [Configure time periods](./time-periods)
- [Configure and start a computation](./run-computation)
