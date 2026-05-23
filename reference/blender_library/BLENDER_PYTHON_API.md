---
title: Blender Python API (bpy) Reference
version: 1.0
last_updated: 2026-05-22
status: live
scope: bpy module reference — data model, context, ops, properties, datablock access, common patterns, footguns. The MCP connector wraps this surface; everything reachable here is reachable via the connector.
dependencies: BLENDER_LIBRARY_INDEX.md, BLENDER_DATA_MODEL.md, BLENDER_UI_VOCABULARY.md
---

# BLENDER PYTHON API (bpy) — REFERENCE

`bpy` is Blender's embedded Python API. It exposes the entire scene graph, every datablock, every operator, every property, and every UI region as Python objects. The Blender Foundation's MCP connector is a thin transport over this surface — anything you can do in the Scripting workspace's Python console, the connector can do. Calls succeed or fail based on the same context, datablock, and mode rules that govern in-app scripting.

This file is the foundation reference. See `[[BLENDER_DATA_MODEL]]` for the deeper datablock taxonomy, `[[BLENDER_UI_VOCABULARY]]` for in-app term mappings, `[[BLENDER_GEOMETRY_NODES]]` and `[[BLENDER_SHADER_NODES]]` for node-tree specifics.

**Core facts:**
- Target Blender 4.2 LTS minimum; 4.5 LTS preferred. Both are stable until at least 2026-2027.
- Blender 4.2 ships Python 3.11. Blender 4.5 also ships 3.11. Do not assume 3.12+ features.
- `bpy` is single-threaded. All scene-graph mutations must run on the main thread. Background threads can compute but cannot touch `bpy.data` or operators safely.
- Almost every call is context-dependent. The same operator that works in the 3D Viewport will fail in headless / script mode unless you supply a context override.
- The undo stack records most data mutations. Heavy scripts can blow up undo memory — disable undo for batch work with `bpy.context.preferences.edit.use_global_undo = False` when appropriate, restore after.
- Datablock names are unique per collection. New blocks with colliding names auto-suffix `.001`, `.002`, etc. This is the #1 source of "I added a cube but my old code can't find it" bugs.
- Operators (`bpy.ops.*`) are convenient but brittle. The data API (`bpy.data.*`) is the durable surface for scripting.
- Mode matters. Object mode, Edit mode, Sculpt mode, Pose mode each gate which operators are valid. `bpy.context.mode` reports current mode; switch with `bpy.ops.object.mode_set(mode='EDIT')`.
- Evaluated vs original: `obj` is the original datablock; `obj.evaluated_get(depsgraph)` returns the post-modifier, post-driver, post-animation version. For reading "final" geometry, always go through the depsgraph.
- All IDs (datablocks) share a `name`, `users`, `use_fake_user`, `library`, `tag` interface. Knowing the ID model lets you script consistently across meshes, materials, worlds, node trees, images, etc.

---

## 1. The Five Top-Level Submodules

`bpy` is mostly a façade for five submodules. Pick the right one for the job:

- **`bpy.data`** — the datablock store. Every mesh, object, material, image, scene, world, action, node tree, etc. lives under here. Use for *creation*, *deletion*, *lookup by name*, *iteration*. Stable. Context-free.
- **`bpy.context`** — the current state of the editor. What's active, what's selected, which area / region / scene the call is happening in. Use for *reading current state*. Required as an implicit input to most operators.
- **`bpy.types`** — the type system. Every class (Object, Mesh, Material, ID, Operator, Panel, PropertyGroup) lives here. Use for *introspection*, *registering custom properties*, *defining new operators or panels*.
- **`bpy.ops`** — operators. Anything the user can do from a menu — add a cube, extrude a face, render, export, bake — has a matching `bpy.ops.*` call. Use sparingly. Prefer `bpy.data` when both paths exist.
- **`bpy.props`** — property definition functions. Used at *class definition time* to declare typed properties on custom PropertyGroups or registered datablock subclasses. Not for setting values; for declaring schemas.

Two more worth knowing:
- **`bpy.app`** — version info, handlers, timers, drivers namespace, translations.
- **`bpy.utils`** — registration helpers, preset directories, blend file path helpers.

---

## 2. bpy.data — The Data API

`bpy.data` is the canonical, context-independent way to reach every datablock in the open .blend file. Each datablock type has a top-level collection:

- `bpy.data.objects` — all Object datablocks (the scene-graph nodes that wrap meshes/lights/cameras/empties/etc.)
- `bpy.data.meshes` — Mesh datablocks (geometry, separate from objects)
- `bpy.data.materials`
- `bpy.data.images`
- `bpy.data.textures`
- `bpy.data.node_groups` — geometry node trees, shader node groups, compositor node groups
- `bpy.data.lights`
- `bpy.data.cameras`
- `bpy.data.scenes`
- `bpy.data.worlds`
- `bpy.data.collections` — Outliner collections (the 2.8+ replacement for layers/groups)
- `bpy.data.actions` — animation actions
- `bpy.data.armatures`
- `bpy.data.curves`
- `bpy.data.metaballs`
- `bpy.data.fonts`
- `bpy.data.sounds`
- `bpy.data.movieclips`
- `bpy.data.libraries` — linked .blend files
- `bpy.data.brushes`
- `bpy.data.particles`
- `bpy.data.linestyles`
- `bpy.data.workspaces`
- `bpy.data.screens`
- `bpy.data.window_managers`
- `bpy.data.texts` — text datablocks (scripts, drivers)
- `bpy.data.volumes`
- `bpy.data.grease_pencils` (legacy 2.x grease pencil)
- `bpy.data.grease_pencils_v3` (Blender 4.3+ rewrite)
- `bpy.data.hair_curves`
- `bpy.data.pointclouds`
- `bpy.data.lightprobes`
- `bpy.data.lattices`
- `bpy.data.speakers`
- `bpy.data.cache_files`
- `bpy.data.masks`
- `bpy.data.shape_keys`
- `bpy.data.paint_curves`
- `bpy.data.palettes`
- `bpy.data.bl_rna` — introspection

