---
title: Blender Data Model
version: 1.0
last_updated: 2026-05-22
status: live
scope: How a Blender file is organized — Scene, Collection, Object, Mesh, Material, NodeTree, Image, World, Camera, Light, Armature, Action, and other ID datablocks. Linking, naming, ownership, garbage collection.
dependencies: BLENDER_LIBRARY_INDEX.md, BLENDER_PYTHON_API.md
---

# BLENDER DATA MODEL

"The Blender data model" is the in-memory shape of a `.blend` file: a flat set of typed datablock collections under `bpy.data`, plus a scene-graph that links them together by reference. Every datablock is an **ID** — a named, ref-counted, garbage-collected object that other datablocks can point at. An agent driving Blender via MCP must reason about this graph **before** issuing calls, because most "did the wrong thing" bugs come from confusing an object with its data, sharing a datablock without realising it, or losing a datablock to GC on save.

Target Blender: 4.2 LTS minimum, 4.5+ preferred. The data model is stable across this range; library overrides are the most recently evolved subsystem and are flagged where relevant.

**Core facts:**
- Everything top-level in a `.blend` file is an **ID datablock** — Scene, Collection, Object, Mesh, Material, Image, Action, etc. All inherit from `bpy.types.ID`.
- Datablocks live in named collections under `bpy.data` — `bpy.data.objects`, `bpy.data.meshes`, `bpy.data.materials`, etc. Each collection holds one ID type.
- Names are **unique per collection**. Two meshes cannot share a name; a mesh and an object can.
- When a name collision occurs on create, Blender appends `.001`, `.002`, ... — silently. After any `new()` call, look up by `.get()` if you depended on a specific name.
- The scene-graph hierarchy is: **Scene → Collection → Object → ObjectData**. Objects hold the transform; their `.data` field links to the mesh/light/camera/etc.
- Multiple Objects can share the same `ObjectData` — that's instancing at the data level. Linked duplicates work this way.
- **Linking** = read-only reference to another `.blend` file. **Appending** = deep copy from another `.blend`. **Library overrides** sit on top of linking to allow local edits.
- Datablocks use **reference counting** (`id.users`). On file save, anything with `users == 0` is dropped unless `use_fake_user` is True.
- `bpy.ops.outliner.orphans_purge()` clears unused datablocks immediately, recursively if you ask for it.
- Modifiers, constraints, mesh vertices, node sockets, and FCurve keyframes are **not** IDs — they live inside IDs and are owned by them. You can't reference them globally.
- View-layer visibility (`exclude`) is per-view-layer; `hide_viewport` and `hide_render` are global to the file.

---

## The ID System

Every top-level datablock derives from `bpy.types.ID`. The ID base class defines the universal properties an agent can rely on across every type:

- **`id.name`** — string, unique within the datablock's collection. Read/write.
- **`id.name_full`** — same as `name` but library-prefixed for linked data (`MaterialName` vs `MA.001LinkedLib`). Read-only.
- **`id.users`** — int, current user count. Read-only. Includes both real users (other datablocks pointing at this one) and the fake user.
- **`id.use_fake_user`** — bool. When True, Blender pretends there's always one user, so the datablock survives a save even with no real references.
- **`id.library`** — `bpy.types.Library` or `None`. If set, this ID was linked from an external `.blend`.
- **`id.override_library`** — `IDOverrideLibrary` or `None`. Present when this ID is a local override over a linked one.
- **`id.asset_data`** — `AssetMetaData` or `None`. Present when this ID has been marked as an asset.
- **`id.tag`** — bool, free temporary flag scripts can use to mark visited IDs during traversal. Reset before use, since other scripts may have set it.
- **`id.is_embedded_data`** — bool. True for IDs that don't live in `bpy.data` directly but are owned by a parent (a Scene's master Collection, a NodeTree embedded in a Material).
- **`id.is_evaluated`** — bool. True if this is the evaluated (depsgraph) copy, not the original.
- **`id.original`** — the original ID this evaluated copy came from. For original IDs, `id.original is id`.

**Evaluated vs original.** Blender keeps two parallel copies of most data: the **original** (what you edit and what gets saved) and the **evaluated** result after modifiers, drivers, animation, and constraints run. Scripts almost always want originals — `bpy.data.objects['Cube']` returns originals. The depsgraph (`bpy.context.evaluated_depsgraph_get()`) returns evaluated copies. Writing to evaluated data is unsupported.

