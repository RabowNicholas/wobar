---
title: Modeling — Edit Mode, Modifiers, BMesh Reference
version: 1.0
last_updated: 2026-05-22
status: live
scope: Traditional mesh modeling — Edit-mode tools, the modifier stack (procedural and destructive), the BMesh Python API for direct topology editing, mesh primitives, common modeling patterns and gotchas.
dependencies: BLENDER_LIBRARY_INDEX.md, BLENDER_PYTHON_API.md, BLENDER_DATA_MODEL.md
---

# MODELING — EDIT MODE, MODIFIERS, BMESH

Traditional mesh modeling in Blender runs along **three parallel paths**, and the agent picks based on what the job demands:

1. **Edit-mode operators** — interactive tools (`bpy.ops.mesh.*`) that act on the current selection. Fast, expressive, but mode-locked and selection-dependent.
2. **The modifier stack** — non-destructive procedural ops on top of base mesh data. Stackable, reorderable, applied on demand.
3. **The BMesh API** — direct topology editing in Python (`bmesh.ops.*`, `bm.verts/edges/faces`). Scriptable, deterministic, the right tool for generative geometry.

Sculpting (`[[BLENDER_SCULPTING]]`) and Geometry Nodes (`[[BLENDER_GEOMETRY_NODES]]`) are sibling paths covered in their own files. This file is the *traditional* polygon workflow.

**Core facts:**
- Mesh data is verts, edges, polygons (faces), loops, UVs, vertex colors, and named custom attributes. Loops carry per-corner data (UVs, split normals, vertex colors).
- Edit mode is **mode-locked**: most `bpy.ops.mesh.*` operators require the active object to be in `EDIT` mode. Switch with `bpy.ops.object.mode_set(mode='EDIT')`.
- The modifier stack evaluates **top-down** — top entry runs first, its output feeds the next. Order is load-bearing; a Bevel before Subsurf is not the same shape as a Bevel after.
- Modifiers are **non-destructive** until applied. Apply collapses them into base mesh data and removes the entry.
- **BMesh** is the editable, half-edge-style in-memory form of a mesh. It exposes ops that aren't safe to do on `bpy.types.Mesh` directly (topology changes, merges, dissolves).
- The **depsgraph** evaluates the full modifier stack at render/preview time. `obj.data` is the *base* mesh; `obj.evaluated_get(depsgraph).data` is the *post-stack* mesh — use the latter to read final geometry.
- Edit-mode operators are macros that act on the current selection mask; the agent must set selection state explicitly before calling them.
- `bpy.ops.*` calls require a valid context. For automation in scripts, prefer BMesh or direct data writes; reserve operators for things they uniquely do (Knife, interactive Bevel, etc.).
- Selection sync: changes via BMesh while in Edit mode need `bmesh.update_edit_mesh(mesh)` to push back; otherwise the viewport doesn't see the edit.
- Custom attributes (`mesh.attributes`) on points/edges/faces/corners are first-class — Geometry Nodes and shaders read them by name.
- Normals: as of 4.1 the old object-data "Auto Smooth" toggle was **removed**. Smooth-shading-by-angle is now a stock Geometry Nodes modifier (`Smooth by Angle`) added via *Object → Shade Auto Smooth*.
- Mesh validation: `mesh.validate(verbose=True)` repairs invalid topology after Python edits; call it before saving generative meshes.

---

## Selection Modes — Read This First

Edit mode has three selection masks. They drive which operators do what:

- **Vertex mode** (`1` key) — selection is per-vertex. Best for grab/move and topology work.
- **Edge mode** (`2` key) — selection is per-edge. Best for loops, bevels, creases.
- **Face mode** (`3` key) — selection is per-polygon. Best for extrudes, insets, face-level ops.

In Python the mode is a 3-tuple of booleans on the mesh: `mesh.select_mode = (vert, edge, face)`. Multiple can be true; setting `(True, False, False)` is vertex-only.

To set from a script:
```python
bpy.ops.mesh.select_mode(type='VERT')   # or 'EDGE', 'FACE'
```

Selection state lives on the mesh data and on BMesh elements (`v.select`, `e.select`, `f.select`). When using BMesh you must also set `bm.select_flush(True)` to push selection between masks.

---

## Mesh Primitives

All primitive operators add a single object at the 3D cursor and enter Object mode. Each takes a `size` (or `radius`/`depth`), location, rotation, and topology-specific params.

### Plane
- Op: `bpy.ops.mesh.primitive_plane_add(size=2.0)`
- 1 quad, 4 verts. Use: ground, base for displacement, base for arrays.

