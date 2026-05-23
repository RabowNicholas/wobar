---
title: Workflow — Building Assets in Blender for Live Real-Time-Engine Consumption
version: 1.0
last_updated: 2026-05-22
status: live
scope: Producing 3D assets (meshes + materials + textures) in Blender that will be loaded live by a real-time engine (TouchDesigner via geo SOP / Geometry COMP, Resolume's Wire). Format choice (GLB vs FBX), axis/scale conventions, topology guidance, material conversion (Principled → glTF PBR), naming, the bpy export API surface.
dependencies: BLENDER_LIBRARY_INDEX.md, BLENDER_ASSET_IO.md, BLENDER_MODELING.md, BLENDER_MATERIALS.md, BLENDER_GEOMETRY_NODES.md
---

# WORKFLOW — BUILDING ASSETS IN BLENDER FOR LIVE REAL-TIME-ENGINE CONSUMPTION

This file covers the **live asset pipeline** — you author a 3D asset (mesh + materials + textures, optionally with animation) in Blender, export it as a file, and the destination real-time engine loads that file at runtime and lights / animates / composites it itself. The mesh ships cold; the engine owns the look from there.

The other Blender → TD path is **rendered footage** — see [[BLENDER_WORKFLOW_RENDER_FOR_TD]]. There you render the asset in Cycles/EEVEE inside Blender and ship a video file that the engine plays back as a texture. The two paths are complementary, not interchangeable:

- **Live asset (this file)** — interactive, parametric, cheap GPU cost, but limited to what the destination's PBR renderer can do.
- **Rendered footage** — full Cycles fidelity (volumetrics, SSS, complex GI), but baked-in lighting and a fixed camera.

Target destination throughout: **TouchDesigner** via the `geo SOP` / `Geometry COMP` and `pbrMAT`. Secondary destinations (Resolume's Wire, Unity, Unreal) follow the same conventions because they all consume glTF/FBX.

**Core facts:**

- TD reads meshes via the **`geo SOP`** (file path field, supports FBX/OBJ) or the **`Geometry COMP`** with imported geometry as its child SOP. The `Geometry COMP` is the scene-graph node — transform, material assignment, render-flags all live here.
- **GLB is the cleanest carrier** for PBR materials end-to-end. It's a single binary file containing geometry + materials + embedded textures, defined by the glTF 2.0 spec which maps cleanly to TD's `pbrMAT`.
- **FBX is the universal-but-brittle option.** Geometry and rigs survive; PBR materials roundtrip badly. Use when GLB fails or for geometry-only work into an engine that doesn't take GLB.
- **OBJ is pure geometry.** No animation, no materials beyond a basic MTL. Use for static reference meshes only.
- **TD uses Y-up, Blender uses Z-up.** The glTF spec is Y-up so the GLB exporter handles the axis flip automatically. FBX you have to declare. OBJ has no convention so you guess.
- **Scale unit consistency** matters once you start parenting / instancing — mismatched units cause objects to be 100x or 0.01x the expected size. Blender default = 1 BU = 1 meter; TD default = 1 unit = 1 meter; line them up.
- **Topology should be quad-friendly or explicitly triangulated.** Real-time engines triangulate internally; doing it yourself on export removes ambiguity in vertex normal interpolation.
- **TD materials are PBR via `pbrMAT`** — base color, metallic, roughness, normal, emission, ambient occlusion. This is roughly the Principled BSDF surface minus the exotic lobes.
- **Light is set in the destination engine, not in Blender.** Your Blender lights don't export into GLB usefully, and even when they do (the glTF lights extension) TD ignores them. Build lights in TD's `Light COMP`.
- **The Blender camera doesn't export either.** TD owns its own `Camera COMP`.
- **Modifiers don't roundtrip.** Subdivision Surface, Bevel, Mirror, Array, Boolean — none survive export. Either apply them before export (best) or let the GLB exporter bake them via `export_apply=True`.
- **Geometry Nodes don't roundtrip either** — apply the GN modifier first, which realizes the procedural geometry into static mesh data the exporter can write.
- **Animation in GLB** is limited to skeletal (armature) and shapekey tracks. Constraint-driven, physics-baked, or modifier-driven animation must be baked to keyframes first via Object → Animation → Bake Action.

---

## Format Choice — GLB vs FBX vs OBJ vs USD vs Alembic

For the live-asset path, format choice is the single most consequential decision. Pick once per project; don't mix.

### GLB (preferred for TD)

A single binary file containing geometry, materials, embedded textures, and optional animation. Defined by the glTF 2.0 spec (Khronos Group).

- **Pros:** materials roundtrip cleanly via the spec's metallic-roughness PBR model; textures are embedded so no file-path breakage; Y-up convention matches TD; small file size (binary, optionally Draco-compressed); the modern format with the most active tooling.
- **Cons:** exotic Principled BSDF lobes (subsurface, sheen, coat, anisotropic, transmission) are lost; some animation features (constraints, drivers) require baking first.
- **Export:** `bpy.ops.export_scene.gltf(filepath='...', export_format='GLB')`.
- **TD consumption:** `geo SOP` with the .glb path, or `Geometry COMP` → import GLB via the File menu / drag-drop.

### FBX

Autodesk's interchange format. Universal in DCC pipelines (Maya, Max, MotionBuilder, Unity, Unreal).

- **Pros:** broadest cross-app support; rigs and animation survive; widely understood by every tool.
- **Cons:** PBR material support is inconsistent across exporters; binary format is proprietary; texture paths can break; axis convention is per-exporter so you have to set it explicitly.
- **Export:** `bpy.ops.export_scene.fbx(filepath='...', axis_forward='-Z', axis_up='Y')`.
- **Use when:** GLB fails, or the destination only takes FBX, or you need to hit a Maya/Max-based downstream stage.

### OBJ

Wavefront's plain-text geometry format from 1992.

- **Pros:** human-readable; absolutely universal; no animation = no animation bugs.
- **Cons:** geometry only; the MTL file alongside it carries Phong-style materials, not PBR; no animation; no rigs; no instancing.
- **Use when:** static reference geometry, photogrammetry handoff, or as a last-resort lowest-common-denominator dump. Never as a final pipeline output for PBR work.

### USD

Pixar's Universal Scene Description. Studio-pipeline format, rising fast.

- **Pros:** scene-graph composition, layering, variants, references — far richer than glTF; first-class material support via UsdPreviewSurface (a PBR model nearly identical to glTF's).
- **Cons:** TD's USD support varies by version; some engines treat USD as static-scene-only.
- **Verify with a test asset first.** Don't commit a pipeline to USD without confirming the destination actually reads what you wrote.

### Alembic

Baked geometry caches — per-frame vertex positions for simulated / animated meshes.

- **Pros:** the only sane way to ship cloth, fluid, soft-body, or any non-skeletal simulated geometry into a real-time engine.
- **Cons:** carries no materials, no shaders, no rigs. File size grows linearly with frame count and vertex count.
- **TD consumption:** `geo SOP` with Alembic file path; per-frame mesh swap during playback.

**Default choice for TD live-asset pipeline: GLB.** Reach for FBX only when GLB fails or the destination explicitly demands it. Reach for Alembic only when shipping simulation. Everything else is a special case.

---

## Axis and Scale

Blender is **Z-up, -Y forward.** TouchDesigner (and Unity, Unreal, Resolume) are **Y-up, -Z forward.** This mismatch must be resolved at exactly one stage of the pipeline — pick one and stick to it.

Three resolution paths:

### Path A — Let GLB handle it (recommended)

The glTF 2.0 spec mandates Y-up. The Blender glTF exporter knows this and applies the rotation automatically on export. You author in Z-up, the file is written Y-up, TD reads it Y-up, and the orientation in TD's viewport matches your orientation in Blender's viewport.

**No flags to set.** The default `export_format='GLB'` already does the right thing.

### Path B — FBX with explicit axis flags

The FBX exporter doesn't auto-rotate. You declare the destination axis convention as exporter args:

```python
bpy.ops.export_scene.fbx(
    filepath='/path/to/asset.fbx',
    axis_forward='-Z',
    axis_up='Y',
    apply_unit_scale=True,
    bake_space_transform=True,
)
```

`bake_space_transform=True` writes the rotation into the mesh data itself, so the destination doesn't need to apply a transform on import. Verify with a test asset — FBX axis behavior varies subtly between Blender minor versions.

### Path C — Rotate inside TD

Import as-is and apply a **90° rotation on the X-axis** at the `Geometry COMP` level. This works but adds a permanent transform every consumer of the asset has to know about. Avoid unless paths A and B both fail.

**Recommendation:** GLB with default settings. The axis dance is handled, you forget it exists, and every downstream tool agrees on orientation.

---

## Scale Unit

Blender's unit system lives on `bpy.context.scene.unit_settings`. Defaults are fine for most work; verify before exporting if you've ever touched them:

```python
import bpy
scene = bpy.context.scene
print(scene.unit_settings.system)       # 'METRIC' (default)
print(scene.unit_settings.scale_length) # 1.0 (default — 1 Blender unit = 1 meter)
print(scene.unit_settings.length_unit)  # 'METERS' (default display unit)
```

- **METRIC + scale_length=1.0** is the canonical setup for real-time export. 1 BU = 1 meter, matches TD's default 1 unit = 1 meter, matches glTF's spec which assumes meters.
- **scale_length != 1.0** means your unit system displays one thing but writes another to file. Set it back to 1.0 unless you have a reason.
- **Use the `apply_unit_scale=True` flag** on FBX export to bake the unit scale into the exported coordinates. GLB doesn't need this — it always writes meters.

Consistency matters most when **parenting and instancing** — a parent at scale 100 with a child at scale 0.01 looks right in Blender but on export the world-space scale is what gets written, and that's the number TD interprets.

---

## Topology Guidance for Live-Asset Consumption

TD itself doesn't care about quads vs tris — the GPU rasterizer triangulates everything at draw time. But several Blender-side topology decisions affect what the destination sees:

- **Triangulate before export** if you want determinism on UV interpolation and vertex normal shading. Add a Triangulate modifier or apply Ctrl+T in Edit Mode. Otherwise the exporter / engine triangulates and the diagonal choice may differ from what you saw in Blender.
- **N-gons are illegal** in most real-time pipelines. The exporter will triangulate them but the triangulation can be visually surprising. Triangulate manually first if you want predictable results.
- **Edge loops at silhouettes** for clean shading. The destination engine uses your vertex normals; sparse topology at curved silhouettes gives faceted shading even with smooth-shading enabled.
- **Vertex count budget.** TD on Apple Silicon (M1/M2/M3) handles roughly 1M triangles for static geometry without breaking a sweat. Dynamic / instanced geometry drops the budget by 10x or more. Keep individual assets in the 5k–200k tri range for headroom.
- **Subdivision Surface modifier must be applied (or baked via `export_apply=True`) before export.** Without it the destination sees the low-poly cage, not the smooth result.
- **UV maps must exist on every face** the materials use. Missing UVs → texture sampler reads garbage → flat color or undefined behavior in TD.
- **Vertex normals should be sane.** If you've been manually editing custom normals, verify they export — the Blender → glTF normal export is solid but some hand-painted normal setups confuse FBX.
- **Smooth vs flat shading** is per-face data that does export. Set explicitly in Edit Mode (Mesh → Shade Smooth / Shade Flat) before export.

---

## Materials — Principled BSDF to glTF PBR Mapping

The Blender glTF exporter maps Principled BSDF inputs to the glTF 2.0 metallic-roughness PBR model. The mapping is well-defined but lossy — anything outside the metallic-roughness model gets dropped or baked into the closest equivalent.

### What roundtrips cleanly

| Principled BSDF input | glTF target | Notes |
|---|---|---|
| Base Color | `baseColorFactor` / `baseColorTexture` | Direct map. RGBA. |
| Metallic | `metallicFactor` / `metallicRoughnessTexture` (B channel) | Blue channel of the combined metallicRoughness texture. |
| Roughness | `metallicRoughnessTexture` (G channel) | Green channel. |
| Normal | `normalTexture` | Tangent-space normals. Set the texture to Non-Color. |
| Emission | `emissiveFactor` / `emissiveTexture` | RGB. |
| Emission Strength | `KHR_materials_emissive_strength` extension | Optional extension — destination must support it. |
| Alpha | `alphaCutoff` (Clip mode) or `alphaMode='BLEND'` | Set in the material's Blend Mode dropdown before export. |
| Occlusion (separate texture node) | `occlusionTexture` | Pack into the R channel of the metallicRoughness texture for ORM packing. |

### What does NOT roundtrip

These Principled BSDF lobes are **dropped on GLB export**:

- **Subsurface** — color, scale, radius, IOR, anisotropy
- **Sheen** — weight, tint, roughness
- **Coat** — weight, roughness, IOR, tint, normal
- **Anisotropic** — anisotropic, anisotropic rotation
- **Transmission** — weight, roughness (some experimental glTF extensions exist; TD doesn't support them)
- **IOR** — index of refraction

TD's `pbrMAT` accepts: base color, normal, metallic, roughness, emissive, ambient occlusion. **That's the whole surface.** Anything not in that list either gets baked into base color (rough approximation) or is gone.

**Workflow implications:**

- **Bake exotic lobes into base color or emission** if the look depends on them. A glass material → bake the transmission look into base color + emission as a hack.
- **Or accept the loss** and re-author the look in TD via post-process compositing.
- **Don't author in Cycles-only features** and expect TD to display them.

---

## Textures — sRGB vs Non-Color

Same convention as in [[BLENDER_MATERIALS]], enforced by the glTF spec:

- **Base Color** — **sRGB** colorspace. The exporter writes the sRGB curve into the file metadata.
- **Roughness / Metallic / Normal / Ambient Occlusion** — **Non-Color** (Linear). These are data textures, not color. sRGB curves applied to data textures = wrong values.
- **Emission** — **sRGB** (it's color light).

In Blender's Shader Editor, set the Image Texture node's Color Space dropdown explicitly. In TD's Texture TOP / `pbrMAT`, the colorspace setting must match what the file says. The glTF spec encodes this in the file so TD reads it correctly by default; FBX has no such convention so you set it manually on both sides.

---

## The `export_apply` Flag

The GLB exporter has an `export_apply` flag that bakes the modifier stack into the exported mesh:

```python
bpy.ops.export_scene.gltf(
    filepath='/path/to/asset.glb',
    export_format='GLB',
    export_apply=True,  # bake modifiers (Subsurf, Mirror, Array, Bevel, Boolean) into the mesh
)
```

**Always `True`** unless you have a specific reason to preserve the modifier stack — and you usually don't, because the destination (TD, Unity, Resolume) doesn't have your modifiers anyway. With `export_apply=False`, a cube with a Subsurf modifier exports as an 8-vertex cube, not the smooth subdivided mesh you see in the viewport.

Exception: if you're handing the GLB to another Blender install via append/link, you might want the modifiers preserved — but at that point use a .blend file, not GLB.

---

## Animation in the Live-Asset Pipeline

GLB supports two animation modes:

- **Skeletal animation** — armature + bones + skinned mesh + actions. Exported via `export_animations=True` and `export_skins=True`.
- **Shapekey (morph target) animation** — per-shapekey value keyframes. Exported automatically with `export_animations=True`.

TD's GLB loader reads both. You trigger playback via the `Geometry COMP`'s animation params or via tscript.

**Limitations:**

- **Constraint-driven animation** (Track To, Copy Rotation, Damped Track, etc.) — must be **baked to keyframes** first via Object → Animation → Bake Action. The constraints themselves don't export.
- **Driver-based animation** — same deal. Bake first.
- **Physics simulations** (rigid body, cloth, soft body) — bake to keyframes if the topology is stable, otherwise use Alembic for per-frame mesh data.
- **Geometry Nodes animation** — apply the GN modifier first, which freezes the procedural result at one frame. If the GN graph is time-varying, you can't ship it as a live asset; render to video instead via [[BLENDER_WORKFLOW_RENDER_FOR_TD]].

For **procedural / parametric animation in TD**, prefer to export the static mesh and animate via TD's instancing / transform / displacement. The asset is the building block; the engine drives the motion.

For **baked simulations** where topology may not be stable across frames, ship Alembic. GLB skeletal/shapekey animation assumes vertex count never changes.

---

## Asset Naming Conventions

Names propagate through the pipeline. Choose them in Blender; TD reads what you wrote.

- **Object name** (`obj.name` in Blender, before export) → the object identifier inside the GLB → the node name TD exposes in the `Geometry COMP`.
- **Mesh name** (`obj.data.name`, the data-block name distinct from the object) → glTF mesh name.
- **Material name** (`mat.name`) → glTF material name → the identifier TD uses when looking up the `pbrMAT` reference.
- **Image name** (`img.name`) → glTF image name when textures are embedded.

**Rules:**

- **Use `snake_case` or `kebab-case`.** Both survive every format. Pick one and stick to it across the project.
- **No spaces.** Spaces in material names are a top-three cause of glTF parsing failures and TD path-lookup bugs.
- **No special characters.** No `/`, `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|`, `.`, or unicode. Stick to `[a-z0-9_-]`.
- **Be descriptive.** `Cube.001.material.002` tells the agent nothing. `crystal_shard_emissive` tells it everything.
- **Match across Blender ↔ TD.** If TD's network refers to a material called `glow_blue`, the Blender material must be named `glow_blue` — exact case, exact spelling.
- **Clean up `.001`, `.002` duplicates** before export. Blender appends these silently when a name collides. They cause confusion downstream.

---

## The Blender → TD Round-Trip Test

The minimum-viable pipeline test, run once at the start of every new project:

1. **In Blender:** add a default Cube. Add a new Material. Switch Principled BSDF's Base Color to red (`1.0, 0.0, 0.0`). Save the .blend.
2. **Export:** `File → Export → glTF 2.0 (.glb)` with default settings, or `bpy.ops.export_scene.gltf(filepath='/path/test_cube.glb', export_format='GLB', export_apply=True)`.
3. **In TD:** create a new project. Drop a `Geometry COMP`. Inside it, add a `geo` SOP and point its File field at `/path/test_cube.glb`. Add a `pbrMAT` and assign the cube's material to it. Wire `Geometry COMP` into a `Render TOP` with a `Camera COMP` and a `Light COMP`.
4. **Verify:** the cube renders red in TD's viewport, oriented the same as in Blender, at the same scale.

**If broken — diagnosis order:**

- **Object missing entirely** → check the file path; check `use_selection=False` if you only meant to export specific objects.
- **Object present but wrong orientation** → axis convention mismatch. GLB should be automatic; FBX needs explicit `axis_forward='-Z', axis_up='Y'`.
- **Object present, oriented right, but black / flat-shaded** → material didn't roundtrip. Check `export_materials='EXPORT'` (not `'NONE'` or `'PLACEHOLDER'`).
- **Object present, materials too, but wrong color** → texture colorspace mismatch. Base Color must be sRGB, data textures must be Non-Color.
- **Object present at 0.01x or 100x scale** → unit scale mismatch. Verify `scene.unit_settings.scale_length == 1.0`.

---

## The bpy API for Asset Export

Paste-ready snippets. All target Blender 4.2+ / 4.5+.

### GLB export with applied modifiers and materials

```python
import bpy

bpy.ops.export_scene.gltf(
    filepath='/path/to/asset.glb',
    export_format='GLB',
    export_apply=True,            # bake modifiers into mesh
    export_materials='EXPORT',    # include materials
    export_image_format='AUTO',   # PNG for sRGB / lossless, JPEG where lossy is fine
    export_animations=True,       # include animation tracks
    export_skins=True,            # include armature skinning
    export_morph=True,            # include shapekeys
    export_yup=True,              # default — write Y-up
)
```

### FBX export with TD-friendly axis

```python
import bpy

bpy.ops.export_scene.fbx(
    filepath='/path/to/asset.fbx',
    use_selection=False,
    axis_forward='-Z',
    axis_up='Y',
    apply_unit_scale=True,
    bake_space_transform=True,
    mesh_smooth_type='FACE',
    use_mesh_modifiers=True,      # bake modifiers
    add_leaf_bones=False,         # avoid extra null bones in armatures
    bake_anim=True,
    bake_anim_use_all_actions=True,
)
```

### Single-object export

```python
import bpy

target_obj_name = 'crystal_shard'

# Deselect all, select only the target
bpy.ops.object.select_all(action='DESELECT')
obj = bpy.data.objects[target_obj_name]
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

bpy.ops.export_scene.gltf(
    filepath=f'/path/to/{target_obj_name}.glb',
    export_format='GLB',
    use_selection=True,
    export_apply=True,
)
```

### Collection export

```python
import bpy

collection_name = 'export_set'
collection = bpy.data.collections[collection_name]

# Select everything in the collection
bpy.ops.object.select_all(action='DESELECT')
for obj in collection.all_objects:
    obj.select_set(True)

bpy.ops.export_scene.gltf(
    filepath=f'/path/to/{collection_name}.glb',
    export_format='GLB',
    use_selection=True,
    export_apply=True,
)
```

### Strip armature when destination doesn't need it

```python
import bpy

# Temporarily unparent meshes from armatures for static export
for obj in bpy.context.selected_objects:
    if obj.parent and obj.parent.type == 'ARMATURE':
        obj.parent = None

bpy.ops.export_scene.gltf(
    filepath='/path/to/static_asset.glb',
    export_format='GLB',
    export_skins=False,
    export_animations=False,
    use_selection=True,
    export_apply=True,
)
```

### Batch export — one GLB per object

```python
import bpy
import os

out_dir = '/path/to/exports/'
os.makedirs(out_dir, exist_ok=True)

original_selection = list(bpy.context.selected_objects)

for obj in original_selection:
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    safe_name = obj.name.lower().replace(' ', '_')
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(out_dir, f'{safe_name}.glb'),
        export_format='GLB',
        use_selection=True,
        export_apply=True,
    )

# Restore original selection
bpy.ops.object.select_all(action='DESELECT')
for obj in original_selection:
    obj.select_set(True)
```

---

## Common Asset Workflow Recipes

### Recipe 1 — Single static mesh with PBR materials

The bread-and-butter case. Author a mesh, give it a Principled BSDF material, export GLB.

1. Model in Edit Mode. Apply Subsurf / Bevel / Mirror modifiers via Object → Apply → Visual Geometry to Mesh (or use `export_apply=True`).
2. UV unwrap (`U → Smart UV Project` for quick work, manual seams for hero assets).
3. Add a Material. Set Principled BSDF Base Color (or assign a texture). Set Roughness and Metallic.
4. Verify textures: Base Color = sRGB, Normal/Roughness/Metallic = Non-Color.
5. Export GLB with `export_apply=True`.
6. Drop into TD's `geo SOP`, assign `pbrMAT`.

### Recipe 2 — Animated character / rigged mesh

1. Model the mesh. Add an Armature object. Parent mesh to armature with Automatic Weights (`Ctrl+P → Armature Deform → With Automatic Weights`).
2. Pose Mode: animate the bones. Create one Action per animation clip in the NLA Editor.
3. Verify: mesh deforms correctly when bones move. Weight-paint corrections if needed.
4. Export GLB with `export_animations=True`, `export_skins=True`, `export_apply=True`.
5. In TD: `Geometry COMP` reads the GLB; animation params expose the clip names; trigger playback via tscript or animation table.

### Recipe 3 — Procedurally-generated mesh from Geometry Nodes

1. Build the GN graph on a base mesh — instance, scatter, deform, displace.
2. Verify the result in the viewport.
3. **Apply the Geometry Nodes modifier** — right-click the modifier in the Properties panel → Apply. This realizes the procedural result into static mesh data.
4. Now you have a static mesh. Add materials (the GN graph may have set Material Index per face — preserve those material slots).
5. Export GLB as Recipe 1.
6. **If the GN graph is time-varying**, you can't ship it live — either bake to keyframes (rare, complicated), render to video via [[BLENDER_WORKFLOW_RENDER_FOR_TD]], or shape-key approximate.

### Recipe 4 — Modular asset kit

Generate N variant meshes; ship as individual GLBs; TD swaps by changing the file path.

1. In Blender: build a collection per variant, or use the Asset Browser to mark each variant as an asset.
2. Use the batch export script above to write one .glb per object / collection.
3. In TD: parameterize the `geo SOP`'s File field on a variant index → `f'/path/to/asset_{idx}.glb'`.
4. Bonus: if all variants share the same material naming convention, the same `pbrMAT` reference works across the whole kit.

---

## Common Footguns

10+ ways this pipeline breaks. Sanity-check against this list when something looks wrong:

1. **Forgot to apply Subdivision Surface modifier** (and forgot `export_apply=True`) → TD shows the low-poly cage, not the smooth subdivided result. Fix: set `export_apply=True` or apply modifiers in Blender first.
2. **Used FBX with default axis flags** → object appears sideways or upside-down in TD. Fix: set `axis_forward='-Z'`, `axis_up='Y'` on export, or use GLB which handles axis automatically.
3. **Material name has spaces or special characters** → glTF parsing chokes, or TD's pbrMAT lookup by name fails silently. Fix: rename to `snake_case` before export.
4. **Used Principled BSDF Subsurface / Coat / Sheen / Transmission** → material looks flat in TD because those lobes don't roundtrip. Fix: bake the look into Base Color + Emission, or accept the loss.
5. **Forgot to set material Blend Mode for transparency** → object renders opaque in TD despite Blender preview showing transparency. Fix: Material Properties → Surface → Blend Mode → Alpha Blend (or Alpha Clip with a cutoff), then re-export.
6. **Ran `use_selection=True` with no object selected** → empty GLB file (4 KB, no geometry). Fix: select the object before export, or use `use_selection=False`.
7. **Mesh has a vertex group but no armature** → meaningless skinning data bloats the GLB. Fix: delete unused vertex groups (Object Data Properties → Vertex Groups → minus icon) before export.
8. **Exported n-gons without triangulating** → some engines refuse to load the file, others triangulate with surprising diagonals. Fix: add a Triangulate modifier or Ctrl+T in Edit Mode before export.
9. **Instances in Blender (Collection Instances, GN instances, Array modifier)** → TD only sees the realized geometry. Fix: enable Realize Instances in the GN graph, or apply the Array modifier, or `export_apply=True`.
10. **Emission Strength > 1.0 used in Blender** → clamped to 1.0 in TD unless the destination supports `KHR_materials_emissive_strength`. Fix: verify TD's GLB importer version, or scale emission up via Emit Color RGB > 1.0 and accept HDR clamping.
11. **Textures linked, not packed** → GLB embeds textures fine (GLB is one file), but if you exported glTF + .bin + textures separately and moved the file, texture paths break. Fix: use GLB (single binary) or pack images via `File → External Data → Pack Resources` before exporting separate glTF.
12. **Modifiers stack referencing other objects** (Mirror with a mirror object, Array with an offset object) — `export_apply=True` resolves them, but the other objects must be present in the scene at export time. Fix: keep dependency objects in the scene; apply modifiers first if removing them.
13. **Scene unit scale != 1.0** → object exports at 100x or 0.01x scale in TD. Fix: `scene.unit_settings.scale_length = 1.0` before export.
14. **Object has zero faces** (e.g., a curve that wasn't converted to mesh) → silent skip on GLB export, no error. Fix: convert curves to mesh (`Object → Convert → Mesh`) before export.
15. **Custom normals or smooth-by-angle baked into the mesh that the exporter doesn't preserve** → shading looks wrong in TD. Fix: verify with a test asset, fall back to explicit Triangulate + Shade Smooth/Flat per face.

---

## Cross-References

- [[BLENDER_ASSET_IO]] — broader asset I/O reference covering all import/export formats and the Asset Browser.
- [[BLENDER_MATERIALS]] — Principled BSDF surface in depth; texture node setup; colorspace rules.
- [[BLENDER_MODELING]] — mesh editing, modifiers, topology decisions.
- [[BLENDER_GEOMETRY_NODES]] — procedural geometry; how to apply the GN modifier into static mesh.
- [[BLENDER_WORKFLOW_RENDER_FOR_TD]] — the complementary pipeline for when live-asset isn't enough and you ship rendered video instead.
- `TD_OPERATORS_SOP.md` — `geo SOP` and SOP-family operators in TD.
- `TD_OPERATORS_COMP.md` — `Geometry COMP`, `Camera COMP`, `Light COMP`, scene-graph composition.
- `TD_PATTERNS_3D_SCENES.md` — how the imported asset slots into a full TD 3D scene.

---

## Sources

- glTF/GLB exporter docs — https://docs.blender.org/manual/en/latest/addons/import_export/scene_gltf2.html
- glTF 2.0 specification — https://github.com/KhronosGroup/glTF/blob/main/specification/2.0/README.md
- FBX exporter docs — https://docs.blender.org/manual/en/latest/addons/import_export/scene_fbx.html
- TouchDesigner `geo SOP` reference — https://docs.derivative.ca/Geometry_SOP
- TouchDesigner `pbrMAT` reference — https://docs.derivative.ca/PBR_MAT
- Khronos glTF extensions registry — https://github.com/KhronosGroup/glTF/tree/main/extensions
