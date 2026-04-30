---
title: WOBAR TD Index
version: 1.0
last_updated: 2026-04-15
status: live
scope: Single entry point for all TouchDesigner work. Decision tree for which docs to load, in what order, for each task type. Read this instead of guessing which TD files to pull.
---

# WOBAR TD INDEX

Read this before any TD build or advice. It tells you exactly what else to read and when.

---

## Document Registry

| File | Size | Purpose — one line |
|------|------|---------------------|
| `working/TD_CLAUDE_DEBUG_LOG.md` | Small | Confirmed wrong advice + corrected patterns. **Read before any action.** |
| `reference/WOBAR_TD_AGENT_RULES.md` | Medium | Build conventions: naming, architecture, color/material rules, visual identity lens, act identity (no hard constraints), Python rules. Non-negotiable. |
| `touchdesigner/reference_networks/README.md` | Medium | Structural examples — node chains + taste decisions for Act 1 circle, Act 3 tunnel. Diff against these before building from scratch. |
| `reference/WOBAR_TWOZERO_GUIDE.md` | Small | Confirmed operator type strings, parameter names, MCP limitations, known behaviors. |
| `reference/WOBAR_TD_REFERENCE.md` | **Large** | Full specs: audio pipeline, visual primitives by act, color system, export settings, failure patterns. Load by section, not full file. |
| `reference/WOBAR_MOVE_SYSTEM.md` | Small | Move JSON schema, lifecycle, network→comp mapping table, auto-rollback spec. |
| `reference/WOBAR_TD_EXPRESSION_COOKBOOK.md` | Medium | Paste-ready expressions: CHOP access, audio-reactive mappings, time, footguns. |
| `reference/WOBAR_GLSL_PATTERNS.md` | Medium | Act-specific GLSL shaders (10 total), utility functions, act color reference table. |
| `reference/WOBAR_TWOZERO_MCP_CATALOG.md` | **Large** | Full parameter tables for all 35 TWOZERO tools. Load by group, not full file. |
| `working/TD_BUILD_LOG.md` | Medium | Session-by-session build log. Correction tracker (2+ occurrences → promoted to AGENT_RULES). |
| `reference/td_library/TD_LIBRARY_INDEX.md` | **Library** | General TD knowledge base (brand-agnostic). 27 files covering all operator families, patterns, workflows. Read the index; it routes to the right file. |

---

## Related — General TD Library

The `td_library/` subfolder is a brand-agnostic TouchDesigner knowledge base. Use it when the question is about TD itself (operators, patterns, workflows) rather than WOBAR-specific conventions. When both apply, brand files (above) override — WOBAR_TD_AGENT_RULES and WOBAR_TD_REFERENCE are the source of truth for brand constraints.

Entry point: `td_library/TD_LIBRARY_INDEX.md` — routes by task (building audio reactivity, optimizing a slow project, exporting a music video, going live, projection mapping, installations).

---

## Decision Tree

### For any TD build or advice
1. `TD_CLAUDE_DEBUG_LOG.md` — check for matching past failures first (Rule 0)
2. `WOBAR_TD_AGENT_RULES.md` — naming, architecture, color/material rules, visual identity lens, act identity
3. `reference_networks/README.md` — find closest structural match (Rule 0b)
4. `WOBAR_TWOZERO_GUIDE.md` — confirmed type strings + limitations before calling TWOZERO

Then branch:

---

### Building a new visual module (new base COMP)
- `WOBAR_TD_REFERENCE.md` → Section 3 (Visual Primitives by Act) for node chains
- `WOBAR_FRAMEWORK.md` → act identity (emotional register + visual descriptors)
- `WOBAR_MOVE_SYSTEM.md` → network→comp mapping table, move schema
- If GLSL shader involved → `WOBAR_GLSL_PATTERNS.md`
- If POPX modules involved (any of: instancing, aim/look-at, mesh scatter, falloff fields, fluid sim, fractal growth, soft body / cloth / hair, strange attractors, voxel-art, typography rig, Voronoi shatter, etc.) → `td_library/TD_POPX_GUIDE.md`. **Read the capability table at top first** (rows ~25–90) — find the row matching your need, then jump to the named module's section. Guide is large (2651 lines) — load by section, not whole-file. Note POPX is a 3rd-party dep — bake to native POPs before final tox commits.

---

### Modifying an existing visual
- `reference_networks/README.md` — what the baseline should look like
- `WOBAR_TD_REFERENCE.md` → relevant section only (color = §4, feedback = §3, export = §8)
- If writing expressions → `WOBAR_TD_EXPRESSION_COOKBOOK.md`

---

