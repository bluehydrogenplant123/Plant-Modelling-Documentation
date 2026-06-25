---
title: Configure Time Periods
sidebar_position: 8
description: Use Base TP, Global TP, TP Node, and TP Specs to manage time-period duration and node-specific TP data.
---

# Configure Time Periods

Use this page when you need Base TP or Multi-TP behavior before running calculations.

## Before You Start

- Open and save a diagram.
- Click **Verify Model** in the **Model** section before using advanced TP workflows.
- Decide whether you are editing Base TP only or Multi-TP ranges.

## Set Base TP Duration

1. Open the **Model** section.
2. Click **Base TP**.
3. In the **Base TP** dialog, edit the duration fields.
4. Click **Save**.

## Edit Base TP Specs

1. Open the **Model** section.
2. Click **Specs**.
3. In the **TP Specs** dialog, add or edit rows in the grid.
4. Click **Add** if a new spec row is needed.
5. Click **Save**.

## Configure Global TP

1. Open the **Multi-TP** section.
2. Click **Global TP**.
3. In the **Global TP** dialog, enter how many TPs to add or delete.
4. Click **Build Grid**.
5. Review TP rows and duration fields.
6. Click the apply action shown in the dialog.

## Assign Node Model Versions by TP

1. Open the **Multi-TP** section.
2. Click **TP Node - Model Version Control**.
3. In the dialog, filter or review TP rows.
4. Update model-version selections where editing is available.
5. Click **Save (persist)**.

## Edit Multi-TP Specs

1. Open the **Multi-TP** section.
2. Click **TP Specs**.
3. In the **TP Specs** dialog, review TP-specific rows.
4. Edit allowed grid cells.
5. Click **Save**.

## Result

Base TP and Multi-TP settings are saved for the diagram. TP rows can drive node variables, specs, and Multi-TP economic values.

## Troubleshooting

| Problem | What To Check |
| --- | --- |
| **Base TP** is disabled | The diagram may already have Multi-TP ranges. |
| **TP Specs** says to save the diagram first | Save the diagram, then reopen **TP Specs**. |
| **TP Node - Model Version Control** does not allow range editing | Current UI allows model-version updates while TP structure editing is gated. |
| Multi-TP economic rows are missing | Configure and save TP ranges before opening Multi-TP economic panels. |

## Related Pages

- [Configure economic data](./economic-data)
- [Edit node settings, streams, variables, and specs](./edit-node-variables)
- [Code explanation: Time Period and Economic Flow](../CodeExplanation/time-period-and-economic-flow)
