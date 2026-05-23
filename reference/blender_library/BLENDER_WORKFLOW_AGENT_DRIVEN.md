---
title: Agent-Driven Workflow — Working with Claude via the MCP Connector
version: 1.0
last_updated: 2026-05-22
status: live
scope: How to use the Blender Foundation MCP connector well — the four Anthropic-blessed workflows, prompt shapes that succeed, the read-then-write pattern, save discipline, capability ceiling, error-recovery patterns, the agent-human handoff for areas (sculpting, complex rigging, hand-keyed animation) that require human authorship.
dependencies: BLENDER_LIBRARY_INDEX.md, BLENDER_PYTHON_API.md, BLENDER_FOOTGUNS.md
---

# AGENT-DRIVEN WORKFLOW — WORKING WITH CLAUDE VIA THE MCP CONNECTOR

The Blender Foundation MCP connector wraps the full `bpy` Python API. Anything Blender's Python layer can do, the agent can do — read scene graphs, mutate datablocks, build node trees, render frames, save files. But *capability* is not *quality*. The quality of an agent-driven session depends almost entirely on how the human collaborates: which prompt shapes ground the agent, when to read before write, when to save, when to hand off.

This file is the meta-layer. Not what Blender can do — that's `[[BLENDER_PYTHON_API]]`. This is how to do it well with Claude in the loop.

**Core facts:**
- The connector is a Blender add-on distributed by Blender Lab at `blender.org/lab/mcp-server/`. Launched 2026-04-28.
- The add-on opens a local socket inside the running Blender process; Claude Desktop is the canonical client.
- One MCP instance per Blender process — can't connect Desktop + Cursor + Code to the same `.blend` simultaneously.
- Tool calls have a **300-second timeout**. Anything longer must be chunked.
- Tool responses have a **~150K character cap**. Filter, sort, or summarize before returning data.
- **First command after Connect to Claude** sometimes errors. Known quirk — re-issue and it works.
- Modifications are **file-state only** until Blender's File → Save commits them to disk.
- `execute_blender_code` is the arbitrary-Python escape hatch — same safety profile as TD's `td_execute_python`.
- The four Anthropic-blessed workflows are about **understanding existing scenes**, not generating new ones from scratch.
- Create-from-scratch works through `bpy.data.*` and `bpy.ops.*` calls, but it's community territory — no canonical demos.
- Free-tier eligible via Claude Desktop. No paid plan required.
- Blender 4.2 LTS minimum; 4.5+ preferred for current `bpy` surface.

---

## The Four Anthropic-Blessed Workflows

These are the launch-tutorial canonical demos. Each is a real artist task. Each exercises a different slice of the API.

### Workflow 1 — Scene-graph cleanup with batch rename

**Prompt pattern:** *"Look at the open scene and rename the data blocks so each name matches what it contains. Flag any names that are misleading."*

**Use case:** Cleaning up downloaded asset packs where everything is `Cube.001 / Cube.002`. Normalizing a project file before handing off. Pre-flight before a render-farm submit.

**What the agent does:** Iterates `bpy.data.objects`, `bpy.data.materials`, `bpy.data.meshes`. Inspects geometry / material slots / modifier stacks to infer intent. Proposes renames. On confirm, mutates `.name`. Flags ambiguous cases for human decision.

### Workflow 2 — Geometry Nodes explanation, written into the file

**Prompt pattern:** *"Walk through the Geometry Nodes modifier on the active object. Explain what each node group does in the order data flows through them, and write your notes as frame labels inside the node editor so the explanation is saved in the file."*

**Use case:** Documenting a complex node graph for future-you. Onboarding another artist. Generating a written record of a procedural setup so the `.blend` is its own documentation.

**What the agent does:** Reads `obj.modifiers['GeometryNodes'].node_group.nodes`. Walks links to determine flow order. Creates `NodeFrame` nodes via `nodes.new('NodeFrame')`. Parents related nodes to each frame. Writes the explanation into `frame.label` and `frame.text` (if a Text datablock is attached).

### Workflow 3 — Material dependency audit

**Prompt pattern:** *"List everything in this file that uses the '[material_name]' material, including objects, node groups, and Geometry Nodes setups. Tell me what would break if I removed it."*

**Use case:** Refactoring shared assets across a project. Deciding whether a material is safe to delete. Tracking down where a shared shader is referenced before renaming it.

**What the agent does:** Cross-references `bpy.data.materials[name]` against every `obj.material_slots`, every shader node group's `node_tree`, every Geometry Nodes Set Material node, every linked library. Produces a dependency report.