**Lookup by name:**
```python
cube = bpy.data.objects["Cube"]                # KeyError if missing
cube = bpy.data.objects.get("Cube")            # None if missing — prefer this
cube = bpy.data.objects.get("Cube", default_obj)
```

Names are case-sensitive and exact. The `.get()` form is safer for scripts that may run repeatedly.

**Membership / iteration:**
```python
if "Cube" in bpy.data.objects: ...
for obj in bpy.data.objects:
    print(obj.name, obj.type)
len(bpy.data.materials)
```

**The `.new()` pattern** — every collection that supports creation has `.new(name, ...)`:
```python
me  = bpy.data.meshes.new(name="MyMesh")           # empty mesh
obj = bpy.data.objects.new(name="MyObj", object_data=me)
mat = bpy.data.materials.new(name="MyMat")
img = bpy.data.images.new(name="MyImg", width=1024, height=1024)
ng  = bpy.data.node_groups.new(name="MyTree", type='ShaderNodeTree')
col = bpy.data.collections.new(name="MyCol")
```

Newly created objects are **not** linked to any scene/collection. You must link them, or they won't appear:
```python
bpy.context.scene.collection.objects.link(obj)     # add to scene root
# or: bpy.data.collections["MyCol"].objects.link(obj)
```

**The `.remove()` pattern:**
```python
bpy.data.objects.remove(obj, do_unlink=True)
bpy.data.meshes.remove(me)
bpy.data.materials.remove(mat)
```

`do_unlink=True` (default `True` in 4.x for most types) removes the datablock from every collection / scene / parent that references it. Pass `False` only if you're certain nothing references it; otherwise you'll leak references that break on save/reload.

**Orphan data and purge:**
A datablock with zero users is "orphan" — it survives in memory and will save into the .blend unless you purge or mark with no fake user. Purge programmatically:
```python
bpy.ops.outliner.orphans_purge(
    do_local_ids=True,
    do_linked_ids=True,
    do_recursive=True
)
# Or, since 3.x, the data-level call:
bpy.data.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
```

The recursive flag matters — purging a mesh may free a material whose only user was that mesh; without recursion that material stays.

**Fake users:**
A datablock with `use_fake_user = True` always has at least one user (a synthetic one) and won't be purged. UI button: the shield icon. Use sparingly — fake-user proliferation is its own pain.

---

## 3. bpy.context — The Context API

`bpy.context` reflects "what is happening right now in the editor." It's read-only in most respects; you don't assign to it, you override it.

**Common members:**
- `bpy.context.scene` — the active Scene datablock
- `bpy.context.view_layer` — the active ViewLayer within the scene
- `bpy.context.window` / `window_manager` / `screen` / `workspace` / `area` / `region` / `space_data`
- `bpy.context.active_object` — the single "active" object (yellow outline in viewport)
- `bpy.context.object` — alias for `active_object` in most contexts
- `bpy.context.selected_objects` — list of selected objects in current view layer
- `bpy.context.selected_editable_objects` — selected, not from a linked library
- `bpy.context.visible_objects`
- `bpy.context.mode` — `'OBJECT'`, `'EDIT_MESH'`, `'SCULPT'`, `'POSE'`, `'PAINT_WEIGHT'`, etc.
- `bpy.context.tool_settings`
- `bpy.context.collection` — the active collection (may differ from scene root)
- `bpy.context.scene.collection` — always the scene's root collection
- `bpy.context.preferences` — `bpy.context.preferences.edit`, `view`, `addons`, etc.
- `bpy.context.evaluated_depsgraph_get()` — returns a `Depsgraph` for evaluated geometry lookups

**Headless / script gotcha:**
When Blender runs `--background` or a script runs from the CLI before any window opens, many context members are `None`:
- `bpy.context.area` → None
- `bpy.context.region` → None
- `bpy.context.space_data` → None
- `bpy.context.selected_objects` → may be `[]` even when scene has objects

Operators that need a viewport area (anything UI-bound — view rotation, selection ops in the 3D view) will fail with a `RuntimeError: Operator bpy.ops.X.Y.poll() failed, context is incorrect`.

**`bpy.context.copy()`** — returns a dict snapshot of the current context for use as an override basis:
```python
ctx = bpy.context.copy()
ctx["selected_objects"] = [obj_a, obj_b]
ctx["active_object"]    = obj_a
```

**`bpy.context.temp_override(**overrides)`** (Blender 3.2+, required in 4.x) — the canonical way to invoke an operator under a custom context:
```python
with bpy.context.temp_override(
    selected_objects=[obj_a, obj_b],
    active_object=obj_a,
    scene=bpy.context.scene,
):
    bpy.ops.object.delete()
```

The older pattern of passing a context dict as the first positional argument to `bpy.ops.*` is **deprecated** since 3.2 and removed in 4.x. Always use `temp_override`.

**Finding a valid area for viewport ops** (when running headless or from a non-3D-view region):
```python
def find_view3d_override():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        return dict(
                            window=window,
                            screen=window.screen,
                            area=area,
                            region=region,
                            scene=bpy.context.scene,
                        )
    return None
```

---

## 4. bpy.types — The Type System

Every Python-visible object in Blender is an instance of a class registered under `bpy.types`. The hierarchy roughly:

- `bpy_struct` — base of everything RNA-exposed
- `ID` — the datablock base class. Mesh, Object, Material, NodeTree, Image, Scene, etc. all inherit from ID.
- `PropertyGroup` — user-defined property containers, attachable to IDs as custom properties.
- `Operator`, `Panel`, `Menu`, `Header`, `UIList` — UI / behavior registration classes.

**ID common attributes** (inherited by every datablock):
- `name` (string, unique within its collection)
- `name_full` (includes library prefix when linked)
- `users` (read-only int)
- `use_fake_user` (bool)
- `library` (Library or None)
- `tag` (bool; volatile mark-and-sweep flag for scripts)
- `is_embedded_data` (bool)
- `override_library` (Library override info or None)
- `original` (the original datablock when this one is evaluated)
- `evaluated_get(depsgraph)` (returns the evaluated copy)
- `copy()` (deep copy — creates a new datablock with `.001` suffix)
- `user_remap(other)` (point every reference to self at `other`)
- `user_clear()` (set users to zero, marking orphan)
- `make_local()` (convert linked-from-library to local)
- `asset_mark()` / `asset_clear()` (Asset Browser integration)

