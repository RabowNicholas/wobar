---
title: Move History System Spec
version: 1.0
last_updated: 2026-04-12
status: locked
scope: Defines the move history system for tracking and undoing AI agent changes to TouchDesigner networks.
dependencies: [[reference/WOBAR_TD_AGENT_RULES]]
---

# MOVE HISTORY SYSTEM

Granular undo for AI-agent TouchDesigner changes. Tracks every logical unit of work ("move") so it can be reversed.

---

## Core Concepts

- **Move** = everything the agent does in response to one user request. One request, one move.
- **Move stack** = ordered list of moves per network. Last in, first out. No surgical mid-stack undo.
- **Checkpoint** = `.tox` save. Flushes move history. Hard undo point.

---

## Folder Structure

```
wobar/touchdesigner/networks/
  [network_name]/
    [network_name]_v001.tox
    [network_name]_v002.tox
    CHANGE_LOG.md
    moves/
      move_001.msgpack
      move_002.msgpack
```

- One folder per visual/network.
- `.tox` checkpoints and `CHANGE_LOG.md` at the network root.
- `moves/` subfolder holds the move stack.

---

## Move File Schema (MessagePack)

Each `.msgpack` file contains:

```
{
  "label": "add caustic layer",
  "timestamp": "2026-04-12T14:32:00Z",
  "operations": [
    {
      "type": "create_node",
      "path": "/project1/base_act2/caustic_glsl",
      "before": null
    },
    {
      "type": "set_parameter",
      "path": "/project1/base_act2/lvc",
      "parameter": "contrast",
      "before": 1.30
    },
    {
      "type": "connect",
      "from": "/project1/base_act2/null_caustic_out",
      "to": "/project1/base_act2/comp_surface",
      "input_index": 1,
      "before": null
    }
  ]
}
```

### Operation Types

| Type | Before State | Undo Action |
|------|-------------|-------------|
| `create_node` | `null` (didn't exist) | Delete the node |
| `delete_node` | Full node serialization | Recreate the node |
| `set_parameter` | Previous parameter value | Set parameter to previous value |
| `connect` | Previous connection (or `null`) | Restore previous connection (or disconnect) |
| `disconnect` | The connection that existed | Reconnect |

---

## Move Lifecycle

### On Build (td-build)

1. Agent receives user request.
2. Agent inspects current state of everything it plans to touch via TWOZERO.
3. Agent captures before-state for each operation.
4. Agent executes all TWOZERO calls.
5. If all calls succeed: write `move_NNN.msgpack` to `moves/`.
6. If any call fails mid-move: auto-rollback — replay all before-states captured so far in reverse order. No move file written.

### On Undo (td-undo)

1. Read last N move files (default: 1).
2. For each move in reverse order: replay before-states via TWOZERO in reverse operation order.
3. Delete the move files.

### On Save (td-save)

1. Save `.tox` via TWOZERO: `op('[base]').saveToFile('[path]')`.
2. Increment version number: `[network]_v001.tox` → `[network]_v002.tox`.
3. Delete all files in `moves/`.
4. Move numbering restarts at `move_001` for next session.
5. Analyze session: review undone moves and parameter corrections. Update `TD_BUILD_LOG.md`. Check correction tracker — if any correction hits 2+ occurrences, propose promotion to `WOBAR_TD_AGENT_RULES.md`.

---

## Auto-Rollback

If a TWOZERO call fails during a move:

1. Stop executing further operations.
2. Reverse all operations already executed in this move, in reverse order.
3. Do not write a move file.
4. Report the failure and what was rolled back.

---

## Scope

- Only tracks changes made by the AI agent through TWOZERO.
- Manual changes in TD are not tracked.
- The before-state captured at move start reflects whatever is in TD at that moment, including manual edits.