### Cube
- Op: `bpy.ops.mesh.primitive_cube_add(size=2.0)`
- 6 quads, 8 verts. Use: hard-surface base, bevel-and-subsurf chassis.

### Circle
- Op: `bpy.ops.mesh.primitive_circle_add(vertices=32, radius=1.0, fill_type='NOTHING')`
- `fill_type`: NOTHING / NGON / TRIFAN. Use: extrudable profile, base for lathe (Screw), wheel.

### UV Sphere
- Op: `bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=1.0)`
- Standard pole-and-ring topology. Good UVs, pinching at poles.

### Ico Sphere
- Op: `bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1.0)`
- Triangulated geodesic. No poles, uniform density. Use: subdiv base, exploding shells.

### Cylinder
- Op: `bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=1.0, depth=2.0, end_fill_type='NGON')`
- Use: bottles, pillars, wires.

### Cone
- Op: `bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=1.0, radius2=0.0, depth=2.0)`
- `radius2=0` → cone, nonzero → truncated cone / frustum.

### Torus
- Op: `bpy.ops.mesh.primitive_torus_add(major_radius=1.0, minor_radius=0.25, major_segments=48, minor_segments=12)`
- Use: rings, tubes-along-curves alternative.

### Grid
- Op: `bpy.ops.mesh.primitive_grid_add(x_subdivisions=10, y_subdivisions=10, size=2.0)`
- Pre-subdivided plane. Use: displacement, cloth, water.

### Monkey (Suzanne)
- Op: `bpy.ops.mesh.primitive_monkey_add(size=2.0)`
- Test mesh — shading, UVs, modifier behaviour.

---

## Edit-Mode Operators by Category

All listed under `bpy.ops.mesh.*` unless noted. Most respect current selection mask and require Edit mode.

### Extrude family
- `bpy.ops.mesh.extrude_region_move(...)` — extrude selection along normal. The most-used model op.
- `bpy.ops.mesh.extrude_faces_move(...)` — extrude each face individually (no shared edges between extrusions).
- `bpy.ops.mesh.extrude_edges_move(...)` — extrude edges only (no cap face).
- `bpy.ops.mesh.extrude_vertices_move(...)` — extrude verts as new edges.
- `bpy.ops.mesh.extrude_region_shrink_fatten(...)` — extrude then offset along normal in one step.

### Bevel family
- `bpy.ops.mesh.bevel(offset=0.1, segments=2, profile=0.5, affect='EDGES')` — bevel selected edges or verts.
- `affect`: 'VERTICES' (corner round) or 'EDGES' (chamfer).
- `profile`: 0.5 round, 1.0 sharp, 0.25 hollow.
- Bevel **weights** (`bpy.ops.mesh.edges_set_bevel_weight`) drive the Bevel *modifier* selectively.

### Loop cut family
- `bpy.ops.mesh.loop_cut_slide(...)` — interactive loop cut + slide. Operator form: `bpy.ops.mesh.loopcut_slide(MESH_OT_loopcut={"number_cuts":1})`.
- `bpy.ops.mesh.subdivide(number_cuts=1, smoothness=0.0)` — subdivide selected edges/faces.
- `bpy.ops.mesh.offset_edge_loops(...)` — slide a parallel loop on each side.

### Inset
- `bpy.ops.mesh.inset(thickness=0.1, depth=0.0, use_individual=False)` — inset selected faces.
- `use_individual=True` insets each face separately (greeble pattern).

### Knife / Bisect
- `bpy.ops.mesh.knife_tool(...)` — interactive only, not script-friendly.
- `bpy.ops.mesh.bisect(plane_co=(0,0,0), plane_no=(0,0,1), use_fill=False, clear_inner=False, clear_outer=False)` — cut mesh with a plane. The scriptable knife.

### Merge / Dissolve
- `bpy.ops.mesh.merge(type='CENTER')` — types: 'CENTER', 'CURSOR', 'COLLAPSE', 'FIRST', 'LAST'.
- `bpy.ops.mesh.remove_doubles(threshold=0.0001, use_unselected=False)` — merge by distance. Renamed in UI to "Merge by Distance" but the operator string remains `remove_doubles`.
- `bpy.ops.mesh.dissolve_verts()` — remove verts and stitch surrounding geometry.
- `bpy.ops.mesh.dissolve_edges(use_verts=False)` — remove edges between faces, leaving n-gons.
- `bpy.ops.mesh.dissolve_faces()` — merge selected faces into one face.
- `bpy.ops.mesh.dissolve_limited(angle_limit=0.0872665)` — auto-dissolve coplanar geometry (great for cleanup after Boolean).