**RNA introspection** — every instance has a `bl_rna`:
```python
obj.bl_rna.properties.keys()                  # all property names
obj.bl_rna.properties["location"].description # docstring for the location prop
obj.bl_rna.functions.keys()                   # callable methods exposed via RNA
type(obj).__doc__                             # class docstring
```

This is how you discover what a datablock can do without leaving Python. Combined with `dir(obj)`, it's the agent's primary self-documentation surface.

**Subclassing — registering custom types:**
```python
class MyProps(bpy.types.PropertyGroup):
    intensity: bpy.props.FloatProperty(default=1.0)

bpy.utils.register_class(MyProps)
bpy.types.Scene.my_props = bpy.props.PointerProperty(type=MyProps)

# Then: bpy.context.scene.my_props.intensity = 2.0
```

Always unregister symmetrically (`bpy.utils.unregister_class`) when an addon disables.

---

## 5. bpy.ops — Operators

Operators are the procedural verbs Blender exposes — exactly what a menu click runs. Convention: `bpy.ops.{module}.{operator}(**kwargs)`. Examples:

- `bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 0))`
- `bpy.ops.object.delete(use_global=False)`
- `bpy.ops.object.modifier_add(type='SUBSURF')`
- `bpy.ops.render.render(write_still=True)`
- `bpy.ops.export_scene.gltf(filepath="/tmp/out.glb")`

**Return value** — a Python set with one of:
- `{'FINISHED'}` — succeeded
- `{'CANCELLED'}` — operator decided not to run
- `{'PASS_THROUGH'}` — modal operator letting events through
- `{'RUNNING_MODAL'}` — modal operator started
- `{'INTERFACE'}` — UI-only

**Poll failure** — every operator has a `poll()` method that checks if the context is valid. If poll fails:
```
RuntimeError: Operator bpy.ops.mesh.primitive_cube_add.poll() failed, context is incorrect
```
This means the operator's required context wasn't met — wrong mode, no active object, no valid area, etc. Fix with `temp_override` or by switching mode first.

**Common context requirements:**
- Mesh edit ops require `mode == 'EDIT_MESH'` and an active mesh object.
- Selection ops require objects to actually be selected via `obj.select_set(True)`.
- Modifier ops require an active object that supports modifiers.
- Render ops require a scene with a render engine set.

**When to avoid ops:**
- When a data-API path exists. `bpy.data.objects.remove(obj)` is more robust than `bpy.ops.object.delete()`.
- When the operator triggers UI side effects (selection state changes, mode flips) you don't want.
- When you're running in `--background` and the operator needs a 3D view.
- When you're inside a tight loop — ops add to the undo stack and can be slow.

**When ops are unavoidable:**
- Mesh editing primitives that have no clean data-API equivalent (`bpy.ops.mesh.extrude_region_move`, `bpy.ops.mesh.bevel`).
- Modal interactive operators.
- File I/O for non-blend formats (import / export ops).
- Render invocation.

Always prefer: data API → `bmesh` → `bpy.ops` in that order.

---

## 6. bpy.props — Property Definition

Used in *class bodies* to declare typed properties. Not for setting values on existing instances; for defining schemas on subclasses.

**Functions:**
- `IntProperty(default, min, max, soft_min, soft_max, step, description, subtype, options)`
- `FloatProperty(...)` — subtypes: `'NONE'`, `'DISTANCE'`, `'ANGLE'`, `'FACTOR'`, `'PERCENTAGE'`, `'TIME'`, `'COLOR'`, `'COLOR_GAMMA'`, `'UNSIGNED'`
- `BoolProperty(default, description)`
- `StringProperty(default, maxlen, subtype)` — subtypes: `'FILE_PATH'`, `'DIR_PATH'`, `'BYTE_STRING'`, `'PASSWORD'`
- `EnumProperty(items, default, description)` — `items` is a list of `(identifier, name, description)` or `(identifier, name, description, icon, number)` tuples, or a callback returning that list
- `PointerProperty(type, poll)` — typed reference to another ID or PropertyGroup
- `CollectionProperty(type)` — typed list of PropertyGroups
- `FloatVectorProperty(size, default, subtype)` — subtypes: `'COLOR'`, `'TRANSLATION'`, `'DIRECTION'`, `'VELOCITY'`, `'ACCELERATION'`, `'MATRIX'`, `'EULER'`, `'QUATERNION'`, `'AXISANGLE'`, `'XYZ'`
- `IntVectorProperty(...)`
- `BoolVectorProperty(...)`

**Declaration style — annotations** (4.x mandatory):
```python
class MyPanel(bpy.types.PropertyGroup):
    intensity: bpy.props.FloatProperty(name="Intensity", default=1.0)
    color: bpy.props.FloatVectorProperty(subtype='COLOR', size=4, default=(1,1,1,1))
    mode: bpy.props.EnumProperty(items=[
        ('A', "Alpha", ""),
        ('B', "Beta",  ""),
    ])
```

The annotation syntax (`name: bpy.props.FloatProperty(...)`) is required since 2.8. Don't use class-body assignment (`name = bpy.props.FloatProperty(...)`) — Blender will warn and the property may not register correctly.

**Attaching to existing types** — adds custom properties to a built-in datablock:
```python
bpy.types.Scene.my_intensity = bpy.props.FloatProperty(default=1.0)
# usage: bpy.context.scene.my_intensity = 0.5
```

These persist in the .blend file. Remove on unregister:
```python
del bpy.types.Scene.my_intensity
```

**Update callbacks:**
```python
def on_intensity_change(self, context):
    print("changed to", self.intensity)

bpy.types.Scene.my_intensity = bpy.props.FloatProperty(
    default=1.0, update=on_intensity_change
)
```

The callback fires on every value change, including from drivers and animation evaluation — keep it cheap.

