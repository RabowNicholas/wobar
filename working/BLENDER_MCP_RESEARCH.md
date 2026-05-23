---
title: Blender MCP Research
version: 1.0
last_updated: 2026-05-22
status: live
scope: Findings from research into Blender MCP connectors. Compares the official Blender Foundation MCP against community alternatives. Feeds the Phase 2 stock-Blender brain build and eventually the WOBAR-specific Blender vault.
dependencies: none yet — will feed BLENDER_TWOZERO_GUIDE.md (or equivalent) once chosen connector is installed
---

# BLENDER MCP RESEARCH

Research conducted 2026-05-22. Two viable candidates surveyed. Decisive leader identified.

## TL;DR

**Winner: the official Blender Foundation MCP connector** at `blender.org/lab/mcp-server/`, distributed via Anthropic's connectors directory. Launched April 28, 2026. Built by Blender Lab (Blender Foundation's experimental program). Anthropic became Blender Foundation Corporate Patron (€240k+/year) at the same time — long-term commitment to the Python API the connector wraps.

It is a thin wrapper around Blender's full `bpy` Python API exposed over MCP. Drag-and-drop install. No terminal commands, no JSON config edit, no `uv`. Free-tier eligible via Claude Desktop. Anything a Blender Python developer can script today, Claude can call.

The community variant (`ahujasid/blender-mcp`) remains useful as a complement — it ships asset-pipeline integrations (Poly Haven, Hyper3D Rodin, Sketchfab, Hunyuan3D) the official one does not.

## Phase 1 — Anthropic MCP Registry (Cowork-side)

Query: `mcp__mcp-registry__search_mcp_registry` with keywords ["blender", "3d", "modeling", "geometry"], also tried ["mesh", "scene", "viewport", "shader"] and plain ["blender"].

Result: **empty**. Cowork's connector registry does not currently list the Blender connector. Adjacent results: Three.js 3D Viewer (demo, no tools), Trimble SketchUp (wrong tool), Adobe for Creativity (not Blender). Note this is a registry-indexing lag — the connector exists in Anthropic's main connectors directory at `claude.ai/connectors`, just not surfaced via Cowork's search yet.

## Phase 2 — Candidate Comparison

### Rubric (from research plan)

1. Connection model — addon-to-running-Blender, headless bpy CLI, or file-based
2. Tool surface — what's exposed, mapped against TWOZERO categories
3. Read access — scene state, materials, viewport
4. bpy escape hatch — full `run_python` or sandboxed subset
5. Maintainer activity, version cadence
6. Platform compat — M1 macOS, Blender 4.x
7. Install ergonomics — Cowork-compatible, Claude Code-compatible, Claude Desktop-compatible

### Candidates

| Dimension | Blender Foundation MCP (official) | ahujasid/blender-mcp (community) |
|-----------|-----------------------------------|----------------------------------|
| Source | Blender Lab — first-party Blender Foundation project | Siddharth Ahuja, MIT, third-party |
| Launch | 2026-04-28 | Live >1 year as of May 2026; v1.5.5 |
| Connection model | Blender addon + socket-style server, talks to running Blender | Same pattern — addon (port 9876) + MCP server bridge |
| bpy surface | Full Python API — wraps `bpy` directly | Full Python API via `execute_blender_code` |
| Read access | Scene graph, datablocks, modifiers, materials, geometry nodes, render camera, polygon counts | Scene info, object info, **viewport screenshots** (a real plus) |
| Write access | Anything bpy can do | Anything bpy can do |
| Bundled integrations | None — clean bpy only | Poly Haven (HDRIs/textures/models, free), Hyper3D Rodin (text-to-mesh), Sketchfab (search/DL), Hunyuan3D |
| Install ergonomics | Drag-and-drop. Open `blender.org/lab/mcp-server/`, drag install link into Blender 2×, click "Connect to Claude" in N-panel | `uvx blender-mcp` + JSON config edit + manual addon install |
| Tutorial/docs | Anthropic-hosted official tutorial at `claude.com/resources/tutorials/using-the-blender-connector-in-claude` | README + community videos |
| Platform compat | macOS / Windows / Linux. Blender 4.2+. Claude Desktop required | macOS / Windows / Linux. Blender 3.0+. Claude Desktop, Claude Code, Cursor, VS Code |
| Tier requirement | Every Claude plan including Free (via Claude Desktop) | No tier requirement — runs locally |
| Maintainer signal | Blender Foundation + €240k/yr Anthropic patronage earmarked for the Python API the connector depends on | 18.5k GitHub stars, active commits, telemetry can be disabled |
| Cowork registry | Not currently listed | Not listed (third-party) |
| Claude Code support | Not advertised officially. Plausible — the local server is just an MCP endpoint, Claude Code can be configured against any MCP server. Needs verification at install time. | Explicit: `claude mcp add blender uvx blender-mcp` |

