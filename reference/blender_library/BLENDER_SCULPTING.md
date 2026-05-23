---
title: Sculpting — Brushes, Dyntopo, Multires, Retopology
version: 1.0
last_updated: 2026-05-22
status: live
scope: Blender Sculpt Mode reference — brushes, dyntopo (dynamic topology), multires modifier, sculpt masks, retopology workflow. Most sculpt work requires a human at a tablet; this file flags what's agent-scriptable (prep, finalization, modifier setup) vs human-only (stroke authoring).
dependencies: BLENDER_LIBRARY_INDEX.md, BLENDER_MODELING.md, BLENDER_PYTHON_API.md
---

# SCULPTING — BRUSHES, DYNTOPO, MULTIRES, RETOPOLOGY

Sculpt Mode is Blender's brush-based, stroke-driven mesh deformation system. Since the 2.80 → 3.x → 4.x sculpt overhauls (Pose, Cloth, Boundary, Face Sets, Multires Displacement brushes; Voxel Remesh; sculpt-mode Mask attribute) it has become genuinely competitive with ZBrush for hard-surface and creature work. Studios ship Blender-sculpted hero assets.

**The central honesty:** sculpting is the area of Blender *least* suited to agent-driven authoring. The canonical workflow is a human at a graphics tablet, free-handing strokes with pressure-sensitive radius/strength. An LLM cannot produce a sculpt "look" by calling operators — there is no `bpy.ops.sculpt.draw_dragon_face()`. What an agent *can* do is **prepare** the mesh (modifier stack, dyntopo settings, symmetry, mask vertex groups, multires levels) and **finalize** the result (apply modifiers, retopology setup, bake high → low normal map, shade smooth, decimate). The strokes between prep and finalize are the human's.

**Core facts:**
- Sculpt Mode operates on a single active **mesh object**. Curves, surfaces, metaballs are not sculptable.
- The unit of work is the **stroke** — a brush dragged across the surface. Strokes are not exposed in `bpy.ops` as a callable function.
- Two topology strategies: **Dyntopo** (geometry added/removed under the brush, on the fly) vs **Multires** (subdivided fixed topology with sculpt detail captured per subdivision level).
- A third option: sculpt directly on a static, manually-subdivided base mesh (no Dyntopo, no Multires).
- **Masks** isolate sculpt strokes to unmasked regions. Stored as a per-vertex float attribute (`.sculpt_mask`).
- **Face Sets** are integer-tagged face groupings used by Pose, Boundary, and Auto-Mask features.
- **Cloth** and **Pose** brushes use simulated physics (cloth solver / IK-like chain) during the stroke.
- **Brush engines:** Draw / Smooth / Pinch / Grab / Snake Hook / Clay / Flatten / etc. — about 30 in 4.5.
- **Tablet pressure** drives Radius and Strength by default — keyboard/mouse work is possible but cripples expressiveness.
- A sculpt result is typically high-poly (millions of tris) and requires **retopology** to be production-usable.
- Modifier stack interacts with sculpt: Multires must usually be the **first** modifier in the stack while sculpting.
- Symmetry is per-axis (X/Y/Z) and tiled — toggled in the sculpt header, accessible via `tool_settings.sculpt.use_symmetry_x/y/z`.

---

## Entering Sculpt Mode

```python
import bpy
obj = bpy.context.view_layer.objects.active
# obj must be a mesh
bpy.ops.object.mode_set(mode='SCULPT')
```

Requires an active mesh object. Once in sculpt mode the operator vocabulary narrows — `bpy.ops.sculpt.*` exposes mask ops, dyntopo toggle, face set ops, symmetrize, and a handful of others. The brush strokes themselves are not in this namespace.

See [[BLENDER_MODELING]] for mesh prep before sculpting (clean topology, manifold check, scale applied).

---

## The Brush Set

Brushes live under `bpy.data.brushes`. The active brush is `bpy.context.tool_settings.sculpt.brush`.

