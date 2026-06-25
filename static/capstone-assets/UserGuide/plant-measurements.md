---
title: Set Up Plant Measurements
sidebar_position: 7
description: Create measurement sets, map instruments to variables, import measurement rows, and save validated plant data.
---

# Set Up Plant Measurements

Use this page when you need to connect real plant measurement instruments to model variables for DataRec workflows.

## Before You Start

- Open a saved diagram.
- Make sure the current diagram contains the network, nodes, ports, and variables you want to map.
- Keep the diagram out of computation mode; the **Plant Measurements** workflow is read-only while computation is processing.

## Create a Measurement Set

1. Open the **Analysis** section in the header toolbar.
2. Click **Plant Measurements**.
3. In the **Plant Measurements** dialog, click **New Measurement Set**.
4. In the **New Measurement Set** dialog, select **Network**.
5. Enter **Set Name** or keep the default placeholder.
6. Click **Create Set**.

## Map Instruments to Variables

1. In **Plant Measurements**, select the set from **Measurement Set**.
2. Open the **Instrument Mapping** tab.
3. Click **Add Mapping**.
4. Fill the mapping row with the network path, node, port, variable, instrument name, units, and optional accuracy or bounds.
5. Click **Save**.

## Enter or Import Measurements

1. Open the **Plant Measurements** tab inside the same dialog.
2. Click **Add Measurement** to enter rows manually.
3. Click **Import** to load `.csv`, `.xlsx`, or `.xls` measurement rows.
4. Review row errors and warnings.
5. Fix invalid rows before saving.
6. Click **Save**.

## Delete a Measurement Set

1. Select the set from **Measurement Set**.
2. Click **Delete Set**.
3. Confirm the deletion prompt.

## Result

The measurement set stores variable-instrument mappings and validated measurement rows. Saved rows can be used later by DataRec input generation.

## Troubleshooting

| Problem | What To Check |
| --- | --- |
| The dialog asks you to save the diagram first | Save the diagram, then reopen **Plant Measurements**. |
| **Add Measurement** is disabled | Select a measurement set and create at least one valid instrument mapping first. |
| Imported rows show errors | Check **Instrument Name**, **Value**, **Units**, **Date**, and **Time** fields. |
| A measurement does not match a mapping | Confirm the instrument name and units match exactly one saved mapping. |

## Related Pages

- [Edit node settings, streams, variables, and specs](./edit-node-variables)
- [Configure and start a computation](./run-computation)
- [Code explanation: Plant Measurements and Instrument Mapping](../CodeExplanation/plant-measurements-and-instrument-mapping)
