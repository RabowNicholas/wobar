---
title: TD Library Index
version: 1.0
last_updated: 2026-04-16
status: live
scope: Entry point for general TouchDesigner knowledge base. Brand-agnostic. Decision tree — pull files by task.
dependencies: none
td_version_target: 2025.32460 (Non-Commercial)
platform_target: Apple Silicon (M1 MacBook Pro + M1 Mac Studio)
---

# TD LIBRARY INDEX

Brand-agnostic TouchDesigner knowledge base. This file set is the general TD expertise layer — Wobar-specific rules live in `reference/WOBAR_TD_*.md`. Read this index first, then pull only what the task needs.

Target: TD 2025.32460 Non-Commercial on Apple Silicon. Output capped at 1280×1280. H.264 export unavailable (Commercial-only); ProRes native.

---

## How To Use This Library

1. Identify task type — see Decision Tree below.
2. Read this file plus the 2–4 files it points to for the task.
3. If the task involves a specific operator, read the relevant operator catalog (POP/TOP/CHOP/SOP/MAT/DAT/COMP) by section.
4. Operator catalogs are encyclopedic — use Grep or section jump, do not read top to bottom.
5. Brand-specific decisions (act identity, color, motion rules) come from `WOBAR_TD_*.md`, not this library.

---

## Document Registry

### Foundations — Read Early
| File | Scope | When to pull |
|------|-------|-------------|
| TD_LIBRARY_INDEX.md | This file — map of the library | First, every TD task |
| TD_APPLE_SILICON.md | Metal/MoltenVK, codec limits, license gotchas, known macOS bugs | Before export, before install, when anything platform-specific breaks |
| TD_NETWORK_VS_GLSL.md | Decision framework: build with nodes vs write GLSL | Before any new build; when tempted to default to GLSL |
| TD_EFFICIENT_NETWORKS.md | Cook cost, CHOP→TOP bridging, Select/Null discipline, caching | Optimization; any build that runs at live framerate |
| TD_FOOTGUNS.md | Failure patterns + exact fixes, broader than brand debug log | Debugging; before shipping anything live |

### Operator Catalogs — Encyclopedic
| File | Family | When to pull |
|------|--------|-------------|
| TD_OPERATORS_POP.md | POPs — GPU points (new in 2025) | Particles, instancing, generative geometry |
| TD_OPERATORS_TOP.md | TOPs — GPU textures | Any visual; compositing; feedback; shaders |
| TD_OPERATORS_CHOP.md | CHOPs — channels/time/audio | Audio reactivity; timing; control signals; MIDI/OSC |
| TD_OPERATORS_SOP.md | SOPs — CPU geometry | 3D scenes; procedural modeling; imported meshes |
| TD_OPERATORS_MAT.md | MATs — materials/shaders for 3D | Rendering 3D with lighting; PBR; custom GLSL MATs |
| TD_OPERATORS_DAT.md | DATs — tables/text/scripts/network | Python; OSC routing; text data; config |
| TD_OPERATORS_COMP.md | COMPs — components; 3D objects; containers | Scene graph; UI; Engine; Replicator; Base/Container |

### Third-Party Libraries
| File | Library | When to pull |
|------|---------|-------------|
| TD_POPX_GUIDE.md | POPX 1.3.0 — high-level POP toolkit (~30 modules, all 55 official examples surveyed). Covers: Instancer, Aim, MoveAlongCurve/Mesh, Distribution, Convert, Unpack, Pivot, Reorient, Texture/Shape/Paint/Noise/Infection/Attribute Falloff, Spring, Transform/Color/Noise Modifier, Magnetize, Measure, Subdivider, Sweep, Planar Patch, Voxelize, Explode (Voronoi/perprim), Mesh Fill, Strange Attractor, DLA, DLG, Physarum 2D/3D, Shortest Path, Flow (Eulerian fluid), POPX Particle (Lagrangian SPH), SSFR, Soft Body suite (cloth/struts/pressure/string), Constraints, Constraint Property, SBPP, Path Tracer, POPX Material/Light. Includes integration patterns for typography, living Voronoi, voxel-art, hair on rigged characters, audio-reactive crystallization. | Whenever POPX modules are involved. Capability table at top maps "without POPX → with POPX" recipes — find the row, then jump to the named module's section. |

### Pattern Library — Recipes
| File | Scope | When to pull |
|------|-------|-------------|
| TD_PATTERNS_AUDIO_REACTIVITY.md | Audio pipeline, band splits, envelope followers, onset | Any audio-driven visual |
| TD_PATTERNS_FEEDBACK.md | Feedback TOP loops — zoom, trails, generative feedback | Tunnels, trails, bloom, psychedelic forms |
| TD_PATTERNS_GENERATIVE.md | Noise, L-systems, reaction-diffusion, fractals | Abstract / non-referential visuals |
| TD_PATTERNS_3D_SCENES.md | Camera, lighting, render setup, post-stack | Any 3D render |
| TD_PATTERNS_INSTANCING.md | Geometry/POP instancing; Replicator COMP | Many copies of a thing driven by data |
| TD_PATTERNS_COMPOSITING.md | Layer stacks, mattes, blend modes, post FX | Final look assembly |
| TD_PATTERNS_PARTICLES.md | POP particle systems (Mac-safe); legacy Particle SOP notes | Swarms, dust, sparks, sprays |
| TD_PATTERNS_TEXT.md | Text TOP / Text SOP / Text POP (2025) + typography | Title cards, lyric reactive, typographic visuals |

