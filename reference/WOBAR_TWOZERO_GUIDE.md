---
title: TWOZERO MCP Guide
version: 0.1
last_updated: 2026-04-14
status: live
scope: Empirical reference for the TWOZERO MCP server. Capabilities, limitations, operator type strings, and known behaviors discovered through use. Add entries as they are confirmed.
dependencies: [[reference/WOBAR_TD_AGENT_RULES]]
---

# TWOZERO MCP GUIDE

Living doc. Not speculative — only add entries that have been confirmed in a real session.

---

## Tool Index

| Tool | What it does |
|------|-------------|
| `td_create_operator` | Create a new operator in a network |
| `td_set_operator_pars` | Set one or more parameters on an operator |
| `td_get_operator_info` | Read current state of an operator (type, pars, connections) |
| `td_get_par_info` | Read parameter details for an operator |
| `td_get_network` | Read all operators in a network |
| `td_navigate_to` | Navigate the TD UI to a specific operator |
| `td_find_op` | Find an operator by name or path |
| `td_get_screenshot` | Screenshot of the TD window |
| `td_get_screen_screenshot` | Screenshot of a specific operator's viewer |
| `td_execute_python` | Run arbitrary Python in TD |
| `td_read_chop` | Read channel values from a CHOP |
| `td_read_dat` | Read text content from a DAT |
| `td_write_dat` | Write text content to a DAT |
| `td_get_errors` | Get current TD errors and warnings |
| `td_get_perf` | Get performance metrics |
| `td_get_focus` | Get currently focused network and selected ops |
| `td_get_hints` | Get operator creation hints / type strings |
| `td_get_docs` | Get TD documentation for an operator type |
| `td_input_execute` | Execute a textport command |
| `td_dev_log` | Read the developer log |

---

## Confirmed Operator Type Strings

Entries added only after confirmed successful use.

| Operator | Type string |
|----------|------------|
| (none yet) | — |

---

## Confirmed Parameter Behaviors

How specific parameter types behave when set via `td_set_operator_pars`.

| Operator type | Parameter | Notes |
|--------------|-----------|-------|
| (none yet) | — | — |

---

## Confirmed Limitations

Things TWOZERO cannot do, confirmed through failure.

| Limitation | Workaround |
|-----------|-----------|
| (none yet) | — |

---

## DAT / GLSL Text Workflow

*To be populated — have not yet confirmed the exact td_write_dat behavior for GLSL TOP shader DATs.*

---

## Known Behaviors

Quirks, timing issues, or non-obvious behavior confirmed through use.

| Behavior | Notes |
|----------|-------|
| (none yet) | — |
