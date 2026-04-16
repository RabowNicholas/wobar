---
title: TWOZERO MCP Tool Catalog
version: 1.0
last_updated: 2026-04-15
status: live
scope: Complete parameter-level reference for all 36 TWOZERO MCP tools. Decision tree at the bottom.
dependencies: [[reference/WOBAR_TWOZERO_GUIDE]], [[reference/WOBAR_TD_AGENT_RULES]]
---

# TWOZERO MCP TOOL CATALOG

35 tools confirmed with schemas. 1 listed under "Schema Unknown."

---

## GROUP 1 — Node Creation

### `td_create_operator`
Create a new operator in a TD network.

| Parameter | Type | Req | Notes |
|-----------|------|-----|-------|
| `type` | string | ✅ | TD type string e.g. `glslTOP`, `constantCHOP`, `baseCOMP` |
| `name` | string | — | TD auto-names if omitted |
| `parent` | string | — | Parent COMP path; defaults to currently open network |
| `parameters` | object | — | Key-value pars to set on creation; include `nodeX`, `nodeY` here |
| `target_instance` | string | — | |

**Example:** `td_create_operator(type="constantCHOP", name="ctrl_fractal", parent="/project1/base_act2", parameters={"nodeX": -400, "nodeY": 0})`

**Gotchas:** Response includes a `📋 PAR` block — read it for exact par names before calling `td_set_operator_pars`. Connections must be wired separately via `td_execute_python`.

**vs. sibling:** Use `td_execute_python` for batch creation of 5+ ops.

---

## GROUP 2 — Parameter Editing

### `td_set_operator_pars`
Set parameter values and flags on an existing operator.

| Parameter | Type | Req | Notes |
|-----------|------|-----|-------|
| `path` | string | ✅ | Full operator path |
| `parameters` | object | — | Par name → value pairs |
| `bypass` | bool | — | Set bypass state |
| `viewer` | bool | — | Set viewer flag |
| `allowCooking` | bool | — | COMP-only; stops internal network from cooking |
| `target_instance` | string | — | |

**Example:** `td_set_operator_pars(path="/project1/base/lvc", parameters={"brightness1": 2.0, "gamma1": 0.70})`

**Gotchas:** Cannot set expressions — use `td_execute_python` with `par.expr + par.mode = ParMode.EXPRESSION`. Never set `par.val` before an expression; it poisons the read cache.

---

### `td_get_par_info`
Get parameter names and details for a TD operator type.

| Parameter | Type | Req | Notes |
|-----------|------|-----|-------|
| `op_type` | string | ✅ | e.g. `"levelTOP"`, `"blurTOP"` |
| `pars` | string[] | — | Specific par names for full detail |
| `target_instance` | string | — | |

**Example:** `td_get_par_info(op_type="levelTOP", pars=["contrast", "brightness1"])`

**Gotchas:** None confirmed. Call before setting pars on an unfamiliar op type.

**vs. sibling:** Faster than `td_get_operator_info` when you only need par names for a type, not a live instance.

---

## GROUP 3 — Connection / Wiring

### `td_execute_python`
Run arbitrary Python inside TD. Only tool that can wire connections and set expressions.

| Parameter | Type | Req | Notes |
|-----------|------|-----|-------|
| `code` | string | ✅ | Python code; print output and last expression returned |
| `target_instance` | string | — | |

**Example:**
```python
td_execute_python(code="""
rec = op('/project1/base/rec_out')
null = op('/project1/base/null_out')
rec.inputConnectors[0].connect(null)
""")
```

**Gotchas:**
- All `op()` calls must be inside a function body — no script-level globals
- No list comprehensions referencing outer-scope vars — use explicit for loops
- Use `par.eval()` not `par.val` to verify expression results

---

## GROUP 4 — Inspection

### `td_get_network`
List all operators at a network path.

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `path` | string | `"/"` | Network to inspect |
| `depth` | int | 0 | 0=current level, 1=include COMP children |
| `nodeXY` | bool | false | Include node coordinates |
| `includeSystem` | bool | false | Include `/ui`, `/sys` |
| `target_instance` | string | — | |

**Example:** `td_get_network(path="/project1/base_audio", depth=0)`

**Gotchas:** `depth=1` can be slow on large projects.

---

### `td_get_operator_info`
Read full state of one live operator — connections, expressions, non-default pars, CHOP channels.

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `path` | string | ✅ | Full operator path |
| `detail` | enum | `"full"` | `"summary"` or `"full"` — use summary unless you need everything |
| `target_instance` | string | — | |