### Workflow Playbooks — End-to-End
| File | Scope | When to pull |
|------|-------|-------------|
| TD_WORKFLOW_OPTIMIZATION.md | Perform mode, cook flags, Null TOP caching, instancing | Project runs slow or drops frames |
| TD_WORKFLOW_EXPORT.md | ProRes pipeline on Mac; render passes; resolution cap | Delivering a music video or loop |
| TD_WORKFLOW_LIVE_VJ.md | APC40 / Launchpad / Launch Control XL; scene switching; Engine COMP | Performance; gig prep |
| TD_WORKFLOW_LIVE_AUDIOREACTIVE.md | Ableton Link, TDAbleton, BlackHole routing, onset timing | Visuals that lock to your live DJ set |
| TD_WORKFLOW_MIDI_OSC.md | MIDI In Map vs MIDI In; OSC In/Out; controller mapping | Hardware/software control |
| TD_WORKFLOW_AV_INTEGRATION.md | Front-of-house replacement; Resolume handoff; Syphon/Spout | Multi-app AV rigs |
| TD_WORKFLOW_PROJECTION_MAPPING.md | kantan mapper, CamSchnappr, edge-blend, keystone | Venue projection |
| TD_WORKFLOW_INSTALLATION.md | Kiosk, crashAutoSave, watchdog, sensor input | Long-running installs |

---

## Decision Tree

**"I am starting a new visualizer."**
→ TD_NETWORK_VS_GLSL.md (pick approach) → TD_PATTERNS_AUDIO_REACTIVITY.md (audio pipeline) → pattern file for the look → TD_EFFICIENT_NETWORKS.md (keep it cheap)

**"I am exporting a music video."**
→ TD_APPLE_SILICON.md (codec reality) → TD_WORKFLOW_EXPORT.md → TD_WORKFLOW_OPTIMIZATION.md (if cook time is an issue)

**"I am prepping for a live set."**
→ TD_WORKFLOW_LIVE_VJ.md → TD_WORKFLOW_LIVE_AUDIOREACTIVE.md → TD_WORKFLOW_MIDI_OSC.md → TD_WORKFLOW_OPTIMIZATION.md

**"I am building an installation."**
→ TD_WORKFLOW_INSTALLATION.md → TD_WORKFLOW_AV_INTEGRATION.md (if multi-app) → TD_WORKFLOW_PROJECTION_MAPPING.md (if mapped)

**"I want to use POPs for X."**
→ TD_OPERATORS_POP.md (section for the task) → TD_PATTERNS_INSTANCING.md or TD_PATTERNS_PARTICLES.md → TD_APPLE_SILICON.md (GPU points limits on Metal)

**"Something is broken."**
→ TD_FOOTGUNS.md first → operator catalog for the specific node → TD_APPLE_SILICON.md if platform-smelling

**"I want to write a shader."**
→ TD_NETWORK_VS_GLSL.md (confirm you should) → TD_OPERATORS_TOP.md §GLSL TOP / §GLSL Multi TOP → existing `WOBAR_GLSL_PATTERNS.md` for Wobar work

**"I want to instance 10,000 things cheaply."**
→ TD_OPERATORS_POP.md §Point Generator / §Attribute POPs → TD_PATTERNS_INSTANCING.md → TD_EFFICIENT_NETWORKS.md §GPU Instancing

**"I want instances to aim at / follow / scatter on a surface."**
→ TD_POPX_GUIDE.md — start with the capability table (rows ~25–90), find the row matching your need, then jump to the named module's section.

---

## Cross-References To Brand Files

The brand-locked Wobar TD files live at `reference/WOBAR_TD_*.md`. Never modify them from this library. They take precedence when working on Wobar content.

| Brand file | When it overrides this library |
|------------|-------------------------------|
| WOBAR_TD_INDEX.md | Wobar-specific decision tree — read before this one on Wobar work |
| WOBAR_TD_AGENT_RULES.md | Naming, act constraints, control architecture |
| WOBAR_TD_REFERENCE.md | Wobar-specific spec (colors, primitives, export) |
| WOBAR_GLSL_PATTERNS.md | Act-specific shader code |
| WOBAR_TWOZERO_GUIDE.md | Wobar's MCP integration rules |

---

## Living Document

Add to this library when:
- A new TD version ships and changes operator behavior
- A pattern is used 3+ times and proves itself
- A failure is hit twice — promote it from memory into `TD_FOOTGUNS.md`
- A new workflow (e.g., adding lidar sensors) is tackled end-to-end

Never add brand content here. That stays in `WOBAR_TD_*.md`.
