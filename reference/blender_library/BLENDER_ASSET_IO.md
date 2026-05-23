---
title: Asset I/O — Import, Export, Asset Browser, Poly Haven, HDRIs
version: 1.0
last_updated: 2026-05-22
status: live
scope: All asset I/O paths in Blender — FBX, GLB/GLTF, OBJ, USD, Alembic, STL, PLY format conventions; the Asset Browser and asset marking; link vs append for .blend; Poly Haven workflow (CC0 textures, models, HDRIs); HDRI World setup; the bpy.ops import/export APIs.
dependencies: BLENDER_LIBRARY_INDEX.md, BLENDER_PYTHON_API.md, BLENDER_DATA_MODEL.md, BLENDER_MATERIALS.md
---

# ASSET I/O — IMPORT, EXPORT, ASSET BROWSER, POLY HAVEN, HDRIS

Blender's asset I/O lives on three rails. **Interchange formats** (FBX, GLB/glTF, OBJ, USD, Alembic, STL, PLY) move geometry, materials, and animation between Blender and other DCCs / engines / printers. **.blend-native** (link, append, library override) moves anything Blender can store — nodes, modifiers, drivers, geometry nodes graphs — but only between Blender installs. **CC0 asset libraries** (Poly Haven, the bundled Essentials library, BlenderKit) provide free production assets that bypass authoring entirely.

The agent's most common job: import an asset, set up materials, export to a real-time engine or DCC downstream. Get the format choice right and most other problems vanish.