---

## 7. Datablock (ID) Model

Every datablock obeys these rules:

**Uniqueness within collection.** `bpy.data.objects["Cube"]` is one specific Object. You can't have two objects named "Cube". On creation, conflicting names get `.001`, `.002`, etc. appended.

**Names are not stable references.** If a user (or another script) renames the object, your cached `obj` variable still works (the reference is to the Python object, not the name), but `bpy.data.objects["Cube"]` will fail. Cache the Python reference, not the name string.

**Linking vs appending:**
- *Link* (`bpy.ops.wm.link`) — datablock points to an external .blend; read-only locally. Edits must happen in the source file.
- *Append* (`bpy.ops.wm.append`) — copies the datablock into this .blend; fully local and editable.

At the data level:
```python
with bpy.data.libraries.load("/path/to/asset.blend", link=True) as (data_from, data_to):
    data_to.objects = data_from.objects   # link all objects
# After the with block, objects are loaded (linked or appended depending on `link`).
```

**Library overrides** — a 2.9+ mechanism for editing a linked datablock locally without breaking the link. Use `obj.override_create()` or `make_local()`. The override stores a delta against the linked original. Library override is the modern alternative to fully-appending an asset when you want updates to flow through.

**`use_fake_user`** — sets a synthetic user count of 1. Without it, a datablock with no scene/material/etc. referencing it is purged on save. Use for utility node groups, shared materials, etc. that aren't currently linked anywhere.

**`user_remap(other)`** — atomically redirect every reference to this datablock so it points at `other` instead. Useful for swapping out a mesh, material, or node group everywhere it's used.

**`copy()`** — produces a new datablock with the same data, `.001` suffix. Used for duplication. Be careful with this in loops: a script that calls `obj.copy()` 100 times creates 100 distinct datablocks. If you wanted instances (shared data), set `target.data = source.data` instead — multiple objects pointing at one mesh.

**Single-user vs multi-user data:**
- Object → Mesh is many-to-one. Two objects can share a Mesh. Edits to the mesh affect both objects.
- Material → NodeTree is one-to-one for materials (the node tree is embedded in the material) but Material is many-to-Mesh-slot.
- To break sharing: `obj.data = obj.data.copy()` makes a single-user mesh.

---

## 8. Common Patterns

Paste-ready snippets covering the most-asked tasks.

**Create an object and link it to the scene:**
```python
import bpy
me  = bpy.data.meshes.new("MyMesh")
obj = bpy.data.objects.new("MyObj", me)
bpy.context.scene.collection.objects.link(obj)
```

**Delete an object cleanly (data API, robust):**
```python
obj = bpy.data.objects.get("MyObj")
if obj is not None:
    bpy.data.objects.remove(obj, do_unlink=True)
```

**Delete via op (requires selection state):**
```python
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)
bpy.context.view_layer.objects.active = obj
bpy.ops.object.delete()
```

**Switch modes:**
```python
bpy.context.view_layer.objects.active = obj    # operator needs active object
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.object.mode_set(mode='OBJECT')
```

**Select / deselect:**
```python
obj.select_set(True)
obj.select_set(False)
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.object.select_all(action='SELECT')
```

**Get / set transforms:**
```python
obj.location       = (1.0, 0.0, 2.0)
obj.rotation_euler = (0.0, 0.0, 1.5708)
obj.scale          = (2.0, 2.0, 2.0)

import mathutils
obj.matrix_world = mathutils.Matrix.Translation((5, 0, 0))
```

**Iterate mesh vertices (read-only, object mode):**
```python
me = obj.data
for v in me.vertices:
    print(v.index, v.co.x, v.co.y, v.co.z)
```

**Modify mesh from object mode (no edit-mode toggle):**
```python
me = obj.data
me.vertices[0].co.z += 1.0
me.update()                 # recompute normals etc.
```

**Create a material and assign to active object:**
```python
mat = bpy.data.materials.new(name="MyMat")
mat.use_nodes = True
if obj.data.materials:
    obj.data.materials[0] = mat
else:
    obj.data.materials.append(mat)
```

**Add a Principled BSDF and connect to Material Output:**
```python
mat = bpy.data.materials["MyMat"]
nt  = mat.node_tree
nt.nodes.clear()
out = nt.nodes.new(type='ShaderNodeOutputMaterial')
out.location = (300, 0)
bsdf = nt.nodes.new(type='ShaderNodeBsdfPrincipled')
bsdf.location = (0, 0)
nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
```

**Add an image texture and load a file:**
```python
img = bpy.data.images.load("/path/to/tex.png")
tex_node = nt.nodes.new(type='ShaderNodeTexImage')
tex_node.image = img
nt.links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])
```

**Add a modifier and configure:**
```python
mod = obj.modifiers.new(name="Subdivision", type='SUBSURF')
mod.levels = 2
mod.render_levels = 3
```

**Set render output and render current frame:**
```python
scn = bpy.context.scene
scn.render.engine             = 'CYCLES'           # or 'BLENDER_EEVEE_NEXT' in 4.2+
scn.render.resolution_x       = 1920
scn.render.resolution_y       = 1080
scn.render.fps                = 30
scn.render.filepath           = "/tmp/render_"
scn.render.image_settings.file_format = 'PNG'
bpy.ops.render.render(write_still=True)
```

**Render an animation:**
```python
scn.frame_start = 1
scn.frame_end   = 120
bpy.ops.render.render(animation=True)
```

**List all object names:**
```python
for o in bpy.context.scene.objects:
    print(o.name)
```

**Create an empty:**
```python
empty = bpy.data.objects.new("MyEmpty", None)
empty.empty_display_type = 'PLAIN_AXES'
bpy.context.scene.collection.objects.link(empty)
```

**Parent one object to another:**
```python
child.parent = parent
child.matrix_parent_inverse = parent.matrix_world.inverted()
```

**Add a keyframe:**
```python
obj.location = (0, 0, 0)
obj.keyframe_insert(data_path="location", frame=1)
obj.location = (5, 0, 0)
obj.keyframe_insert(data_path="location", frame=60)
```