**Example:** `td_get_operator_info(path="/project1/base/fractal_glsl", detail="summary")`

**vs. sibling:** Use `td_get_par_info` to look up par names by type; use this for live instance state.

---

### `td_find_op`
Find operators by name and/or type across the project.

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `name` | string | — | Substring match on op name |
| `type` | string | — | Substring match on OPType |
| `root` | string | `/project1` | Search root |
| `max_depth` | number | — | Recursion limit |
| `max_results` | int | 50 | |
| `detail` | enum | `"basic"` | `"basic"` or `"summary"` |
| `target_instance` | string | — | |

**Example:** `td_find_op(type="glslTOP", root="/project1")`

**vs. sibling:** Use when path is unknown. Use `td_search` to find ops by code/expression content.

---

### `td_search`
Search for text across all DAT code, expressions, and string parameter values.

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `query` | string | ✅ | Words = OR; quotes = exact phrase |
| `root` | string | `/project1` | |
| `scope` | enum | `"all"` | `code`, `editable`, `expressions`, `parameters`, `all` |
| `context` | int | 0 | Lines before/after each match |
| `count_only` | bool | false | Fast existence check |
| `max_results` | int | 50 | |
| `target_instance` | string | — | |

**Example:** `td_search(query="sub_pressure", scope="expressions")`

**Gotchas:** `scope="all"` is slow (~1.5s). Use `scope="expressions"` or `"code"` when possible.

---

### `td_get_focus`
Get the currently open network and selected operators.

| Parameter | Type | Notes |
|-----------|------|-------|
| `screenshots` | bool | Start screenshot batch for all selected ops |
| `as_top` / `max_size` | | Passed to screenshot batch |
| `target_instance` | string | |

**Example:** `td_get_focus()`

**Gotchas:** Rollover (mouse-under) ≠ selected. When user says "this operator," use selected, not rollover. Call first whenever user uses spatial language.

---

### `td_get_hints`
Compact tips and correct parameter names for a topic before building.

| Parameter | Type | Req | Notes |
|-----------|------|-----|-------|
| `topic` | string | ✅ | `construction`, `connections`, `parameters`, `scripting`, `animation`, `noise`, `ui_analysis`, `panel_layout`, `screenshots`, `input_simulation`, `undo`, `networking`, `all` |
| `target_instance` | string | — | |

**Example:** `td_get_hints(topic="construction")`

**Gotchas:** Always call with `topic="construction"` before any multi-op build. Always call `topic="input_simulation"` before using `td_input_execute`.

**vs. sibling:** Compact tips. Use `td_get_docs` for full in-depth reference.

---

### `td_get_docs`
In-depth documentation on a TD topic.

| Parameter | Type | Notes |
|-----------|------|-------|
| `topic` | string | Omit to list available topics |
| `target_instance` | string | |

**Example:** `td_get_docs()` to list topics, `td_get_docs(topic="glsl")` for detail.

---

### `td_get_errors`
Find errors, warnings, and broken expressions across operators.

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `path` | string | current network | `"/"` for entire project |
| `recursive` | bool | true | |
| `include_log` | bool | true | Includes script error log |
| `target_instance` | string | — | |

**Gotchas:** Always call after fixing issues to confirm no new errors appeared.

---

### `td_get_perf`
Performance metrics — FPS, cook times, slowest operators.

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `path` | string | current network | `"/"` for project-wide |
| `top` | int | 15 | Number of slowest ops to return |
| `target_instance` | string | — | |

**Gotchas:** GPU cook times show `0.0` when GPU-cached — not a real zero.

---

### `td_agents_md`
Read, write, or update an `agents_md` documentation DAT inside a COMP.

| Parameter | Type | Req | Notes |
|-----------|------|-----|-------|
| `path` | string | ✅ | COMP path |
| `action` | enum | ✅ | `read`, `update`, `write` |
| `content` | string | — | Only for `action="write"` |
| `target_instance` | string | — | |

**Gotchas:** `update` refreshes auto-generated sections (children, connections) but preserves human-written sections.

---

## GROUP 5 — CHOP / DAT Data I/O

### `td_read_chop`
Read channel sample values from a CHOP.

| Parameter | Type | Notes |
|-----------|------|-------|
| `path` | string ✅ | |
| `channels` | string[] | Omit to read all |
| `start` / `end` | int | Sample range (0-based) |
| `target_instance` | string | |