### Workflow 4 — Render-cost triage

**Prompt pattern:** *"For each mesh in the scene, report its polygon count alongside how large it appears in the active camera's final render. Sort by polygon count and flag anything that's heavy but small on screen."*

**Use case:** Optimization pass before a final render. Identifying which assets are wasting render budget. Targeting decimation or LOD work.

**What the agent does:** Iterates `bpy.data.meshes` for poly counts. Computes screen-space bounding box from object world position + camera matrix + render resolution. Sorts. Flags high-poly-small-on-screen as the priority decimation list.

---

## The Read-Then-Write Pattern

The safest pattern for agent-driven work. Four steps, in order, every time the change is non-trivial.

**Step 1 — READ.** Agent inspects the relevant scene state via `bpy.data.*` and `bpy.context.*` and reports what it sees. *"The active object is `Suzanne`. It has 2 modifiers: Subdivision Surface (viewport 2, render 3) and Solidify (thickness 0.02). Its material is `Material.001`."*

**Step 2 — HUMAN CONFIRMS.** Human reviews the read, confirms the agent has identified the right target, or corrects the plan. *"Yes, that's the one — but bump the subdiv render level to 4, not 3."*

**Step 3 — WRITE.** Agent applies the change via `bpy.data.*` mutations or, when necessary, `bpy.ops.*` with proper context.

**Step 4 — READ-VERIFY.** Agent reads the post-write state and confirms. *"Confirmed: `Suzanne.modifiers['Subdivision'].render_levels` is now 4."*

This pattern catches the entire "agent assumed the wrong object was active" / "agent grabbed the wrong material slot" / "agent operated on a stale selection" failure class before it cascades. It is the single most important habit when driving Blender via MCP.

---

## The Safe-First-Prompt Pattern

The canonical first prompt of every new session:

> *"Get the current scene's collection structure and report each top-level collection's object count."*

This prompt does three things at once:

- Exercises **read-only access** — nothing can be broken if it succeeds or fails.
- Confirms the **connector is alive** and the socket handshake worked.
- Gives the agent **baseline context** for what's in the file — collection names, object counts, scale of the scene.

If the first command errors (the known first-command-after-connect quirk), re-issue the same prompt. If it errors twice, check the BlenderMCP N-panel — the "Connect to Claude" button may have disconnected.

---

## Prompt Shapes That Work Well

Every shape below is a template followed by a concrete example.

### Read-only inspection

> *"List all [object type / material / modifier] in the file and report [property]."*

Example: *"List all materials in the file and report which objects use each one."*

### Targeted modification

> *"On the active object, change [property] to [value]. Verify by reading it back."*

Example: *"On the active object, set the Subdivision Surface modifier viewport level to 2, and confirm."*

The "verify by reading it back" half is the critical part — without it the agent may write and silently fail (e.g., wrong object active).

### Annotation

> *"Walk through [graph/structure] and add explanatory [labels / notes / frames] for each [unit]."*

Example: *"Walk through the active object's Geometry Nodes modifier and add a frame around each group of nodes with a label summarizing what that section does."*

### Audit

> *"Find all [criterion] in the file and report which would break if [action]."*

Example: *"Find all objects using the 'Floor' material and tell me what would break if I deleted it."*

### Batch operation

> *"For each [object/material/modifier matching criterion], do [operation]."*

Example: *"For each object whose name starts with 'rock_', set its Cycles ray visibility to Camera Off."*

### Setup

> *"Set up [pipeline-piece] with [params]."*

Example: *"Set up Cycles with 256 samples, OIDN denoiser, AgX view transform, 1080p, 60fps. Verify each setting."*

---

## Prompt Shapes That Fail

### Vibes-only prompts

Bad: *"Make it look cinematic."*

The agent has no anchor for what "cinematic" means in this scene. It will pick defaults that may not match your intent.

Better: *"Set up cinematic camera language — 35mm lens, f/2.8 DOF focused on the active object, AgX High Contrast view transform, motion blur shutter 0.5."*

### Multi-step creative prompts without checkpoints

Bad: *"Build a dungeon scene with a dragon guarding gold."*

Too much state change at once. By the time the agent has built the geometry, lit it, and posed the dragon, no individual step has been verified and the file is full of cruft from earlier mis-steps.

Better: build incrementally with read-verify between steps. First a floor + walls, save. Then lighting, save. Then the dragon model, save. Then the gold, save.

