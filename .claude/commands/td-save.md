---
description: "Save .tox checkpoint via TWOZERO, flush move history, analyze session for learnings."
allowed-tools: ["Read", "Write", "Edit", "Bash", "Glob", "Grep", "mcp__twozero*"]
---

# td-save — Checkpoint, Flush, Learn

Save the current network state as a .tox checkpoint, flush move history, and analyze the session for learnings.

## Arguments

$ARGUMENTS

- If a network name is provided, save that network. Otherwise, use the most recently modified network.

## Required Reading

1. Read `reference/WOBAR_MOVE_SYSTEM.md` for flush rules
2. Read `working/TD_BUILD_LOG.md` for existing correction tracker

## Execution

### Step 1: Identify Network

1. If no network specified, find the most recently modified network under `touchdesigner/networks/`.
2. Confirm the network folder exists.

### Step 2: Determine Version Number

1. List existing `.tox` files in the network folder.
2. Find the highest version number.
3. Next version = highest + 1. Zero-padded to 3 digits.
4. If no `.tox` files exist, start at `v001`.

### Step 3: Save .tox via TWOZERO

Execute the save command via TWOZERO. The TD base COMP path should match the network being saved.

```python
op('[base_comp_path]').saveToFile('[full_path_to_network_folder]/[network_name]_vNNN.tox')
```

Confirm the file was written by checking the filesystem.

### Step 4: Flush Move History

Delete all files in the network's `moves/` folder. Move numbering restarts at `move_001` for the next session.

### Step 5: Log Checkpoint in CHANGE_LOG.md

Append an entry to the network's `CHANGE_LOG.md`:

```
### vNNN — YYYY-MM-DD
STATE: [brief description of what the visual looks like at this checkpoint]
MOVES: [how many moves were flushed]
```

### Step 6: Session Learnings Analysis

Review the move files that were just flushed (read them before deleting in Step 4). Analyze:

1. **What got undone** — any `/td-undo` calls this session? Those are mistakes. What went wrong?
2. **Parameter corrections** — did the agent set a value and then change it in a later move? What was the correction?
3. **Patterns** — any new conventions discovered that aren't in the rules yet?

Update `working/TD_BUILD_LOG.md`:
- Add a new build session entry with what was built, what worked, what needed correction.
- Check the correction tracker table. If any correction now appears 2+ times across sessions, flag it for promotion to `reference/WOBAR_TD_AGENT_RULES.md` and propose the rule.

## Report

After completion, state:
- .tox file saved (path and version)
- Number of moves flushed
- Any learnings or corrections flagged
- Any rules proposed for promotion