### Smoothing / shading
- `bpy.ops.object.shade_smooth()` — smooth shading on all faces (Object mode op).
- `bpy.ops.object.shade_flat()` — faceted shading.
- `bpy.ops.object.shade_auto_smooth(angle=0.5236)` — **4.1+** adds the Smooth-by-Angle GN modifier. Replaces the old object-data Auto Smooth toggle.
- `bpy.ops.mesh.faces_shade_smooth()` / `bpy.ops.mesh.faces_shade_flat()` — per-face shading inside Edit mode.
- `bpy.ops.mesh.vertices_smooth(factor=0.5, repeat=1)` — Laplacian smoothing on selected verts.

### Selection helpers
- `bpy.ops.mesh.select_all(action='SELECT' | 'DESELECT' | 'INVERT' | 'TOGGLE')`
- `bpy.ops.mesh.select_linked(delimit={'NORMAL'})` — grow selection over connected geometry.
- `bpy.ops.mesh.select_more()` / `select_less()` — grow/shrink one ring.
- `bpy.ops.mesh.loop_multi_select(ring=False)` — edge loops; `ring=True` for edge rings.
- `bpy.ops.mesh.select_face_by_sides(number=4, type='EQUAL')` — pick quads / tris / n-gons. Critical for topology audits.
- `bpy.ops.mesh.select_interior_faces()` — find buried geometry post-Boolean.

### Topology cleanup
- `bpy.ops.mesh.normals_make_consistent(inside=False)` — recalc outward (Shift+N).
- `bpy.ops.mesh.flip_normals()` — flip selected faces.
- `bpy.ops.mesh.fill()` / `bpy.ops.mesh.fill_grid()` — fill a closed loop with a face / grid.
- `bpy.ops.mesh.bridge_edge_loops(...)` — join two parallel loops with quads.

---

## Modifiers — Reference

Add via UI Properties → Modifier Properties, or in Python with:
```python
mod = obj.modifiers.new(name="Bevel", type='BEVEL')
mod.width = 0.05
mod.segments = 3
```

The full set, grouped as Blender's UI groups them. Bracketed kwargs are the most-common Python properties on the modifier object.

### Generate
- **Array** (`'ARRAY'`) — repeat the mesh N times. Modes: Fixed Count, Fit Length, Fit Curve. `count`, `relative_offset_displace`, `use_merge_vertices`. Stacks for grid arrays.
- **Bevel** (`'BEVEL'`) — round edges. `width`, `segments`, `limit_method` ('ANGLE' | 'WEIGHT' | 'VGROUP'), `profile`, `harden_normals`.
- **Boolean** (`'BOOLEAN'`) — union / difference / intersect with another object. `operation`, `object`, `solver` ('FAST' | 'EXACT'). Exact is slower but topology-clean.
- **Build** (`'BUILD'`) — animated face-by-face construction. `frame_start`, `frame_duration`.
- **Decimate** (`'DECIMATE'`) — reduce polycount. Modes: 'COLLAPSE' (ratio), 'UNSUBDIV' (iterations), 'DISSOLVE' (angle limit). Collapse is the LOD workhorse but kills UVs.
- **Edge Split** (`'EDGE_SPLIT'`) — split edges by angle or marked-sharp. Legacy hard-edge tool; superseded by Smooth-by-Angle GN in 4.1+ for shading.
- **Geometry Nodes** (`'NODES'`) — apply a node group as a modifier. See `[[BLENDER_GEOMETRY_NODES]]`.
- **Mask** (`'MASK'`) — hide geometry by vertex group or armature bone. `vertex_group`, `invert_vertex_group`.
- **Mirror** (`'MIRROR'`) — mirror across axes. `use_axis` (x/y/z), `use_mirror_merge`, `merge_threshold`, `use_clip`, `mirror_object`.
- **Multires** (`'MULTIRES'`) — multi-level sculpt subdivision. See `[[BLENDER_SCULPTING]]`.
- **Remesh** (`'REMESH'`) — rebuild topology. Modes: 'BLOCKS', 'SMOOTH', 'SHARP', 'VOXEL'. Voxel mode → uniform-density retopo for sculpt cleanup.
- **Screw** (`'SCREW'`) — lathe a profile around an axis. `axis`, `angle`, `screw_offset`, `steps`. Bottles, threads.
- **Skin** (`'SKIN'`) — wrap a flesh around edges via per-vertex skin radii. Combined with Subsurf → organic tubes.
- **Solidify** (`'SOLIDIFY'`) — give surfaces thickness. `thickness`, `offset`, `use_rim`, `use_even_offset`.
- **Subdivision Surface** (`'SUBSURF'`) — Catmull-Clark subdivision. `levels_viewport`, `render_levels`. The single most-used modifier; pair with creases or Bevel.
- **Triangulate** (`'TRIANGULATE'`) — quads/n-gons → tris. `quad_method`, `ngon_method`. Place last for export.
- **Volume to Mesh** (`'VOLUME_TO_MESH'`) — mesh a volume object via threshold/adaptivity.
- **Weld** (`'WELD'`) — merge close verts at modifier-stack time. `merge_threshold`. Non-destructive `remove_doubles`.
- **Wireframe** (`'WIREFRAME'`) — convert edges into rendered tubes. `thickness`, `use_replace`, `use_relative_offset`.

