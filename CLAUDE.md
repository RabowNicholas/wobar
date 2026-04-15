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
1. Read `reference/WOBAR_TD_AGENT_RULES.md` — build conventions, naming, architecture. **Non-negotiable.**
2. Read the relevant section of `reference/WOBAR_TD_REFERENCE.md` — exact parameter values, node chains, color palettes.
3. If the build targets a specific act, read `reference/WOBAR_FRAMEWORK.md` for act identity.

Do not build from general TD knowledge. Build from these files. Every parameter value, every naming convention, every color hex is specified. Use the specified values.

---

## Reference File Pull Guide

| File | When to pull |
|------|-------------|
| reference/WOBAR_TD_AGENT_RULES.md | ANY TouchDesigner build or modification |
| reference/WOBAR_TD_REFERENCE.md | Parameter values, node chains, audio pipeline, color system, export |
| reference/WOBAR_TWOZERO_GUIDE.md | TWOZERO tool usage, operator type strings, confirmed limitations |
| reference/WOBAR_MOVE_SYSTEM.md | Move history schema, undo mechanics, auto-rollback spec |
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

1. **Read the rules** — WOBAR_TD_AGENT_RULES.md + relevant WOBAR_TD_REFERENCE.md section.
2. **Confirm scope** — which act, which visual primitive, what's the output target.
3. **Inspect first** — use TWOZERO to read the current project state before creating anything. Understand what exists.
4. **Build** — create the network following the conventions exactly. Use the naming patterns, the control architecture, the color pipeline.
5. **Validate** — check the build against the act constraint table in WOBAR_TD_AGENT_RULES.md before presenting.
6. **Log** — after the session, append what happened to `working/TD_BUILD_LOG.md`.

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
