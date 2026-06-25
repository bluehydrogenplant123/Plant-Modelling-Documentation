---
title: Configure and Start a Computation
sidebar_position: 9
description: Configure solver and algorithm options, start a computation, monitor status, stop a run, and review run results.
---

# Configure and Start a Computation

Use this page when the model is ready to run through the solver and algorithm pipeline.

## Before You Start

- Save the diagram.
- Click **Verify Model** and confirm the model is verified.
- Configure required **Set Run** solver and algorithm options before starting the run.

## Configure Solver and Algorithm Settings

1. Open the **Set Run** section in the header toolbar.
2. Open the **Solver** dropdown.
3. Select the solver configuration you want to edit.
4. Update the fields in the run-config dialog.
5. Save the configuration if the dialog is editable.
6. Open the **Algorithm** dropdown.
7. Select and save the algorithm configuration in the same way.

## Start a Computation

1. Click **Run**.
2. If prompted about unsaved changes, choose whether to save before continuing.
3. In the **Computation Panel**, enter **Run Name**.
4. Enter **Max Execution Time** and choose **Seconds**, **Minutes**, or **Hours**.
5. Select **Solver**.
6. Select **Algorithm**.
7. Select **Log level**.
8. Click **Start Computation**.

## Monitor or Stop a Computation

1. Watch **Elapsed Time** and **Computation Status** in the **Computation Panel**.
2. If the status is **waiting**, review the waiting and computing tasks shown in the panel.
3. Click **Stop Computation** if the run should be aborted.
4. Wait for the stopping confirmation before closing or starting another run.

## Review Run Results

1. Click **Run Result** in the header toolbar.
2. Review the **Run Result** table.
3. Check **Run Name**, status, and **Run Time**.
4. Click **Delete** only when the stored result should be removed.

## Result

The computation is queued or started with the selected solver, algorithm, run name, execution limit, and log level. Results are available from **Run Result** after the backend stores them.

## Troubleshooting

| Problem | What To Check |
| --- | --- |
| **Start Computation** is disabled | Check for duplicate **Run Name**, missing solver, missing algorithm, or an active computation. |
| The panel asks for a valid execution time | Enter a positive integer within the selected unit's limit. |
| The run stays **waiting** | Review the waiting queue shown in the panel. |
| Results are not visible | Open **Run Result** after the computation completes and confirm the run name. |

## Related Pages

- [Create, open, save, import, and export models](./model-workflow)
- [Configure economic data](./economic-data)
- [Set up plant measurements](./plant-measurements)
