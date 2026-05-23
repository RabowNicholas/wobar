---
title: Materials — PBR Pipeline & Baking Reference
version: 1.0
last_updated: 2026-05-22
status: live
scope: Applied material work — PBR texture-set conventions, UV mapping, baking maps, displacement vs bump, color management (sRGB vs Non-Color vs ACES), procedural-vs-image-texture decision, the material slot model.
dependencies: BLENDER_LIBRARY_INDEX.md, BLENDER_SHADER_NODES.md, BLENDER_DATA_MODEL.md, BLENDER_PYTHON_API.md
---

# MATERIALS — PBR PIPELINE & BAKING REFERENCE

This is the **applied** layer of Blender materials — the conventions, color-space rules, UV plumbing, baking procedures, and slot model. It assumes the agent already knows how individual shader nodes wire together; that mechanical reference lives in [[BLENDER_SHADER_NODES]]. Engine-specific behavior (sampling, lightprobes, ray visibility, displacement modes) lives in [[BLENDER_RENDER_CYCLES]] and [[BLENDER_RENDER_EEVEE]]. Python construction patterns live in [[BLENDER_PYTHON_API]]. Importing material-bearing assets (USD, glTF, FBX) lives in [[BLENDER_ASSET_IO]].

If the question is "what does this node do," go to [[BLENDER_SHADER_NODES]]. If the question is "what color space goes on this map," "how do I bake AO," "why is my normal map wrong," "how do I assign per-face materials," you're in the right file.

**Core facts:**
- Materials live in `bpy.data.materials` — they are a top-level datablock, not owned by any object.
- An object exposes material slots via `obj.material_slots`; the underlying mesh exposes a parallel slot list via `obj.data.materials`.
- Each slot has a Link mode (OBJECT or DATA) — OBJECT-linked slots travel with the object and survive mesh swaps; DATA-linked slots travel with the mesh and are shared by every object using that mesh.
- The slot dropdown in the Properties Editor exposes the Link mode as a tiny icon next to the material name.
- The active material index (`obj.active_material_index`) determines which slot new faces are assigned to in Edit Mode and which slot the UI shows as selected.
- A single material can be shared across many objects — `material.users` is the link count.
- `material.use_nodes = True` is the modern default; without it the material falls back to legacy viewport-only properties.
- Per-face material is stored on the mesh as `mesh.polygons[i].material_index` — an integer index into the slot list.
- Materials are not the same as textures — a material is a shader graph that *may* reference image textures.
- The bake target is whatever Image Texture node is **selected** in the active material's node tree. The active UV layer of the mesh is the bake's UV source.

---

## The Material Slot Model

Blender has **two parallel slot systems** on every object, and the distinction matters when scripting:

- `obj.material_slots[i]` — the per-object slot list. Each entry has `.material`, `.link`, and `.name`.
- `obj.data.materials[i]` — the per-mesh slot list. Direct list of material datablocks.

Both lists have the same length and the same indices. The difference is **Link mode**, set per slot:

- **Link to DATA** (default) — the material is stored on the mesh datablock. Every object sharing that mesh sees the same material. Editing it in one object edits all of them.
- **Link to OBJECT** — the material is stored on the object. Different objects can share a mesh but have different materials in slot 0.

Use **DATA** for the normal case (single mesh, single material set). Use **OBJECT** when you have N instances of the same mesh and want each instance to have its own material — for example, ten copies of a banner mesh, each with a different image texture.

### Per-face assignment

Faces don't store materials directly. They store an integer `material_index` that points into the slot list:

```python
import bpy
mesh = bpy.context.active_object.data
for poly in mesh.polygons:
    if poly.normal.z > 0.5:        # upward-facing faces
        poly.material_index = 1    # slot 1
mesh.update()
```

In Edit Mode, the equivalent UI workflow is: select faces → pick a slot in the Properties Editor → click **Assign**.

### Empty slots are fine

A slot whose `.material` is `None` is legal. Faces pointing at an empty slot render as the default magenta placeholder in solid view and as a missing-material warning in render view. Cleaning empty trailing slots is cosmetic, not required.

---

## The PBR Texture Set

