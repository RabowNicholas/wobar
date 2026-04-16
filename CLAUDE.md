# WOBAR — Claude Code Project Instructions

You are working with Nick on WOBAR, an audio-reactive AV system for live DJ/EDM performance and content creation. This repo is a structured knowledge vault with reference files that govern all output.

---

## MCP Servers

### TWOZERO (TouchDesigner)
- URL: `http://localhost:40404/mcp`
- Purpose: Create, modify, and inspect TouchDesigner networks directly.
- Only available when TouchDesigner is running with the twozero plugin active.
- Before using TWOZERO tools: read the agent rules and reference files below.

---

## Orientation — Every Session

Before doing anything:
1. Read `WOBAR_CONTEXT.md` — master index of all files
2. Read `working/WOBAR_ACTIVE.md` — open loops, current status

Do not narrate this. Let context inform your work silently.

---

## TouchDesigner Builds — Required Reading

Before creating or modifying ANY TouchDesigner network:
1. Read `reference/WOBAR_TD_INDEX.md` — the TD decision tree. It tells you exactly which docs to load for the current task.
2. The index handles everything: debug log, agent rules, reference networks, TWOZERO guide, GLSL patterns, expression cookbook, section targeting for large files.

Do not build from general TD knowledge. Build from these files. Every parameter value, every naming convention, every color hex is specified.

---

## Reference File Pull Guide

### TouchDesigner
| File | When to pull |
|------|-------------|
| reference/WOBAR_TD_INDEX.md | **First** — any TD build, advice, or debugging. Decision tree lives here. |
| working/TD_CLAUDE_DEBUG_LOG.md | Always before TD action (Rule 0) — confirmed failures + corrected patterns |
| reference/WOBAR_TD_AGENT_RULES.md | Always — build conventions, naming, act constraints |
| touchdesigner/reference_networks/README.md | Always before building — find closest structural match first (Rule 0b) |
| reference/WOBAR_TWOZERO_GUIDE.md | Before any TWOZERO tool call — type strings, limitations, known behaviors |
| reference/WOBAR_TD_REFERENCE.md | By section — audio §2, visual primitives §3, color §4, export §8, failures §9 |
| reference/WOBAR_MOVE_SYSTEM.md | td-build / td-save / td-undo — move schema, network→comp mapping |
| reference/WOBAR_TD_EXPRESSION_COOKBOOK.md | Writing CHOP expressions or Python DAT scripts |
| reference/WOBAR_GLSL_PATTERNS.md | Writing or modifying GLSL shaders |
| reference/WOBAR_TWOZERO_MCP_CATALOG.md | Specific TWOZERO tool parameters — load the relevant group only |
| working/TD_BUILD_LOG.md | td-save — update session learnings; debugging — check correction tracker |

### Non-TD
| File | When to pull |
|------|-------------|
| reference/WOBAR_FRAMEWORK.md | Act identity, arc structure, percentages |
| reference/WOBAR_BRAND.md | Brand positioning, mission, archetype |
| reference/WOBAR_COPY.md | Any written output |
| reference/WOBAR_SONIC.md | Sonic identity, genre, reference artists |
| reference/WOBAR_ARCHIVE.md | Archive footage sourcing |
| reference/WOBAR_CLAUDE.md | Communication style, output standards |
| reference/WOBAR_PATCH_SYSTEM.md | Serum 2 patch naming and macro conventions |

---

## Communication Standards

- Terse, direct. No preamble, no postamble.
- First pass should be usable, not a rough draft.
- Speak act language fluently: "Act 3/4 cusp," "early Act 4 register," "Act 2→3 transition."
- Never conflate Act 3 and Act 4.
- Never produce generic output that could apply to any bass artist.

---

## Build Workflow with TWOZERO

When Nick asks to build or modify a TD network:

1. **Read WOBAR_TD_INDEX.md** — get the exact reading list for this task type.
2. **Check debug log** — TD_CLAUDE_DEBUG_LOG.md before any action (Rule 0).
3. **Check reference networks** — find closest structural match, diff against it (Rule 0b).
4. **Confirm scope** — which act, which visual primitive, what's the output target.
5. **Inspect first** — use TWOZERO to read the current project state before creating anything.
6. **Build** — follow naming conventions, control architecture, color pipeline exactly.
7. **Validate** — check act constraint table in WOBAR_TD_AGENT_RULES.md before presenting.
8. **Log** — append to `working/TD_BUILD_LOG.md` at session end.

---

## Session Close-Out

At the end of every session:
1. Update `working/WOBAR_ACTIVE.md` — rewrite touched loop entries.
2. Ask if loops are closed or still open. Move closed loops to `working/WOBAR_CLOSED.md`.
3. Add a row to the session log in WOBAR_ACTIVE.md.
4. If a TD build happened, append to `working/TD_BUILD_LOG.md`.

---

## Feedback Loop

`working/TD_BUILD_LOG.md` is the improvement mechanism. Every TD session logs:
- What was built
- What the agent got right first pass
- What needed manual correction
- New patterns discovered

If a correction appears 2+ times in the log, it becomes a rule in `reference/WOBAR_TD_AGENT_RULES.md`. Nick or Claude (in Cowork) will periodically review the log and promote patterns to rules.
