---
title: Blender Library Index
version: 1.0
last_updated: 2026-05-22
status: live
scope: Entry point for general Blender knowledge base. Brand-agnostic. Decision tree — pull files by task.
dependencies: none
blender_version_target: 4.2 LTS minimum, 4.5+ preferred
platform_target: Apple Silicon (M1 MacBook Pro + M1 Mac Studio)
mcp_target: Blender Foundation official MCP connector (Claude Desktop, drag-and-drop install from blender.org/lab/mcp-server/)
total_files: 23
total_lines: ~13,500
---

# BLENDER LIBRARY INDEX

Brand-agnostic Blender knowledge base. This file set is the general Blender expertise layer — WOBAR-specific rules will live in `reference/WOBAR_BLENDER_*.md` (Phase 3, not yet built). Read this index first, then pull only what the task needs.

Target: Blender 4.2+ on Apple Silicon. MCP-driven workflow via Blender Foundation's official connector.

---

## How To Use This Library

1. Identify task type — see Decision Tree below.
2. Read this file plus the 2–4 files it points to for the task.
3. Operator-equivalent docs (Python API, Geometry Nodes, Shader Nodes) are encyclopedic — use Grep or section jump, do not read top to bottom.
4. Brand-specific decisions (palette, act register, naming conventions) come from `WOBAR_BLENDER_*.md` (Phase 3 — not yet built), not from this library.
5. The MCP connector wraps the full `bpy` Python API. Anything the API can do, the agent can drive — see `BLENDER_PYTHON_API.md`.

---

## Document Registry

### Foundations — Read Early

| File | Scope | When to pull |
|------|-------|-------------|
| BLENDER_LIBRARY_INDEX.md | This file — map of the library | First, every Blender task |
| BLENDER_PYTHON_API.md | `bpy` reference — data model, context, ops, properties, datablock access, footguns | Always before any agent-driven action |
| BLENDER_DATA_MODEL.md | Scene / Collection / Object / Mesh / Material / NodeTree, linking, naming, garbage collection | Understanding what an MCP read/write actually touches |
| BLENDER_UI_VOCABULARY.md | Editor names, panel names, modes, layout — speaking Blender | Communicating with Nick or interpreting blender.org docs |
| BLENDER_APPLE_SILICON.md | Metal renderer, EEVEE Next on M1, Cycles GPU/Metal, memory caps, version-specific gotchas | Before any render; when anything platform-specific breaks |

### Primitives — Building Things

| File | Scope | When to pull |
|------|-------|-------------|
| BLENDER_MODELING.md | Edit-mode tools, modifiers, BMesh API | Creating or editing geometry |
| BLENDER_SCULPTING.md | Sculpt mode, brushes, dyntopo, multires, retopology | Organic/sculpted geometry (mostly-manual zone) |
| BLENDER_GEOMETRY_NODES.md | Procedural geometry graph — fields, attributes, scatter, instance, deform, sample, repeat-zones, simulation zones | Procedural modeling; the Blender analog of TD's POPX |
| BLENDER_SHADER_NODES.md | Shader graph — Principled BSDF, subsurface, anisotropic, emission, volume, displacement | Any custom material |
| BLENDER_MATERIALS.md | PBR conventions, baking, UV-vs-procedural, displacement-vs-bump, color management | Applied material work |
| BLENDER_ANIMATION.md | Keyframes, drivers, F-curves, NLA, armatures, constraints, audio-driven via baked sound | Anything that moves; includes bake-audio-to-driver pattern |

### Rendering & Output

| File | Scope | When to pull |
|------|-------|-------------|
| BLENDER_RENDER_EEVEE.md | EEVEE Next — real-time-ish raster engine, light sampling, shadows, SSR, M1 perf | Fast previews; stylized real-time-ish renders |
| BLENDER_RENDER_CYCLES.md | Path-traced render — samples, denoiser, light paths, motion blur, DOF, volume rendering | Cinematic offline renders; where Blender outpaces TD |
| BLENDER_COMPOSITOR.md | Post-comp node graph — glare, blur, color, masks, file output, render layers, cryptomatte | Final-frame compositing offline |