### Modify
- **Data Transfer** (`'DATA_TRANSFER'`) — copy normals / UVs / vertex groups / colors between meshes.
- **Mesh Cache** (`'MESH_CACHE'`) — replay a baked deformation cache (MDD/PC2).
- **Mesh Sequence Cache** (`'MESH_SEQUENCE_CACHE'`) — Alembic / USD playback.
- **Normal Edit** (`'NORMAL_EDIT'`) — override normals by direction/target. Sphere-blend cheat.
- **Weighted Normal** (`'WEIGHTED_NORMAL'`) — area- or angle-weighted custom normals. Hard-surface bevel-shading fix.
- **UV Project** (`'UV_PROJECT'`) — camera-style projection from N projector objects.
- **UV Warp** (`'UV_WARP'`) — animate UVs via two transforms.
- **Vertex Weight Edit** (`'VERTEX_WEIGHT_EDIT'`) — remap a vertex group with a curve.
- **Vertex Weight Mix** (`'VERTEX_WEIGHT_MIX'`) — blend two vertex groups.
- **Vertex Weight Proximity** (`'VERTEX_WEIGHT_PROXIMITY'`) — distance-to-object → weight.

### Deform
- **Armature** (`'ARMATURE'`) — skinned rig deform.
- **Cast** (`'CAST'`) — push verts toward sphere/cylinder/cuboid.
- **Curve** (`'CURVE'`) — deform along a curve object. `object`, `deform_axis`.
- **Displace** (`'DISPLACE'`) — push verts along normal by a texture. `texture`, `texture_coords`, `strength`, `midlevel`.
- **Hook** (`'HOOK'`) — empty/bone drives a vertex group.
- **Laplacian Deform** (`'LAPLACIAN_DEFORM'`) — anchor verts, deform rest organically.
- **Lattice** (`'LATTICE'`) — FFD via a lattice object.
- **Mesh Deform** (`'MESH_DEFORM'`) — driven by a low-res cage mesh.
- **Shrinkwrap** (`'SHRINKWRAP'`) — snap to target surface. `target`, `wrap_method`, `offset`. Retopo workhorse.
- **Simple Deform** (`'SIMPLE_DEFORM'`) — twist / bend / taper / stretch. `deform_method`, `angle`, `factor`.
- **Smooth** (`'SMOOTH'`) — Laplacian smoothing. `factor`, `iterations`.
- **Smooth Corrective** (`'CORRECTIVE_SMOOTH'`) — preserve shape under skinning.
- **Smooth Laplacian** (`'LAPLACIANSMOOTH'`) — volume-preserving smoothing.
- **Surface Deform** (`'SURFACE_DEFORM'`) — bind to another surface; deforms with it.
- **Warp** (`'WARP'`) — fall-off-based deform between two empties.
- **Wave** (`'WAVE'`) — animated sinusoidal displace. `height`, `width`, `speed`, `time_offset`.

### Physics
- **Cloth** (`'CLOTH'`) — cloth simulation. CPU-bound on M1, expect slow bake. Physics-sim is a deliberate gap in the brain v1.0 — add a `BLENDER_SIMULATION.md` file if Mantaflow / Cloth / Soft Body workflows become load-bearing.
- **Collision** (`'COLLISION'`) — declares the object a collider.
- **Dynamic Paint** (`'DYNAMIC_PAINT'`) — vertex-color or wetmap painting from collisions.
- **Explode** (`'EXPLODE'`) — split mesh per particle.
- **Fluid** (`'FLUID'`) — domain/flow/effector for the fluid sim.
- **Ocean** (`'OCEAN'`) — animated ocean surface from spectrum.
- **Particle Instance** (`'PARTICLE_INSTANCE'`) — instance this mesh on another's particles.
- **Particle System** (`'PARTICLE_SYSTEM'`) — legacy particles (use auto-added entry, not manual).
- **Soft Body** (`'SOFT_BODY'`) — vertex-spring soft-body sim.

---

## Modifier Stack Mechanics

