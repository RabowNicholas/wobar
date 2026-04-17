---
title: Wobar Context Index
version: 1.0
last_updated: 2026-04-16
status: live
scope: Master index for all Wobar reference files. Read this first in every conversation.
dependencies: none
---

# WOBAR CONTEXT INDEX

This is the index file for the Wobar project reference system. Read this file first. Pull additional files only as needed for the task at hand.

## File Registry

### Project / Brand
| File | Location | Scope | Status |
|------|----------|-------|--------|
| [[skills/README]] | /skills | Source of truth for WOBAR Claude skills — `~/.claude/skills/` on each machine is a synced copy | live |
| [[working/WOBAR_ACTIVE]] | /working | Open project loops, current context, session history | live |
| [[working/WOBAR_CLOSED]] | /working | Completed project loops, archived from WOBAR_ACTIVE | live |
| [[reference/WOBAR_BRAND]] | /reference | Foundation, mission, archetypes, beliefs, positioning | locked |
| [[reference/WOBAR_FRAMEWORK]] | /reference | 5-Act Portal Framework, act definitions, percentages | locked |
| [[reference/WOBAR_COPY]] | /reference | Voice, lexicon, anti-vocabulary, writing tests | locked |
| [[reference/WOBAR_SONIC]] | /reference | Sonic identity, reference artists, genre positioning | locked |
| [[reference/WOBAR_CONTENT]] | /reference | Content system, release architecture, posting | locked |
| [[reference/WOBAR_ARCHIVE]] | /reference | Archive sourcing by act, portal depth, pipeline | locked |
| [[reference/WOBAR_CLAUDE]] | /reference | How to work with Nick | locked |
| [[reference/WOBAR_PATCH_SYSTEM]] | /reference | Serum 2 patch naming, 8-macro standard, versioning | locked |
| [[reference/WOBAR_OBSCURA]] | /reference | Obscura visual identity and reference system | locked |

### TouchDesigner — Entry Point
| File | Location | Scope | Status |
|------|----------|-------|--------|
| [[reference/WOBAR_TD_INDEX]] | /reference | **TD entry point** — decision tree for which TD docs to load per task | live |

### TouchDesigner — Core Rules & Conventions
| File | Location | Scope | Status |
|------|----------|-------|--------|
| [[reference/WOBAR_TD_AGENT_RULES]] | /reference | Build conventions: naming, architecture, act constraints, Python rules | live |
| [[reference/WOBAR_TD_REFERENCE]] | /reference | Full specs: audio pipeline, visual primitives, color system, export — load by section | locked |
| [[reference/WOBAR_MOVE_SYSTEM]] | /reference | Move history system spec — JSON schema, lifecycle, network→comp mapping | locked |

### TouchDesigner — TWOZERO MCP
| File | Location | Scope | Status |
|------|----------|-------|--------|
| [[reference/WOBAR_TWOZERO_GUIDE]] | /reference | Confirmed type strings, parameter names, limitations, known behaviors | live |
| [[reference/WOBAR_TWOZERO_MCP_CATALOG]] | /reference | Full parameter tables for all 35 TWOZERO tools — load by group, not full file | live |

### TouchDesigner — Snippet Libraries
| File | Location | Scope | Status |
|------|----------|-------|--------|
| [[reference/WOBAR_TD_EXPRESSION_COOKBOOK]] | /reference | Paste-ready expressions: CHOP access, audio-reactive mappings, time, footguns | live |
| [[reference/WOBAR_GLSL_PATTERNS]] | /reference | Act-specific GLSL shaders (10 total), utility functions, act color reference | live |
| [[touchdesigner/reference_networks/README]] | /touchdesigner | Structural examples — node chains + taste decisions per network type | live |

### TouchDesigner — Session Logs
| File | Location | Scope | Status |
|------|----------|-------|--------|
| [[working/TD_CLAUDE_DEBUG_LOG]] | /working | Confirmed wrong advice + corrected patterns — read before any TD action | live |
| [[working/TD_BUILD_LOG]] | /working | Session-by-session build log — correction tracker, patterns | live |
| touchdesigner/networks/[network]/CHANGE_LOG.md | /touchdesigner | Per-network change log — why changes were made | live |
| touchdesigner/networks/[network]/moves/ | /touchdesigner | Per-network move history — JSON files for granular undo | live |