### Build / Add brushes
- **Draw** — push verts outward along surface normal. The workhorse; default brush.
- **Draw Sharp** — same as Draw but with hard-edge falloff; for crisp ridges.
- **Clay** — flat-builds geometry into a smooth surface; for bulking out forms.
- **Clay Strips** — flat-build with a hard square footprint; aggressive plane-building, popular for hard-surface and creature work.
- **Clay Thumb** — clay-strips-like smearing with a thumb-press feel.
- **Layer** — raises a defined-thickness plateau; height clamps so repeat strokes don't compound.
- **Inflate** — pushes verts outward along *each vertex's* normal (no brush-plane constraint).
- **Blob** — Inflate localized to a smaller falloff; for spherical bumps.
- **Crease** — pushes inward with sharp falloff while pinching; for hard concave seams.

### Smooth / Flatten brushes
- **Smooth** — relaxes topology; shortcut `Shift` while any brush is active.
- **Flatten** — pushes verts toward the average plane under the brush.
- **Fill** — pushes only verts *below* the plane upward (fills recesses).
- **Scrape** — pushes only verts *above* the plane downward (scrapes ridges).
- **Multi-plane Scrape** — uses two angled planes to scrape, producing clean bevels and hard-surface intersections.
- **Pinch** — pulls verts toward the brush center.

### Grab / Deform brushes
- **Grab** — drags the masked region of verts like wet clay; no normal projection.
- **Elastic Deform** — soft physically-plausible falloff (grab/twist/scale/bi-scale modes); for large-scale form changes.
- **Snake Hook** — pulls a long protrusion as you drag (good for horns, tendrils).
- **Thumb** — smears verts in the drag direction along the surface.
- **Pose** — armature-like deformation; defines a chain of segments from Face Sets and bends them.
- **Nudge** — light directional push, no stretching.
- **Rotate** — rotates verts within the brush radius around the brush center.
- **Slide Relax** — slides verts along their connected edges to relax topology without changing shape.
- **Boundary** — manipulates open-mesh boundaries (loops at mesh edges) with bend/twist/inflate.
- **Cloth** — runs a local cloth simulation under the brush; for drapery, sagging skin.
- **Simulation** — local physics-driven deformation (4.x addition).

### Paint / Mask / Face Set brushes
- **Paint** — paints vertex color (requires Color Attribute on the mesh).
- **Smear** — smears existing vertex color.
- **Mask** — paints the sculpt mask attribute (Ctrl+Click to add, Ctrl+Shift to subtract).
- **Face Set** — paints face set IDs onto faces.
- **Multires Displacement Eraser / Smear** — operate on multires displacement data specifically.

The full list is in **Sculpt header → Brush asset shelf** in 4.x; older Toolbar brushes were migrated to asset-based brushes in 4.3+.

---

## Brush Settings

Per-brush, exposed in the N-panel and the top header:

- **Radius** — brush size, px or world units; F to scrub, tablet pressure scales it.
- **Strength** — depth-per-stroke; Shift+F to scrub.
- **Pressure response** — toggles for radius/strength/jitter. `brush.use_pressure_size`, `brush.use_pressure_strength`.
- **Stroke method** — **Dots** (continuous spaced), **Drag Dot** (single stamp dragged), **Anchored** (fixed origin, drag size), **Line** (straight-line stamp), **Curve** (stamp along a drawn curve), **Space** (deprecated/aliased).
- **Falloff** — Smooth / Sphere / Root / Sharp / Linear / Pop / Constant / Inverse Square / Custom Curve.
- **Brush Plane** — area-plane vs view-plane; affects Flatten/Fill/Scrape behavior.
- **Topology vs Brush plane modes** — for flat brushes: should the plane track local topology or the brush direction.
- **Auto-masking** — Topology / Face Sets / Boundary Edges / Boundary Face Sets / Cavity / View Normal. Limits stroke effect by mesh feature.

API access:
```python
sc = bpy.context.tool_settings.sculpt
br = sc.brush
br.size = 80          # radius in px (default unit setup)
br.strength = 0.5
br.use_pressure_size = True
br.use_pressure_strength = True
br.stroke_method = 'DOTS'
br.curve_preset = 'SMOOTH'
```

---

## Dyntopo — Dynamic Topology

**Dyntopo** rebuilds local geometry under the brush as you stroke — adding triangles where detail is needed, collapsing where it isn't. Start from a low-poly base; let dyntopo grow the resolution.

- Toggle: sculpt header **Dyntopo** checkbox, or `bpy.ops.sculpt.dyntopo_toggle()`.
- **Detail Method:**
    - **Relative Detail** — detail in pixels of screen space (zoom-dependent).
    - **Constant Detail** — detail in world units (stable across zoom; preferred for consistent results).
    - **Brush Detail** — scales with brush radius.
    - **Manual** — only refines on Flood Fill / explicit ops.