- **Order matters.** Top entry evaluates first. Common right-order patterns:
  - Mirror → Subsurf (mirror raw, then subdivide; otherwise the seam over-subdivides).
  - Array → Curve (build the chain, then bend along the curve).
  - Bevel → Subsurf (sharp bevels first, then smooth them).
  - Geometry Nodes that read attributes → before any modifier that destroys them (Decimate, Triangulate).
- **Visibility toggles** — each modifier has icons for: viewport, render, edit-mode display, edit-mode cage. The edit-mode cage toggle is what lets you sculpt/edit through Subsurf at the cage level.
- **Apply** — `bpy.ops.object.modifier_apply(modifier="Name")` collapses one entry into base mesh data. Order-sensitive: apply top-down. Applying a deform modifier on a mesh with shape keys is blocked unless the deform doesn't add geometry.
- **Reorder** — `bpy.ops.object.modifier_move_up(modifier="Name")` / `_down`. In Python directly: `obj.modifiers.move(from_index, to_index)`.
- **Remove** — `obj.modifiers.remove(obj.modifiers["Name"])`.
- **Copy to selected** — `bpy.ops.object.make_links_data(type='MODIFIERS')` or per-modifier *Copy To Selected*.

---

## Geometry Nodes as a Modifier

`'NODES'` modifier hosts a `bpy.types.GeometryNodeTree`. Inputs on the modifier appear as named sockets; outputs feed back into the mesh stream.

```python
mod = obj.modifiers.new("GN", type='NODES')
mod.node_group = bpy.data.node_groups["MyNodeGroup"]
mod["Socket_2"] = 0.5    # set named input by socket identifier
```

Full GN coverage in `[[BLENDER_GEOMETRY_NODES]]`. For modeling, GN's role is: anything procedural that you'd otherwise BMesh, but want to keep editable and stack-driven.

---

## BMesh API — Intro

BMesh is Blender's editable, half-edge-style mesh representation. It exposes safe topology ops that you can't perform on a `bpy.types.Mesh` directly. Two usage patterns:

### Edit-mode pattern (interactive scripts)
```python
import bmesh
me = bpy.context.edit_object.data
bm = bmesh.from_edit_mesh(me)

# ... edit bm.verts / bm.edges / bm.faces ...

bmesh.update_edit_mesh(me)
```
- Object must already be in Edit mode.
- Don't call `bm.free()` — it's owned by Edit mode.

### Object-mode pattern (generative scripts)
```python
import bmesh
me = obj.data
bm = bmesh.new()
bm.from_mesh(me)

# ... edits ...

bm.to_mesh(me)
bm.free()
me.update()
```
- Independent BMesh, full ownership, must `free()`.
- For pure-generation (build from scratch), skip `from_mesh` and just emit verts/edges/faces.

---

## BMesh Collections

- `bm.verts` — vertex sequence.
- `bm.edges` — edge sequence.
- `bm.faces` — face sequence.
- `bm.loops` — read-only loop access via faces (`f.loops`).

### Iteration
```python
for v in bm.verts:
    if v.select:
        v.co.z += 0.5
```

### Creation
```python
v1 = bm.verts.new((0, 0, 0))
v2 = bm.verts.new((1, 0, 0))
v3 = bm.verts.new((1, 1, 0))
f = bm.faces.new((v1, v2, v3))
```

### Removal
```python
bm.verts.remove(v)   # removing a vert removes incident edges/faces
bm.edges.remove(e)
bm.faces.remove(f)
```

### Lookup table — critical
After adding or removing geometry, index-based lookup (`bm.verts[i]`) is **invalid** until you call:
```python
bm.verts.ensure_lookup_table()
bm.edges.ensure_lookup_table()
bm.faces.ensure_lookup_table()
```
Forgetting this is the #1 BMesh footgun. Iteration (`for v in bm.verts`) is always safe; indexing is not.

### Indices
- `v.index`, `e.index`, `f.index` — but call `bm.verts.index_update()` first if you've mutated the sequence.

### Selection sync
```python
bm.select_flush(True)         # push vert-selection up to edges and faces
bm.select_flush_mode()        # sync to current select_mode
```

---

## `bmesh.ops` — Common Operators

`bmesh.ops` is the procedural counterpart to `bpy.ops.mesh.*`. Operators take a BMesh + geometry list + kwargs and return a dict of newly-created elements.

```python
import bmesh
ret = bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=2, use_grid_fill=True)
new_geom = ret["geom_inner"]
```

The catalog:

- **extrude_face_region** — `geom=[faces...]` → `geom` (mix of v/e/f). Then transform the returned verts.
- **extrude_edge_only** — extrude raw edges, no cap.
- **extrude_individual_faces** — like extrude_face_region but per-face.
- **subdivide_edges** — `edges`, `cuts`, `use_grid_fill`, `smooth`. Returns `geom_inner`, `geom_split`, `geom`.
- **bevel** — `geom=[edges or verts]`, `offset`, `segments`, `profile`, `affect` ('EDGES'|'VERTICES'), `clamp_overlap`.
- **inset_individual** — `faces`, `thickness`, `depth`, `use_even_offset`, `use_interpolate`.
- **inset_region** — `faces`, `thickness`, `depth`, `use_boundary`, `use_even_offset`.
- **remove_doubles** — `verts`, `dist`. Merge-by-distance.
- **triangulate** — `faces`, `quad_method`, `ngon_method`.
- **bridge_loops** — `edges` (must be a closed loop set). Joins two loops with quads.
- **pointmerge** — `verts`, `merge_co`. Collapse selection to one location.
- **dissolve_verts** — `verts`, `use_face_split`, `use_boundary_tear`.
- **dissolve_edges** — `edges`, `use_verts`, `use_face_split`.
- **dissolve_faces** — `faces`, `use_verts`.
- **mirror** — `geom`, `matrix`, `merge_dist`, `axis`, `mirror_u`, `mirror_v`. Returns mirrored geom.
- **recalc_face_normals** — `faces`. Outward-facing pass.
- **connect_verts** — `verts`. Drops new edges between selected verts on shared faces.
- **connect_verts_concave** — connect verts to split concave faces.
- **convex_hull** — `input` (verts). Returns hull geom + interior verts.
- **delete** — `geom`, `context`: 'VERTS' | 'EDGES' | 'FACES' | 'FACES_ONLY' | 'EDGES_FACES' | 'FACES_KEEP_BOUNDARY' | 'TAGGED_ONLY'.
- **duplicate** — `geom`. Returns `geom` (verts + edges + faces).
- **holes_fill** — `edges`, `sides`. Fill closed boundary edges with up-to-N-sided faces.
- **smooth_vert** — `verts`, `factor`, `use_axis_x/y/z`, `mirror_clip_x/y/z`.
- **spin** — `geom`, `cent`, `axis`, `dvec`, `angle`, `steps`. Lathe in Python.
- **transform** — `verts`, `matrix`, `space`. Apply a 4×4 to a vert set.
- **rotate** — `verts`, `cent`, `matrix`.
- **scale** — `vec`, `space`, `verts`.

Full list: `dir(bmesh.ops)` returns every op; signatures via `help(bmesh.ops.X)`.

---

## Direct Mesh Data Manipulation

When you don't need topology changes, you can write straight to `mesh` attributes without entering Edit mode or building a BMesh.

```python
me = obj.data
for v in me.vertices:
    v.co.z += 0.1
me.update()
```

- `mesh.vertices[i].co` — position. Mutable from Object mode.
- `mesh.vertices[i].normal` — read-only (recomputed by Blender).
- `mesh.edges[i].vertices` — pair of vert indices, immutable.
- `mesh.polygons[i].vertices` — n vert indices, immutable.
- `mesh.polygons[i].normal` — read-only.
- `mesh.uv_layers["UVMap"].data[loop_index].uv` — per-loop UV.

For bulk reads/writes the **foreach** API is dramatically faster than per-element Python:
```python
import numpy as np
co = np.empty(len(me.vertices) * 3, dtype=np.float32)
me.vertices.foreach_get("co", co)
co.shape = (-1, 3)
co[:, 2] += np.sin(co[:, 0])
me.vertices.foreach_set("co", co.ravel())
me.update()
```

**Constraint:** topology-changing edits (add/remove verts, change face vert counts) must go through BMesh or `mesh.from_pydata(verts, edges, faces)`.

---

## Custom Mesh Attributes

Named attributes attach to a *domain* (point/edge/face/corner) and have a *type*.

```python
attr = me.attributes.new(name="density", type='FLOAT', domain='POINT')
# write
import numpy as np
data = np.random.rand(len(me.vertices)).astype(np.float32)
attr.data.foreach_set("value", data)
```

**Domains:**
- `'POINT'` — per-vertex.
- `'EDGE'` — per-edge.
- `'FACE'` — per-polygon.
- `'CORNER'` — per-loop (per face-vertex).

**Types:** `'FLOAT'`, `'INT'`, `'FLOAT_VECTOR'`, `'FLOAT_COLOR'`, `'BYTE_COLOR'`, `'BOOLEAN'`, `'FLOAT2'`, `'INT8'`, `'QUATERNION'`.

The same attribute system stores UVs, vertex colors, vertex groups, and split normals — they're presented in dedicated UI but live in `mesh.attributes` under the hood.