**Gotchas:** Large CHOPs (e.g. recordCHOP after a full song) exceed token limits — analyze inside TD via `td_execute_python` instead.

---

### `td_read_dat`
Read text content of a DAT with line numbers.

| Parameter | Type | Notes |
|-----------|------|-------|
| `path` | string ✅ | |
| `start_line` / `end_line` | int | 1-based; omit to read full file |
| `target_instance` | string | |

---

### `td_write_dat`
Write or patch text content of a DAT.

| Parameter | Type | Notes |
|-----------|------|-------|
| `path` | string ✅ | |
| `text` | string | Full replacement |
| `old_text` + `new_text` | string | Targeted patch — `old_text` must be unique |
| `replace_all` | bool | Replace all occurrences of `old_text` |
| `target_instance` | string | |

**Example (patch):** `td_write_dat(path="...", old_text="pow(uChaos, 1.8)", new_text="pow(uChaos, 3.0)")`

**Gotchas:** `old_text` must be unique in the file — provide more surrounding context if it fails.

---

## GROUP 6 — Screenshots & Visual Feedback

### `td_get_screenshot`
Screenshot of a specific operator's viewer. Two-step async.

| Parameter | Type | Notes |
|-----------|------|-------|
| `path` | string ✅ | Step 1: full op path |
| `request_id` | string ✅ | Step 2: retrieve result |
| `max_size` | int | Default 512 |
| `as_top` | bool | Capture TOP directly, preserves alpha |
| `format` | enum | `auto`, `jpg`, `png` |
| `output_path` | string | Custom save location |

**Example:** Step 1 → `td_get_screenshot(path="...", max_size=600)` → get `requestId` → Step 2 → `td_get_screenshot(request_id="abc")` → Read file.

**vs. sibling:** Operator viewer. Use `td_get_screen_screenshot` for what user sees on monitor.

---

### `td_get_screenshots`
Batch screenshot multiple operators. Two-step async via `batch_id`.

| Parameter | Type | Notes |
|-----------|------|-------|
| `paths` | string[] ✅ | Step 1 |
| `batch_id` | string ✅ | Step 2 |
| `max_size` / `format` / `as_top` / `output_dir` | | Same as `td_get_screenshot` |

---

### `td_get_screen_screenshot`
Screenshot of the actual monitor. Two-step async.

| Parameter | Type | Notes |
|-----------|------|-------|
| `request_id` | string | Step 2 |
| `crop_x/y/w/h` | int | Actual screen pixels |
| `max_size` | int | Auto: 1920 full / 1:1 for crop |
| `display` | int | Default 0 |

**Gotchas:** Use with `td_click_screen_point` or `td_screen_point_to_global` for UI interaction.

---

### `td_navigate_to`
Navigate the Network Editor to show a specific operator.

| Parameter | Type | Req |
|-----------|------|-----|
| `path` | string | ✅ |
| `target_instance` | string | — |

**Gotchas:** Only navigates — does not select.

---

### `td_op_screen_rect`
Get screen bounding box of an operator node in the network editor.

| Parameter | Type | Req |
|-----------|------|-----|
| `path` | string | ✅ |
| `target_instance` | string | — |

Returns `{x, y, w, h, cx, cy}`. **Gotchas:** Only works if the parent network is currently open in a pane.

---

## GROUP 7 — UI Interaction (Mouse / Keyboard)

### `td_input_execute`
Send a sequence of mouse/keyboard commands to TD.

| Parameter | Type | Req | Notes |
|-----------|------|-----|-------|
| `commands` | object[] | ✅ | Types: `focus`, `move`, `click`, `dblclick`, `mousedown`, `mouseup`, `key`, `type`, `wait`, `scroll` |
| `coord_space` | enum | — | `logical` (default) or `physical` |
| `on_error` | enum | — | `stop` (default) or `continue` |

**Example:** `td_input_execute(commands=[{"type":"focus"},{"type":"key","keys":"ctrl+z"}])`

**Gotchas:** Returns immediately — poll `td_input_status` until `status="idle"` before next action. Call `td_get_hints(topic="input_simulation")` before first use.

---

### `td_input_status`
Poll the input command queue. Returns `{status, queue_remaining, last_error}`. No required params.

---

### `td_input_clear`
Clear the input queue immediately. No required params. Use when a command sequence gets stuck.

---

### `td_click_screen_point`
Click a point derived from a `td_get_screen_screenshot` result.