### TouchDesigner — General Library (brand-agnostic)
| File | Location | Scope | Status |
|------|----------|-------|--------|
| [[reference/td_library/TD_LIBRARY_INDEX]] | /reference/td_library | **Entry point for general TD knowledge** — routes to operator catalogs, patterns, workflows | live |
| [[reference/td_library/TD_APPLE_SILICON]] | /reference/td_library | M1 constraints: Metal/MoltenVK, codec/license limits, Syphon/NDI state, sensor compatibility | live |
| [[reference/td_library/TD_NETWORK_VS_GLSL]] | /reference/td_library | Decision framework — when to use networks vs GLSL, hybrid patterns, red flags | live |
| [[reference/td_library/TD_EFFICIENT_NETWORKS]] | /reference/td_library | Cook model, Cook Type, Null discipline, CHOP→TOP bridging, GPU instancing, canonical templates | live |
| [[reference/td_library/TD_FOOTGUNS]] | /reference/td_library | 50+ general TD failure patterns (feedback, audio, network, render, POPs, MIDI/OSC, export, perform, platform) | live |
| [[reference/td_library/TD_OPERATORS_POP]] | /reference/td_library | Full POP catalog — 2025 GPU point ops (Generators, Transform, Attribute, Control, Simulation) | live |
| [[reference/td_library/TD_OPERATORS_TOP]] | /reference/td_library | Full TOP catalog by role — Generators, Filters, Compositing, GPU Shader, Feedback, Analysis | live |
| [[reference/td_library/TD_OPERATORS_CHOP]] | /reference/td_library | Full CHOP catalog by function — Audio, Analysis, Timing, Math, Hardware, Pattern, Export | live |
| [[reference/td_library/TD_OPERATORS_SOP]] | /reference/td_library | Full SOP catalog — Generators, Deformers, Modifiers, Attributes, Combinations, Specialty | live |
| [[reference/td_library/TD_OPERATORS_MAT]] | /reference/td_library | MATs — Constant, Phong, PBR, Point Sprite, Line, Wireframe, GLSL + assignment patterns | live |
| [[reference/td_library/TD_OPERATORS_DAT]] | /reference/td_library | DATs — Text/Script, Table, Format bridges, Web/Network + Python/Extension patterns | live |
| [[reference/td_library/TD_OPERATORS_COMP]] | /reference/td_library | COMPs — 3D Object, Container, Execution, Panel/UI + Geometry Instance cheat sheet | live |
| [[reference/td_library/TD_PATTERNS_AUDIO_REACTIVITY]] | /reference/td_library | 6-stage audio spine, band splits, onset detection, spectral analysis, tempo sync | live |
| [[reference/td_library/TD_PATTERNS_FEEDBACK]] | /reference/td_library | Feedback TOP loop, 3 critical params, 14 patterns (trails/tunnel/streaking/etc) | live |
| [[reference/td_library/TD_PATTERNS_GENERATIVE]] | /reference/td_library | Noise/flow/L-systems/reaction-diffusion/SDF raymarching/boids/Voronoi/metaballs | live |
| [[reference/td_library/TD_PATTERNS_3D_SCENES]] | /reference/td_library | Scene graph, camera control, lighting, PBR/IBL, depth, post stack, procedural environments | live |
| [[reference/td_library/TD_PATTERNS_INSTANCING]] | /reference/td_library | 10 instancing patterns (POP→Geometry, CHOP-driven, Replicator, data-driven, etc) | live |
| [[reference/td_library/TD_PATTERNS_COMPOSITING]] | /reference/td_library | Layer Mix vs Composite chain, blend modes, alpha, mattes, chroma key, post FX order | live |
| [[reference/td_library/TD_PATTERNS_PARTICLES]] | /reference/td_library | POP-based particle spine, emission, forces, lifespan + 7 canonical recipes | live |
| [[reference/td_library/TD_PATTERNS_TEXT]] | /reference/td_library | Text TOP/SOP/POP paths, typography patterns, audio-reactive text, data-driven text | live |
| [[reference/td_library/TD_WORKFLOW_OPTIMIZATION]] | /reference/td_library | Perf tuning protocol — measure, quick wins, feedback/render/DAT audits, debug protocol | live |
| [[reference/td_library/TD_WORKFLOW_EXPORT]] | /reference/td_library | ProRes pipeline, image sequences, upscaling around 1280 cap, vertical export, long renders | live |
| [[reference/td_library/TD_WORKFLOW_LIVE_VJ]] | /reference/td_library | Engine COMP scene architecture, APC40/Launchpad/LCXL wiring, Perform Mode, pre-gig checklist | live |
| [[reference/td_library/TD_WORKFLOW_LIVE_AUDIOREACTIVE]] | /reference/td_library | Link + TDAbleton + BlackHole, latency comp, per-song calibration | live |
| [[reference/td_library/TD_WORKFLOW_MIDI_OSC]] | /reference/td_library | MIDI In Map/OSC In/Out, controller wiring, phone apps, mapping patterns | live |
| [[reference/td_library/TD_WORKFLOW_AV_INTEGRATION]] | /reference/td_library | Syphon/NDI routing, Resolume handoff, multi-machine, FOH replacement roadmap, DMX/Art-Net | live |
| [[reference/td_library/TD_WORKFLOW_PROJECTION_MAPPING]] | /reference/td_library | kantan Mapper, CamSchnappr, keystone, edge blending, interactive mapping | live |
| [[reference/td_library/TD_WORKFLOW_INSTALLATION]] | /reference/td_library | Kiosk Mode, crashAutoSave, watchdog, sensor input, long-run reliability | live |

**Brand files above override the general library** — WOBAR_TD_AGENT_RULES and WOBAR_TD_REFERENCE are source of truth for brand constraints. Use td_library when the question is about TD itself, not WOBAR-specific conventions. Don't read the whole library — pull the one file the task needs via `TD_LIBRARY_INDEX`.

## Current State
Brand 6.0 locked March 2026. All files reflect current version.
TWOZERO MCP integration added April 2026. TD agent rules established.
Move history system added April 2026. Three slash commands: /td-build, /td-undo, /td-save.
TD doc library expanded April 2026: MCP catalog, debug log, expression cookbook, GLSL patterns, reference networks, TD index all added.
TD general library added April 2026: `reference/td_library/` — 27 files covering all operator families, patterns, workflows (brand-agnostic, scoped to 2025.32460 Non-Commercial on M1).
Skills source of truth added April 2026: `skills/` — git-tracked WOBAR Claude skills. `~/.claude/skills/` on each machine is a synced copy.
WOBAR_PROJECT_INSTRUCTIONS.md is deprecated — CLAUDE.md is the authority.

## Notes
When a file status is in-flux, confirm current state with Nick before using as reference.
