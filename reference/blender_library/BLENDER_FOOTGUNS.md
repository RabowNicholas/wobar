---
title: Blender Footguns — Confirmed Failure Patterns
version: 1.0
last_updated: 2026-05-22
status: live
scope: Confirmed failure patterns + fixes for agent-driven Blender work via the MCP connector. Mirror of TD_FOOTGUNS / TD_CLAUDE_DEBUG_LOG. Read before any non-trivial agent action. Append empirically as new failures surface — no speculative entries.
dependencies: BLENDER_LIBRARY_INDEX.md, BLENDER_PYTHON_API.md, BLENDER_WORKFLOW_AGENT_DRIVEN.md
---

# BLENDER FOOTGUNS — CONFIRMED FAILURE PATTERNS

This file is the analog of TouchDesigner's `TD_CLAUDE_DEBUG_LOG.md` + `TD_FOOTGUNS.md`. **Read before any non-trivial agent action.** Append only entries confirmed by a real failure in a real session — no speculative additions.

**Format per entry:**
- **Symptom:** what the agent or human observes
- **Cause:** why it happens
- **Fix:** the concrete remediation
- **Source:** session date / file in vault / cross-reference, if any

---

## Status

This file is **seeded** as of 2026-05-22 — Phase 2 of the Blender brain build. Entries below are pulled from the research file (`working/BLENDER_MCP_RESEARCH.md`) and from the install-time verification flags surfaced by the per-domain library agents during the Phase 2 build. They are **expected** failures, not yet *confirmed in a WOBAR session*. Mark each as `confirmed` once observed in real use.

The file will grow naturally as we use the MCP connector and the brain — that's the feedback loop. If a footgun appears 2+ times, promote it to a rule in the relevant primary doc (e.g. `BLENDER_PYTHON_API.md` → footguns section, or `BLENDER_MATERIALS.md`, etc.) the same way TD promotes corrections to `WOBAR_TD_AGENT_RULES.md`.

---

## MCP-Connector-Layer (Seeded)