The Principled BSDF expects a specific set of inputs. A typical PBR download (Poly Haven, AmbientCG, Quixel, texture.com) ships with these maps. Color space matters more than anything else here.

| Map | Color Space | Socket | Notes |
|---|---|---|---|
| **Base Color (Albedo)** | sRGB | Base Color | The diffuse color. Avoid baked lighting in this map — keep it flat. |
| **Roughness** | Non-Color | Roughness | 0 = perfect mirror, 1 = fully diffuse. Linear scalar. |
| **Metallic** | Non-Color | Metallic | 0 = dielectric, 1 = metal. Treat as binary — values in between are physically meaningless. |
| **Normal** | Non-Color | Normal (via Normal Map node) | Tangent-space RGB. Must run through a Normal Map node before reaching Principled. |
| **Height / Displacement** | Non-Color | Material Output → Displacement | Signed displacement around 0.5 gray. Pair with a Displacement node. |
| **AO (Ambient Occlusion)** | Non-Color | multiplied into Base Color, or Principled's "Coat AO" path | Avoid baking into Base Color when the engine already computes shadowing. |
| **Subsurface (radius/weight)** | Non-Color | Subsurface Weight / Subsurface Radius | Scalar mask or RGB radius. |
| **Emission color** | sRGB | Emission Color | Treat as a color image — sRGB. |
| **Emission strength mask** | Non-Color | Emission Strength | Single-channel scalar. |
| **Specular (dielectric)** | Non-Color | Specular IOR Level | Rarely needed — Principled derives specular from IOR. Skip unless the source asset includes one. |
| **Opacity / Alpha** | Non-Color | Alpha | Single-channel. Set Material's Blend Mode in render settings if you need transparency to sort correctly. |

**Rule of thumb:** if the map represents a *color* a human would name (red wood, green moss, blue paint), it's sRGB. If the map represents a *number* the shader will do math on (how rough, how metallic, how tall, how transparent), it's Non-Color.

---

## The Standard PBR Node Chain

For a four-map PBR set (Base Color, Roughness, Metallic, Normal):

```
Texture Coordinate (UV) ──► Mapping ──┬──► Image Texture (Base Color, sRGB) ──────────► Principled.Base Color
                                       ├──► Image Texture (Roughness, Non-Color) ──────► Principled.Roughness
                                       ├──► Image Texture (Metallic, Non-Color) ───────► Principled.Metallic
                                       └──► Image Texture (Normal, Non-Color) ──► Normal Map ──► Principled.Normal
                                                                                                         │
                                                                                              Principled.BSDF
                                                                                                         │
                                                                                                Material Output
```

Verbal: one Texture Coordinate feeds one Mapping node (so all four maps share scale/offset). The Mapping's Vector output fans out into all four Image Texture nodes. Base Color goes straight to Principled. The three scalar maps connect by **single channel** — wire the Color output of the Image Texture and let Principled coerce it, or explicitly use a Separate Color and pick the channel that the source map encoded into. Normal goes through a Normal Map node (default: Tangent Space) before reaching Principled.

### Constructing it in Python

```python
import bpy

def make_pbr_material(name, base_path, roughness_path, metallic_path, normal_path):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links
    nodes.clear()

    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    nmap = nodes.new('ShaderNodeNormalMap')
    coord = nodes.new('ShaderNodeTexCoord')
    mapping = nodes.new('ShaderNodeMapping')

    tex_base = nodes.new('ShaderNodeTexImage')
    tex_rough = nodes.new('ShaderNodeTexImage')
    tex_metal = nodes.new('ShaderNodeTexImage')
    tex_norm = nodes.new('ShaderNodeTexImage')

    tex_base.image = bpy.data.images.load(base_path)
    tex_rough.image = bpy.data.images.load(roughness_path)
    tex_metal.image = bpy.data.images.load(metallic_path)
    tex_norm.image = bpy.data.images.load(normal_path)

    # Color spaces — the load-time critical step
    tex_base.image.colorspace_settings.name = 'sRGB'
    tex_rough.image.colorspace_settings.name = 'Non-Color'
    tex_metal.image.colorspace_settings.name = 'Non-Color'
    tex_norm.image.colorspace_settings.name = 'Non-Color'

    links.new(coord.outputs['UV'], mapping.inputs['Vector'])
    for tex in (tex_base, tex_rough, tex_metal, tex_norm):
        links.new(mapping.outputs['Vector'], tex.inputs['Vector'])

    links.new(tex_base.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(tex_rough.outputs['Color'], bsdf.inputs['Roughness'])
    links.new(tex_metal.outputs['Color'], bsdf.inputs['Metallic'])
    links.new(tex_norm.outputs['Color'], nmap.inputs['Color'])
    links.new(nmap.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat
```

