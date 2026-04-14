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
3. Read `reference/WOBAR_MOVE_SYSTEM.md` for move schema
4. If act-specific, read `reference/WOBAR_FRAMEWORK.md`

## Determine Network Context

- Check if this is a new visual or modifying an existing one.
- If new: create `touchdesigner/networks/[descriptive_name]/` with a `moves/` subfolder.
- If existing: identify the network folder under `touchdesigner/networks/`.
- Count existing move files in `moves/` to determine next move number.

## Execute the Move

### Step 1: Inspect Before-State

Before touching anything in TD, use TWOZERO to read the current state of every node, parameter, and connection you plan to modify. Record this as the before-state.

For each planned operation, capture:
- **create_node**: before = `null` (node doesn't exist yet)
- **set_parameter**: before = current parameter value (read via TWOZERO)
- **connect**: before = current connection at that input (or `null` if empty)
- **disconnect**: before = the connection that exists
- **delete_node**: before = full node state (type, parameters, connections)

### Step 2: Execute via TWOZERO

Make all the TD changes. Build left to right. Follow naming conventions (`ctrl_`, `null_`, `base_`). Follow all rules from WOBAR_TD_AGENT_RULES.md.

### Step 3: Handle Failures

If any TWOZERO call fails mid-move:
1. Stop immediately. Do not continue.
2. Reverse all operations already executed, in reverse order, using the before-states.
3. Do NOT write a move file.
4. Report what failed and what was rolled back.

### Step 4: Write Move File

If all operations succeeded, write the move file as JSON (msgpack conversion happens later if needed):

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
      "type": "create_node|set_parameter|connect|disconnect|delete_node",
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

Use zero-padded 3-digit numbering: `move_001.json`, `move_002.json`, etc.

### Step 5: Validate

After the build, check the result against the act constraint table in WOBAR_TD_AGENT_RULES.md:

| Act | Required | Forbidden |
|-----|----------|-----------|
| 1 | Circles, warm purple glow, breath rhythm | Sharp geometry, aggressive motion, cool colors |
| 2 | Inward spiral, depth, tightening with audio | Outward expansion, warm colors dominating |
| 3 | Tunnel, 85-90% mirror, infinite depth, glitch on peaks | Emotional relief, warm/orange tones, perfect symmetry |
| 4 | Outward radial expansion, full color palette, rhythm | Inward motion, cool-only palette |
| 5 | Circle returns, portal closing, breath rhythm | New visual concepts |

If the build violates its act constraint, fix it (as another operation within the same move) before reporting completion.

## Report

After completion, state:
- What was built (brief)
- Move file location and number
- Any constraint violations caught and fixed