**GN integration:** any custom attribute is readable in Geometry Nodes via *Named Attribute* and writable via *Store Named Attribute*. This is the bridge between Python modeling and procedural nodes.

---

## Normals

- **Shade Smooth / Shade Flat** — per-face shading flag. `bpy.ops.object.shade_smooth()` / `shade_flat()`.
- **Smooth by Angle (4.1+)** — Geometry Nodes modifier that splits shading at edges above an angle threshold. Replaces the *removed* `mesh.use_auto_smooth` / `mesh.auto_smooth_angle` properties. Add via `bpy.ops.object.shade_auto_smooth(angle=0.5236)` (30° default) or `bpy.ops.object.modifier_add_node_group(asset_library_type='ESSENTIALS', ...)`.
- **Custom Split Normals** — `mesh.use_auto_smooth` removed; custom normals are now stored as a corner-domain attribute. `mesh.normals_split_custom_set_from_vertices(per_vert_normals)` still works for setting from Python.
- **Weighted Normal modifier** — area/angle-weighted normals; fixes the "bevel shading dent" on hard-surface models. Place after Bevel.
- **Recalc outside** — `bpy.ops.mesh.normals_make_consistent(inside=False)` in Edit mode; `bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])` from a script.
- **Flip** — `bpy.ops.mesh.flip_normals()` or set `f.normal_flip()` on a BMFace.
- **Mark Sharp** — `bpy.ops.mesh.mark_sharp(clear=False, use_verts=False)` — flags edges as sharp; the Smooth-by-Angle modifier and Edge Split modifier respect this flag.

---

## Common Modeling Recipes

### 1. Rounded-edge cube (subdiv-friendly hard-surface chassis)
```
Cube → Bevel (width 0.05, segments 3, limit_method='ANGLE') → Subdivision Surface (levels 2)
```
Keep Bevel above Subsurf. Use Weighted Normal at the bottom if you see shading dents.

### 2. Inset + extrude greeble pattern
```python
# in edit mode, faces selected
bpy.ops.mesh.inset(thickness=0.05, use_individual=True)
bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0,0,0.02)})
```
Run twice for nested panel detail.

### 3. Curve-driven array (chain, rope, vine)
```
Mesh link → Array (count 30, relative offset X=1.0) → Curve (target = path)
```
Order matters: Array first, Curve second. Origin of the source mesh sits on the curve start.

### 4. Mirror with merge + clip + bisect
```
Mirror (axis X, use_mirror_merge True, merge_threshold 0.001, use_clip True, use_bisect_axis X True)
```
`use_bisect_axis` deletes geometry on the mirror side before mirroring — handy when sculpting brought verts across the seam.

### 5. Boolean cut + cleanup
```
Cutter object → Boolean (operation 'DIFFERENCE', solver 'EXACT', use_self True)
Apply, then in Edit mode:
  bpy.ops.mesh.select_all(action='SELECT')
  bpy.ops.mesh.dissolve_limited(angle_limit=0.087)   # 5°
  bpy.ops.mesh.tris_convert_to_quads()
```
Exact solver gives cleaner topology than Fast at the cost of speed.

### 6. Lattice deform for non-destructive blob shaping
- Add Lattice object, set divisions (e.g. 4×4×4).
- On mesh: Modifier → Lattice → target = lattice object.
- Edit lattice in Edit mode; mesh follows.

### 7. Subdiv-friendly topology guide
- All quads where possible.
- Edge loops support every feature — bevel needs 2 loops per edge.
- Avoid n-gons in deforming regions; they sub-divide unpredictably.
- 3-, 4-, 5-pole verts only. 6-pole pinches.

### 8. Hard-surface bevel weights
```python
# in edit mode, edge mode, edges selected
bpy.ops.transform.edge_bevelweight(value=1.0)
```
Then on the Bevel modifier set `limit_method='WEIGHT'`. Selectively bevels only flagged edges.

### 9. Procedural city block from a plane
```
Plane → Subdivide (N cuts) → Inset Individual (thickness 0.4) → Extrude (random Z per face via Random Transform or GN)
```
For variation use GN with a `Random Value` node feeding face-domain Extrude Mesh — keeps it non-destructive.

### 10. Vertex-group-driven displacement
```
Vertex group "noise" painted on a plane → Displace modifier
   texture: Image or Procedural noise
   vertex_group: "noise"
   strength: 0.5
```
Useful for masked terrain bumps without affecting flat zones.

### 11. Skin + Subsurf organic tube
```
Edge chain → Skin modifier (size via Ctrl+A in Edit mode) → Subdivision Surface (level 2)
```
Treat skin radii like a procedural metaball graph.