The `colorspace_settings.name` lines are the single most common failure mode — if you skip them, the normal map will look washed-out and the roughness will be wrong.

---

## Color Management — The Deepest Pitfall

Blender's color pipeline is a stack. Image data goes in at one color space, render math happens in linear scene-referred space, and output is squashed back down to a display space through a View Transform. Confusing any layer breaks the image.

### The stack

1. **Input color space** — set on each Image Texture node (`image.colorspace_settings.name`). Tells Blender how to decode the file's bits.
2. **Working / scene-referred space** — linear, internal. All shader math happens here.
3. **Display Device** — sRGB on most monitors. Rec.709, P3-Display, Rec.2020 for specific outputs.
4. **View Transform** — the tone-mapping curve from scene-linear HDR to displayable range.
5. **Look** — optional contrast / saturation grade (None, Medium Contrast, High Contrast, etc.).

### View Transform options (4.2+)

- **Standard** — direct linear-to-sRGB, no tone mapping. Easy to over-expose; whites clip hard.
- **Filmic** — the old default (pre-4.0). Compresses highlights into a film-like roll-off. Tends to desaturate brights and dim emission.
- **AgX** — the modern default for cinematic / aesthetic work. Better highlight handling than Filmic, holds saturation in over-exposed regions. Default for new files since 4.0.
- **Khronos PBR Neutral** — added in 4.2. Designed for PBR color accuracy: sRGB base color in, near-identical sRGB color out, with controlled highlight roll-off only where needed. The right choice for product viz, ecommerce, CAD-style accuracy.
- **False Color** — diagnostic. Maps exposure zones to a color scale so you can spot blown highlights and crushed shadows.
- **Raw** — passes scene-linear through with no tone map. For technical buffers, mattes, and lightmap bakes — never for final beauty.

### Per-image color space — the choice that matters

On any Image Texture node, the **Color Space** dropdown is the single most important setting in materials:

- **sRGB** — for images that look correct on a normal monitor: photos, hand-painted color, base color maps.
- **Non-Color** — for data maps: roughness, metallic, normal, height, masks. Anything that is a number, not a color.
- **Linear Rec.709 / Linear** — for HDR / EXR data already in linear, or for color images that were authored in linear.
- **Filmic / AgX log** — rarely set on import; used for log-encoded plates.

A normal map loaded with `sRGB` will appear blue-tinted and washed out because Blender will apply an inverse-sRGB curve to the RGB values before treating them as a vector. The vector is then wrong everywhere except flat 0.5/0.5/1.0 regions. **Always set normal maps to Non-Color.**

### Picking the right transform

| Goal | View Transform | Look |
|---|---|---|
| Cinematic render | AgX | None or Medium High Contrast |
| Product / CAD / ecommerce | Khronos PBR Neutral | None |
| Technical buffer / lightmap | Raw | None |
| Highlight diagnostic | False Color | None |
| Legacy match (pre-4.0) | Filmic | Medium High Contrast |

---

## UV Mapping Basics

A UV map is a per-mesh layer that assigns each vertex of each face a 2D coordinate in `[0,1]` texture space. UVs are how 3D faces find their pixels in a 2D image.