### Prompts that assume context the agent can't see

Bad: *"Make this match the reference image."*

The agent has no reference image. It has the `.blend`. It will guess.

Better: describe what you want to match in the prompt itself, or paste the image inline so the agent can see it, or break the request into specific deltas ("the sky should be warmer," "the camera should be lower").

---

## Save Discipline

Modifications live in Blender's memory only. They do not touch disk until File → Save commits them. The connector cannot save autonomously in the same way a script can — and even when it can, **you don't want it to**. Manual save is the trust boundary.

The save habits:

- **Before any non-trivial session:** *"Save the file. Confirm the save path."* If the file is unsaved or in an unexpected location, you want to know before you mutate anything.
- **After any successful change-set:** *"Save the file."* Commit the good state before the next experiment.
- **Before `execute_blender_code` with anything potentially destructive:** Save first, always. The arbitrary-Python tool can do anything `bpy` can do, including data loss.
- **For long sessions:** Save at each natural checkpoint — after the lighting pass, after the material pass, after the camera setup. Treat checkpoints like a Git commit cadence.
- **Before a render:** Save. Renders sometimes hang, and crash recovery from `.blend1` autosave is not guaranteed for in-memory changes.

A practical rule: if you'd be unhappy losing the last 10 minutes, save now.

---

## `execute_blender_code` Discipline

The structured MCP tools cover most read/write needs. But Blender's API has corners the structured tools don't surface, and sometimes you need a multi-step operation in a single tool call to stay atomic. That's what `execute_blender_code` is for.

When to reach for it:

- The MCP's structured tools don't cover the operation — e.g., direct BMesh edits, custom property writes, library override creation.
- You need a **multi-step atomic operation** — e.g., create a material, add 8 nodes, link them, assign to object — all in one call to avoid partial state.
- The operation is repetitive — e.g., process 200 objects with the same transform.

Rules for the code itself:

- **Save before**, especially on the first run of a new code block. Save is cheap; recovery from a runaway script is not.
- **Prefer `bpy.data.*` over `bpy.ops.*`** in scripted code. `data` calls are context-independent — they work regardless of which editor is active. `ops` calls depend on the active area, the selection, the mode, and many other invisible bits of state.
- **Use `bpy.context.temp_override()`** when you must call an operator that requires a specific editor context. Don't just call `bpy.ops.something()` and hope.
- **Wrap mutations in try/except** when running on data you didn't explicitly create — assume the worst about what's in the file.
- **Print state at the end** of the script. The agent's stdout becomes its return value — a final `print(...)` makes verification cheap.

---

## Error-Recovery Patterns

Common error classes and the canonical response.

### "Context is incorrect"

Cause: an `ops` call ran in the wrong editor context. The operator needs the 3D Viewport active, or the Shader Editor, or the Node Editor.

Fix: use `bpy.context.temp_override(area=area, region=region)` with the right area type, or switch via `area.type = 'VIEW_3D'` before the call. Better: rewrite the call as `bpy.data.*` if possible.

### "Object not found" / `KeyError`

Cause: the agent referenced a name that doesn't exist. Either the object was renamed mid-session, or the agent guessed a name from earlier context.

Fix: always look up via `bpy.data.objects.get(name)` and check for `None` before mutating. Never assume a name exists.

### "Tool call timed out"

Cause: operation exceeded the 300-second timeout. Common with large geometry analysis, full renders, or unbounded loops.

Fix: chunk into smaller steps. For a 5000-object scene, process 500 at a time. For a render, render a low-sample preview first.

### "Response too long"

Cause: tool response exceeded the ~150K character cap. Usually a "list everything" prompt on a large scene.

Fix: filter, sort, or summarize *inside* the Python before returning. Return counts and exemplars, not raw dumps. *"127 materials total. Top 10 by user count: …"*

### First-command-after-connect error

Cause: known quirk of the connector handshake.

Fix: re-issue the same command. If it errors twice, check the BlenderMCP N-panel and re-click Connect to Claude.

### "Material created but doesn't render"

Cause: `material.use_nodes = True` was not set, or the material slot isn't assigned to the object's mesh.

Fix: after `bpy.data.materials.new(name)`, immediately `mat.use_nodes = True`. Then verify `obj.material_slots[i].material = mat` and check the mesh face material indices.

### Geometry changes don't appear in evaluated mesh

Cause: the depsgraph hasn't been updated since the change.