**Save the file:**
```python
bpy.ops.wm.save_as_mainfile(filepath="/tmp/out.blend")
```

**Export glTF:**
```python
bpy.ops.export_scene.gltf(filepath="/tmp/out.glb", export_format='GLB')
```

**Bake an action to keyframes (visual transforms):**
```python
bpy.ops.nla.bake(
    frame_start=1, frame_end=120,
    only_selected=True,
    visual_keying=True,
    clear_constraints=False,
    bake_types={'OBJECT'},
)
```

**Create and link a new collection:**
```python
col = bpy.data.collections.new("Trees")
bpy.context.scene.collection.children.link(col)
col.objects.link(obj)
```

---

## 9. BMesh Basics

`bpy.data.meshes` exposes a Mesh's verts/edges/faces as flat arrays, fine for reading and small modifications. For **topology edits** (extrude, subdivide, dissolve, bevel, merge by distance, etc.) at the data level, use `bmesh`.

**Two patterns:**

**A. Standalone BMesh (edit mesh data outside of edit mode):**
```python
import bmesh
bm = bmesh.new()
bm.from_mesh(obj.data)              # copy mesh into bm

# ... edit bm.verts, bm.edges, bm.faces, or use bmesh.ops.* ...

bm.to_mesh(obj.data)                 # write back
bm.free()
obj.data.update()
```

**B. Live edit-mode BMesh (when the object is currently in edit mode):**
```python
import bmesh
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(obj.data)

# ... edits ...

bmesh.update_edit_mesh(obj.data)     # do NOT call bm.free() in this case
```

**Element access:**
```python
for v in bm.verts: ...
for e in bm.edges: ...
for f in bm.faces: ...
# index lookup requires ensure:
bm.verts.ensure_lookup_table()
v0 = bm.verts[0]
```

After adding/removing elements, indices invalidate — call `ensure_lookup_table()` again before indexing.

**bmesh.ops.*** — the standalone topology operators (different from `bpy.ops`):
```python
bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=2, use_grid_fill=True)
bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.1, segments=2, affect='EDGES')
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
```

These work directly on the BMesh — fast, no operator context required.

**Always free standalone BMeshes** (`bm.free()`) — they hold memory outside Python's GC.

---

## 10. Drivers and Animation API

**F-Curves** are the underlying animation primitive. Keyframes are points on F-Curves. Drivers are F-Curves whose value is computed from a Python expression rather than interpolated keyframes.

**Add a driver:**
```python
fcurve = obj.driver_add("location", 2)        # Z axis of location
drv    = fcurve.driver
drv.type = 'SCRIPTED'                          # or 'AVERAGE', 'SUM', 'MIN', 'MAX'
drv.expression = "sin(frame / 10.0) * 2"
```

Empty array indices for whole-property drivers:
```python
fcurve = obj.driver_add("hide_render")        # boolean, no index
```

**Driver variables** — feed external values into the expression:
```python
var = drv.variables.new()
var.name = "src_x"
var.type = 'SINGLE_PROP'
target = var.targets[0]
target.id_type = 'OBJECT'
target.id = bpy.data.objects["Source"]
target.data_path = "location.x"

drv.expression = "src_x * 2"
```

Variable types:
- `'SINGLE_PROP'` — any single property path on any ID
- `'TRANSFORMS'` — convenient access to an object's transform channels (location/rotation/scale, world/local space)
- `'ROTATION_DIFF'` — angle between two bones
- `'LOC_DIFF'` — distance between two objects/bones
- `'CONTEXT_PROP'` — Blender 3.0+ — read from active scene / active view layer

**Remove a driver:**
```python
obj.driver_remove("location", 2)
```

**Why drivers over keyframes for parametric work:**
Keyframes bake a value at a frame. Drivers compute a value at every frame from the current scene state, so they react to live changes (other object transforms, custom properties, scene time). For audio-reactive, procedural, or constraint-style relationships, drivers are the right tool.

**Direct F-Curve manipulation** (for explicit keyframe authoring):
```python
action = obj.animation_data.action      # may need: obj.animation_data_create()
fc = action.fcurves.find("location", index=0)
for kp in fc.keyframe_points:
    print(kp.co.x, kp.co.y)             # (frame, value)
```

---

## 11. Node-Tree Manipulation

Three node-tree flavors share the same Python interface but live in different places:

- **Shader node trees** — attached to a Material (`material.node_tree`), a World (`world.node_tree`), or a Light (`light.node_tree`). Type id: `'ShaderNodeTree'`.
- **Geometry node trees** — `bpy.data.node_groups` of type `'GeometryNodeTree'`. Attached to a Geometry Nodes modifier (`modifier.node_group = ...`).
- **Compositor node trees** — `scene.node_tree` when `scene.use_nodes = True`. Type id: `'CompositorNodeTree'`.

**Create / access:**
```python
mat.use_nodes = True                # ensures mat.node_tree exists
tree = mat.node_tree

gn_tree = bpy.data.node_groups.new("MyGN", 'GeometryNodeTree')
```

**Add a node:**
```python
n = tree.nodes.new(type='ShaderNodeBsdfPrincipled')
n.location = (0, 0)
n.label    = "Main"                  # user-visible label
n.name     = "main_bsdf"             # programmatic id
```

Common shader node types: `ShaderNodeOutputMaterial`, `ShaderNodeBsdfPrincipled`, `ShaderNodeBsdfTransparent`, `ShaderNodeMixShader`, `ShaderNodeTexImage`, `ShaderNodeTexNoise`, `ShaderNodeMapping`, `ShaderNodeTexCoord`, `ShaderNodeRGB`, `ShaderNodeValue`, `ShaderNodeMath`, `ShaderNodeMixRGB` (deprecated 3.4+) / `ShaderNodeMix`, `ShaderNodeNormalMap`, `ShaderNodeBump`, `ShaderNodeEmission`, `ShaderNodeFresnel`, `ShaderNodeLayerWeight`.