- **Detail Size** — the resolution number (px for Relative, world units for Constant).
- **Refine Method** — Subdivide Edges / Collapse Edges / Both.

**When to use Dyntopo:**
- Sketching forms from a low-poly base (cube, sphere).
- You don't care about final topology (will be retopologized or remeshed later).
- Creature / organic work where detail density should follow form.

**When to avoid:**
- You need clean quads for animation.
- You have UVs, vertex groups, or shape keys you want to preserve — **Dyntopo destroys all of these.**
- You're working on a Multires mesh (incompatible).

API:
```python
sc = bpy.context.tool_settings.sculpt
sc.detail_type_method = 'CONSTANT'   # or 'RELATIVE', 'BRUSH', 'MANUAL'
sc.constant_detail_resolution = 12   # world-unit detail
bpy.ops.sculpt.dyntopo_toggle()
```

---

## Multires Modifier

The non-destructive alternative to Dyntopo. Subdivide the base mesh into multiple levels; sculpt at any level; detail is captured per-level as displacement.

- Add: `bpy.ops.object.modifier_add(type='MULTIRES')`.
- Subdivide: `bpy.ops.object.multires_subdivide(modifier='Multires')` — repeat for each level.
- Three independent levels: **Viewport Level** (what you see in object mode), **Sculpt Level** (what you sculpt on), **Render Level** (what renders).
- Detail captured at higher levels can be reconstructed at lower levels via **Reshape** / **Apply Base**.

**Modifier stack rule:** Multires should usually be the **top** (first) modifier — sculpt edits land on the base topology, then downstream modifiers apply.

**Multires bake-down workflow** — the canonical high-to-low pipeline:
1. Sculpt at high Sculpt Level until detail is locked.
2. Make or designate a low-poly target (either a retopologized mesh, or the level-0 base).
3. **Bake** the high-poly detail into a normal map (see "Multires Bake to Normal Map" below).
4. Apply the normal map on the low-poly material.

API:
```python
bpy.ops.object.modifier_add(type='MULTIRES')
for _ in range(5):
    bpy.ops.object.multires_subdivide(modifier='Multires')
obj.modifiers['Multires'].sculpt_levels = 5
obj.modifiers['Multires'].levels = 2          # viewport
obj.modifiers['Multires'].render_levels = 5
```

---

## Masking

Masks isolate sculpt strokes to unmasked regions. Stored as a per-vertex float in `[0,1]` on the mesh attribute `.sculpt_mask`.

- **Mask brush** — Ctrl+Click to paint, Ctrl+Shift+Click to erase.
- **Display** — `M` toggles mask visibility.
- **Clear** — `Alt+M`. Invert — `Ctrl+I`.
- **Sharpen / Grow / Shrink / Smooth** — under Sculpt menu → Mask.
- Brushes that respect mask: nearly all — Draw, Clay, Smooth, Flatten, Inflate, Grab, Pose, etc.
- **Mask from Vertex Group** — convert a vertex group's weights into mask values: `bpy.ops.sculpt.mask_from_vertex_group()`. The inverse (mask to vertex group) is `bpy.ops.sculpt.mask_to_vertex_group` in modern builds, or `bpy.ops.paint.mask_flood_fill` variants.
- **Mask from Cavity / AO** — generates a mask procedurally from surface curvature.

Agent use: pre-paint a vertex group in Object Mode (or via a Weight Paint script), then `mask_from_vertex_group` to hand the human a sculpt-ready mask.

---

## Face Sets

Colored, integer-tagged face groupings (separate from vertex groups). Used by:
- **Pose brush** — chain segments derived from face set boundaries.
- **Auto-mask by Face Set** — confines stroke to one face set.
- **Boundary brush** — operates on face set boundaries.

Initialize from:
- Materials (each material → one face set).
- Loose parts.
- Visible (current visible faces → one set).
- Sharp Edges / By Side / By Normals.

Operators: `bpy.ops.sculpt.face_sets_init(mode='MATERIALS')`, `face_set_change_visibility`, `face_sets_create`.

---

## Retopology