### Why the official wins

1. **Maintenance follows the money.** Anthropic's €240k+/year patronage is earmarked for Blender core development with the Python API explicitly named. The connector and the API it wraps are now maintained by the same team. Any future Blender API breakage gets fixed *before* it breaks the connector.
2. **No install friction.** Drag-and-drop. No `uv` install, no JSON config, no terminal. This matters less for a developer but matters a lot for keeping the workflow durable across multiple machines and Blender upgrades.
3. **The four officially-demoed workflows are exactly what we need to start.** Scene-graph cleanup, Geometry Nodes annotation, material dependency audit, and render-cost triage are all "agentic technical artist" tasks. That's the persona that fits how I'd use the connector — Claude as a senior collaborator who knows the file, not a model generator.
4. **Same `bpy` surface as the community version.** Anything we lose by skipping ahujasid's bundled integrations, we can add later — either by running both connectors or by exposing those services via separate Python wrappers.

### Where the community variant still earns its place

- **Viewport screenshots** are first-class. The official may add this; ahujasid has it today. Critical for any session where Claude needs to see what it just made.
- **Asset bundles ship in.** Poly Haven HDRIs and Sketchfab are exactly what's needed for the Blender → TD asset pipeline (we'd be using Blender to build cinematic environments and assets, and Poly Haven HDRIs are the standard lighting source for that).
- **Hyper3D Rodin / Hunyuan3D / text-to-mesh** matters more for asset rapid-prototyping than for the "agentic technical artist" workflow Anthropic blessed. Useful for WOBAR — the iris, the chamber architectures, the album-art-grade meshes could start from text-to-mesh generation and then get sculpted/refined.

Recommendation: **start with official, layer ahujasid (or its integrations as separate Python modules) only if asset-bundle workflows become friction.**

## Capability Ceiling — What's Outside the MCP

Even with full bpy access, some things stay outside the agent loop and remain manual or external:

- **Manual save commits.** Modifications live in memory only until the user hits File → Save. This is by design (safety) but means session work can be lost on crash. Save protocol matters from day one.
- **300-second tool timeout.** Long renders and large-scene analyses must be chunked. Equivalent to TD's `td_read_chop` token-limit constraint — pattern is "analyze inside Blender, return summary not raw data."
- **~150K character response cap.** Same pattern.
- **One MCP instance per local Blender process.** Can't run the connector simultaneously in Claude Desktop and Cursor and Claude Code against the same Blender.
- **First-command-after-connect quirk.** Known issue: re-issue and it works. Worth documenting in a debug log from day one.
- **`execute_blender_code` runs arbitrary Python.** Mirror of TWOZERO's `td_execute_python` — same safety profile, same need to save before running.
- **Animation, sculpting, geometry-node authoring from scratch, physics sims, render-engine specifics** — all reachable via bpy, but Anthropic has not publicly demoed them and the community hasn't proven production-quality patterns yet. Genuinely open territory.

## Install Path (for when we're ready)

Prerequisites: Blender 4.2 or later, Claude Desktop on macOS, any Claude plan.