**Library overrides** (modern, recommended over the legacy "proxy" system, which is removed) let you locally edit a linked ID without breaking the link. Conceptually: the override is a thin local ID that delegates everything to the linked reference, except for properties the user (or a script) has explicitly overridden. `override_library.reference` points at the linked source; `override_library.properties` is the list of overridden properties. Hierarchy-aware overrides cover whole asset trees (a character's armature + meshes + materials) in one call. See [[BLENDER_PYTHON_API]] for the operator surface.

---

## The Scene-Graph Hierarchy

The runtime tree:

```
Scene
 |- world (-> World)
 |- camera (-> Object)
 |- collection (master Collection, embedded)
 |    |- children (Collections)
 |    |    |- children (Collections)  [recursive]
 |    |    |- objects (Objects)
 |    |- objects (Objects)
 |- view_layers
 |    |- layer_collection (mirrors collection tree, holds exclude/holdout/indirect flags)
 |- render, eevee, cycles, frame settings...
Object
 |- data (-> Mesh | Curve | Light | Camera | Armature | ...)
 |- modifiers (collection of Modifier — NOT IDs)
 |- constraints (collection of Constraint — NOT IDs)
 |- material_slots (-> Material[]; mirrors data.materials by default)
 |- animation_data (-> AnimData, optional)
 |    |- action (-> Action)
 |    |- nla_tracks (-> NlaTrack[])
 |- pose (-> Pose, only if data is Armature)
ObjectData (Mesh / Curve / etc.)
 |- materials (-> Material[])
 |- animation_data (-> AnimData, optional)
 |- type-specific geometry (vertices, splines, bones, ...)
Material
 |- node_tree (embedded ShaderNodeTree)
 |- animation_data (-> AnimData, optional)
World
 |- node_tree (embedded ShaderNodeTree)
```

Key rule: **Object holds the transform; ObjectData holds the geometry.** This is what makes instancing work — two Objects with different `location`/`rotation`/`scale` but the same `data` are linked duplicates of one mesh.

---

## Scene

`bpy.data.scenes` holds Scenes. A Scene is the top-level container for a render context. Each Scene owns:

- **`collection`** — the **master Collection**, an embedded (not-in-`bpy.data.collections`) Collection that roots the scene-graph tree. Everything visible in the Outliner under that scene lives under here.
- **`world`** — pointer to a World, or None.
- **`camera`** — pointer to the active Object whose data is a Camera. Render uses this.
- **`view_layers`** — list of ViewLayer. Each view layer has its own `LayerCollection` tree mirroring `scene.collection`, with per-layer flags like `exclude`, `holdout`, `indirect_only`.
- **Frame range** — `frame_start`, `frame_end`, `frame_current`, `frame_step`, `render.fps`.
- **Render settings** — `render` (resolution, output path, file format, engine), `eevee`, `cycles`, `display_settings`, `view_settings` (color management).
- **`sequence_editor`** — VSE strips, if the scene has a video sequence.
- **`grease_pencil`** — annotation Grease Pencil object (legacy 2D annotations layer).
- **Unit system** — `unit_settings` (metric/imperial, scale).
- **Animation/Time** — `timeline_markers`, `keying_sets`.

A `.blend` can hold **multiple scenes**. They are independent render contexts but can share datablocks (objects, materials, meshes) freely. Switching scenes in the UI changes `bpy.context.scene`. Scripts should read scenes explicitly: `bpy.data.scenes['SceneName']`.

A Scene can also **link to another Scene as a "set"** (`scene.background_set`), making the other scene's master collection render as a background. Rarely used in agent-driven workflows.

---

## Collection

Collections replaced the legacy "Group" system in Blender 2.80. They are IDs (`bpy.data.collections`) and form an arbitrary nested tree:

- **Children** — `collection.children` is a collection of sub-Collections.
- **Objects** — `collection.objects` is a collection of Objects directly inside this Collection.
- An Object can be in **multiple Collections at once**. Linking an Object into a Collection increments the Object's user count.
- The **master Collection** of a Scene (`scene.collection`) is *embedded* in the Scene and does not appear in `bpy.data.collections`. Don't try to look it up by name.

**Instancing a Collection.** An Object whose `instance_type == 'COLLECTION'` and `instance_collection` is set will render an instance of that collection's contents at its transform. This replaces 2.79's "Group Instance" and is the primary way to instance hierarchies cheaply.

**Visibility — three independent layers, easily confused:**

| Property | Scope | Effect |
|---|---|---|
| `layer_collection.exclude` | Per view layer | Excludes from view layer entirely. Affects viewport and render for that layer only. Set via `view_layer.layer_collection`. |
| `collection.hide_viewport` | Global | Hides in all viewports across all view layers. Does NOT affect render. |
| `collection.hide_render` | Global | Excludes from render across all view layers. Does NOT affect viewport. |
| `layer_collection.hide_viewport` | Per view layer | Per-view-layer viewport hide (the eyeball icon). |

Rule of thumb for agents: to fully hide for a render, set both `hide_render` and (if needed) ensure the Collection isn't `exclude`d. To temporarily isolate during a script, prefer `exclude` on the active view layer's `layer_collection`.

---

## Object

`bpy.data.objects`. An Object is a **transform + a link to ObjectData + a list of modifiers + a material list + animation data + parenting**. It is *not* the geometry. It is a node in the scene-graph that *references* geometry.

Key fields:

- **`object.data`** — pointer to the ObjectData ID (Mesh, Curve, Light, Camera, Armature, etc.). Setting this to None makes the Object an **Empty** (`type == 'EMPTY'`).
- **`object.type`** — read-only enum derived from `data` type: `'MESH'`, `'CURVE'`, `'LIGHT'`, `'CAMERA'`, `'EMPTY'`, `'ARMATURE'`, `'LATTICE'`, `'SURFACE'`, `'META'`, `'FONT'`, `'GPENCIL'`, `'VOLUME'`, `'CURVES'`, `'POINTCLOUD'`, `'SPEAKER'`, `'LIGHT_PROBE'`.
- **Transform** — `location`, `rotation_euler`/`rotation_quaternion`/`rotation_axis_angle` (mode set by `rotation_mode`), `scale`. `matrix_world`, `matrix_local`, `matrix_parent_inverse`, `matrix_basis` are derived.
- **`object.parent`** — pointer to another Object. Parenting is a property of the child, not the parent. Optional `parent_type` (`'OBJECT'`, `'BONE'`, `'VERTEX'`, ...) and `parent_bone`.
- **`object.modifiers`** — collection of Modifier instances. Modifiers are **not** IDs; they are owned by the Object. Order matters — modifiers evaluate top-to-bottom.
- **`object.constraints`** — collection of Constraint instances. Also not IDs.
- **`object.material_slots`** — list of MaterialSlot. Each slot has a `material` pointer and a `link` enum ('DATA' or 'OBJECT'). See [[BLENDER_MATERIALS]].
- **`object.animation_data`** — `AnimData` or None. Holds the active Action and NLA tracks.
- **`object.pose`** — `Pose` or None. Present only when `data` is an Armature; holds the PoseBones (the animatable layer).
- **`object.vertex_groups`** — list of VertexGroup (named weight maps). Live on the Object but reference vertex indices in the Object's mesh data. Confusing but historical.

**Why two Objects can share a Mesh.** Setting `obj_b.data = obj_a.data` makes `obj_b` a linked duplicate. Both transform independently; edits to vertices, edges, or faces in Edit Mode are visible on both. The Mesh has a user count of 2.

---

## Mesh and Other ObjectData Types

Every ObjectData type is an ID that lives in its own `bpy.data` collection and holds geometry-or-equivalent state.

| ObjectData ID | `bpy.data` collection | Contents |
|---|---|---|
| **Mesh** | `bpy.data.meshes` | `vertices`, `edges`, `loops`, `polygons`, plus UV layers (`uv_layers`), vertex color/byte color attributes, generic `attributes`, shape keys (via Key), normals. Materials in `mesh.materials`. |
| **Curve** | `bpy.data.curves` | `splines` (Bezier/NURBS/Poly), bevel/depth/extrude/taper settings, used for both 3D curves and text (`Text` uses Curve). |
| **Surface** | `bpy.data.curves` (yes, same as Curve — type discriminated by `dimensions`/internal flag) | NURBS surfaces. |
| **Metaball** | `bpy.data.metaballs` | `elements` — implicit blob surfaces. Renders as a single mesh per "family." |
| **Text (VectorFont/Font Curve)** | `bpy.data.curves` (the text body) + `bpy.data.fonts` (the typeface) | Text geometry as a Curve. The typeface is a separate ID (`VectorFont`). |
| **GreasePencil v3** | `bpy.data.grease_pencils_v3` | Strokes organized in layers and frames. Blender 4.3+. Legacy 2D Grease Pencil is `bpy.data.grease_pencils`. |
| **Volume** | `bpy.data.volumes` | OpenVDB grid reference. The actual voxel data lives on disk or in cache. |
| **Curves (hair)** | `bpy.data.hair_curves` | Many-strand curve geometry — hair, fur, lines. Distinct from `bpy.data.curves`. |
| **PointCloud** | `bpy.data.pointclouds` | Point-only geometry (radius + position + attributes). |
| **Light** | `bpy.data.lights` | Light type (POINT/SUN/SPOT/AREA), color, energy, falloff, shadow settings, optional node tree (Cycles). |
| **Camera** | `bpy.data.cameras` | Lens, sensor size, clip start/end, dof settings, type (PERSP/ORTHO/PANO). |
| **Armature** | `bpy.data.armatures` | Bone hierarchy (rest pose). The animatable pose lives on `Object.pose`, not here. |
| **Lattice** | `bpy.data.lattices` | Lattice deformer cage (U/V/W resolution + control points). |
| **LightProbe** | `bpy.data.lightprobes` | Reflection/irradiance probes for EEVEE. |
| **Speaker** | `bpy.data.speakers` | 3D audio source pointing at a Sound. |

All share the ID base — `.name`, `.users`, `.use_fake_user`, `.library`, `.animation_data`, etc., behave consistently.

**Empty** is special: an Object with `data == None`. Empties have a transform but no geometry. Used for parents, targets, instancers, and references.

---

## Material

`bpy.data.materials`. A Material is an ID that wraps a shader node tree. Reference pattern:

```
Object.material_slots[i].material  -> Material
Object.data.materials[i]           -> Material  (same list by default)
```

There are **two parallel material lists** that an agent must understand:

1. **Data-level slots** — `obj.data.materials` is the canonical list, stored on the Mesh/Curve/etc. Shared across all Objects using that data.
2. **Object-level slots** — `obj.material_slots` mirrors the data list by index. Each slot has a `link` field:
   - `link == 'DATA'` (default) — the slot reads/writes the Material from `obj.data.materials[i]`. All linked Objects share the assignment.
   - `link == 'OBJECT'` — this Object overrides the slot with its own Material. Other Objects sharing the same data still see the data-level material.

So if you want a per-instance material override, set the slot's `link = 'OBJECT'` before assigning. Otherwise, edits propagate to every linked duplicate.

Polygons reference materials by index: `mesh.polygons[i].material_index` → `material_slots[material_index].material`.

**`use_nodes`** (the modern flag — the older `use_node_tree` name is gone) — when True, the material uses its `node_tree` (a `ShaderNodeTree`). When False, only the legacy basic properties (`diffuse_color`, etc.) apply. Agents should set `use_nodes = True` and work via the node tree.

The shader node tree is **embedded** in the Material — `material.node_tree` is an ID but `is_embedded_data` is True, so it does not appear in `bpy.data.node_groups`. See [[BLENDER_SHADER_NODES]].

---

## NodeTree

`bpy.data.node_groups` holds **reusable** NodeTrees — what you create when you "Make Group" or build a Geometry Nodes asset. Three concrete subtypes by `bl_idname`:

- **ShaderNodeTree** — for Materials, Worlds, Lights.
- **GeometryNodeTree** — for Geometry Nodes modifiers and tools.
- **CompositorNodeTree** — for the Compositor (one per Scene, plus reusable groups).
- **TextureNodeTree** — for legacy procedural textures (rarely used in modern workflows).

Each NodeTree has:
- `nodes` — collection of Node instances. Nodes are **not** IDs.
- `links` — collection of NodeLink, connecting `from_socket` → `to_socket`.
- `interface` (4.0+) — typed inputs/outputs for groups, replacing the older `inputs`/`outputs` collections. Sockets here belong to the group, not a node instance.

**Embedded vs reusable node trees.** A Material's `node_tree`, a World's `node_tree`, and a Scene's `node_tree` (Compositor) are embedded — they exist inside their parent ID, never in `bpy.data.node_groups`. NodeGroups created for reuse live in `bpy.data.node_groups` and can be referenced from multiple parent trees via a Group node.

**Geometry Nodes specifics.** A Geometry Nodes **modifier** stores a pointer to a `GeometryNodeTree` in `bpy.data.node_groups` — not an embedded tree. See [[BLENDER_GEOMETRY_NODES]]. Modifier inputs (`modifier["Input_2"]`, etc.) are exposed through the group's interface.

---

## Image

`bpy.data.images`. Holds raster image data. Key fields:

- **`image.source`** — enum: `'FILE'` (file on disk), `'SEQUENCE'` (numbered files), `'MOVIE'` (video file), `'GENERATED'` (procedural — blank, UV grid, color grid), `'VIEWER'` (compositor/render viewer), `'TILED'` (UDIM tiles).
- **`image.filepath`** / **`image.filepath_raw`** — disk path. Relative paths use `//` prefix.
- **`image.packed_file`** / **`image.packed_files`** — when packed, image bytes are stored inside the `.blend` itself. Pack via `image.pack()`; unpack via `image.unpack()`.
- **`image.colorspace_settings.name`** — `'sRGB'`, `'Non-Color'`, `'Raw'`, etc. **Critical**: textures used as normal maps, masks, or data must be `'Non-Color'`. Color textures should be `'sRGB'`. Mismatches are the #1 cause of "why does my normal map look wrong."
- **`image.alpha_mode`** — `'STRAIGHT'`, `'PREMUL'`, `'CHANNEL_PACKED'`, `'NONE'`.
- **`image.size[0]`, `image.size[1]`** — width, height. Read-only for FILE source; settable when GENERATED.
- **`image.pixels`** — flat float array (RGBA × W × H), read/write but slow. Use only when you have to.

**Reloading.** If the source file on disk changes, call `image.reload()` to pick it up. Blender does not auto-reload.

**Movies and sequences** are also Images — they store the source ref and frame state. A separate `MovieClip` ID (`bpy.data.movieclips`) exists for VSE/tracker use.

---

## World

`bpy.data.worlds`. The environment/background for a Scene. Each World has:

- **`world.node_tree`** — embedded ShaderNodeTree, used when `use_nodes` is True. The Background node here drives the environment lighting.
- **`world.color`** — fallback flat background color (used only when `use_nodes` is False).
- **`world.light_settings`** — ambient occlusion settings (mostly legacy; Cycles/EEVEE use the node tree).
- **`world.mist_settings`** — atmospheric mist.

A World is referenced by a Scene via `scene.world`. Multiple Scenes can share a World.

---

## Action, FCurves, and NLA

Animation in Blender lives on **Actions** (`bpy.data.actions`). An Action is a container of FCurves; an FCurve is the storage form of a single animated channel (e.g. `location[0]` on an Object, `default_value` on a node socket).

**AnimData** — the bridge. Any ID that can be animated has an `animation_data` property that is either None or an `AnimData` block. `AnimData` holds:
- `action` — the currently active Action.
- `nla_tracks` — stacked Actions for non-linear animation.
- `drivers` — driver FCurves (formulas that compute a property from other values; not tied to an Action).

To animate something the first time, the API creates the AnimData and an Action automatically if you keyframe via `obj.keyframe_insert()`.

**FCurve structure.** Each FCurve has a `data_path` (a Python-style accessor string like `"location"` or `"modifiers[\"Subdivision\"].levels"`) and an `array_index` (which channel of a vector property). It owns a list of `keyframe_points` and optional modifiers (cyclic, noise).

**Action slots** (Blender 4.4+) — Actions now support multiple "slots" so one Action can drive several IDs. Older `.blend` files use the legacy single-slot Action — both forms coexist. Agents reading Actions should handle both layouts; check `action.slots` if present.

**NLA stacking.** NLA tracks let you layer Actions in time. Each NlaStrip references an Action. Useful for character animation pipelines; less relevant for procedural agent work.

**Where AnimData lives.** Not every ID supports animation. Scene, Object, ObjectData, Material, World, NodeTree, Armature, Camera, Light, ParticleSettings, MetaBall, Speaker, Key, and a few others do. Mesh attributes are usually animated indirectly via shape keys (a separate `Key` ID per mesh).

---

## Armature, Pose, and Bones

Three confusable types, mode-dependent:

- **Bone** — lives on the Armature data (`armature.bones`). Read-only at runtime. The "rest" definition: head, tail, roll, parenting, deform flag.
- **EditBone** — lives on the Armature only in **Edit Mode** (`armature.edit_bones`). Writable representation of the rest pose. Outside Edit Mode, this collection is empty.
- **PoseBone** — lives on the **Object** (`object.pose.bones`), not the Armature data. The animatable layer: `location`, `rotation_quaternion`, `scale`, constraints, custom shapes. PoseBones reference their Bone via `pose_bone.bone`.

**Why this split.** The Armature data is shared across multiple Objects (linked rigs). The Pose is per-Object so two characters can share a skeleton but pose independently.

To edit the rest pose, you must:
1. Set the Object active and in EDIT mode (`bpy.ops.object.mode_set(mode='EDIT')`).
2. Read/write `armature.edit_bones`.
3. Return to OBJECT mode to commit (and for `armature.bones` to repopulate).

PoseBone changes can be made in any mode and are what an animation Action targets via data_paths like `pose.bones["Bone.001"].rotation_quaternion`.

---

## Brushes, Textures, Sounds, and Other Content IDs

- **`bpy.data.brushes`** — Sculpt/Paint/GP brushes. Each brush references a Texture for its stroke shape/alpha.
- **`bpy.data.textures`** — Legacy procedural textures (Voronoi, Wood, Magic, Image). Used by brushes, modifiers (Displace, Warp), and particle systems. Shader nodes use Image + node-based procedurals instead, so this list mostly holds brush textures in modern files.
- **`bpy.data.sounds`** — Audio file references. Used by Speakers and the VSE.
- **`bpy.data.movieclips`** — Video files for the motion tracker and VSE. Separate from Image-source MOVIEs.
- **`bpy.data.masks`** — 2D mask shapes for the compositor and clip editor.
- **`bpy.data.palettes`** — Color palettes.
- **`bpy.data.paint_curves`** — Curves used by paint strokes.
- **`bpy.data.particles`** — `ParticleSettings`. Note: a particle *system* (an instance of settings on an object) is **not** an ID; it's owned by the Object. ParticleSettings IDs hold the parameters.
- **`bpy.data.cache_files`** — Alembic/USD cache references.
- **`bpy.data.linestyles`** — Freestyle line styles.

---

## Library, Link, Append, Override

A `.blend` file can reference other `.blend` files.

- **Link** — `bpy.ops.wm.link()` — creates IDs in the current file that *point at* IDs in another file. The pointed-at IDs are **read-only**. Their `.library` field is non-None. Linked IDs are re-read every time the file opens; changes in the source propagate automatically. Use linking for shared assets across many files.
- **Append** — `bpy.ops.wm.append()` — copies IDs (and their dependencies) into the current file as **local** copies. `.library` is None. Edits stay local; no automatic sync with the source. Use appending when you need to modify or detach the asset.
- **Library Override** — sits on top of linking. The linked ID stays linked and read-only, but a **local override ID** is created that delegates to the linked ID and lets you override specific properties. Created via `bpy.ops.object.make_override_library()` or `id.override_create()`. The override has `override_library.reference` pointing to the linked source and `override_library.properties` listing per-property diffs.
  - Hierarchy overrides cover whole asset chains in one call — overriding a character's Armature Object also creates overrides for its mesh Objects, its rig data, materials, etc. (4.0+, refined through 4.5).
  - `override_library.is_in_hierarchy`, `is_system_override`, `hierarchy_root` help an agent reason about the override tree.
  - Resync — when the linked source's structure changes, overrides need a resync (`bpy.ops.outliner.lib_override_resync()`). Modern Blender does this on file load when feasible, but agents touching long-lived files should call it explicitly after changes.

**Orphan and purge.** Linked datablocks that nothing in the file references are orphans the next time you reload. Purging (`bpy.ops.outliner.orphans_purge()`) drops them. See next section.

---

## User Count and Garbage Collection

Every ID has a refcount: `id.users`. The count increments when another datablock starts referring to this ID and decrements when the reference is dropped.

**Save behavior:**
- On save, datablocks with `users == 0` are written out by default in recent Blender (the historical "drop on save" behavior changed — unused IDs are now preserved across saves so undo works after delete). They still appear in the file but show up as orphans.
- `use_fake_user = True` adds one virtual user, keeping the datablock alive against any auto-purge logic. Materials and Actions you want to ship in an asset library should be fake-user-protected.
- `bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)` immediately drops orphans. Recursive purge handles chains (orphan Material → its embedded NodeTree → its Image references becoming orphan too).

**Agent practice:** when creating temporary datablocks for an intermediate step, either parent them to something with a real user before saving, or call `orphans_purge()` at the end. Don't rely on auto-purge.

**Refcount gotchas:**
- Assigning `obj.data = new_mesh` decrements the old mesh's user count. If it drops to 0 and no fake user, it becomes orphan.
- Removing an Object from all Collections drops its user count. An Object not in any Collection won't appear in any Scene's tree even if it's still in `bpy.data.objects`.
- `bpy.data.meshes.remove(mesh, do_unlink=True)` unlinks the mesh from all users and removes it. Without `do_unlink=True`, you'll get an error if `mesh.users > 0`.

---

## Names, Collisions, and `.001`

Blender enforces unique names **per collection of IDs**. Within `bpy.data.objects`, no two Objects share a name. Within `bpy.data.materials`, no two Materials share a name. But an Object and a Material can both be named `"Cube"`.

**Auto-numbering.** When you call `bpy.data.meshes.new("Plane")` and `"Plane"` already exists, Blender returns a new mesh named `"Plane.001"`. If `"Plane.001"` also exists, it tries `"Plane.002"`, and so on. No error is raised; no warning.

**Agent rule:** after any `new()` call, **bind the returned reference** and never look up by the name you passed in:

```python
mesh = bpy.data.meshes.new("Plane")   # might be Plane.003
# do NOT then do: bpy.data.meshes["Plane"]
# the variable `mesh` is your handle.
```

If you need to find a specific datablock later in a script, use `.get(name)` (returns None on miss) rather than subscripting (raises KeyError):

```python
m = bpy.data.materials.get("Brand_Primary")
if m is None:
    m = bpy.data.materials.new("Brand_Primary")
```

**Renaming** assigns a new unique name; if a collision happens, Blender silently appends `.NNN`.

**Library prefixes.** Linked IDs disambiguate via `name_full` (`SC.0001MyLib`) but their `.name` is the bare name. Two linked materials from different libraries can have the same `.name`; they're distinguished by `.library`.

---

## Read-Only vs Writable from Script

Most properties are writable. A few categories are not:

- **Type discriminators** — `object.type`, `id_data`, `bl_rna`, `rna_type` are read-only. To change an Object's type, replace its `.data`.
- **Derived transforms** — `matrix_world`, `matrix_local` are read-only on most types (computed from `location`/`rotation`/`scale`). Set the source fields instead. Some IDs allow direct matrix assignment, but it's the exception.
- **Evaluated copies** — anything obtained via `depsgraph.id_eval_get()` or `obj.evaluated_get(depsgraph)` is read-only.
- **Linked data** — IDs where `id.library is not None` are read-only at the property level. To edit, either Append or create a Library Override.
- **Mode-gated** — `armature.edit_bones` is only populated and writable in EDIT mode. `mesh.vertices` should not be mutated while in EDIT mode (the BMesh edit copy is separate; use `bmesh` then write back).
- **Context-gated operators** — `bpy.ops.*` calls often require a specific `bpy.context` (active object, mode, area type). Override with `bpy.context.temp_override(...)` rather than hoping the global context is right.

If a property assignment silently does nothing, suspect: (a) the ID is linked, (b) wrong mode, (c) it was a computed/derived property.

---

## What's NOT a Datablock

These live **inside** IDs and are not themselves IDs. They cannot exist in `bpy.data` and cannot be referenced globally:

- **Modifier** instances on an Object (`obj.modifiers[i]`). Owned by the Object.
- **Constraint** instances on an Object or PoseBone.
- **MaterialSlot** entries on an Object.
- **ShapeKey** entries within a `Key` ID (the `Key` itself **is** an ID, in `bpy.data.shape_keys`).
- **Mesh elements** — vertices, edges, loops, polygons. Owned by the Mesh.
- **Curve splines** — owned by the Curve.
- **Bones** — owned by the Armature data (rest) or Object's Pose (animatable).
- **Node** instances inside a NodeTree. The NodeTree is the ID; the nodes are not.
- **NodeSocket** instances — both per-node sockets and group interface sockets.
- **NodeLink** — connections between sockets.
- **FCurve** and `Keyframe` — owned by Action or AnimData.drivers.
- **ParticleSystem** instances on an Object — the `ParticleSettings` is the ID; the system is the per-Object instance.
- **VertexGroup**, **UVLayer**, **ColorAttribute**, generic `Attribute` — owned by Mesh.
- **TimelineMarker** — owned by Scene.
- **NlaStrip**, **NlaTrack** — owned by AnimData.

**Implication for an agent:** you cannot rename or "link" a modifier across objects. To replicate a modifier setup, copy its property values into a fresh modifier on the target object. The single exception that feels like reuse is the Geometry Nodes modifier — the *node tree* it points to is a NodeGroup ID, so two objects can share the same geometry-nodes "modifier program" while still having two independent modifier instances.

---

## Cheat-Sheet Table: `bpy.data` Collections

The complete list of top-level datablock collections an agent will commonly touch.

| `bpy.data.X` | ID type | Holds | Typical agent usage |
|---|---|---|---|
| `scenes` | Scene | Render contexts | Read frame range, switch active scene, set world/camera. |
| `collections` | Collection | Hierarchy nodes | Create groups; nest; instance via Empty. |
| `objects` | Object | Transforms + data links | The most-touched collection. Create, parent, move, animate. |
| `meshes` | Mesh | Polygonal geometry | Create from scratch, modify vertices/UVs/attributes. |
| `curves` | Curve | Bezier/NURBS curves + Text bodies | Procedural curves, text geometry. |
| `metaballs` | MetaBall | Implicit blob surfaces | Rare. |
| `lattices` | Lattice | Deformer cages | Used by Lattice modifier. |
| `armatures` | Armature | Rest-pose bone hierarchy | Rigs. |
| `cameras` | Camera | Lens + sensor settings | Set render camera. |
| `lights` | Light | Light data | Create/edit lights. |
| `lightprobes` | LightProbe | EEVEE probes | EEVEE reflection/irradiance. |
| `speakers` | Speaker | 3D audio sources | Audio in scene. |
| `volumes` | Volume | OpenVDB grid refs | Volumetric data. |
| `hair_curves` | Curves | Hair/strand geometry | Particle hair replacement. |
| `pointclouds` | PointCloud | Point geometry | Procedural point data. |
| `grease_pencils_v3` | GreasePencilv3 | Stroke geometry (4.3+) | 2D animation, annotations. |
| `materials` | Material | Shader + slot ref | Create materials, assign to slots. |
| `node_groups` | NodeTree | Reusable shader/geom/comp groups | Build/instantiate Geometry Nodes asset groups. |
| `textures` | Texture | Legacy procedurals + brush textures | Mostly brush textures now. |
| `images` | Image | Raster image data | Load textures, pack, set colorspace. |
| `movieclips` | MovieClip | Video for tracking/VSE | Motion tracking. |
| `worlds` | World | Scene environment | Set background HDRI / sky. |
| `actions` | Action | FCurves + slots | Animation; assign to AnimData. |
| `shape_keys` | Key | Shape-key data | Per-mesh shape key blocks; usually managed via `mesh.shape_keys`. |
| `brushes` | Brush | Sculpt/paint brushes | Brush configuration. |
| `palettes` | Palette | Color palettes | Paint workflow. |
| `paint_curves` | PaintCurve | Stroke curves | Paint workflow. |
| `particles` | ParticleSettings | Particle parameters | Used by particle systems on objects. |
| `cache_files` | CacheFile | Alembic/USD refs | External cache pipelines. |
| `linestyles` | FreestyleLineStyle | Freestyle settings | Line rendering. |
| `masks` | Mask | 2D masks | Compositor/VSE. |
| `sounds` | Sound | Audio refs | Speakers, VSE. |
| `texts` | Text | Internal text blocks (scripts, notes) | OSL shaders, embedded Python scripts. |
| `fonts` | VectorFont | Typefaces | Used by Text Curves. |
| `libraries` | Library | External `.blend` refs | Set per-linked-ID via `id.library`. |
| `workspaces` | WorkSpace | UI workspaces | Rarely touched by scripts. |
| `screens` | Screen | UI layouts | Rarely touched by scripts. |
| `window_managers` | WindowManager | Top-level UI state | Read-only in practice. |

---

## Quick Reference for Common Reasoning

- **"Where does this property live?"** Walk up the ownership chain: socket → node → node tree → material (or modifier) → object → collection → scene. Most "where do I write this" questions reduce to which ID actually owns the property.
- **"Will this edit propagate to other instances?"** Edit on the Object → local to that Object. Edit on the `.data` → propagates to all Objects sharing that data. Edit on a Material in a 'DATA'-linked slot → propagates. Edit a NodeGroup → propagates to every tree referencing it.
- **"Will this survive a save?"** If `id.users > 0` from a real reference, yes. If `users == 0` and not `use_fake_user`, it depends on Blender version and purge behavior — don't rely on it; either reference or fake-user it.
- **"Can I rename freely?"** Yes, but expect `.001` collisions and update any name-based lookups.
- **"Why does my linked asset not edit?"** Because it's linked. Either Append or create a Library Override.