### Assets & I/O

| File | Scope | When to pull |
|------|-------|-------------|
| BLENDER_ASSET_IO.md | FBX, GLB, OBJ, USD, Alembic, asset browser, link vs append, Poly Haven workflow, HDRI workflow | Bringing geometry/materials in or out |
| BLENDER_ADDONS.md | Add-on system, must-haves (Node Wrangler, Loop Tools, Hard Ops, Quad Remesher), the MCP-as-addon | Configuring Blender; troubleshooting addons |

### Pattern Library — Recipes

| File | Scope | When to pull |
|------|-------|-------------|
| BLENDER_PATTERNS_PROCEDURAL.md | Procedural environments, scatter, instancing, recursive growth, generative form | Building cinematic 3D environments procedurally |
| BLENDER_PATTERNS_LIGHTING.md | 3-point, studio, HDRI-only, cinematic darkness, single-source dramatic, volumetric god rays | Lighting any 3D scene |
| BLENDER_PATTERNS_CINEMATIC.md | Camera language — DOF, motion blur, lens choice, framing, shot types, render-cost-vs-quality | Filmic look; shot composition |

### Workflow Playbooks — End-to-End

| File | Scope | When to pull |
|------|-------|-------------|
| BLENDER_WORKFLOW_RENDER_FOR_TD.md | Producing Mirror clips offline → ingest into TD (ProRes/PNG sequence, alpha, color management, frame rate, vertical export) | The Blender → TD pipeline for footage |
| BLENDER_WORKFLOW_ASSET_FOR_TD.md | Producing meshes/materials Blender → TD as `.glb`/`.fbx` (topology, naming, scale, axes, material conversion) | The Blender → TD pipeline for live assets |
| BLENDER_WORKFLOW_AGENT_DRIVEN.md | Working with Claude via MCP — the four Anthropic-blessed workflows + community patterns, prompt shapes, save discipline | Any agent-driven Blender session |

### Session Log — Live

| File | Scope | When to pull |
|------|-------|-------------|
| BLENDER_FOOTGUNS.md | Confirmed failure patterns — starts mostly empty, grown each session | Debugging; before any non-trivial agent action |

---

## Decision Tree

### For any Blender task (agent-driven)
1. `BLENDER_FOOTGUNS.md` — check for matching past failures first (Rule 0, mirrors TD pattern)
2. `BLENDER_PYTHON_API.md` — always, before any MCP action
3. `BLENDER_DATA_MODEL.md` — understanding what gets touched
4. `BLENDER_UI_VOCABULARY.md` — if Nick references a specific editor/panel/mode

Then branch:

### Building geometry from scratch
- `BLENDER_MODELING.md` — primitive shapes, modifiers
- `BLENDER_GEOMETRY_NODES.md` — if it's procedural / parametric

### Building a procedural environment / scatter / generative form
- `BLENDER_GEOMETRY_NODES.md` — first
- `BLENDER_PATTERNS_PROCEDURAL.md` — recipes

### Sculpting an organic form
- `BLENDER_SCULPTING.md` — but flag manual work zones to Nick

### Creating or modifying a material
- `BLENDER_SHADER_NODES.md` — graph mechanics
- `BLENDER_MATERIALS.md` — PBR, baking, UVs

### Setting up a render
- Real-time / fast: `BLENDER_RENDER_EEVEE.md`
- Cinematic / offline: `BLENDER_RENDER_CYCLES.md`
- Lighting setup: `BLENDER_PATTERNS_LIGHTING.md`
- Camera language: `BLENDER_PATTERNS_CINEMATIC.md`

### Final compositing for export
- `BLENDER_COMPOSITOR.md` — post stack
- `BLENDER_WORKFLOW_RENDER_FOR_TD.md` — if output feeds TD