1. Claude Desktop → Customize → Connectors → search "Blender" → Add.
2. Open `blender.org/lab/mcp-server/` next to Blender.
3. Drag install link from that page into Blender window → Allow Blender Lab extension repository.
4. Drag the same link in again → installs the add-on.
5. Each session: open the `.blend`, press N in 3D Viewport, open BlenderMCP tab, click Connect to Claude.

Safe first-run prompt (read-only): *"Get the current scene's collection structure and report each top-level collection's object count."*

**Claude Code compatibility — open question.** The official connector is distributed via Claude Desktop's connectors directory, but the underlying MCP server is a local socket the addon spins up. In principle Claude Code can be configured against any MCP endpoint, including this one. Needs verification by reading the addon source or testing at install time. If Claude Code support turns out to be ad-hoc, that affects whether the Blender workflow mirrors the TD workflow (Claude Code as primary interface) or breaks the symmetry (Blender uses Claude Desktop, TD uses Claude Code).

## Open Questions for Phase 2 — Stock Blender Deep Dive

Now that we know the connector is a thin `bpy` wrapper, the "brain" we build is essentially **the Blender Python API reference + Blender's UI vocabulary + best-practice patterns** — what we'd want Claude to know before driving an actual build. Specifically:

1. **bpy domain decomposition.** Top-level split for the brain — Modeling / Sculpting / Geometry Nodes / Shader Nodes / Materials / Animation / Render (EEVEE/Cycles) / Compositor / Python API conventions / Add-on system. This becomes the equivalent of TD's operator catalogs.
2. **Geometry Nodes pattern library.** Direct analog to TD's POPX guide. Procedural meshing, scatter, instancing, mesh deformation. Many WOBAR forms (chambers, iris, fractal structures) are best built here.
3. **Shader Nodes patterns.** Direct analog to TD's GLSL patterns. PBR, subsurface, anisotropic, volume, displacement — mapped to WOBAR's palette and act registers.
4. **Render preset library.** EEVEE Next vs. Cycles, light path settings, denoiser configuration. Critical for the "render Mirror clips offline → ingest as TD Mirror-Frame footage" pipeline.
5. **Asset workflows.** Poly Haven, HDRI for IBL, FBX/GLB import-export conventions for the Blender → TD asset pipeline.
6. **What stays manual.** Sculpting (high-poly stroke-based work), retopology, UV unwrapping, hand-keyed animation. Even though bpy can drive these, no current agent reliably does them.
7. **Live feedback channel.** Does the official connector expose viewport screenshots or render-preview-to-base64? If not, when we install we'll need a manual screenshot habit or a workaround via `bpy.ops.render.opengl()` → save → return path. This is the equivalent of TD's `td_get_screenshot`.

## Sources

- [Creative AI News — Claude's Official Blender Connector: Setup and Workflow](https://www.creativeainews.com/articles/claude-blender-connector-official-setup-workflow/) — most detailed account of the official launch, install path, blessed workflows, and limits
- [9to5Mac — Anthropic releases 9 Claude connectors for creative tools, including Blender and Adobe](https://9to5mac.com/2026/04/28/anthropic-releases-9-new-claude-connectors-for-creative-tools-including-blender-and-adobe/) — launch announcement, full connector list, Anthropic-Blender patronage detail
- [Anthropic launch blog post (referenced in sources)](https://www.anthropic.com/news/claude-for-creative-work) — official announcement
- [Anthropic Blender connector tutorial](https://claude.com/resources/tutorials/using-the-blender-connector-in-claude) — the canonical install bible
- [Blender Foundation — MCP Server page](https://www.blender.org/lab/mcp-server/) — official Blender Lab distribution page (note: client-rendered, content not retrievable via WebFetch — visit in browser)
- [GitHub — ahujasid/blender-mcp](https://github.com/ahujasid/blender-mcp) — community variant, full feature list and install options
- [CG Channel — Anthropic becomes Blender Corporate Patron](https://www.cgchannel.com/2026/04/ai-developer-anthropic-becomes-blenders-latest-corporate-patron/) — €240k/yr patronage detail and significance

