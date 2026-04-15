---
description: "Wraps all TouchDesigner modifications with move tracking. Captures before-state, executes changes via TWOZERO, writes move file for undo."
allowed-tools: ["Read", "Write", "Bash", "Glob", "Grep", "Agent", "mcp__twozero*"]
---

# td-build — TouchDesigner Build with Move Tracking

You are executing a TD modification request with full move tracking. One user request = one move.

## User Request

$ARGUMENTS

## Required Reading — Do This First

1. Read `reference/WOBAR_TD_AGENT_RULES.md`
2. Read the relevant section of `reference/WOBAR_TD_REFERENCE.md` for the visual primitive being built
3. Read `reference/WOBAR_MOVE_SYSTEM.md` for move schema and network→comp mapping
4. If act-specific, read `reference/WOBAR_FRAMEWORK.md`

## Determine Network Context

- Check if this is a new visual or modifying an existing one.
- Look up the network folder in the Network → TD Comp Mapping table in `WOBAR_MOVE_SYSTEM.md`.
- If new network: create `touchdesigner/networks/[descriptive_name]/` with a `moves/` subfolder and a `CHANGE_LOG.md` file with header `# CHANGE LOG — [network_name]`. Add the new network to the mapping table in `WOBAR_MOVE_SYSTEM.md`.
- If existing: confirm the network folder path.
- Determine next move number: find the highest existing move file number in `moves/` and add 1. Do not count files — use max + 1.

## Execute the Move

### Step 1: Inspect Before-State

Before touching anything in TD, use TWOZERO to read the current state of every node, parameter, connection, and DAT text you plan to modify. Record this as the before-state.

For each planned operation, capture:
- **create_node**: before = `null` (node doesn't exist yet)
- **set_parameter**: before = current parameter value (read via TWOZERO)
- **connect**: before = current connection at that input (or `null` if empty)
- **disconnect**: before = the connection that exists
- **delete_node**: before = full node state (type, parameters, connections)
- **set_dat_text**: before = full current text content of the DAT (read via TWOZERO)

### Step 2: Execute via TWOZERO

Make all the TD changes. Build left to right. Follow naming conventions (`ctrl_`, `null_`, `base_`). Follow all rules from WOBAR_TD_AGENT_RULES.md.

### Step 3: Handle Failures

If any TWOZERO call fails mid-move:
1. Stop immediately. Do not continue.
2. Reverse all operations already executed, in reverse order, using the before-states.
3. Do NOT write a move file.
4. If the rollback itself fails partway, write `move_NNN_failed.json` documenting what was intended, what succeeded, and where rollback broke. Report that manual TD inspection is required.
5. Report what failed and what was rolled back.

### Step 4: Write Move File

If all operations succeeded, write the move file:

```
touchdesigner/networks/[network]/moves/move_NNN.json
```

Schema:
```json
{
  "label": "short description of what was done",
  "timestamp": "ISO 8601",
  "network": "network folder name",
  "operations": [
    {
      "type": "create_node|set_parameter|connect|disconnect|delete_node|set_dat_text",
      "path": "/full/td/path",
      "parameter": "param_name (if set_parameter)",
      "from": "source path (if connect)",
      "to": "target path (if connect)",
      "input_index": 0,
      "before": null
    }
  ]
}
```

### Step 5: Validate Against Act Constraints

Check the act constraint table in `reference/WOBAR_TD_AGENT_RULES.md`. If the build violates its act constraint, fix it (as another operation within the same move) before reporting completion.

## Report

After completion, state:
- What was built (brief)
- Move file location and number
- Any constraint violations caught and fixed