### Animating something
- `BLENDER_ANIMATION.md` — keyframes, drivers, NLA
- For audio-driven motion: the bake-audio-to-F-curve section in `BLENDER_ANIMATION.md`

### Importing or exporting an asset
- `BLENDER_ASSET_IO.md` — formats, conventions
- `BLENDER_WORKFLOW_ASSET_FOR_TD.md` — if destination is TD

### Anything render-related on M1
- `BLENDER_APPLE_SILICON.md` — first, always

### MCP-specific behavior (tool calls, prompt shape, save discipline)
- `BLENDER_WORKFLOW_AGENT_DRIVEN.md` — first
- `BLENDER_PYTHON_API.md` — for the underlying API behavior

---

## File Status

| File | Status | Lines |
|------|--------|-------|
| BLENDER_LIBRARY_INDEX.md | live v1.0 | this file |
| BLENDER_PYTHON_API.md | live v1.0 | 1177 |
| BLENDER_DATA_MODEL.md | live v1.0 | 472 |
| BLENDER_UI_VOCABULARY.md | live v1.0 | 455 |
| BLENDER_APPLE_SILICON.md | live v1.0 | 335 |
| BLENDER_MODELING.md | live v1.0 | 587 |
| BLENDER_SCULPTING.md | live v1.0 | 348 |
| BLENDER_GEOMETRY_NODES.md | live v1.0 | 897 |
| BLENDER_SHADER_NODES.md | live v1.0 | 732 |
| BLENDER_MATERIALS.md | live v1.0 | 514 |
| BLENDER_ANIMATION.md | live v1.0 | 1061 |
| BLENDER_RENDER_EEVEE.md | live v1.0 | 511 |
| BLENDER_RENDER_CYCLES.md | live v1.0 | 820 |
| BLENDER_COMPOSITOR.md | live v1.0 | 641 |
| BLENDER_ASSET_IO.md | live v1.0 | 814 |
| BLENDER_ADDONS.md | live v1.0 | 283 |
| BLENDER_PATTERNS_PROCEDURAL.md | live v1.0 | 823 |
| BLENDER_PATTERNS_LIGHTING.md | live v1.0 | 586 |
| BLENDER_PATTERNS_CINEMATIC.md | live v1.0 | 619 |
| BLENDER_WORKFLOW_RENDER_FOR_TD.md | live v1.0 | 647 |
| BLENDER_WORKFLOW_ASSET_FOR_TD.md | live v1.0 | 508 |
| BLENDER_WORKFLOW_AGENT_DRIVEN.md | live v1.0 | 372 |
| BLENDER_FOOTGUNS.md | live v1.0 (seeded) | grows |

All 23 files written 2026-05-22. Brain is live.

**Empirical-verification flags at install time** (collected from per-file agent reports):
- Exact Blender version on installed build (4.2 LTS vs 4.5 LTS vs later) — affects engine string (`BLENDER_EEVEE_NEXT` vs future names), Grease Pencil collection (`grease_pencils` vs `grease_pencils_v3`), Action Slot system (4.4+), Khronos PBR Neutral View Transform (4.4+).
- Exact MCP connector tool surface — research was from press coverage. Confirm actual tool names, parameter shapes, viewport-screenshot availability, and Claude Code vs Claude Desktop compatibility once installed.
- The 60+ `bl_idname` strings catalogued in the Python / Geometry / Shader / Compositor files — most are stable, but spot-check via `node.bl_idname` introspection on the live build before relying on any unfamiliar string.
- OIDN GPU (Metal) device availability — verify the denoiser dropdown actually offers GPU.
- macOS minimum version — flagged `verify per release notes` for any Blender point release later than 4.5.
- Library override behavior, asset library paths, and the Extensions vs legacy add-on installation paths — all confirmed via documentation but worth a smoke test in the real environment.
