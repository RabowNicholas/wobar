---
description: "Undo last N TouchDesigner moves by replaying before-states. Default: undo 1 move."
allowed-tools: ["Read", "Bash", "Glob", "Grep", "mcp__twozero*"]
---

# td-undo — Reverse Last N Moves

Undo the last N moves made by the agent in a TD network. Pops moves off the stack in reverse order.

## Arguments

$ARGUMENTS

- If a number is provided (e.g., `/td-undo 3`), undo that many moves.
- If no number, undo 1 move.
- If a network name is provided, operate on that network. Otherwise, use the most recently modified network.

## Execution

### Step 1: Identify Network and Moves

1. If no network specified, find the most recently modified network by checking modification times of files in `touchdesigner/networks/*/moves/`.
2. List all `.json` move files in that network's `moves/` folder, sorted by number (highest first).
3. Confirm the requested number of moves exist. If user asks to undo 3 but only 2 exist, report this and ask whether to undo the 2 that exist.

### Step 2: Read Move Files

Read the last N move files in reverse order (highest number first).

### Step 3: Replay Before-States

For each move, in reverse order, process its operations list in reverse:

| Operation Type | Undo Action |
|---------------|-------------|
| `create_node` | Delete the node at `path` via TWOZERO |
| `delete_node` | Recreate the node from the stored before-state via TWOZERO |
| `set_parameter` | Set the parameter back to `before` value via TWOZERO |
| `connect` | Restore previous connection from `before` (or disconnect if `before` was `null`) |
| `disconnect` | Reconnect using the stored `before` connection |

### Step 4: Delete Move Files

After successfully replaying all before-states, delete the move files that were undone.

### Step 5: Handle Failures

If a TWOZERO call fails during undo:
1. Stop and report which operation failed and why.
2. Do NOT delete any move files — the state is now uncertain.
3. Report what was successfully undone and what remains.

## Report

After completion, state:
- How many moves were undone
- What each move was (use the label from the move file)
- Current move count remaining in the stack