Common geometry node types: `GeometryNodeInputPosition`, `GeometryNodeSetPosition`, `GeometryNodeMeshCube`, `GeometryNodeMeshSubdivide`, `GeometryNodeInstanceOnPoints`, `GeometryNodeJoinGeometry`, `GeometryNodeGroupInput`, `GeometryNodeGroupOutput`, `GeometryNodeProximity`, `GeometryNodeNoiseTexture`.

Common compositor node types: `CompositorNodeRLayers`, `CompositorNodeComposite`, `CompositorNodeViewer`, `CompositorNodeBlur`, `CompositorNodeGlare`, `CompositorNodeColorBalance`, `CompositorNodeMixRGB`.

**Link sockets:**
```python
tree.links.new(node_a.outputs['Color'], node_b.inputs['Base Color'])
# or by index:
tree.links.new(node_a.outputs[0], node_b.inputs[0])
```

`tree.links.remove(link)` to remove. Iterate `tree.links` to inspect.

**Set socket default value** (when no link is feeding the socket):
```python
bsdf.inputs['Roughness'].default_value = 0.3
bsdf.inputs['Base Color'].default_value = (0.8, 0.2, 0.1, 1.0)   # RGBA
```

**Remove a node:**
```python
tree.nodes.remove(node)
```

**Group I/O for node groups:**
```python
ng = bpy.data.node_groups.new("MyGroup", 'ShaderNodeTree')
# 4.x uses ng.interface API
ng.interface.new_socket(name="In Color", in_out='INPUT',  socket_type='NodeSocketColor')
ng.interface.new_socket(name="Out",      in_out='OUTPUT', socket_type='NodeSocketColor')
```

The `interface` API replaced the older `inputs` / `outputs` collection-on-NodeTree pattern (which was deprecated in 4.0 and removed in 4.x onwards). See `[[BLENDER_GEOMETRY_NODES]]` for the full migration.

---

## 12. Rendering From Script

**Engine selection:**
```python
scn = bpy.context.scene
scn.render.engine = 'CYCLES'                    # path tracer
scn.render.engine = 'BLENDER_EEVEE_NEXT'        # Blender 4.2+ EEVEE rewrite
scn.render.engine = 'BLENDER_WORKBENCH'         # viewport / solid
```

Note: `'BLENDER_EEVEE'` (the old EEVEE) was removed in 4.2 in favor of `'BLENDER_EEVEE_NEXT'`. Pre-4.2 scripts that reference `'BLENDER_EEVEE'` will silently fail or fall back.

**Resolution and frame:**
```python
scn.render.resolution_x          = 1920
scn.render.resolution_y          = 1080
scn.render.resolution_percentage = 100
scn.render.fps                   = 30
scn.frame_start = 1
scn.frame_end   = 240
scn.frame_current = 60
```

**Output:**
```python
scn.render.filepath = "/path/to/out_"            # trailing underscore — Blender appends frame number
scn.render.image_settings.file_format = 'PNG'    # 'JPEG', 'OPEN_EXR', 'OPEN_EXR_MULTILAYER', 'TIFF', 'FFMPEG', etc.
scn.render.image_settings.color_mode  = 'RGBA'
scn.render.image_settings.color_depth = '16'
```

For video output:
```python
scn.render.image_settings.file_format = 'FFMPEG'
scn.render.ffmpeg.format              = 'MPEG4'
scn.render.ffmpeg.codec               = 'H264'
scn.render.ffmpeg.constant_rate_factor = 'HIGH'
```

**Invoke render:**
```python
bpy.ops.render.render(write_still=True)         # current frame, write file
bpy.ops.render.render(animation=True)           # whole frame range
```

Without `write_still=True`, the render happens but no file is written.

**Cycles-specific:**
```python
scn.cycles.samples       = 128
scn.cycles.use_denoising = True
scn.cycles.device        = 'GPU'                 # or 'CPU'
```

**EEVEE Next-specific:**
```python
scn.eevee.taa_render_samples = 64
scn.eevee.use_raytracing     = True              # 4.2+ ray tracing
```

---

## 13. The Handlers System

`bpy.app.handlers` lets scripts hook into Blender's event loop. Each handler is a Python list of callables; append your function to subscribe.

**Common handlers:**
- `bpy.app.handlers.load_pre(scene)` — before file load
- `bpy.app.handlers.load_post(scene)` — after file load
- `bpy.app.handlers.save_pre(scene)` / `save_post(scene)`
- `bpy.app.handlers.frame_change_pre(scene, depsgraph)` — before frame change (playback or scrub)
- `bpy.app.handlers.frame_change_post(scene, depsgraph)` — after frame change
- `bpy.app.handlers.render_init(scene)` — before render starts
- `bpy.app.handlers.render_pre(scene)` — before each frame's render
- `bpy.app.handlers.render_post(scene)` — after each frame's render
- `bpy.app.handlers.render_cancel(scene)` / `render_complete(scene)`
- `bpy.app.handlers.depsgraph_update_pre(scene)` / `depsgraph_update_post(scene)`
- `bpy.app.handlers.undo_pre(scene)` / `undo_post(scene)`
- `bpy.app.handlers.redo_pre(scene)` / `redo_post(scene)`

**Registering:**
```python
def on_frame(scene, depsgraph):
    print("frame", scene.frame_current)

bpy.app.handlers.frame_change_post.append(on_frame)
```

**Persistence across file loads** — handlers are cleared when a .blend loads unless decorated:
```python
@bpy.app.handlers.persistent
def on_load(scene):
    print("file loaded")
bpy.app.handlers.load_post.append(on_load)
```

**Threading caveat for `frame_change_*`:** during animation playback the render and viewport draw run on separate threads. Mutating data the viewport reads can crash Blender. Prefer reads; if you must write, write into custom properties and let drivers handle propagation.

**Timer handlers** — `bpy.app.timers` — schedule a callable to run after N seconds, optionally repeating:
```python
def tick():
    print("tick")
    return 1.0      # call again in 1.0 s; return None to stop

bpy.app.timers.register(tick)
```

Timers run on the main thread between editor events. Safe for `bpy.data` mutation.

---

## 14. The Operator + Panel Pattern (Briefly)