### Writing a GLSL shader
- `WOBAR_GLSL_PATTERNS.md` — find closest act match, diff against it
- `WOBAR_TD_REFERENCE.md` → §4 (Color System) for exact palette hex values
- TD GLSL conventions (no #version, vUV.st, TDOutputSwizzle, uniforms via color page) are in WOBAR_GLSL_PATTERNS.md header

---

### Writing CHOP expressions or Python DAT scripts
- `WOBAR_TD_EXPRESSION_COOKBOOK.md` — paste-ready patterns
- Key footguns already in §7 of that doc: stale `.val`, export stealing, script-level globals, breakdown returning 0

---

### Using a specific TWOZERO tool
- `WOBAR_TWOZERO_GUIDE.md` first — confirmed behaviors and limitations
- `WOBAR_TWOZERO_MCP_CATALOG.md` — load only the relevant group section:
  - Network inspection → Group 1 (td_get_network, td_get_operator_info, td_find_op)
  - Creating operators → Group 2 (td_create_operator)
  - Setting parameters → Group 3 (td_set_operator_pars, td_execute_python)
  - DAT / GLSL text → Group 4 (td_read_dat, td_write_dat)
  - Reading data → Group 5 (td_read_chop, td_get_perf)
  - Saving / .tox → Group 6 (td_input_execute)
  - Navigation / UI → Group 7 (td_navigate_to, td_get_screenshot)

---

### Debugging a TD issue
- `TD_CLAUDE_DEBUG_LOG.md` — check first (failure log)
- `WOBAR_TD_REFERENCE.md` → §9 (Common Failure Patterns)
- `WOBAR_TD_EXPRESSION_COOKBOOK.md` → §7 (Common Footguns)
- `TD_BUILD_LOG.md` → Correction Tracker table for recurring issues

---

### Running td-save (end of session)
- `WOBAR_MOVE_SYSTEM.md` → On Save lifecycle
- `TD_BUILD_LOG.md` → update with session learnings, check correction tracker
- After writing: check if any correction hit 2+ occurrences → propose rule for AGENT_RULES.md

---

### Setting up audio pipeline
- `WOBAR_TD_REFERENCE.md` → §2 (Audio Pipeline) — full signal chain, channel reference, lag values
- `TD_CLAUDE_DEBUG_LOG.md` → audio tag entries (filterCHOP vs audiofilterCHOP, rmspower vs average, null_audio vs audio_in)

---

### Export / render setup
- `WOBAR_TD_REFERENCE.md` → §8 (Export Settings) — platform-specific tables, FFmpeg command, upload protocol
- `TD_CLAUDE_DEBUG_LOG.md` → export tag entries

---

## Large File Section Guide

### WOBAR_TD_REFERENCE.md sections
| Section | Lines (approx) | When to read |
|---------|----------------|-------------|
| §1 Operator Family Quick Reference | 1–45 | Orientation only |
| §2 Audio Pipeline | 46–165 | Building/debugging audio |
| §3 Visual Primitives by Act | 166–255 | Building a new visual |
| §4 Color System | 256–300 | Color pipeline, palette hex values |
| §5 Analog Grain | 301–325 | Adding grain layer |
| §6 Archive Footage | 326–370 | Integrating archive clips |
| §7 Scene Architecture | 371–415 | Timer sequencing, switching |
| §8 Export Settings | 416–545 | Render and upload |
| §9 Common Failure Patterns | 546–585 | Debugging |

### WOBAR_TWOZERO_MCP_CATALOG.md groups
Load only the group you need. Searching the file for the tool name is faster than reading the whole catalog.

---

## File Status

| File | Status | Updated |
|------|--------|---------|
| TD_CLAUDE_DEBUG_LOG.md | live — append as failures confirmed | 2026-04-15 |
| WOBAR_TD_AGENT_RULES.md | live — append when correction promoted | 2026-04-15 |
| WOBAR_TWOZERO_GUIDE.md | live — append as behaviors confirmed | 2026-04-15 |
| WOBAR_TD_REFERENCE.md | locked — update only on major architecture change | 2026-04-15 |
| WOBAR_MOVE_SYSTEM.md | locked | 2026-04-14 |
| WOBAR_TD_EXPRESSION_COOKBOOK.md | live — append new patterns | 2026-04-15 |
| WOBAR_GLSL_PATTERNS.md | live — append new shaders | 2026-04-15 |
| WOBAR_TWOZERO_MCP_CATALOG.md | live — append as tool behaviors confirmed | 2026-04-15 |
| TD_BUILD_LOG.md | live — append each session | 2026-04-15 |
| reference_networks/README.md | live — add entry after each saved network | 2026-04-15 |
