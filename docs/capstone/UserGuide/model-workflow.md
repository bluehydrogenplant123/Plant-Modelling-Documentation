---
title: Create, Open, Save, Import, and Export Models
sidebar_position: 3
description: Use the Model toolbar to manage HyProNet diagrams and network files.
---

# Create, Open, Save, Import, and Export Models

Use this page when you need to create a model, reopen an existing network, save your work, verify the model, or move diagram data through JSON import and export.

## Before You Start

- Sign in to HyProNet.
- Stay on the canvas page unless you are creating your first model.
- Wait until no computation is running; many model actions are disabled during computation.

## Create a New Model

1. Open the **Model** section in the header toolbar.
2. Click **New Model**.
3. In the **New Model** dialog, enter **Diagram Name**.
4. Choose **Select Domain**.
5. Choose **Calculation Type**.
6. Enter **Description**.
7. Click **Create Diagram**.

## Open an Existing Network

1. Open the **Model** section.
2. Click **Open**.
3. In the **Open Network** dialog, find the network you want.
4. Open the network from the row action.
5. Use **Export** in the same row if you need a JSON copy before opening or sharing the network.

## Save or Rename the Current Network

1. Edit the **Canvas name** field in the header if the network name needs to change.
2. Click **Save** in the header toolbar.
3. Confirm that the save status changes from **Not saved** or **Saving...** to a recent **Last saved** value.

## Duplicate a Network

1. Open the **Model** section.
2. Click **Duplicate Network**.
3. In the **Duplicate Network** dialog, enter **Network Name**.
4. Confirm the name is available.
5. Click **Duplicate**.

## Import a Diagram

1. Open the **Model** section.
2. Click **Import**.
3. Select a `.json` diagram file.
4. Wait for the import to complete and the imported model to open or appear in the available networks.

You can also import a diagram from the **New Model** dialog by clicking **Import Diagram**.

## Export Data

1. Open the **Model** section.
2. Click **Export**.
3. In the **Export Data** dialog, choose **Full Data**, **Solver Data**, or **Algorithm Data**.
4. If you choose **Full Data**, edit **Export File Name** if needed.
5. Click **Export**.

## Verify the Model

1. Open the **Model** section.
2. Click **Verify Model**.
3. Wait for the button state to show **Verified**.
4. Continue to Multi-TP or Run workflows only after verification succeeds.

## Result

Your diagram is created, opened, saved, duplicated, imported, exported, or verified from the Model toolbar. The header save status shows whether the current network has been persisted.

## Troubleshooting

| Problem | What To Check |
| --- | --- |
| **New Model** cannot create a diagram | Check that **Diagram Name**, **Select Domain**, **Calculation Type**, and **Description** are filled. |
| **Duplicate** is disabled | Enter a non-empty network name that is not already used. |
| **Import** fails | Confirm the file is a JSON diagram export. |
| Save status stays **Not saved** | Click **Save** again and check whether any error alert appears. |
| **Verify Model** does not become **Verified** | Fix model validation errors before using Multi-TP or Run actions. |

## Related Pages

- [Edit node settings, streams, variables, and specs](./edit-node-variables)
- [Configure time periods](./time-periods)
- [Configure and start a computation](./run-computation)