### M-1 — First command after Connect to Claude sometimes errors
**Symptom:** First tool call after pressing "Connect to Claude" in the BlenderMCP N-panel returns an error.
**Cause:** Known quirk of the connector handshake (documented in Anthropic's tutorial and community reports).
**Fix:** Re-issue the same command. It will succeed on the second attempt.
**Source:** `working/BLENDER_MCP_RESEARCH.md` (research conducted 2026-05-22).
**Status:** expected, not yet confirmed.

### M-2 — Modifications lost on Blender crash
**Symptom:** Scene was modified by the agent across multiple tool calls; Blender crashes; reopening the file shows none of the changes.
**Cause:** All MCP-driven modifications live in memory until Blender's File → Save commits them to disk.
**Fix:** Save the file at every natural checkpoint. Ask the agent to "Save the file. Confirm the save path." as a standing instruction at the start of any non-trivial session. Cross-ref `[[BLENDER_WORKFLOW_AGENT_DRIVEN]]` § Save Discipline.
**Source:** Anthropic's official tutorial documents this constraint.
**Status:** expected, not yet confirmed.

### M-3 — Tool call timeout at 300 seconds
**Symptom:** A long operation (large render, full-scene analysis, batch operation on thousands of objects) returns "Tool call timed out."
**Cause:** MCP connector tool calls cap at 300 seconds.
**Fix:** Chunk the operation. For renders: render-region or split by frame range. For analysis: filter to a subset first. For batch ops: process in groups of N.
**Source:** `working/BLENDER_MCP_RESEARCH.md`.
**Status:** expected, not yet confirmed.

### M-4 — Response truncated at ~150K chars
**Symptom:** Agent returns a long list (e.g. all 800 objects in a scene with full property dumps) and the response is cut off.
**Cause:** Response cap at ~150,000 characters per tool call.
**Fix:** Filter / sort / summarize before returning. Ask for "the top 20 X by Y" instead of "all X."
**Source:** `working/BLENDER_MCP_RESEARCH.md`.
**Status:** expected, not yet confirmed.

### M-5 — Running MCP from Claude Desktop AND Cursor against the same Blender
**Symptom:** Tool calls behave erratically or fail; the addon socket gets confused.
**Cause:** Only one MCP client at a time can talk to the Blender addon.
**Fix:** Pick one client per session. Disconnect the other.
**Source:** `working/BLENDER_MCP_RESEARCH.md`.
**Status:** expected, not yet confirmed.

---

## bpy API Common Pitfalls (Seeded)

### B-1 — Operator runs in script but fails in MCP context
**Symptom:** A `bpy.ops.*` call works in the Blender Scripting workspace's Python console but fails or behaves wrongly from the MCP connector.
**Cause:** Operators are context-dependent. The MCP connector's `execute_blender_code` may not have the editor context the operator expects (e.g. an operator that requires the 3D Viewport to be active).
**Fix:** Use `bpy.context.temp_override(area=area, region=region)` to supply the needed context, OR rewrite the call to use `bpy.data.*` direct mutation when possible (preferred). Cross-ref `[[BLENDER_PYTHON_API]]` § bpy.ops vs bpy.data.
**Source:** Per-file install-time verification flags from Phase 2 build.
**Status:** expected, not yet confirmed.

### B-2 — Object lookup by name returns None after creation
**Symptom:** Agent creates an object via `bpy.data.objects.new(name='Cube', ...)`, then immediately accesses `bpy.data.objects['Cube']` and gets the *wrong* one (or the lookup returns None unexpectedly).
**Cause:** Name collisions auto-append `.001` / `.002` / etc. If a Cube already existed, the new one is `'Cube.001'`, not `'Cube'`. The `.get(name)` pattern returns the first match, which may be the OLD object.
**Fix:** After creating, capture the returned object directly: `new_obj = bpy.data.objects.new(name='Cube', object_data=mesh)`. Reference `new_obj` going forward, not `bpy.data.objects['Cube']`. Cross-ref `[[BLENDER_DATA_MODEL]]` § Names and collisions.
**Source:** `[[BLENDER_PYTHON_API]]` § Footguns.
**Status:** expected, not yet confirmed.

### B-3 — Material color setting requires 4-tuple, not 3-tuple
**Symptom:** Setting `node.inputs['Base Color'].default_value = (1.0, 0.0, 0.0)` errors with a tuple-size mismatch.
**Cause:** Color sockets in shader nodes are 4-channel RGBA. Vector sockets are 3-channel.
**Fix:** Always pass 4-tuples: `(1.0, 0.0, 0.0, 1.0)`. Cross-ref `[[BLENDER_SHADER_NODES]]` § Footguns.
**Source:** `[[BLENDER_SHADER_NODES]]`.
**Status:** expected, not yet confirmed.

### B-4 — `material.use_nodes` not set after creation
**Symptom:** Created a material, added shader nodes, assigned to object — but the object renders as default gray.
**Cause:** `material.use_nodes = True` was not set. Without it, the node tree exists but Blender uses the diffuse color slider from the legacy path.
**Fix:** Always set `material.use_nodes = True` as the first step after `bpy.data.materials.new()`. Cross-ref `[[BLENDER_MATERIALS]]`.
**Source:** `[[BLENDER_SHADER_NODES]]`, `[[BLENDER_MATERIALS]]`.
**Status:** expected, not yet confirmed.

### B-5 — Normal map looks washed out
**Symptom:** A normal map texture is loaded and linked through a Normal Map node into Principled BSDF; the result looks washed-out / wrong.
**Cause:** Image Texture node's `colorspace_settings.name` defaults to `'sRGB'`. Normal maps must be `'Non-Color'`.
**Fix:** `image_node.image.colorspace_settings.name = 'Non-Color'` for normal / roughness / metallic / AO / displacement maps. Only the Base Color stays sRGB. Cross-ref `[[BLENDER_MATERIALS]]` § Color management.
**Source:** `[[BLENDER_MATERIALS]]`.
**Status:** expected, not yet confirmed.

### B-6 — Frame change doesn't update dependent properties
**Symptom:** Set `scene.frame_current = 100`; read a driven property; the value is from frame 0, not 100.
**Cause:** Setting `frame_current` directly doesn't trigger a depsgraph update for drivers / constraints / modifiers.
**Fix:** Call `bpy.context.scene.frame_set(100)` instead. This both sets and triggers the dependency graph update.
**Source:** `[[BLENDER_PYTHON_API]]`, `[[BLENDER_ANIMATION]]`.
**Status:** expected, not yet confirmed.

### B-7 — Drivers disabled on file open
**Symptom:** Open a .blend file with drivers; drivers don't fire; properties show their static F-curve values instead of driver expressions.
**Cause:** Blender disables Python drivers by default for untrusted files (security).
**Fix:** In the file's load dialog or via Preferences → Save & Load, enable "Auto Run Python Scripts" globally OR trust the specific file. From script: `bpy.app.driver_namespace.update({...})` to re-enable. Cross-ref `[[BLENDER_ANIMATION]]` § Drivers.
**Source:** `[[BLENDER_ANIMATION]]`.
**Status:** expected, not yet confirmed.

---

## Render & Output Footguns (Seeded)

### R-1 — Alpha channel missing despite `film_transparent=True`
**Symptom:** Set `scene.render.film_transparent = True`, render, open in image viewer — no alpha.
**Cause:** Output format doesn't support alpha. JPEG and H.264 strip alpha. ProRes 422 strips alpha. Only PNG / EXR / ProRes 4444 carry alpha through.
**Fix:** Set `scene.render.image_settings.color_mode = 'RGBA'` AND choose a format that supports alpha (PNG, EXR, ProRes 4444). Cross-ref `[[BLENDER_WORKFLOW_RENDER_FOR_TD]]` § Alpha channel.
**Source:** `[[BLENDER_WORKFLOW_RENDER_FOR_TD]]`.
**Status:** expected, not yet confirmed.

### R-2 — Image sequence frames overwrite each other
**Symptom:** Rendered a 100-frame animation as PNG sequence; the output folder has only 1 PNG.
**Cause:** `scene.render.filepath` didn't include a `#` placeholder for frame number. Without it, every frame writes to the same filename.
**Fix:** Include `####` (or more `#`s) in the filepath: `/path/to/output/frame_####.png`.
**Source:** `[[BLENDER_WORKFLOW_RENDER_FOR_TD]]`.
**Status:** expected, not yet confirmed.

### R-3 — Cycles renders on CPU despite GPU device available
**Symptom:** Cycles render is slow; viewport shows CPU usage spiking; expected GPU rendering.
**Cause:** GPU device wasn't enabled in Preferences → System → Cycles Render Devices, OR the scene's device setting (`scene.cycles.device`) is `'CPU'`.
**Fix:** Set both: (1) Preferences enable a GPU device (set `prefs.compute_device_type = 'METAL'` on M1, then enable specific devices), (2) `scene.cycles.device = 'GPU'`. Cross-ref `[[BLENDER_APPLE_SILICON]]`, `[[BLENDER_RENDER_CYCLES]]`.
**Source:** `[[BLENDER_RENDER_CYCLES]]`, `[[BLENDER_APPLE_SILICON]]`.
**Status:** expected, not yet confirmed.

### R-4 — OptiX denoiser selected on M1 → silent fallback or missing
**Symptom:** Set Cycles denoiser to OptiX on an Apple Silicon Mac; either renders without denoising or errors.
**Cause:** OptiX is NVIDIA / CUDA-only. Not available on Metal.
**Fix:** Use `'OPENIMAGEDENOISE'` (OIDN). On 4.2+ with the OIDN-GPU-Metal option enabled, performance is good.
**Source:** `[[BLENDER_APPLE_SILICON]]`, `[[BLENDER_RENDER_CYCLES]]`.
**Status:** expected, not yet confirmed.

### R-5 — EEVEE Next engine string is `BLENDER_EEVEE_NEXT`, not `BLENDER_EEVEE`
**Symptom:** Setting `scene.render.engine = 'BLENDER_EEVEE'` in Blender 4.2–4.5 errors with unknown engine.
**Cause:** EEVEE Next replaced legacy EEVEE in 4.2. The engine string changed. (Note: Blender 5.0 may reclaim `'BLENDER_EEVEE'` for EEVEE Next.)
**Fix:** Use `'BLENDER_EEVEE_NEXT'` for 4.2 through (at least) 4.5. Verify the exact string for the installed version via `bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items.keys()` at install time.
**Source:** `[[BLENDER_RENDER_EEVEE]]`.
**Status:** expected, not yet confirmed.

### R-6 — Expecting Bloom in EEVEE — removed in 4.2
**Symptom:** Looking for the EEVEE Bloom checkbox; can't find it.
**Cause:** The legacy EEVEE Bloom option was removed when EEVEE Next launched in 4.2. Bloom is now done in the Compositor via the Glare node.
**Fix:** Enable `scene.use_nodes = True`, add a Glare node (Bloom mode) after Render Layers, link to Composite. Cross-ref `[[BLENDER_COMPOSITOR]]`, `[[BLENDER_RENDER_EEVEE]]`.
**Source:** `[[BLENDER_RENDER_EEVEE]]`.
**Status:** expected, not yet confirmed.

---

## Asset Export Footguns (Seeded)

### A-1 — GLB exported but TD shows blank / wrong material
**Symptom:** Exported a textured Blender mesh as GLB; loaded into TD; renders untextured or wrong color.
**Cause:** One of: (a) `material.use_nodes = False` → no node tree to export, (b) image colorspaces wrong → glTF spec misinterpretation, (c) material name has spaces or special chars → glTF parsing chokes.
**Fix:** Sanity-check before export — `use_nodes` True, image colorspaces correct (sRGB for color, Non-Color for normal/rough/metal), material names snake_case. Cross-ref `[[BLENDER_WORKFLOW_ASSET_FOR_TD]]`.
**Source:** `[[BLENDER_WORKFLOW_ASSET_FOR_TD]]`.
**Status:** expected, not yet confirmed.

### A-2 — Modifier stack not exported with GLB
**Symptom:** Mesh in Blender has a Subdivision Surface + Bevel modifier; exported GLB looks low-poly.
**Cause:** `export_apply=False` (default). Modifiers aren't applied to the exported geometry.
**Fix:** `bpy.ops.export_scene.gltf(filepath='...', export_apply=True, ...)`. Cross-ref `[[BLENDER_WORKFLOW_ASSET_FOR_TD]]`, `[[BLENDER_ASSET_IO]]`.
**Source:** `[[BLENDER_WORKFLOW_ASSET_FOR_TD]]`.
**Status:** expected, not yet confirmed.

---

## Open Track — To Be Confirmed In Live Use

The following are flagged for empirical verification once the MCP connector is installed and used. Each should be promoted to a confirmed entry above (or deleted as false positive) after observation.

- **Claude Code vs Claude Desktop compatibility** — does the official Blender connector reach Claude Code? Research file flagged as untested.
- **Viewport screenshot availability** — does the official MCP expose screenshots? ahujasid's variant does; official's tutorial doesn't explicitly demo this.
- **The exact tool surface of the official MCP** — research was based on press coverage. The full tool list, parameter shapes, and limitations are empirical-only.
- **`execute_blender_code` undo behavior** — flagged as "unreliable; save before" by the agent-driven workflow file. Worth confirming empirically.
- **Grease Pencil v3 vs v2 collection naming** — Blender 4.3+ renamed; 4.2 LTS uses legacy. The exact installed version determines which bpy.data collection to use.
- **Action Slot system (4.4+)** — multi-slot Actions require the agent to understand which slot is active; verify behavior on installed build.

---

## Promotion Discipline

When a footgun appears 2+ times across sessions:
- Promote it from this file into the relevant primary doc (e.g. `BLENDER_MATERIALS.md` § Footguns).
- Keep a stub entry here pointing to the promoted location.
- Update the index file's status block if the discovery shifts a recommendation.

This mirrors the TD pattern in `working/TD_BUILD_LOG.md` → `reference/WOBAR_TD_AGENT_RULES.md`.
