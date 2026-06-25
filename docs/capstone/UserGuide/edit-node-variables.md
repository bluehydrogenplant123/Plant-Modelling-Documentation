---
title: Edit Node Settings, Streams, Variables, and Specs
sidebar_position: 4
description: Use the node toolbar tabs to edit node names, stream values, node variables, and specification fields.
---

# Edit Node Settings, Streams, Variables, and Specs

Use this page when you need to edit data inside a node on the canvas.

## Before You Start

- Open a saved diagram.
- Make sure the node you want to edit is visible on the canvas.
- Save the diagram before editing if you want the current network state to be recoverable.

## Open the Node Editor

1. Click a node on the canvas.
2. Use the node toolbar that appears near the selected node.
3. Choose one of these tabs: **Settings**, **Streams**, **Node Variables**, or **Specs**.

## Update Settings

1. Open the **Settings** tab.
2. Select the relevant **Time Period** if the node has time-period rows.
3. Edit the visible node fields.
4. If you rename the node, check that no duplicate-name warning appears.
5. Click **Save** in the main header toolbar when your node edits are complete.

## Edit Stream Values

1. Open the **Streams** tab.
2. Choose a **Time Period**.
3. Choose a **Port**.
4. If the port is connected, use **Go to Stream** to switch from port variables to stream values.
5. Review **Components**, **Flows**, and **Fractions**.
6. Use **Back to Port** to return to port-level variables.

## Edit Node Variables

1. Open the **Node Variables** tab.
2. Choose a **Time Period**.
3. Edit the visible variable input fields.
4. Use **Show Hidden Variables** if the variable you need is hidden by default.
5. Use **Hide Hidden Variables** after editing if you want to return to the compact view.

## Edit Specs

1. Open the **Specs** tab.
2. Select the port or time-period context shown by the editor.
3. Update specification values that apply to the selected node.
4. Save the diagram from the main header after completing the edits.

## Result

The selected node's settings, streams, variables, or specs are updated in the canvas state and can be persisted with the main **Save** button.

## Troubleshooting

| Problem | What To Check |
| --- | --- |
| The node toolbar does not appear | Click the node body, not empty canvas space. |
| **Go to Stream** is disabled | The selected port may not have a connected edge, or the stream view may not have enough display variables. |
| A variable is missing | Click **Show Hidden Variables** or check whether the selected port and time period are correct. |
| Edits disappear after refresh | Click the main header **Save** button before leaving the page. |

## Related Pages

- [Create, open, save, import, and export models](./model-workflow)
- [Create and save equations](./equation-writing)
- [Configure time periods](./time-periods)