Fix: `bpy.context.view_layer.update()` or `bpy.context.scene.frame_set(bpy.context.scene.frame_current)` to force a refresh. Then read from `obj.evaluated_get(depsgraph)`.

---

## Agent-Human Handoff

The agent should stop and ask — or stop and hand off — when the work requires human authorship.

- **Sculpting strokes.** Pressure curves, stroke timing, the felt sense of pulling form out of clay — hand off to human at tablet. Cross-ref `[[BLENDER_SCULPTING]]`.
- **Complex rigging / IK chains.** Joint placement, weight painting, pole vector orientation — these are decisions about a body, and they're easier to make in the viewport than to describe in a prompt.
- **Hand-keyed character animation.** Timing, spacing, anticipation, follow-through, overshoot — subjective craft. The agent can scaffold (rest pose, blocking) but the final pass is human.
- **Retopology.** Edge flow decisions are art-direction.
- **UV unwrapping for hero assets.** Auto-unwrap is fine for utility geometry; hero assets need human seams.
- **Final art-direction calls.** Color choices, composition, focal length, framing — when there's no objective correct answer, the agent should propose options, not pick.
- **Anything where the agent isn't 75%+ confident the human's intent is clear.** Ask. The cost of a clarifying question is one round-trip; the cost of building the wrong thing is a session.

---

## What the Agent Should Do Well

These are areas where the agent can move with minimal hand-holding — the high-leverage automatable surface.

- **Scene inspection / audit / report.** What's in the file, how big it is, what depends on what.
- **Batch renames and reorganization.** Naming conventions, collection restructuring, datablock cleanup.
- **Modifier stack setup and tuning.** Subdivision, Solidify, Bevel, Array, Mirror, Boolean — the canonical chain.
- **Material creation following PBR conventions.** Principled BSDF, base color / roughness / metallic / normal, image texture wiring.
- **Render settings (Cycles / EEVEE) configuration.** Samples, denoiser, light paths, view transform, resolution, frame range.
- **Camera setup.** Focal length, sensor size, depth of field, focus tracking, framing to a target object.
- **Light setup.** 3-point lighting, HDRI-based IBL, single-source dramatic lighting. Cross-ref `[[BLENDER_PATTERNS_LIGHTING]]`.
- **Procedural geometry via Geometry Nodes graphs.** Scatter, instancing, mesh-to-points, attribute-driven deformation. Cross-ref `[[BLENDER_GEOMETRY_NODES]]`.
- **Asset export.** GLB / FBX for downstream engines, with the right axis conversion and material baking.
- **Compositor post setup.** Bloom, color grade, vignette, lens distortion, glare.

---

## The "Show Me First" Pattern

For any complex modification — new lighting setup, new shader, scene rearrangement — ask the agent to render a **preview** to a temp PNG before committing the full change.

The shape:

> *"Apply [change]. Render a 512×512 preview from the active camera at 16 samples to `/tmp/preview.png`. Then show me the result and wait for confirmation before doing the full version."*

Many "this doesn't look right" issues are visible in a 5-second preview render. A 5-second preview followed by a confirm and a full render is far cheaper than a 5-minute full render of a configuration that turns out to be wrong.

The same pattern applies to viewport screenshots when the connector supports them, and to OpenGL renders (`bpy.ops.render.opengl()`) for fast iteration.

---

## The `bpy` API Surface — Agent's Preferred Subset

When both an `ops` path and a `data` path exist for the same operation, **prefer `data`**. The `ops` path depends on the editor context, the selection, the active object, and the mode. The `data` path doesn't.

Concrete pairs:

- **Object creation.** Prefer `bpy.data.objects.new(name, data)` + `collection.objects.link(obj)`. Avoid `bpy.ops.mesh.primitive_*_add()` from script.
- **Material creation.** Prefer `bpy.data.materials.new(name)`. Avoid `bpy.ops.material.new()`.
- **Modifier add.** Prefer `obj.modifiers.new(name, type)`. Avoid `bpy.ops.object.modifier_add()`.
- **Collection creation.** Prefer `bpy.data.collections.new(name)` + `bpy.context.scene.collection.children.link(coll)`. Avoid the operator.
- **Node creation in a shader/geometry tree.** Prefer `node_tree.nodes.new(type_name)`. Avoid operator-driven node insertion.
- **Linking nodes.** Prefer `node_tree.links.new(output_socket, input_socket)`. There is no operator equivalent worth using here.