The MCP connector is itself a Blender addon; the agent should know the registration cycle to understand what's running inside the host.

**Operator skeleton:**
```python
class MY_OT_do_thing(bpy.types.Operator):
    bl_idname  = "my.do_thing"           # accessible as bpy.ops.my.do_thing()
    bl_label   = "Do Thing"
    bl_options = {'REGISTER', 'UNDO'}

    intensity: bpy.props.FloatProperty(default=1.0)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        # ... do work ...
        return {'FINISHED'}
```

**Panel skeleton:**
```python
class MY_PT_panel(bpy.types.Panel):
    bl_label       = "My Panel"
    bl_idname      = "MY_PT_panel"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category    = "MyTab"

    def draw(self, context):
        layout = self.layout
        layout.operator("my.do_thing")
```

**Registration:**
```python
classes = (MY_OT_do_thing, MY_PT_panel)

def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()
```

Addons follow this exact pattern with `register()` / `unregister()` as module-level functions called by Blender on enable/disable.

Naming conventions (enforced by Blender's class-name checker):
- Operators: `CATEGORY_OT_name`
- Panels: `CATEGORY_PT_name`
- Menus: `CATEGORY_MT_name`
- Headers: `CATEGORY_HT_name`
- UILists: `CATEGORY_UL_name`

---

## 15. Common Footguns

Each entry: failure mode → fix.

1. **`bpy.ops.X.poll() failed, context is incorrect`** → wrap the call in `bpy.context.temp_override(area=..., region=..., active_object=...)`; or fix the precondition (selection, mode).
2. **Operator works in the UI, fails in `--background`** → no 3D viewport exists; use the data API, or find a saved-window area via the loop in section 3.
3. **`obj.data` confused with `obj`** → `obj` is the scene-graph node (transform, parent, modifiers list); `obj.data` is the underlying Mesh / Curve / Light / Camera datablock. Modifying `obj.data` affects every object that shares it.
4. **Edits don't show post-modifier** → you read `obj.data`, which is pre-modifier. Use `obj.evaluated_get(depsgraph).data` after `depsgraph = bpy.context.evaluated_depsgraph_get()`.
5. **`me.vertices[i].co` change has no visible effect** → call `me.update()` after editing; for normals call `me.calc_normals_split()` or recompute via bmesh.
6. **Mesh edit op fails: "context.mode not in {'EDIT_MESH'}"** → switch with `bpy.ops.object.mode_set(mode='EDIT')` after setting an active mesh object. Switch back when done.
7. **`obj.copy()` creates a new datablock every call** → for instancing, share the mesh: `inst = bpy.data.objects.new("Inst", obj.data)` instead.
8. **Names collide and get `.001` suffix unexpectedly** → check `if name in bpy.data.objects: bpy.data.objects.remove(...)` before recreating, or use `.get()` and reuse.
9. **`bpy.ops.object.delete()` deletes nothing** → it deletes *selected* objects. Set `obj.select_set(True)` and `bpy.context.view_layer.objects.active = obj` first. Prefer `bpy.data.objects.remove(obj, do_unlink=True)`.
10. **Datablocks survive across reloads despite no users** → `use_fake_user = True` is set. Toggle it off and run `bpy.data.orphans_purge(do_recursive=True)`.
11. **RNA property assignment raises `AttributeError: ... is read-only`** → some properties are computed (e.g. `obj.matrix_world` when there's a parent — assign `matrix_basis` or unparent first; `users` is always read-only).
12. **`bpy.context.collection` vs `bpy.context.scene.collection`** — the first is the *active* collection (last clicked in Outliner); the second is the scene's root collection. New objects go to the active one if you `bpy.ops.object.link_to_collection` or rely on operator default — set explicitly to avoid surprise.
13. **Property change doesn't propagate / no viewport update** → call `obj.update_tag()` or `obj.data.update_tag()`. For deeper graph invalidation use `bpy.context.view_layer.update()`.
14. **Driver expression silently fails** → check the Drivers Editor or run with the Python console open; bad expressions print a one-time warning then quietly evaluate to 0. Set `drv.use_self = True` to access `self` (the driven property's owner) inside the expression.
15. **Adding a modifier in a script doesn't update geometry** → call `bpy.context.view_layer.update()` or get the evaluated object: `obj.evaluated_get(bpy.context.evaluated_depsgraph_get())`.
16. **`bpy.ops` calls are slow in tight loops** → each adds an undo step. Wrap your batch in:
    ```python
    bpy.context.preferences.edit.use_global_undo = False
    try:
        # ...
    finally:
        bpy.context.preferences.edit.use_global_undo = True
    ```
    Better: switch to the data API or bmesh.
17. **Linked library datablocks throw `AttributeError` on assignment** → linked = read-only. Use `make_local()` or `override_create()` first.
18. **`bmesh.from_edit_mesh()` results stale after operator runs** → operators invalidate the bm reference. Re-fetch `bm = bmesh.from_edit_mesh(obj.data)` after any `bpy.ops.mesh.*` call.
19. **`bm.verts[0]` raises `IndexError` after editing** → call `bm.verts.ensure_lookup_table()` (and `bm.edges.ensure_lookup_table()`, `bm.faces.ensure_lookup_table()`) after any add/remove.
20. **`'BLENDER_EEVEE'` not recognized as render engine** → 4.2 removed it; use `'BLENDER_EEVEE_NEXT'`.
21. **Geometry node group input/output API broke from 3.x** → use `node_group.interface.new_socket(...)` (4.x), not `node_group.inputs.new(...)` (deprecated/removed).
22. **Passing a context dict as the first arg to `bpy.ops.X(ctx, ...)`** → deprecated 3.2, removed 4.x. Use `with bpy.context.temp_override(**ctx): bpy.ops.X(...)`.

---

## 16. Quick-Reference Snippet Library

**Create an empty at origin:**
```python
e = bpy.data.objects.new("E", None); bpy.context.scene.collection.objects.link(e)
```

**Add a cube at a location:**
```python
bpy.ops.mesh.primitive_cube_add(size=2, location=(3, 0, 0))
```

**Switch to edit mode and select all verts:**
```python
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
```

**Create a new material and assign to active object:**
```python
m = bpy.data.materials.new("M"); m.use_nodes = True
bpy.context.object.data.materials.append(m)
```

**Add Principled BSDF linked to output:**
```python
nt = m.node_tree; nt.nodes.clear()
o = nt.nodes.new('ShaderNodeOutputMaterial'); o.location=(300,0)
b = nt.nodes.new('ShaderNodeBsdfPrincipled')
nt.links.new(b.outputs['BSDF'], o.inputs['Surface'])
```

**Save the file:**
```python
bpy.ops.wm.save_as_mainfile(filepath="/tmp/out.blend")
```

**Render current frame to PNG:**
```python
bpy.context.scene.render.filepath = "/tmp/frame.png"
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.ops.render.render(write_still=True)
```

**List all object names in scene:**
```python
[o.name for o in bpy.context.scene.objects]
```

**Delete every object named "Cube*":**
```python
for o in [x for x in bpy.data.objects if x.name.startswith("Cube")]:
    bpy.data.objects.remove(o, do_unlink=True)
```

**Set active and select one object:**
```python
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True); bpy.context.view_layer.objects.active = obj
```

**Add a subsurf modifier:**
```python
obj.modifiers.new("SubSurf", 'SUBSURF').levels = 2
```

**Insert a location keyframe on current frame:**
```python
obj.keyframe_insert(data_path="location", frame=bpy.context.scene.frame_current)
```

**Add a driver on object's Z location:**
```python
fc = obj.driver_add("location", 2); fc.driver.expression = "frame * 0.1"
```

**Import an image as a plane (requires "Import Images as Planes" addon enabled):**
```python
bpy.ops.import_image.to_plane(files=[{"name": "/tmp/img.png"}])
```

**Export selected as glTF:**
```python
bpy.ops.export_scene.gltf(filepath="/tmp/out.glb", use_selection=True)
```

**Set viewport shading to rendered (in 3D view):**
```python
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        area.spaces.active.shading.type = 'RENDERED'
```

**Get evaluated mesh (post-modifier):**
```python
dg = bpy.context.evaluated_depsgraph_get()
ev = obj.evaluated_get(dg); me_eval = ev.to_mesh()
# ... read me_eval.vertices ...
ev.to_mesh_clear()
```

**Create a new scene:**
```python
new_scn = bpy.data.scenes.new("Scene2")
bpy.context.window.scene = new_scn
```

**Set frame range and current frame:**
```python
scn = bpy.context.scene
scn.frame_start, scn.frame_end, scn.frame_current = 1, 250, 1
```

**Make a collection and link the active object into it:**
```python
c = bpy.data.collections.new("MyCol")
bpy.context.scene.collection.children.link(c)
c.objects.link(bpy.context.object)
```

**Add a Geometry Nodes modifier with a new tree:**
```python
ng = bpy.data.node_groups.new("MyGN", 'GeometryNodeTree')
mod = obj.modifiers.new("GN", 'NODES'); mod.node_group = ng
```

---

## 17. Useful Debugging Incantations

**Scene statistics string (vertex count, face count, object count):**
```python
bpy.context.scene.statistics(bpy.context.view_layer)
```

**All RNA-exposed properties on an object:**
```python
list(obj.bl_rna.properties.keys())
```

**Description of a single property:**
```python
obj.bl_rna.properties["location"].description
obj.bl_rna.properties["location"].subtype     # 'TRANSLATION'
```

**Everything Python sees on an instance:**
```python
dir(obj)
```

**Class docstring:**
```python
print(type(obj).__doc__)
print(bpy.types.Object.__doc__)
```

**Enable Python tooltips in the UI** — Edit → Preferences → Interface → Display → enable "Python Tooltips" and "Developer Extras". Hovering any UI field then shows the `bpy.context...` / `bpy.data...` path.

**Open the Python console** — Scripting workspace, bottom-left area. Or change any area's type to "Python Console". Tab-completes `bpy.` namespaces.

**Copy Data Path from UI** — right-click any property field → "Copy Data Path" → paste yields the exact data path like `location[2]` or `node_tree.nodes["Principled BSDF"].inputs[0].default_value`. Combine with `obj.path_resolve("location[2]")` to read programmatically.

**Find an operator's full module name** — right-click the menu item → "Online Python Reference" (opens docs), or "Copy Python Command" → puts the literal `bpy.ops.x.y(...)` call on the clipboard.

**Log every `bpy.ops` call Blender makes** — set the Info editor at the top of the screen to "Info" type; every operator invocation prints there with arguments. Filters: Info → Filter by Type → enable "Operators".

**Check Blender's Python version at runtime:**
```python
import sys; print(sys.version)
print(bpy.app.version, bpy.app.version_string)
```

**Check whether something is a linked datablock:**
```python
obj.library is not None
obj.is_library_indirect
```

**List all addons currently enabled:**
```python
list(bpy.context.preferences.addons.keys())
```

**Find every datablock referencing a target:**
```python
target = bpy.data.materials["MyMat"]
[u for u in bpy.data.user_map(subset={target})[target]]
# bpy.data.user_map() is the supported 3.x+ API for "who uses what"
```

**Force a viewport / depsgraph refresh:**
```python
bpy.context.view_layer.update()
for area in bpy.context.screen.areas: area.tag_redraw()
```

**Check current mode and active object cleanly:**
```python
print(bpy.context.mode, bpy.context.active_object)
```

**Print the full operator return + last reports** (useful when an op returns `{'CANCELLED'}` silently):
```python
result = bpy.ops.mesh.primitive_cube_add()
print(result)
# Hover the bottom status bar after a failed op; or check the Info log.
```

---

End of file. Sister files: `[[BLENDER_DATA_MODEL]]` (deeper ID taxonomy and relationships), `[[BLENDER_UI_VOCABULARY]]` (Outliner / Properties Editor terminology), `[[BLENDER_GEOMETRY_NODES]]`, `[[BLENDER_SHADER_NODES]]`.