**Core facts:**
- Most import/export operators are addons that ship with Blender but must be enabled in Preferences → Add-ons. If `bpy.ops.import_scene.fbx` returns `None` or errors, the addon is disabled.
- **FBX** is the cross-DCC workhorse for rigged + animated geometry. Strongest Maya/Max/Unity/Unreal support; weakest PBR material mapping.
- **glTF/GLB** is the modern standard for real-time pipelines (web, Unity, Unreal, TouchDesigner). Best PBR roundtrip in Blender — materials map cleanly to Principled BSDF.
- **USD** (Pixar's Universal Scene Description) is the rising studio-pipeline format. Blender's USD I/O has matured rapidly through 4.x.
- **Alembic** is for baked geometry caches — per-frame mesh data. Carries no shaders, no rigs. Use to hand off simulation output.
- **OBJ, STL, PLY** are geometry-only formats. OBJ for max compatibility, STL for 3D printing, PLY for photogrammetry / vertex colors.
- **.blend** files are the only format that preserves Blender-specific data (geometry nodes graphs, shader node trees, modifiers, drivers, NLA tracks).
- **Link** creates a read-only reference to a datablock in another .blend; the linked data updates when the source changes. **Append** is a deep copy — no source link, larger file.
- **Library overrides** make linked data partially editable — the modern replacement for proxies. Used to animate a linked rig without breaking the link.
- The **Asset Browser** (Blender 3.0+) is the unified asset-management UI. Mark any datablock as an asset, give it a preview + tags, expose it across all your .blend files via Preferences → File Paths → Asset Libraries.
- **Poly Haven** (polyhaven.com) is the de-facto free CC0 source for HDRIs, PBR textures, and models. All assets are CC0 — no attribution required.
- The **Essentials** asset library ships with Blender 4.0+ and lives in `[install]/4.x/datafiles/assets/` — basic materials, geometry node groups, brushes.
- Cross-app axis convention: Blender is **Z-up, -Y forward**. Unity, Unreal, TouchDesigner are **Y-up**. Either bake the axis transform on export or rotate on import.

---

## The Add-on Preferences Gate — Read This First

Most import/export `bpy.ops` calls require the matching addon to be enabled. Default install enables FBX, glTF, OBJ, STL, PLY, USD, Alembic — but the user may have disabled them, and some Linux/portable installs ship without them.

**Check what's enabled:**
```python
import bpy
addons = bpy.context.preferences.addons.keys()
print('FBX enabled:', 'io_scene_fbx' in addons)
print('glTF enabled:', 'io_scene_gltf2' in addons)
print('OBJ enabled:', 'io_scene_obj' in addons)  # 4.x: built-in C, no addon needed
print('USD enabled:', 'io_scene_usd' in addons)  # 4.x: built-in C, no addon needed
print('Alembic enabled:', 'io_scene_alembic' in addons)  # built-in C, no addon needed
```

**Enable an addon programmatically:**
```python
bpy.ops.preferences.addon_enable(module='io_scene_fbx')
bpy.ops.preferences.addon_enable(module='io_scene_gltf2')
# Save so the change persists across sessions
bpy.ops.wm.save_userpref()
```

**Module name reference:**
- FBX → `io_scene_fbx`
- glTF/GLB → `io_scene_gltf2`
- OBJ → built-in in 4.x (no module to enable, exposed under `bpy.ops.wm.obj_*`)
- USD → built-in in 4.x (`bpy.ops.wm.usd_*`)
- Alembic → built-in in 4.x (`bpy.ops.wm.alembic_*`)
- STL → built-in C operator in 4.x (`bpy.ops.wm.stl_*`)
- PLY → built-in C operator in 4.x (`bpy.ops.wm.ply_*`)

The 4.x rewrite moved OBJ, STL, PLY, USD, Alembic out of addon-Python and into native C operators under `bpy.ops.wm.*_import` / `bpy.ops.wm.*_export`. The legacy `bpy.ops.import_mesh.stl` paths still exist as deprecated aliases in some 4.x builds but should not be relied on.

---

## FBX — Cross-DCC Workhorse

`bpy.ops.import_scene.fbx(filepath='...')`
`bpy.ops.export_scene.fbx(filepath='...')`

FBX preserves armatures, animation, blend shapes, and broad material slots across Maya, Max, Cinema 4D, Unity, Unreal. Its weakness is PBR — Blender's Principled BSDF maps imperfectly to the FBX material model; expect to rebuild materials on the receiving side.

**Export — key params:**
- `filepath` — output path, must end `.fbx`.
- `use_selection` — export only selected objects. Default `False`.
- `use_visible` — export only visible objects.
- `object_types` — set of types: `{'MESH', 'ARMATURE', 'EMPTY', 'CAMERA', 'LIGHT', 'OTHER'}`.
- `use_mesh_modifiers` — apply modifier stack on export. Usually `True`.
- `mesh_smooth_type` — `'OFF'`, `'FACE'`, `'EDGE'`. Use `'FACE'` for hard-surface; engines read it as smoothing groups.
- `axis_forward` — `'-Z'` default. Unity expects `'-Z'`, Unreal expects `'X'`. Test the receiving side.
- `axis_up` — `'Y'` default. Almost always Y for non-Blender targets.
- `bake_space_transform` — bake the axis change into the geometry instead of as a root transform. Cleaner for game engines.
- `apply_unit_scale` — apply scene unit scale. Default `True`.
- `global_scale` — manual scale multiplier.
- `bake_anim` — export animation as baked keyframes. Default `True`.
- `bake_anim_use_all_bones` — include all bones in armature anim.
- `bake_anim_use_nla_strips` — flatten NLA into single take.
- `embed_textures` — embed image textures inside the .fbx (binary FBX only).
- `path_mode` — `'AUTO'`, `'COPY'`, `'ABSOLUTE'`, `'RELATIVE'`. `'COPY'` + `embed_textures=True` makes a self-contained file.

**Unity preset (rigged + animated character):**
```python
bpy.ops.export_scene.fbx(
    filepath='/out/char.fbx',
    use_selection=True,
    object_types={'MESH', 'ARMATURE'},
    use_mesh_modifiers=True,
    mesh_smooth_type='FACE',
    axis_forward='-Z',
    axis_up='Y',
    bake_space_transform=True,
    apply_unit_scale=True,
    bake_anim=True,
    bake_anim_use_all_bones=True,
)
```

**Import — key params:**
- `filepath` — input path.
- `use_anim` — read animation tracks. Default `True`.
- `use_custom_normals` — preserve custom normals (smoothing).
- `automatic_bone_orientation` — re-roll bones for Blender's convention. Recommended when importing Maya/Max rigs.
- `primary_bone_axis` / `secondary_bone_axis` — manual bone roll if `automatic_bone_orientation=False`.

**When FBX is best:** Maya/Max interop, Unity/Unreal animated characters, broad DCC compatibility. **When it falls short:** PBR material fidelity (expect to redo materials downstream), bleeding-edge geometry data (use glTF or USD instead).

---

## glTF / GLB — Modern Real-Time Standard

`bpy.ops.import_scene.gltf(filepath='...')`
`bpy.ops.export_scene.gltf(filepath='...')`

glTF 2.0 is the Khronos open standard for real-time 3D delivery. Blender's glTF I/O is **the** cleanest PBR roundtrip — Principled BSDF maps 1:1 to glTF's metallic-roughness model. This is the format for web (three.js, Babylon, model-viewer), Unity, Unreal, and TouchDesigner.

**.gltf vs .glb:**
- **.gltf** — JSON manifest + a folder of buffer (.bin) and texture (.png/.jpg) files. Human-readable, easier to inspect, larger on disk.
- **.glb** — single binary file containing JSON + buffers + textures. Self-contained, smaller, faster to load. **Use .glb unless you have a specific reason not to.**

**Export — key params:**
- `filepath` — output path.
- `export_format` — `'GLB'` (binary, recommended), `'GLTF_SEPARATE'` (manifest + folder), `'GLTF_EMBEDDED'` (JSON with base64-embedded binaries; rarely useful).
- `export_selected` / `use_selection` — export selected only (param name varies by version; check the Python tooltip in your build).
- `export_apply` — apply modifiers on export. **Almost always `True`** for real-time targets — otherwise modifier output is missing.
- `export_materials` — `'EXPORT'`, `'PLACEHOLDER'`, `'NONE'`.
- `export_animations` — include animation.
- `export_skins` — include armature skinning.
- `export_morph` — include shape keys (blend shapes).
- `export_cameras` / `export_lights` — include scene cameras / lights.
- `export_extras` — write custom properties as glTF extras.
- `export_yup` — convert Z-up to Y-up. **Default `True` — leave it on for real-time engines.**
- `export_texture_dir` — where to write textures for GLTF_SEPARATE mode.
- `export_image_format` — `'AUTO'`, `'JPEG'`, `'PNG'`, `'WEBP'`. AUTO picks per-image based on alpha.

**Standard real-time export:**
```python
bpy.ops.export_scene.gltf(
    filepath='/out/asset.glb',
    export_format='GLB',
    export_apply=True,
    export_materials='EXPORT',
    export_animations=True,
    export_yup=True,
)
```

**Khronos PBR Neutral / glTF 2.0 alignment:** Principled BSDF's Base Color, Metallic, Roughness, Normal, Emission, Alpha all map directly to glTF's `pbrMetallicRoughness` plus the standard extensions (`KHR_materials_emissive_strength`, `KHR_materials_transmission`, `KHR_materials_clearcoat`, etc.). Subsurface, sheen, and anisotropy partially supported via extensions.

**When glTF/GLB is best:** any real-time engine target, web delivery, materials must survive the trip, modern PBR pipelines. **Falls short on:** legacy DCCs (Max/Maya glTF import has caught up but not universal), some industrial/CAD targets.

---

## OBJ — Geometry Workhorse

`bpy.ops.wm.obj_import(filepath='...')`
`bpy.ops.wm.obj_export(filepath='...')`

OBJ is the lowest-common-denominator mesh format. Geometry + UVs + per-face material assignment via .mtl. No rigs, no animation, no PBR.

The 4.x C rewrite is **roughly 10x faster** than the legacy Python OBJ — large OBJ imports that took 30s in 3.x complete in 3s.

**Export — key params:**
- `filepath` — output `.obj` path.
- `export_selected_objects` — selection-only.
- `export_uv` — write UV coordinates. Default `True`.
- `export_normals` — write per-vertex normals.
- `export_materials` — write a paired .mtl file.
- `export_triangulated_mesh` — force triangulation. Use for engines that hate ngons.
- `export_smooth_groups` — write smoothing groups (`s 1`, `s off` lines).
- `forward_axis` — `'NEGATIVE_Z'` (default), `'X'`, `'Y'`, etc.
- `up_axis` — `'Y'` (default).
- `global_scale` — manual scale.
- `path_mode` — same options as FBX.

**Import — key params:**
- `import_vertex_groups` — read .obj vertex group encoding.
- `validate_meshes` — sanity check on import (recommended for unknown sources).
- `forward_axis` / `up_axis` — axis conversion at read time.

**When OBJ is best:** geometry-only handoff, max compatibility (everything reads OBJ), CAD output, sculpt exchange with ZBrush. **Falls short on:** anything with animation, complex materials, rigs. OBJ also merges materials by name on import — multiple slots with the same .mtl name collapse into one.

---

## USD — Studio Pipeline Format

`bpy.ops.wm.usd_import(filepath='...')`
`bpy.ops.wm.usd_export(filepath='...')`

Pixar's Universal Scene Description. The studio-pipeline format that Sony, Pixar, ILM, Apple (USDZ for AR) use as their interchange spine. Blender's USD support has matured rapidly through 4.x — 4.5 brings near-feature-parity with the major DCC implementations.

**What works in Blender's USD I/O (4.2+):**
- Mesh geometry, UVs, normals, vertex colors.
- Materials with Principled BSDF roundtrip via UsdPreviewSurface — limited but functional.
- Lights and cameras.
- Animation (transforms and skeletal).
- Instancing.
- USDZ archive format (zipped USD + assets, used for AR).
- Variants, references (read-side).
- Volumes (4.5+ improved support).

**What's spotty:**
- Complex shader networks beyond Principled-equivalent — round-trip lossy.
- Some bespoke modifiers — bake to mesh first.
- Geometry nodes output — generally requires `export_apply=True` equivalent (export evaluates the modifier).

**Export — key params:**
- `filepath` — `.usd`, `.usda` (ASCII), `.usdc` (binary), `.usdz` (zipped archive).
- `selected_objects_only` — selection-only.
- `visible_objects_only` — visibility filter.
- `export_animation` — animation range.
- `export_hair`, `export_uvmaps`, `export_normals`, `export_materials`.
- `generate_preview_surface` — write UsdPreviewSurface materials. Default `True`.
- `export_textures` — copy textures into a sibling folder / into the USDZ.
- `evaluation_mode` — `'RENDER'` or `'VIEWPORT'`. RENDER applies all modifiers including subdiv at render levels.

**Studio handoff:**
```python
bpy.ops.wm.usd_export(
    filepath='/out/shot_010.usdc',
    selected_objects_only=False,
    export_animation=True,
    generate_preview_surface=True,
    export_textures=True,
    evaluation_mode='RENDER',
)
```

**When USD is best:** studio pipelines, multi-DCC shot handoff, AR (USDZ), large scenes with instancing. **Falls short on:** small one-off real-time exports (overkill), shader fidelity to non-Pixar receivers.

---

## Alembic — Baked Geometry Cache

`bpy.ops.wm.alembic_import(filepath='...')`
`bpy.ops.wm.alembic_export(filepath='...')`

Alembic (.abc) is pure baked geometry over time. Every frame, the mesh vertex positions are stored — no rigs, no shaders, no procedural data. Use it to hand off the *result* of a simulation, deformation, or modifier stack to a downstream comp / render pipeline.

**Use cases:**
- Cloth or softbody sim baked for offline comp.
- Geometry nodes output handed to Houdini / Maya / Nuke.
- Crowd or particle deformations as final geometry.
- Capturing exact deformed state across an animation range for re-render in another renderer.

**Export — key params:**
- `filepath` — `.abc` path.
- `start` / `end` — frame range.
- `selected` — selection-only.
- `flatten` — flatten hierarchy into world-space.
- `uvs`, `normals`, `vcolors`, `face_sets` — geometry attribute toggles.
- `apply_subdiv` — bake subdivision surface output.
- `compression_type` — `'OGAWA'` (modern, default) or `'HDF5'` (legacy).
- `as_background_job` — run async without blocking UI.

**Standard sim cache export:**
```python
bpy.ops.wm.alembic_export(
    filepath='/out/sim.abc',
    start=1, end=240,
    selected=True,
    uvs=True, normals=True, vcolors=True,
    apply_subdiv=True,
)
```

**Cannot carry:** shaders, materials, rigs, drivers, anything procedural. Pure baked mesh + transforms over time. On the receiving side you reapply materials.

---

## STL — 3D Printing / CAD

`bpy.ops.wm.stl_import(filepath='...')`
`bpy.ops.wm.stl_export(filepath='...')`

STL is triangle soup — no UVs, no materials, no smoothing groups, no normal quality. It's the universal 3D printing format and a common CAD interchange.

**Export params:**
- `filepath` — `.stl`.
- `export_selected_objects` — selection-only.
- `ascii_format` — write ASCII STL (larger, human-readable) vs binary (default, smaller).
- `apply_modifiers` — apply modifier stack.
- `forward_axis`, `up_axis`, `global_scale`.

**Use case:** export to a slicer (Cura, PrusaSlicer, Bambu Studio) for 3D printing. Apply all modifiers, triangulate, single binary STL.

---

## PLY — Photogrammetry / Vertex Colors

`bpy.ops.wm.ply_import(filepath='...')`
`bpy.ops.wm.ply_export(filepath='...')`

PLY stores geometry + vertex colors + per-vertex attributes. Photogrammetry tools (RealityCapture, Meshroom, Polycam) typically export PLY because they need to carry per-vertex color. Useful import path for scan-based assets.

**Export params:**
- `filepath` — `.ply`.
- `export_selected_objects`.
- `export_uv`, `export_normals`, `export_colors` — attribute toggles.
- `ascii_format` — ASCII vs binary.
- `apply_modifiers`.

---

## Other Formats — Skim

- **VRM** — humanoid avatar standard used by VRChat, VTubing. Community addon (`VRM_Addon_for_Blender`). Layers on top of glTF.
- **DAE / Collada** — legacy XML interchange. `bpy.ops.wm.collada_import` / `collada_export`. Prefer glTF for new work; DAE only if a target tool demands it.
- **3DS** — Autodesk 3D Studio legacy. Don't use unless absolutely forced.
- **DXF** — CAD interchange (AutoCAD). Community addon. Curves and meshes only, no shading.
- **X3D / VRML** — legacy web 3D. Obsoleted by glTF.

---

## The .blend → .blend Pipeline — Link vs Append

The most powerful and most Blender-specific I/O path. Inside a .blend file you can reach into another .blend and pull a datablock — an Object, a Collection, a Material, a Node Group, anything in `bpy.data`.

### Link

`bpy.ops.wm.link(filepath='/path/lib.blend/Object/MyObj', filename='MyObj', directory='/path/lib.blend/Object/')`

Creates a **read-only reference** to the datablock in the source .blend. When the source changes and you reload, your file picks up the new data. Used for production pipelines — one master rig linked into 50 shot files. Smaller .blend files (no data is copied; only the reference is stored).

The path syntax is: `/path/to/library.blend/[Category]/[Name]` where `[Category]` is the bpy.data collection name (`Object`, `Collection`, `Material`, `NodeTree`, `Mesh`, `Image`, `World`, etc.).

### Append

`bpy.ops.wm.append(filepath='/path/lib.blend/Object/MyObj', filename='MyObj', directory='/path/lib.blend/Object/')`

**Deep copy.** Pulls the data into the current .blend, fully editable, with no connection to the source. Larger files, complete independence. Use for one-off imports of shared materials, node groups, or geometry where you don't need updates.

### Library Override

`bpy.ops.object.make_override_library()` (with the linked object selected)

The modern way to make linked data partially editable. Link a rig as a Collection. Make a library override on the collection. Now you can animate the rig, edit bone constraints, scale it — but the mesh and base rig structure stay linked. When the source mesh changes, your shots update; your animation on top stays.

This replaced the legacy "proxy" system in 2.8+.

### Python — `bpy.data.libraries.load`

The operator paths (`bpy.ops.wm.link`, `bpy.ops.wm.append`) require operator context (a UI), which makes them awkward in background scripts. The Python-friendly path:

```python
import bpy

# Append (link=False) or Link (link=True)
with bpy.data.libraries.load('/path/to/library.blend', link=False) as (src, dst):
    dst.objects = [name for name in src.objects if name.startswith('Hero_')]
    dst.materials = src.materials  # all materials

# After the with-block, dst.objects holds the imported Object datablocks
for obj in dst.objects:
    bpy.context.collection.objects.link(obj)  # add to active scene collection
```

This is the cleanest way to script .blend → .blend imports — no operator context needed, runs in headless `blender --background --python script.py`.

See `[[BLENDER_PYTHON_API]]` for the broader bpy.data patterns.

---

## The Asset Browser

Introduced in 3.0, the Asset Browser is Blender's unified asset-management UI. It shows datablocks across all configured asset libraries, lets you drag-drop them into scenes, and treats marked objects, materials, node groups, brushes, poses, and worlds as first-class browseable assets.

### Enabling an asset library

Preferences → File Paths → Asset Libraries. Add a folder. Any .blend inside that folder is scanned; any datablock marked as an asset shows up in the browser.

The Essentials library is pre-configured and points at the install directory.

### Marking a datablock as asset

Right-click the datablock in the Outliner → Mark as Asset. Or via Python:

```python
obj = bpy.data.objects['MyAsset']
obj.asset_mark()  # promotes it to an Asset

# Optional: generate a preview (this requires a 3D viewport context)
bpy.ops.ed.lib_id_generate_preview()

# Set metadata
obj.asset_data.description = "A useful prop"
obj.asset_data.tags.new("hero")
obj.asset_data.tags.new("indoor")
obj.asset_data.author = "Studio"
obj.asset_data.catalog_id = "..."  # UUID from the asset_catalogs.cats.txt
```

To unmark:

```python
obj.asset_clear()
```

`asset_mark()` works on Objects, Materials, NodeTrees, Worlds, Actions, Scenes, and more — any subclass of `ID` with the asset flag.

### Catalogs

A `blender_assets.cats.txt` file in the library root defines folder-tree catalogs (categories). The Asset Browser shows them as a hierarchy. Catalog IDs are UUIDs; the file maps `UUID:path/to/cat:DisplayName`.

### Preview render

The Asset Browser shows a thumbnail per asset. Generate one via `bpy.ops.ed.lib_id_generate_preview()` while the asset is active in a 3D viewport, or auto-render from the Asset Browser's drop-down.

---

## The Essentials Library

Blender 4.0+ ships with a small built-in library at `[install dir]/4.x/datafiles/assets/`. It's automatically configured as the **Essentials** asset library in Preferences.

Contents:
- A handful of starter PBR materials (metal, plastic, fabric).
- Geometry node groups for common operations (scatter, array, fillet).
- Sculpt and texture-paint brushes.
- A few HDRIs.

Use it as a sanity check — if Essentials assets appear in the Asset Browser, your library system works. If they don't, the path is wrong or the file index is stale (use the Refresh button).

---

## Poly Haven — CC0 Asset Source

Poly Haven (polyhaven.com) is the de-facto free CC0 asset library — HDRIs (over 700), PBR textures (over 1000), 3D models (over 500). Everything is **CC0 public domain** — no attribution required, commercial use allowed.

### Three workflows

**1. Direct download.** Open polyhaven.com, pick an asset, download the .hdr/.exr for HDRIs, the texture set zip for textures, the .blend or .glb for models. Drop into your project folder, link/append/import normally.

**2. Poly Haven Asset Browser add-on.** Community add-on that exposes Poly Haven inside Blender's Asset Browser. Browse and download directly into your scene. Install: download from polyhaven.com → install via Preferences → Add-ons → Install. Once installed, Poly Haven appears as an asset library.

**3. ahujasid/blender-mcp Poly Haven integration.** If running that community MCP server, the agent can query and download Poly Haven assets via tool calls without leaving the conversation. Tool names typically: `get_polyhaven_categories`, `search_polyhaven_assets`, `download_polyhaven_asset`. Confirm the integration is enabled in the MCP's settings before assuming it works.

### Asset categories

- **HDRIs** — environment lighting. .hdr (16-bit) or .exr (32-bit).
- **Textures** — PBR sets: Diffuse / Albedo, Normal, Roughness, Metallic, AO, Displacement, sometimes Specular. 1k / 2k / 4k / 8k options.
- **Models** — props, foliage, kit pieces. .blend (preserves materials) or .glb.

---

## HDRI Workflow

An HDRI (High Dynamic Range Image) is a 360° environment image used for image-based lighting. Format is typically .hdr (Radiance, 16-bit) or .exr (OpenEXR, 32-bit). Loaded into the World shader tree, an HDRI lights the entire scene with realistic environmental light.

### The canonical World node chain

```
[Texture Coordinate] → [Mapping] → [Environment Texture] → [Background] → [World Output]
                                                                          ↑
                                                                          (Strength: float)
```

- **Texture Coordinate** — supplies the `Generated` output, which is the direction vector for environment lookup.
- **Mapping** — rotates the HDRI around the scene. Adjust Z-rotation to spin the sun direction.
- **Environment Texture** — loads the .hdr or .exr. **Critical: set the image colorspace to `Non-Color` or `Linear`** (Blender often defaults to sRGB which crushes HDR values).
- **Background** — outputs the world light. Strength multiplies the HDRI brightness. Default 1.0; bump up for night HDRIs or dim ones.
- **World Output** — the world surface socket.

### Python — load an HDRI

```python
import bpy

world = bpy.context.scene.world
world.use_nodes = True
nt = world.node_tree
nt.nodes.clear()

tex_coord = nt.nodes.new('ShaderNodeTexCoord')
mapping = nt.nodes.new('ShaderNodeMapping')
env_tex = nt.nodes.new('ShaderNodeTexEnvironment')
bg = nt.nodes.new('ShaderNodeBackground')
out = nt.nodes.new('ShaderNodeOutputWorld')

img = bpy.data.images.load('/path/to/studio.exr')
img.colorspace_settings.name = 'Linear'  # CRITICAL — not sRGB
env_tex.image = img

nt.links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
nt.links.new(mapping.outputs['Vector'], env_tex.inputs['Vector'])
nt.links.new(env_tex.outputs['Color'], bg.inputs['Color'])
nt.links.new(bg.outputs['Background'], out.inputs['Surface'])

bg.inputs['Strength'].default_value = 1.0
```

### Sun rotation via Mapping

`mapping.inputs['Rotation'].default_value = (0, 0, math.radians(45))` rotates the HDRI 45° around Z, swinging the sun. In the viewport's World Preview, Ctrl+Drag rotates interactively.

### Recommended Poly Haven HDRIs by mood

- **Studio lighting:** `studio_small_*`, `photo_studio_*` — soft, neutral, predictable.
- **Sunset / golden hour:** `qwantani`, `kloofendal_43d_clear`, `je_gray_*`.
- **Overcast / soft:** `kloppenheim_06_puresky`, `overcast_soil_puresky`.
- **Night:** `moonlit_golf`, `dikhololo_night`, `kloofendal_38d_partly_cloudy_puresky` at low strength.

See `[[BLENDER_MATERIALS]]` for the broader shading context.

---

## Texture Set Imports — PBR Workflow

A PBR texture set is typically: **BaseColor / Albedo + Normal + Roughness + Metallic + AO** (and sometimes Displacement, Specular, Emission). Each map is a separate image file. Wiring them into a Principled BSDF takes 5+ nodes if done by hand.

### Manual workflow

1. Drag images into a Material's node editor as Image Texture nodes.
2. **Set colorspace per map:**
   - BaseColor / Albedo / Emission → **sRGB**.
   - Normal, Roughness, Metallic, AO, Displacement → **Non-Color**. Treating Non-Color maps as sRGB is the #1 PBR import bug.
3. Insert a Normal Map node between the Normal image and Principled's Normal input.
4. Link each map to the matching Principled input (Base Color, Roughness, Metallic, etc.).

### Node Wrangler shortcut — Ctrl+Shift+T

The Node Wrangler addon (ships with Blender, enable in Preferences → Add-ons) provides **Principled Texture Setup**. Select a Principled BSDF, press **Ctrl+Shift+T**, multi-select all texture files in the file browser. Node Wrangler:

- Creates Image Texture nodes for each file.
- Recognizes the filename suffix (`_Color`, `_Normal`, `_Roughness`, `_Metallic`, `_AO`, `_Disp`) and routes each map to the right Principled input.
- Sets colorspaces correctly per map type.
- Adds the Normal Map and Displacement nodes.

Works perfectly with Poly Haven texture sets — their naming follows the recognized convention.

See `[[BLENDER_ADDONS]]` for the full Node Wrangler reference.

---

## The bpy API — Paste-Ready Snippets

### Import / Export

```python
# FBX
bpy.ops.import_scene.fbx(filepath='/in/char.fbx')
bpy.ops.export_scene.fbx(filepath='/out/char.fbx', use_selection=True,
    axis_forward='-Z', axis_up='Y', bake_space_transform=True,
    use_mesh_modifiers=True, bake_anim=True)

# glTF / GLB
bpy.ops.import_scene.gltf(filepath='/in/asset.glb')
bpy.ops.export_scene.gltf(filepath='/out/asset.glb',
    export_format='GLB', export_apply=True,
    export_materials='EXPORT', export_animations=True)

# OBJ
bpy.ops.wm.obj_import(filepath='/in/mesh.obj')
bpy.ops.wm.obj_export(filepath='/out/mesh.obj',
    export_selected_objects=True, export_materials=True,
    export_triangulated_mesh=True)

# USD
bpy.ops.wm.usd_import(filepath='/in/shot.usd')
bpy.ops.wm.usd_export(filepath='/out/shot.usdc',
    selected_objects_only=False, export_animation=True,
    generate_preview_surface=True, export_textures=True)

# Alembic
bpy.ops.wm.alembic_import(filepath='/in/sim.abc')
bpy.ops.wm.alembic_export(filepath='/out/sim.abc',
    start=1, end=240, selected=True, uvs=True, normals=True)

# STL
bpy.ops.wm.stl_import(filepath='/in/part.stl')
bpy.ops.wm.stl_export(filepath='/out/part.stl',
    export_selected_objects=True, apply_modifiers=True)

# PLY
bpy.ops.wm.ply_import(filepath='/in/scan.ply')
bpy.ops.wm.ply_export(filepath='/out/scan.ply',
    export_colors=True, export_normals=True)
```

### Asset marking

```python
# Mark / unmark
obj = bpy.data.objects['Prop']
obj.asset_mark()
obj.asset_clear()

mat = bpy.data.materials['Concrete']
mat.asset_mark()

ng = bpy.data.node_groups['Scatter']
ng.asset_mark()

# Metadata
obj.asset_data.description = "Concrete bollard, hero-scale"
obj.asset_data.tags.new("street")
obj.asset_data.tags.new("hero")
obj.asset_data.author = "Studio"
```

### Link / Append via `bpy.data.libraries.load`

```python
# Append a Collection
with bpy.data.libraries.load('/lib/props.blend', link=False) as (src, dst):
    dst.collections = ['Hero_Props']
for col in dst.collections:
    bpy.context.scene.collection.children.link(col)

# Link a single Material
with bpy.data.libraries.load('/lib/materials.blend', link=True) as (src, dst):
    dst.materials = ['Master_Metal']
# The linked material is now in bpy.data.materials and assignable

# Link an Object then make a library override
with bpy.data.libraries.load('/lib/rig.blend', link=True) as (src, dst):
    dst.objects = ['Hero_Rig']
for obj in dst.objects:
    bpy.context.scene.collection.objects.link(obj)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
bpy.ops.object.make_override_library()
```

### Image / texture reload

```python
img = bpy.data.images.load('/textures/concrete_diff.png')
img.colorspace_settings.name = 'sRGB'  # color map
# vs:
img_n = bpy.data.images.load('/textures/concrete_normal.png')
img_n.colorspace_settings.name = 'Non-Color'

# If the file on disk changes, reload (changing .source = 'FILE' does NOT reload):
img.reload()
```

---

## The Blender → Real-Time Engine Pipeline

For engines like TouchDesigner, Unity, Unreal, three.js — the agent picks the format based on what data needs to survive the trip.

### Static geometry with materials

**Format:** GLB.
**Why:** Cleanest PBR roundtrip, single-file binary, modifiers baked.

```python
bpy.ops.export_scene.gltf(
    filepath='/out/asset.glb',
    export_format='GLB',
    export_apply=True,         # bake modifiers
    export_materials='EXPORT',
    export_yup=True,           # convert Z-up → Y-up
)
```

### Animated baked geometry (sim cache, deformed mesh sequence)

**Format:** Alembic.
**Why:** Per-frame vertex data, no rig required, TD's pointFile/Alembic SOPs read it natively.

```python
bpy.ops.wm.alembic_export(
    filepath='/out/sim.abc',
    start=1, end=240, selected=True,
)
```

### Rigged + animated character

**Format:** FBX or GLB.
**Why:** FBX has more mature rigging support in Unity/Unreal. GLB works for simpler skeletons and is cleaner for materials.

```python
# Unity-bound FBX
bpy.ops.export_scene.fbx(
    filepath='/out/char.fbx',
    object_types={'MESH', 'ARMATURE'},
    axis_forward='-Z', axis_up='Y',
    bake_space_transform=True, use_mesh_modifiers=True,
    bake_anim=True, bake_anim_use_all_bones=True,
)
```

### Pre-rendered video (out-of-engine final pixels)

Render frames in Cycles or EEVEE → encode to video → load in TD. See `[[BLENDER_WORKFLOW_RENDER_FOR_TD]]` for the full render → comp → video pipeline.

### Axis convention — Blender Z-up vs target Y-up

Blender is Z-up, -Y forward. Unity, Unreal, TD, three.js are Y-up.

- **GLB:** set `export_yup=True` (default). Done.
- **FBX:** set `axis_up='Y'`, `axis_forward='-Z'`, `bake_space_transform=True` to bake the transform into the geometry instead of leaving it as a root rotation.
- **OBJ:** set `forward_axis='NEGATIVE_Z'`, `up_axis='Y'`.
- **Alternative:** rotate on import inside the receiving engine.

See `[[BLENDER_WORKFLOW_ASSET_FOR_TD]]` for the full WOBAR-flavored handoff.

---

## Common Recipes

### Static asset → real-time engine

```python
# 1. Apply transforms (rotation/scale to 1)
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

# 2. Apply modifiers — done as part of export via export_apply=True

# 3. Export
bpy.ops.export_scene.gltf(
    filepath='/out/prop.glb', export_format='GLB',
    export_apply=True, export_materials='EXPORT', export_yup=True,
)
```

### Animated character → Unity

```python
bpy.ops.export_scene.fbx(
    filepath='/out/char.fbx',
    use_selection=True,
    object_types={'MESH', 'ARMATURE'},
    axis_forward='-Z', axis_up='Y',
    apply_unit_scale=True,
    bake_space_transform=True,
    use_mesh_modifiers=True,
    bake_anim=True, bake_anim_use_all_bones=True,
    add_leaf_bones=False,  # Unity prefers no leaf bones
)
```

### Sim cache → downstream comp

```python
bpy.ops.wm.alembic_export(
    filepath='/out/sim.abc',
    start=1, end=240,
    selected=True,
    uvs=True, normals=True, vcolors=True,
    apply_subdiv=True,
)
```

### Import a Poly Haven HDRI

```python
img = bpy.data.images.load('/hdris/studio_small.exr')
img.colorspace_settings.name = 'Linear'
world = bpy.context.scene.world
world.use_nodes = True
env = world.node_tree.nodes.get('Environment Texture') or \
      world.node_tree.nodes.new('ShaderNodeTexEnvironment')
env.image = img
```

### Link a master rig and override for animation

```python
with bpy.data.libraries.load('/lib/master_rig.blend', link=True) as (src, dst):
    dst.collections = ['Hero_Rig']
for col in dst.collections:
    bpy.context.scene.collection.children.link(col)

# Select the collection's root empty / armature, then:
bpy.ops.object.make_override_library()
# Now animatable; mesh stays linked
```

---

## Common Footguns

- **Forgot to enable the addon.** `bpy.ops.import_scene.fbx` returns `None` or raises `AttributeError`. Fix: `bpy.ops.preferences.addon_enable(module='io_scene_fbx')`. Check first with `'io_scene_fbx' in bpy.context.preferences.addons.keys()`.
- **FBX axis flip ruining a Unity / Unreal export.** Unity wants `axis_forward='-Z'`, `axis_up='Y'`, `bake_space_transform=True`. Unreal wants `axis_forward='X'`, `axis_up='Z'` (and Unreal's FBX importer re-rotates). Always test the receiving side; never assume Blender's defaults work for the target.
- **GLB without `export_apply=True`.** Modifiers (Subsurf, Mirror, Array, Geometry Nodes) don't carry through glTF — only base mesh data does. Without apply, the receiving engine sees the un-modifiered cage. Always `export_apply=True` for real-time targets unless you specifically want pre-modifier geometry.
- **HDRI loaded in sRGB colorspace.** Default colorspace for new image datablocks is sRGB; loading an .exr or .hdr as sRGB crushes the high-dynamic-range values. Set `img.colorspace_settings.name = 'Linear'` (or `'Non-Color'` in older Blender versions).
- **Appending when you meant to link.** Appending a 200MB asset library bloats your .blend by 200MB and breaks updates. Default to link; only append when you need full independence.
- **Library override applied to a Library instead of a Collection / Object.** Library overrides need a concrete datablock as the target — Object, Collection, or Material. Selecting the library file itself in the Outliner and trying to override does nothing useful.
- **Asset Browser not showing custom assets.** Check Preferences → File Paths → Asset Libraries — path must point to a folder containing .blend files with marked assets. Refresh the Asset Browser. If using a network drive, ensure it's mounted.
- **OBJ merging materials by name.** OBJ identifies materials by name in the .mtl. Two slots called "Material" collapse to one on import. Rename slots before exporting; don't ship default-named materials.
- **USD Principled mapping varies per receiving app.** Blender → Houdini USD will read most channels; Blender → Maya USD may lose some. Always do a roundtrip test before committing a shot to USD handoff.
- **`bpy.data.images[name].source = 'FILE'` doesn't reload from disk.** It only changes the source-type metadata. Call `img.reload()` to actually re-read the file.
- **Multiple meshes with the same name on import.** Blender appends `.001`, `.002` to duplicate names. After importing several FBXs, you may end up with `Material.001`, `Material.002`. Rename or dedupe before exporting downstream.
- **Asset preview never rendered.** A marked asset with no preview shows a blank tile in the Asset Browser. Either render previews via the Asset Browser dropdown or call `bpy.ops.ed.lib_id_generate_preview()` while the asset is selected in a 3D viewport.
- **`export_yup=False` on a GLB and then wondering why everything is sideways in TD / Unity.** Leave `export_yup=True` for real-time engine targets.
- **Linked library path is absolute and breaks on another machine.** Use Make Paths Relative (`bpy.ops.file.make_paths_relative()`) before committing to source control.
- **Library override edits lost after a re-link.** Overrides survive most edits but a structural change in the source (renamed bones, removed objects) can orphan them. Keep override scope narrow — only override what you need to edit.

---

## See Also

- `[[BLENDER_PYTHON_API]]` — the bpy data model and operator context patterns these snippets sit on.
- `[[BLENDER_DATA_MODEL]]` — how datablocks, libraries, and overrides fit together.
- `[[BLENDER_MATERIALS]]` — Principled BSDF and shader graph patterns that glTF / USD round-trip through.
- `[[BLENDER_ADDONS]]` — Node Wrangler, the bundled importers, and the Poly Haven addon.
- `[[BLENDER_WORKFLOW_ASSET_FOR_TD]]` — concrete asset-handoff recipes for the Blender → TouchDesigner path.
- `[[BLENDER_WORKFLOW_RENDER_FOR_TD]]` — the pre-rendered video alternative when geometry handoff isn't appropriate.