Sculpts produce high-poly meshes (often millions of tris) with bad topology for downstream use (rigging, animation, UVing). **Retopology** is the process of building a clean low-poly mesh that follows the sculpt's silhouette.

### Manual retopology
1. Add a new mesh (plane or face) near the sculpt.
2. Modifier stack on the retopo mesh: **Shrinkwrap** (target = sculpt, Mode = Project, On Surface), then **Mirror** (X axis) if symmetric.
3. Enable **Snap** (Surface) → snap-to-face-of-target so verts stay glued to the sculpt.
4. Manually extrude edges, fill quads, follow form. Use the **PolyBuild** tool or F2 addon for speed.

### Automatic retopology
- **Quad Remesher** — paid addon (Exoside). Industry-gold-standard, fast, produces edge-flow-aware quads.
- **Quadriflow Remesh** — built-in (`Object → Quad Remesh` or in sculpt mode header). Decent quads, but flow is not always correct on complex topology.
- **Voxel Remesh** — built-in (see next section). Uniform-density tris/quads, **topology-poor** — useful as a sculpt prep step (uniform triangulation under brush), not as final retopo.

See [[BLENDER_ADDONS]] for addon-driven retopology tools.

---

## Voxel Remesh

In Sculpt Mode header → **Remesh**, or `Object → Quick Effects → Voxel Remesh`, or `Ctrl+R` (live preview / apply).

- **Voxel Size** — world-unit voxel resolution. Lower = denser mesh.
- Produces a uniformly-dense triangulated mesh that follows the original's volume.
- **Destroys UVs, vertex groups, shape keys, vertex colors** (the topology is completely rebuilt).
- Useful as a sculpt-prep operation: starting from a blob, remesh to uniform density, then dyntopo or sculpt on the result.
- Useless as final topology — every face is the same size, no edge flow.

API:
```python
obj.data.remesh_voxel_size = 0.02
bpy.ops.object.voxel_remesh()
```

---

## Multires Bake to Normal Map (High → Low)

The classic pipeline for getting sculpt detail onto a production low-poly mesh:

1. **Sculpt source** — multires mesh at high Sculpt Level, or any high-poly mesh.
2. **Low-poly target** — retopologized mesh (or just the Multires base at level 0), UV-unwrapped.
3. **New Image Texture** — assigned in the low-poly's material, dimensions e.g. 2048×2048, Color Space = Non-Color.
4. **Select** — first select the **high-poly source**, then **Shift-select the low-poly target so it is active**.
5. **Render properties → Bake panel:**
    - Bake Type: **Normal**
    - Selected to Active: **on**
    - Extrusion: small positive value (e.g. 0.05) — the cage offset
    - (Optional) Cage Object: a slightly-inflated copy of the low-poly for precise control on hard silhouettes.
6. **Bake** (uses Cycles).
7. The baked normal map is now in the low-poly material — wire it into Principled BSDF → Normal via a **Normal Map** node (Tangent Space, Non-Color).

See [[BLENDER_MATERIALS]] for the Normal Map node wiring and [[BLENDER_PYTHON_API]] for `bpy.ops.object.bake` parameters.

API:
```python
bpy.context.scene.render.bake.use_selected_to_active = True
bpy.context.scene.render.bake.cage_extrusion = 0.05
bpy.ops.object.bake(type='NORMAL')
```

---

## bpy API Surface — Agent-Useful Calls

Sculpt strokes themselves are not in `bpy.ops`, but these are:

- `bpy.ops.object.mode_set(mode='SCULPT')` — enter sculpt mode.
- `bpy.context.tool_settings.sculpt` — the SculptToolSettings block.
- `bpy.context.tool_settings.sculpt.brush` — active brush.
- `bpy.context.tool_settings.sculpt.use_symmetry_x/y/z` — symmetry toggles.
- `bpy.ops.sculpt.dyntopo_toggle()` — toggle dynamic topology.
- `bpy.context.tool_settings.sculpt.constant_detail_resolution` — dyntopo detail size.
- `bpy.context.tool_settings.sculpt.detail_type_method` — `'CONSTANT'/'RELATIVE'/'BRUSH'/'MANUAL'`.
- `bpy.ops.object.modifier_add(type='MULTIRES')`.
- `bpy.ops.object.multires_subdivide(modifier='Multires')`.
- `bpy.ops.object.multires_higher_levels_delete`, `multires_reshape`, `multires_base_apply`.
- `bpy.ops.sculpt.mask_from_vertex_group()`.
- `bpy.ops.sculpt.face_sets_init(mode='MATERIALS' | 'LOOSE_PARTS' | 'SHARP_EDGES' | ...)`.
- `bpy.ops.object.voxel_remesh()` — apply voxel remesh on the active sculpt object.
- `bpy.ops.object.shade_smooth()` — Object Mode shade smooth (typical post-sculpt finalization).
- `bpy.ops.object.bake(type='NORMAL' | 'AO' | 'DISPLACEMENT' | ...)` — for the bake-down step.