### 12. Generative mesh from scratch in BMesh
```python
import bmesh, bpy
me = bpy.data.meshes.new("Gen")
obj = bpy.data.objects.new("Gen", me)
bpy.context.collection.objects.link(obj)

bm = bmesh.new()
ring = [bm.verts.new((math.cos(t), math.sin(t), 0)) for t in np.linspace(0, 2*math.pi, 32, endpoint=False)]
for i in range(len(ring)):
    bm.edges.new((ring[i], ring[(i+1) % len(ring)]))
bm.faces.new(ring)
bm.normal_update()
bm.to_mesh(me)
bm.free()
```

---

## Common Footguns

1. **Modifier order wrong.** Bevel after Subsurf produces tiny chamfers on already-rounded edges, not the hard-edge softening you wanted. Bevel goes *before* Subsurf for hard-surface; *after* for stylized rounding.
2. **`remove_doubles` over-merging.** Default threshold 0.0001 m is usually safe; raise it and you'll fuse intentional close geometry (a bolt head into the plate it sits on). Always preview, never blanket-run on a whole mesh.
3. **Boolean → n-gons everywhere.** Exact solver leaves arbitrary-sided faces on the cut. Follow with `dissolve_limited` + `tris_convert_to_quads` or accept that downstream stages need to triangulate.
4. **BMesh edits without `ensure_lookup_table`.** After `bm.verts.new(...)`, `bm.verts[42]` raises or returns stale data. Call `ensure_lookup_table()` on every collection you mutated before indexing.
5. **Editing `obj.data` directly while in Edit mode.** Changes to `mesh.vertices[i].co` while Edit mode is open are masked by the live BMesh copy and lost on mode exit. Either exit Edit mode first or use `bmesh.from_edit_mesh`.
6. **Shade Smooth without angle setup → "soft but faceted" look.** Just calling `shade_smooth()` on a hard-surface mesh makes every face blend into its neighbours, ruining clean edges. In 4.1+ pair with `shade_auto_smooth(angle=...)`; in older files use the legacy auto-smooth toggle.
7. **Mirror misses with off-center origin.** Mirror modifier mirrors around the *object origin*. If the origin drifted (e.g. via `bpy.ops.object.origin_set`), the mirror axis no longer matches the model centerline. Either set origin to world-zero or assign a `mirror_object` empty.
8. **Decimate destroys UVs and vertex groups.** Collapse mode reshuffles topology; UVs come out smeared. For LODs that need clean UVs, retopo or use the *Planar* dissolve mode where possible.
9. **N-gons break Geometry Nodes downstream.** Many GN nodes operate per-corner or assume triangulated input. Triangulate (or at least quad-only) before feeding a GN modifier that does normal-sensitive work.
10. **Modifier order with shape keys.** Shape keys live on base mesh data; modifiers run *after* shape-key evaluation. Applying a deform modifier on a mesh with shape keys is blocked. Generative modifiers (Array, Mirror, Subsurf) still work but the shape-key delta only affects the base instance.
11. **`mesh.from_pydata` doesn't auto-calc normals or update.** After bulk-building geometry call `mesh.update(calc_edges=True)` and `mesh.validate()`.
12. **Apply-on-instance.** Applying a modifier on one of N linked-duplicate objects (`Alt+D` instances) silently un-links the mesh data. Use `obj.data = obj.data.copy()` first if that's not what you want.
13. **The auto-smooth removal trap (4.1+).** Old scripts that set `mesh.use_auto_smooth = True` and `mesh.auto_smooth_angle = math.radians(30)` silently no-op. Replace with `bpy.ops.object.shade_auto_smooth(angle=math.radians(30))` while the object is active.
14. **Operator context errors.** `bpy.ops.mesh.*` outside Edit mode raises `RuntimeError: Operator bpy.ops.mesh.X.poll() failed`. Either switch mode or use BMesh.
15. **Subsurf + n-gon = warped surface.** Catmull-Clark assumes quads. N-gons get auto-triangulated under the hood with unpredictable seams.

---

## Cross-references

- `[[BLENDER_PYTHON_API]]` — `bpy.ops` calling conventions, context overrides, depsgraph.
- `[[BLENDER_DATA_MODEL]]` — how `bpy.data.meshes`, objects, and collections relate.
- `[[BLENDER_GEOMETRY_NODES]]` — procedural modeling via node trees.
- `[[BLENDER_SCULPTING]]` — Multires, dyntopo, sculpt brushes, voxel remesh.
- `[[BLENDER_MATERIALS]]` — UVs, shading, attribute hookups for shaders.