| Parameter | Type | Req | Notes |
|-----------|------|-----|-------|
| `request_id` | string | ✅ | From `td_get_screen_screenshot` |
| `u` + `v` | float | — | Normalized 0–1 inside screenshot |
| `image_x` + `image_y` | float | — | Pixel coords in screenshot image |
| `button` | enum | — | `left`, `right`, `middle` |
| `focus` / `hold` / `duration` | | — | |

---

### `td_screen_point_to_global`
Convert a screenshot point to absolute screen coordinates. Same params as `td_click_screen_point`. Returns physical + logical coords and a ready `td_input_execute` payload.

---

## GROUP 8 — Project & Session Control

### `td_list_instances`
List all running TD instances with active MCP servers. No params. Returns `[{port, project, pid, instanceId}]`.

**Gotchas:** Call at session start when working with multiple TD instances. `instanceId` is passed as `target_instance` to all other tools.

---

### `td_project_quit`
Save and/or close the current TD project.

| Parameter | Type | Default |
|-----------|------|---------|
| `save` | bool | true |
| `force` | bool | false |

**Gotchas:** Shuts down the MCP server. Irreversible in session.

---

### `td_reinit_extension`
Reinitialize an extension on a COMP after editing its code.

| Parameter | Type | Req |
|-----------|------|-----|
| `path` | string | ✅ |

**Gotchas:** Batch all code edits first, then reinit once.

---

### `td_test_session`
Manage test sessions and bug reports.

| Parameter | Type | Req | Notes |
|-----------|------|-----|-------|
| `action` | enum | ✅ | `export_chat_id`, `export_chat`, `submit_report`, `start`, `note`, `import_chat`, `end`, `list`, `pull` |
| `prompt` / `summary` / `outcome` / `tags` / `text` / `session` / `result_op` | | — | Context-dependent on action |

**Gotchas:** Do NOT proactively suggest at session end. Only use when user reports a bug or explicitly asks to export.

---

## GROUP 9 — Logging & Debugging

### `td_read_textport`
Read last N lines from the TD textport. `lines` (int, default 50).

### `td_clear_textport`
Clear the MCP textport buffer. No required params. Call before a debug loop.

### `td_dev_log`
Read last N entries from MCP dev log (dev mode only). `count` (int, default 10).

### `td_clear_dev_log`
Clear and restart the MCP dev log (dev mode only). No required params.

---

## Discovered But Schema Unknown

| Tool | Notes |
|------|-------|
| `td_get_operators_info` | Likely batch version of `td_get_operator_info`. Schema not loaded. |

---

## Decision Tree

| When you want to… | Use |
|-------------------|-----|
| Create a new node | `td_create_operator` |
| Set parameter values | `td_set_operator_pars` |
| Set a parameter expression | `td_execute_python` (`par.expr + par.mode = ParMode.EXPRESSION`) |
| Wire two operators together | `td_execute_python` (`inputConnectors[n].connect(op)`) |
| Know parameter names for an op type | `td_get_par_info` |
| Read full state of a live op | `td_get_operator_info(detail="summary")` |
| List all ops in a network | `td_get_network` |
| Find an op by name (path unknown) | `td_find_op` |
| Find where something is referenced in code/exprs | `td_search(scope="expressions")` |
| Know what the user is looking at | `td_get_focus` |
| Build 5+ operators in batch | `td_execute_python` after `td_get_hints(topic="construction")` |
| Read a GLSL shader or script | `td_read_dat` |
| Write/patch a GLSL shader | `td_write_dat` (patch with `old_text`/`new_text`) |
| Read CHOP channel values | `td_read_chop` |
| See what an op is outputting visually | `td_get_screenshot` (two-step) → Read |
| See the full TD screen | `td_get_screen_screenshot` (two-step) → Read |
| Click something in the TD UI | `td_get_screen_screenshot` → `td_click_screen_point` |
| Simulate a keyboard shortcut | `td_input_execute(commands=[{type:"key",keys:"ctrl+z"}])` |
| Check for errors after a change | `td_get_errors` |
| Check performance / find slow ops | `td_get_perf` |
| Look up correct par names before building | `td_get_hints(topic="construction")` |
| Get deep documentation on a TD topic | `td_get_docs` |
| Navigate the TD UI to an operator | `td_navigate_to` |
| Read console / print output | `td_read_textport` |
| Identify available TD instances | `td_list_instances` |
| Save and close TD | `td_project_quit` |
| Reload a COMP extension after code edit | `td_reinit_extension` |
| Read a COMP's self-documentation DAT | `td_agents_md(action="read")` |