---

## What an Agent Should and Shouldn't Do

**Should:**
- Prep the base mesh: apply scale, clean non-manifold, set origin, add Mirror/Subdivision modifiers as appropriate.
- Configure sculpt symmetry, dyntopo detail size, multires levels before handing off.
- Create vertex groups in Object Mode that the human will use as masks.
- Add a Multires modifier and pre-subdivide to a reasonable starting level.
- Set up the Voxel Remesh size if the human is starting from a primitive blob.
- After the sculpt: apply modifiers, run shade smooth, set up a retopo mesh with Shrinkwrap + Mirror, configure the bake panel for high → low.
- **Explicitly say:** "Sculpt strokes are yours — call me back when the high-poly is done and I'll bake / retopo / finalize."

**Shouldn't:**
- Try to script a sculpt look from a text prompt.
- Brute-force sculpt detail with random Vector Displacement or noise textures and call it a sculpt.
- Promise the user a finished sculpt result without a human at the tablet.
- Auto-apply Dyntopo or Voxel Remesh on a mesh with UVs / vertex groups the user wants to keep — surface this destructive consequence first.

---

## Common Footguns

- **Dyntopo destroys UVs, vertex groups, shape keys, and vertex color attributes.** Blender warns; the warning is real. If those exist, switch to Multires.
- **Multires must be top of the modifier stack** while sculpting. If a Mirror or Subsurf is above it, multires sculpt ops error out or produce wrong displacement.
- **Voxel Remesh destroys UVs, vertex groups, shape keys.** Same destruction surface as Dyntopo. Only use on meshes where topology is disposable.
- **Multires bake at insufficient resolution → muddy normal map.** Bake at 2K minimum for hero assets; 4K for close-ups. Sculpt Level must be high enough that there's actual detail to bake.
- **Selected to Active reversed.** The high-poly is *selected*; the low-poly is *active* (last selected, lighter outline). Reverse this and you bake low → high, getting a flat result.
- **Cage offset too small → bake errors at silhouette / sharp edges.** Increase `cage_extrusion` or add an explicit Cage Object inflated slightly outside the low-poly.
- **Cage offset too large → ray-cast misses, paint bleed from adjacent surfaces.** Use an explicit Cage Object for tight control.
- **Cloth brush on a low-poly mesh → unimpressive deformation.** Cloth needs subdivision density to drape; subdivide or apply Multires first.
- **`use_pressure_strength=True` with no tablet → strokes have no variation.** Mouse input registers as constant 1.0 pressure; strength feels max-power always.
- **Sculpting without applying scale.** Non-uniform scale on the object warps brush radius and strength. Always `bpy.ops.object.transform_apply(scale=True)` before entering Sculpt Mode.
- **N-gons in the base mesh.** Sculpt mode tolerates them, but Multires refuses to subdivide a mesh containing n-gons. Triangulate or quad-fix first.
- **Forgetting `shade_smooth` after the sculpt.** Flat shading on a high-poly sculpt makes it look faceted — a 30-second mistake easy to ship.

---

## Cross-references

- [[BLENDER_MODELING]] — base mesh prep, topology rules, manifold checks.
- [[BLENDER_MATERIALS]] — Normal Map node, baked map wiring, displacement.
- [[BLENDER_PYTHON_API]] — `bpy.ops.object.bake`, modifier API, mode_set patterns.
- [[BLENDER_ADDONS]] — Quad Remesher, F2, retopology helpers.

**Sources:**
- https://docs.blender.org/manual/en/latest/sculpt_paint/sculpting/index.html
- https://docs.blender.org/manual/en/latest/sculpt_paint/sculpting/tools/index.html
- https://docs.blender.org/api/current/bpy.ops.sculpt.html