When you must use an `ops` call — e.g., `bpy.ops.object.join()` requires the right selection and active object — wrap it in `bpy.context.temp_override(...)` with the exact area, region, selected_objects, and active_object you need. Don't trust ambient context.

---

## The Session-Close Pattern

At the end of any non-trivial session, run a four-step close.

1. **Agent summarizes** what was done — bullet list, suitable for pasting into a build log or commit message.
2. **Agent saves the file.** Confirms the save path and timestamp.
3. **Agent flags open questions or follow-ups** — anything that's half-done, deferred, or needs human input next session.
4. **Human reviews the summary** and confirms or corrects. Corrections go back into the build log.

The summary is the bridge between sessions. Without it, the next session starts cold — the agent has no memory of what was decided. With it, the next session opens by reading the prior summary and the file is immediately in context.

---

## Cross-Reference to the Brain

When the agent doesn't know something, the first move is to consult this library, not to guess. The decision tree:

- **"How do I do X in Blender?"** → consult `[[BLENDER_LIBRARY_INDEX]]` and follow the decision tree to the right file.
- **"What's the bpy path for Y?"** → consult `[[BLENDER_PYTHON_API]]`.
- **"Has this failed before?"** → consult `[[BLENDER_FOOTGUNS]]`.
- **"What's a good lighting setup for Z?"** → consult `[[BLENDER_PATTERNS_LIGHTING]]`.
- **"How do I build this with Geometry Nodes?"** → consult `[[BLENDER_GEOMETRY_NODES]]`.
- **"This involves sculpting / rigging / hand-key animation"** → consult `[[BLENDER_SCULPTING]]` (and acknowledge handoff).

The brain is the durable layer. The session is the volatile layer. The brain should grow as patterns are learned; the session should consult the brain at every decision point.

---

## Common Footguns Specific to Agent-Driven Sessions

In addition to general Blender footguns (`[[BLENDER_FOOTGUNS]]`), the agent-driven layer has its own failure modes.

- **Assuming the active object is what you want.** `bpy.context.active_object` may be `None`, may be a leftover from the last click. Always confirm by name.
- **Modifying the scene when the human wanted a preview-only inspection.** Read the prompt verb carefully — "look at" and "report" are read-only; "set up" and "change" are write.
- **Calling operators in script context without `temp_override`.** Works in the interactive Python console; fails in MCP tool calls because there's no active 3D Viewport area to inherit from.
- **Trusting `bpy.context.selected_objects` to be the same set you saw two calls ago.** Selection mutates. Snapshot to a list before iterating if you need stability across operations.
- **Ignoring the "Use Online Access" preference.** Some Extensions and connector behaviors silently no-op when offline access is disabled. Check Preferences → System → Network if something that should work doesn't.
- **Running `execute_blender_code` with `import os; os.system(...)`.** The sandbox boundary is not always clearly defined. Don't shell out from Blender; do it from a separate tool call.
- **Building a 50-node Geometry Nodes graph in one tool call.** Hits the response cap, hits the timeout, and leaves a half-built graph if it fails midway. Chunk into 5-10 node sub-builds with saves between.
- **Setting `material.use_nodes = True` *after* creating nodes.** The node tree exists in memory but `use_nodes` is False so it doesn't render. Set the flag first, then create nodes.
- **Reading evaluated geometry without updating the depsgraph.** `frame_set(frame)` or `view_layer.update()` before reading from `obj.evaluated_get(depsgraph)`.
- **Trusting that "the agent saved the file" means it's on disk.** The connector cannot bypass the manual-save trust boundary in all versions. Verify with a follow-up *"Confirm the save path and the modification timestamp."*
- **Treating `execute_blender_code` as undoable.** It isn't, reliably. Some changes register in the undo stack, others don't. Save before, not after.
- **Driving the agent without reading first.** The single most common failure mode. Read, confirm, write, verify — every time the change is non-trivial.

---

## Sources

- [Anthropic — Using the Blender Connector in Claude](https://claude.com/resources/tutorials/using-the-blender-connector-in-claude) — the canonical install + workflow tutorial.
- [Creative AI News — Claude's Official Blender Connector: Setup and Workflow](https://www.creativeainews.com/articles/claude-blender-connector-official-setup-workflow/) — comprehensive setup writeup, blessed workflow detail.
- [Blender Lab — MCP Server](https://www.blender.org/lab/mcp-server/) — official Blender Lab distribution page.
- `wobar/working/BLENDER_MCP_RESEARCH.md` — the research file feeding this library, written 2026-05-22.