- UV layers live at `mesh.uv_layers`. A mesh can have multiple — typical use is one for albedo/PBR maps and a second for an AO lightmap bake.
- One layer is **active for render** (the one Texture Coordinate's `UV` output reads) and one is **active for editing** (the one shown in the UV Editor). These can differ.
- The UV Editor (Shift-F10, or the UV Editing workspace) shows the active layer's islands.
- `Texture Coordinate.UV` always defaults to the active-for-render layer. To target a specific layer, use a UV Map node (named-input variant of Texture Coordinate).

### Unwrap operators

- **Unwrap** (`U` → Unwrap) — uses marked seams; produces minimal-distortion flat layouts. The standard tool.
- **Smart UV Project** — automatic island detection by face angle. Fast and usable for props without hand-marked seams.
- **Cube Project** — six orthogonal projections, one per face direction. Good for blocky props.
- **Sphere Project / Cylinder Project** — projects from a sphere or cylinder primitive shape.
- **Project from View** — uses the current 3D view as the projection direction. Useful for billboards or face textures.

UV islands should be packed with margin (a few pixels of bleed) to avoid bake seams across the island border. Use the Pack Islands operator (UV Editor → UV → Pack Islands) and set Margin to at least `0.005` for 2K maps.

---

## UV Unwrapping in Practice

Standard workflow for a new mesh that needs a baked PBR set:

1. **Edit Mode** on the mesh.
2. **Mark Seams** on edges where the unwrap should break — typical: along the back of a head, the inside of a cylinder, the bottom of a hard-surface prop.
3. Select all (`A`).
4. **U → Unwrap**.
5. Open the UV Editor (Shift-F10 or split the workspace).
6. Enable **Display Stretch** (N panel → Overlays → Stretch) to see distortion. Blue is good; red is bad.
7. Rearrange islands manually or run **UV → Pack Islands** with a `0.005` margin.
8. Save the .blend — UV layouts live with the mesh.

For autopilot on simple props:

```python
import bpy
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.005)
bpy.ops.object.mode_set(mode='OBJECT')
```

### Generated coordinates — the no-UV escape hatch

If a mesh has no UVs and you only need a procedural texture, use `Texture Coordinate.Generated`. Generated coordinates are bounding-box-relative — they go `[0,1]` across the object's local AABB. They follow the mesh shape, not a flat unwrap, so they work for procedural noise and gradients but not for image textures that need correct face placement.

---

## Procedural vs Image Textures

| | Procedural | Image Texture |
|---|---|---|
| **Resolution** | Infinite — scales with no aliasing | Fixed by the source file |
| **Storage** | None — generated at render | Disk / memory |
| **UVs** | Optional — can use Generated coords | Required for placement |
| **Cycles cost** | Cheap | Cheap |
| **EEVEE cost** | Expensive per pixel (live shader) | Cheap (sampled texture) |
| **Photoreal source** | No — derived from math | Yes |
| **Tileable / seamless** | Yes by construction | Depends on the source |
| **Variation per instance** | Trivial — seed inputs | Hard — needs unique maps |

**Use procedural** for: rock, marble, dirt, fabric weave, ice, wood grain — anything where a real-world reference is generic or expensive to source. Also for backgrounds, breakup masks, and UV-free surfaces.

**Use image** for: anything with a specific real-world identity (a specific brand label, a specific face, a specific photograph), and any PBR scan from Poly Haven / Quixel / texture.com / Polycam.

**Hybrid:** for EEVEE performance, build a procedural in Cycles → bake it to image → use the baked image in EEVEE. This is one of the most common bake recipes (covered below).

---

## Baking — The Full Workflow

Baking means computing the shader at each pixel of a target image, using the mesh's UV layout to know which pixel corresponds to which surface point. The result is an image file (or in-memory image datablock) that captures the shaded result as a portable texture.

- **Cycles only** — baking is a Cycles feature. Switch the render engine to Cycles before baking, even if the final render will be EEVEE.
- **EEVEE Next** (4.2+) can bake light probe volumes via Scene → Light Probes → Bake All Light Probe Volumes, but this is lighting cache, not material baking. For material bakes, always use Cycles.

### Bake types

- **COMBINED** — full beauty render projected to the UV map.
- **AO** — ambient occlusion only.
- **SHADOW** — shadow falloff only.
- **NORMAL** — surface normal, configurable space (Tangent/Object/World).
- **ROUGHNESS** — Principled's Roughness output.
- **GLOSSY / DIFFUSE** — separable contributions; choose Direct, Indirect, Color, or any combination via the bake panel checkboxes.
- **EMIT** — emission output only.
- **ENVIRONMENT** — world background contribution at each surface point.
- **UV** — bakes the UV layout as a UV-space image (debug).
- **POSITION** — bakes world-space position into RGB.
- **MIST** — distance from camera.

### The exact 8-step procedure

1. **Engine** — Render Properties → set engine to **Cycles**.
2. **UV** — confirm the mesh has a UV map. `mesh.uv_layers.active` must not be None.
3. **Bake target image** — create a new image in the Image Editor or via Python (`bpy.data.images.new('BakeTarget', 1024, 1024, alpha=False, float_buffer=False)`). For normal / position bakes, set `float_buffer=True` to avoid 8-bit quantization.
4. **Color space** — set the bake target's color space to **Non-Color** for normal / roughness / metallic / AO / position bakes. Leave sRGB only for diffuse / combined / emit.
5. **Image Texture node** — in the material's node tree, add an Image Texture node, set its image to the bake target, and **leave it selected**. Do not connect it — Blender uses the selected unconnected node as the bake destination.
6. **Bake panel** — Render Properties → Bake → set Bake Type, Margin (16 px for 2K), and any type-specific options (Selected to Active for high→low; Normal Space for normal bakes).
7. **Bake** — press the Bake button (or `bpy.ops.object.bake(type='NORMAL')`).
8. **Save** — `image.save_render(filepath)` or Image Editor → Image → Save As. Until saved, the bake exists only in memory and will be lost on quit.

### Selected to Active (high → low poly bake)

Used to transfer detail from a high-resolution sculpt to a low-resolution game mesh.

1. Select the **high-poly** object first.
2. Shift-select the **low-poly** object last (it becomes active).
3. Enable **Selected to Active** in the Bake panel.
4. Optionally enable **Cage** and set the cage object (an inflated copy of the low-poly used to ray-cast detail).
5. Set Ray Distance / Extrusion to avoid missed pixels.
6. Bake — the result is written into the low-poly's UV space, capturing the high-poly's normal / AO / detail.

---

## Common Bake Recipes

### AO bake to texture
Bake Type: AO. Target: Non-Color 8-bit image. Use case: pre-computed shadowing for stylized renders, EEVEE performance, or as a multiplier into Base Color for hand-painted looks.

### Normal bake high → low poly
Bake Type: NORMAL. Selected to Active: ON. Cage: ON. Target: Non-Color, 16-bit float for clean encoding. Use case: sculpt → game-mesh pipeline.

### Diffuse + Emit combined bake (lightmap)
Bake Type: DIFFUSE with Direct + Indirect + Color checked, then a second pass for EMIT. Combine the two via a compositor pass or shader mix. Use case: shipping a lit scene to a real-time engine that doesn't support full PBR lighting.

### Pointiness / curvature bake
Use a Geometry node's Pointiness output → ColorRamp → Image Texture (selected) → bake EMIT. Use case: edge wear masks, dirt cavity maps.

### Procedural shader → image
Build the look in Cycles with Noise / Voronoi / Musgrave. Add an Image Texture node, set it as the bake target, bake Type: COMBINED or EMIT. Use case: capture a procedural for use in EEVEE, glTF export, or any pipeline that needs a portable texture.

---

## Displacement — Three Flavors Compared

| | Bump | Normal Map | True Displacement |
|---|---|---|---|
| **Geometry moves** | No | No | Yes |
| **Silhouette changes** | No | No | Yes |
| **Self-shadows** | No | No | Yes |
| **Render cost** | Cheap | Cheap | Expensive (subdivision required) |
| **Memory cost** | Tiny | Texture-sized | Texture-sized + subdivided mesh |
| **EEVEE support** | Full | Full | Limited (4.2+ EEVEE Next has partial support) |
| **Cycles support** | Full | Full | Full |
| **Authored from** | Height map (single channel) | RGB normal map | Height map (single channel) |

### Bump
Cheapest. A Bump node takes a single-channel height map and perturbs the surface normal. Plug into Principled's Normal socket. No vertex motion, no silhouette change — only shading changes.

### Normal map
Same shading-only result as Bump but driven by an authored or baked RGB normal map. Pass through a Normal Map node first (set Space: Tangent for tangent-space maps, the standard PBR convention).

### True Displacement
Set Material Properties → Settings → Surface → **Displacement** to one of:

- **Bump only** — height map drives a Bump node automatically.
- **Displacement only** — height map moves actual vertices; requires a Subdivision Surface modifier (adaptive subdivision in Cycles) to provide enough geometry.
- **Displacement and Bump** — large-scale displacement moves verts; small-scale detail is added as bump on top. The recommended setting for serious displacement work.

The Displacement node converts a scalar height into a vector displacement. Plug it into Material Output's **Displacement** socket — not into Principled.

---

## Multi-material Objects

A single mesh can carry many materials, one per slot, with faces pointing at whichever slot they need.

- **Edit Mode workflow** — select faces → in Material Properties pick or add a slot → click **Assign**.
- **Python** — set `mesh.polygons[i].material_index` directly, then `mesh.update()`.
- **Geometry Nodes** — Set Material node assigns a material to a selection. The set is by slot but Geometry Nodes manages the slot list under the hood. Set Material Index is a separate node that just rewrites the index attribute.
- **Active slot UI vs render** — the active material index changes which slot the UI shows and which slot new faces get assigned to. It does **not** change what is rendered — every face renders against the material in its own `material_index` slot.

```python
# Add two materials and split a cube in half by face index
import bpy
obj = bpy.context.active_object
mesh = obj.data
red = bpy.data.materials.new('Red'); red.diffuse_color = (1, 0, 0, 1)
blue = bpy.data.materials.new('Blue'); blue.diffuse_color = (0, 0, 1, 1)
mesh.materials.append(red)
mesh.materials.append(blue)
for i, poly in enumerate(mesh.polygons):
    poly.material_index = 0 if i % 2 == 0 else 1
mesh.update()
```

---

## Sharing vs Duplicating Materials

Materials are reference-counted datablocks. Two objects assigned the same material share one shader graph — edits to either propagate to both.

- `material.users` — link count. Greater than 1 means shared.
- `material.copy()` — creates an independent duplicate with the same node graph but its own datablock.
- **Make Single User** (UI: Object → Relations → Make Single User → Object & Data & Materials) — duplicates everything shared so edits become local.

### When to share
- Many copies of the same asset that should always look identical.
- Procedural materials with global parameters you want to control from one place.

### When to duplicate
- Each instance needs its own image texture, color tint, or per-prop variation.
- You're about to make destructive changes and don't want them to propagate.

```python
# Detect and split a shared material before editing
import bpy
obj = bpy.context.active_object
mat = obj.active_material
if mat and mat.users > 1:
    obj.active_material = mat.copy()    # now we have our own copy
```

---

## Linking Materials Between Files

Two ways to pull a material from another .blend:

- **Append** — File → Append → pick the .blend → Material → select. Deep-copies the material and all its dependencies into the current file. Editable, no longer connected to the source.
- **Link** — File → Link → same path. Creates a read-only reference. The source file remains authoritative; the linked material updates when the source changes. Cannot be edited directly in the receiving file.

**Library Overrides** — for shared shaders that need per-file tweaks: link, then create an Override on the material. The override is local and editable; the linked base remains shared. The standard pipeline pattern for studio asset libraries.

```python
# Append a material from another .blend
import bpy
filepath = "/path/to/source.blend"
with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
    data_to.materials = [name for name in data_from.materials if name == 'MasterMaterial']
mat = bpy.data.materials['MasterMaterial']
```

---

## The Asset Browser and Material Assets

Marking a material as an asset makes it draggable into other files via the Asset Browser.

- `material.asset_mark()` — promotes a material to an asset. Its catalog entry appears in the Asset Browser of any file pointing at the same asset library.
- `material.asset_clear()` — un-marks.
- `material.asset_data` — exposes catalog ID, tags, description, author, preview image.
- Catalogs live in `blender_assets.cats.txt` at the library root.
- The **Essentials** library (4.x) ships with Blender and includes a baseline set of materials. Reference but don't depend on its exact contents — it changes per release.

Drag-and-drop from the Asset Browser into the 3D viewport assigns the material to whatever object is under the cursor — into the active slot if one exists, or appends a new slot if not. Holding Alt while dragging assigns to all slots of the target.

---

## The bpy API Surface for Materials

The minimum vocabulary the agent needs:

```python
import bpy

# Create
mat = bpy.data.materials.new(name='MyMaterial')
mat.use_nodes = True

# Access the node tree
nt = mat.node_tree
bsdf = nt.nodes.get('Principled BSDF')

# Attach to an object via the mesh (DATA link)
obj = bpy.context.active_object
obj.data.materials.append(mat)

# Attach to an object as OBJECT-linked
obj.material_slots[0].link = 'OBJECT'
obj.material_slots[0].material = mat

# Active slot
obj.active_material_index = 0
mat = obj.active_material      # shortcut to the active slot's material

# Remove a slot
obj.data.materials.pop(index=2)

# Duplicate to make independent
mat_copy = mat.copy()

# Delete entirely (only if no users)
bpy.data.materials.remove(mat, do_unlink=True)

# Check sharing
print(mat.users)               # number of objects referencing it

# Load an image with the right color space
img = bpy.data.images.load('/path/to/normal.png')
img.colorspace_settings.name = 'Non-Color'
```

`bpy.data.materials.new()` always returns a new datablock — names auto-increment on collision (`MyMaterial`, `MyMaterial.001`).

---

## Common Footguns

1. **Normal map looks washed out / blue-tinted** — color space is sRGB. Set to **Non-Color**. Same fix for roughness/metallic/height/mask maps.
2. **Material panel shows 5 slots but only 4 are used** — empty trailing slots are normal. Clean cosmetically with `obj.data.materials.pop()` only if needed.
3. **Editing material on one object changes another object** — they share a datablock. Run `material.copy()` and reassign, or use Make Single User.
4. **Emission appears black or weak under Filmic** — Filmic compresses highlights aggressively. Switch View Transform to AgX, Khronos PBR Neutral, or Raw, or increase Emission Strength by 10–100×.
5. **Image Texture loaded via Python defaults to sRGB** — `bpy.data.images.load()` does not infer color space from the map type. Always set `image.colorspace_settings.name` after loading.
6. **UV map renamed; Texture Coordinate still references the old name** — `Texture Coordinate.UV` reads `mesh.uv_layers.active`, not a name. If you used a UV Map node with an explicit name, update the node's `uv_map` property after renaming.
7. **Bake target is the wrong image** — the bake target is the **selected** Image Texture node in the active material, not the active UV layer and not the visible image in the Image Editor. Click the target node in the shader graph before pressing Bake.
8. **Baking produces a black image** — no active UV map, no selected Image Texture node, mesh has zero-area UVs, or the material's surface output is dark. Check `mesh.uv_layers.active`, check the shader graph for a selected unconnected Image Texture, verify UVs are in `[0,1]`.
9. **Bake works but has seams on island borders** — bake margin is too small. Increase Margin in the Bake panel (16 px for 2K, 32 px for 4K) and re-bake.
10. **Bake fails with "No active image"** — every selected object that's part of the bake needs an active Image Texture node in its material. For Selected to Active bakes, only the active (low-poly) object needs the target image; the high-poly does not.
11. **Roughness / metallic map values look wrong even with Non-Color** — the source map encodes data in a single channel (often G or R), not all three. Use a Separate Color node and pick the channel the texture author used. Glossiness maps are inverse-roughness — pass through an Invert node.
12. **EEVEE shows the material correctly; Cycles shows it black** — the surface output is connected to a node EEVEE accepts but Cycles doesn't (or vice versa). Verify with the engine you intend to render in before relying on viewport feedback.
13. **Displacement set to Displacement Only but no silhouette change** — no Subdivision Surface modifier on the mesh, or Adaptive Subdivision not enabled in Cycles. True displacement needs geometry to displace.
14. **ProRes / video export expected but only an image came out of Bake** — baking writes a single image. For video, render the timeline through Output Properties → Output and pick a movie container. Bake is for textures, not for output.
15. **Asset Browser doesn't show the material** — `material.asset_mark()` was not called, or the asset library path in Preferences doesn't include the file containing the material. Check Preferences → File Paths → Asset Libraries.
