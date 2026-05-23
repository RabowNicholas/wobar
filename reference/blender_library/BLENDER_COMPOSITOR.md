---
title: Compositor — Post-Production Node Graph Reference
version: 1.0
last_updated: 2026-05-22
status: live
scope: Blender's Compositor — render-pass combination, Glare (bloom replacement), Blur variants, color grading, masking, Cryptomatte, File Output node for render layers, GPU vs CPU compositor backend, the bpy CompositorNodeTree API.
dependencies: BLENDER_LIBRARY_INDEX.md, BLENDER_PYTHON_API.md, BLENDER_RENDER_CYCLES.md, BLENDER_RENDER_EEVEE.md
---

# COMPOSITOR — POST-PRODUCTION NODE GRAPH

The Compositor is Blender's post-render node graph. It is **not** the shader graph — shader nodes define materials before render; compositor nodes process the framebuffer **after** render. It sits between the renderer and the final image on disk: Renderer → Render Layers → Compositor → Composite / File Output → file.

The Compositor lives in the **Compositing** workspace (top tab bar) or in any editor switched to "Compositor" via the editor-type dropdown. The graph is per-scene, not per-view-layer, but it ingests data from one or more View Layers through `Render Layers` input nodes. See [[BLENDER_RENDER_CYCLES]] and [[BLENDER_RENDER_EEVEE]] for what the renderer hands the compositor.

**Core facts:**
- The Compositor is a node graph operating on framebuffers / multi-layer EXR data — every link carries an image, vector, value, or color.
- It runs **after** rendering. For final renders, the post stack is applied per-frame as each frame finishes.
- One **Composite** output node defines the final image written to the render slot and to disk.
- The **Viewer** node is a preview only — it feeds the Image Editor backdrop and the compositor backdrop. It does not write to disk.
- The **File Output** node writes per-frame files independently of Composite — use it for per-pass output (multilayer EXR, etc.).
- The **CPU compositor** is the historical backend. Fully featured. Slower; used by F12 final renders by default in older versions.
- The **GPU Compositor / Realtime Compositor** introduced in 3.5 and matured through 4.5 is a parallel backend. Most nodes have GPU implementations; some are CPU-only and silently fall back. Toggled per-view-layer in Properties → View Layer → Compositor.
- In 4.5, GPU coverage expanded significantly (texture nodes, Denoise on GPU, Vector Math, Float Curve, Blackbody, Image Info, Image Coordinates, Relative To Pixel).
- Compositor processes the **Combined** pass by default; other passes must be explicitly enabled per view layer.
- Compositor scenes need `scene.use_nodes = True` and `scene.render.use_compositing = True` to actually execute on render — both are on by default in new files, but easy to forget when scripting.
- The Compositor is **resolution-aware** but **not** auto-cropping — feeding mismatched-size images into Mix produces fit-to-first-input behavior.
- All color math inside the compositor is **scene linear** (typically Linear Rec.709). Display transform happens at the Composite output. See [[BLENDER_RENDER_CYCLES]] for color management details.

---

## Enabling the Compositor

The compositor has three switches that all must be on for it to run:

```python
import bpy
scene = bpy.context.scene
scene.use_nodes = True               # creates scene.node_tree, enables editing
scene.render.use_compositing = True  # apply compositor on render
scene.render.use_sequencer = False   # if False, comp output goes to image; if True, VSE sees it
```

- `scene.use_nodes = True` — creates and enables `scene.node_tree`. **Without this, the compositor does nothing**, even if a graph exists.
- `scene.render.use_compositing` — master switch. F12 renders skip the compositor entirely when False.
- `scene.render.use_sequencer` — if also using the VSE, the compositor output is treated as a strip source. Leave False when not using VSE.
- The **Combined pass** must be enabled on the View Layer (default on) for the Render Layers node to output an Image.

When `use_nodes` is True for the first time, Blender auto-creates a default graph: `Render Layers → Composite`.

---

## Render Layers Node — the Source

The `Render Layers` node is how the compositor receives data from the renderer. One node per View Layer reference.

- The dropdown picks **which View Layer** to read from. Add additional Render Layers nodes for multi-View-Layer compositing.
- The **output sockets are the enabled passes**. Image is always there (Combined). Depth/Normal/Vector/Mist/CryptoObject/etc. appear only if enabled in Properties → View Layer → Passes.
- The node re-renders nothing — it samples the most recent render result for that view layer.
- `bpy` type string: `CompositorNodeRLayers`.
- Use `node.layer = "ViewLayerName"` and `node.scene = bpy.data.scenes["..."]` to point it.

To enable additional passes:

```python
vl = bpy.context.view_layer
vl.use_pass_z = True
vl.use_pass_normal = True
vl.use_pass_vector = True
vl.use_pass_mist = True
vl.use_pass_cryptomatte_object = True
vl.cycles.use_pass_volume_direct = True  # Cycles-specific passes
```

---

## Composite vs Viewer vs File Output

Three output destinations, three jobs.

**Composite** (`CompositorNodeComposite`):
- The canonical final image. One per graph (additional Composite nodes are ignored).
- Sets the **Image** that F12/F3 saves and that appears in the Image Editor's "Render Result".
- If disconnected, the render result is whatever Combined was (no compositing applied to the saved frame).

**Viewer** (`CompositorNodeViewer`):
- Preview only. Shows in the compositor backdrop (Alt-V toggles backdrop) and in the Image Editor when switched to "Viewer Node" image.
- Free placement — drop multiple Viewers anywhere mid-graph for debugging.
- Doesn't write to disk.

**File Output** (`CompositorNodeOutputFile`):
- Writes images to disk **directly**, independent of Composite.
- Add multiple input sockets — each socket = one file (or one layer if EXR Multilayer mode).
- Per-socket: file path, file format, color depth, codec.
- Critical for **multi-pass output** — feeding each render pass into its own File Output socket gives per-pass EXR/PNG files.
- `#####` in path becomes the frame number with that many digits of padding.

**Split Viewer** (`CompositorNodeSplitViewer`):
- Two-input Viewer with a split-screen slider for A/B comparison.

---

## Node Taxonomy by Category

Categories match the Add menu. `type=` is the `bpy` string for `tree.nodes.new()`.

### Input

| Node | `type=` | What it does |
|---|---|---|
| Image | `CompositorNodeImage` | Load image / image sequence / movie file |
| Movie Clip | `CompositorNodeMovieClip` | Reference an MCE-tracked clip |
| Render Layers | `CompositorNodeRLayers` | Pull rendered passes from a View Layer |
| RGB | `CompositorNodeRGB` | Constant color |
| Value | `CompositorNodeValue` | Constant float |
| Texture | `CompositorNodeTexture` | Procedural texture as input |
| Time | `CompositorNodeTime` | Frame-driven curve value |
| Track Position | `CompositorNodeTrackPos` | XY of a motion track |
| Bokeh Image | `CompositorNodeBokehImage` | Procedural aperture shape for Bokeh Blur |
| Mask | `CompositorNodeMask` | Reference a Mask datablock (painted in Image Editor → Mask mode) |

### Output

| Node | `type=` |
|---|---|
| Composite | `CompositorNodeComposite` |
| Viewer | `CompositorNodeViewer` |
| File Output | `CompositorNodeOutputFile` |
| Split Viewer | `CompositorNodeSplitViewer` |

### Color

| Node | `type=` | Notes |
|---|---|---|
| Bright/Contrast | `CompositorNodeBrightContrast` | Linear brightness offset, contrast around 0.5 |
| Gamma | `CompositorNodeGamma` | Power curve, default 1.0 |
| Hue Saturation Value | `CompositorNodeHueSat` | HSV shift |
| Invert | `CompositorNodeInvert` | 1 − x per channel |
| Mix Color | `CompositorNodeMixRGB` (4.x: also `CompositorNodeMix` for unified Mix) | Mix two inputs with blend mode + factor |
| RGB Curves | `CompositorNodeCurveRGB` | Per-channel + composite curves; main grading tool |
| Tonemap | `CompositorNodeTonemap` | Reinhard / Photoreceptor tonemap |
| Color Balance | `CompositorNodeColorBalance` | Lift/Gamma/Gain or Offset/Power/Slope |
| Color Correction | `CompositorNodeColorCorrection` | Three-way (Master/Highlights/Midtones/Shadows) |
| Hue Correct | `CompositorNodeHueCorrect` | Per-hue saturation curves |
| Exposure | `CompositorNodeExposure` | Stops adjustment (×2^n) |
| Posterize | `CompositorNodePosterize` | Step quantization |

### Filter

| Node | `type=` | Notes |
|---|---|---|
| Blur | `CompositorNodeBlur` | Gaussian / Box / Mitchell / Tent / Quad / Cubic / Catmull-Rom kernel |
| Bokeh Blur | `CompositorNodeBokehBlur` | Aperture-shaped blur, optionally radius-driven |
| Defocus | `CompositorNodeDefocus` | DOF from Z, camera-aware |
| Despeckle | `CompositorNodeDespeckle` | Removes hot pixels |
| Dilate/Erode | `CompositorNodeDilateErode` | Grow/shrink mask edges |
| Filter | `CompositorNodeFilter` | Sharp/Soft/Laplace/Sobel/Prewitt/Kirsch/Shadow kernels |
| Glare | `CompositorNodeGlare` | **Bloom replacement.** Streaks / Ghosts / Fog Glow / Simple Star / Bloom |
| Pixelate | `CompositorNodePixelate` | Nearest-pixel downsample, used after Scale Down |
| Sun Beams | `CompositorNodeSunBeams` | Radial light streaks from a point |
| Vector Blur | `CompositorNodeVecBlur` | Post motion blur from Vector pass |
| Anti-Aliasing | `CompositorNodeAntiAliasing` | SMAA on edges |
| Convert Premul | `CompositorNodePremulKey` | Straight ↔ premultiplied alpha |

### Vector

| Node | `type=` |
|---|---|
| Map Range | `CompositorNodeMapRange` |
| Map Value | `CompositorNodeMapValue` |
| Normal | `CompositorNodeNormal` |
| Normalize | `CompositorNodeNormalize` |
| Vector Curves | `CompositorNodeCurveVec` |

### Matte

| Node | `type=` | Notes |
|---|---|---|
| Box Mask | `CompositorNodeBoxMask` | Rectangular mask, animatable |
| Channel Key | `CompositorNodeChannelMatte` | Per-channel matte |
| Chroma Key | `CompositorNodeChromaMatte` | HSV-based greenscreen |
| Color Key | `CompositorNodeColorMatte` | Color-range matte |
| Color Spill | `CompositorNodeColorSpill` | Remove green/blue spill |
| Cryptomatte (V2) | `CompositorNodeCryptomatteV2` | **Per-object/material/asset isolation.** Eyedropper picks targets |
| Cryptomatte (legacy) | `CompositorNodeCryptomatte` | Pre-V2; takes manual pass connections |
| Difference Key | `CompositorNodeDiffMatte` | Subtract clean plate |
| Distance Key | `CompositorNodeDistanceMatte` | RGB-distance matte |
| Double Edge Mask | `CompositorNodeDoubleEdgeMask` | Inner/outer edge → gradient mask |
| Ellipse Mask | `CompositorNodeEllipseMask` | Elliptical mask, animatable |
| Keying | `CompositorNodeKeying` | All-in-one keyer (despill + matte + cleanup) |
| Keying Screen | `CompositorNodeKeyingScreen` | Build clean-color screen from tracking markers |
| Luminance Key | `CompositorNodeLumaMatte` | Brightness-based matte |

### Distort

| Node | `type=` |
|---|---|
| Corner Pin | `CompositorNodeCornerPin` |
| Crop | `CompositorNodeCrop` |
| Displace | `CompositorNodeDisplace` |
| Flip | `CompositorNodeFlip` |
| Lens Distortion | `CompositorNodeLensdist` |
| Map UV | `CompositorNodeMapUV` |
| Movie Distortion | `CompositorNodeMovieDistortion` |
| Plane Track Deform | `CompositorNodePlaneTrackDeform` |
| Rotate | `CompositorNodeRotate` |
| Scale | `CompositorNodeScale` |
| Stabilize 2D | `CompositorNodeStabilize` |
| Transform | `CompositorNodeTransform` |
| Translate | `CompositorNodeTranslate` |

### Converter

| Node | `type=` |
|---|---|
| Alpha Convert | `CompositorNodePremulKey` |
| Color Ramp | `CompositorNodeValToRGB` |
| RGB to BW | `CompositorNodeRGBToBW` |
| Set Alpha | `CompositorNodeSetAlpha` |
| Switch | `CompositorNodeSwitch` |
| Combine Color | `CompositorNodeCombineColor` (mode: RGB/HSV/HSL/YCC/YUV) |
| Separate Color | `CompositorNodeSeparateColor` |
| Combine XYZ | `CompositorNodeCombineXYZ` |
| Separate XYZ | `CompositorNodeSeparateXYZ` |

### Misc

| Node | `type=` |
|---|---|
| ID Mask | `CompositorNodeIDMask` |
| Z Combine | `CompositorNodeZcombine` |
| Levels | `CompositorNodeLevels` |
| Denoise | `CompositorNodeDenoise` (GPU-supported in 4.5+) |

---

## Glare Node — the Bloom Replacement

In Blender 4.2+, the EEVEE bloom checkbox was removed when EEVEE-Next shipped. Bloom is now done in the compositor through the Glare node's **Bloom** type.

**Glare types:**
- **Bloom** — soft, wide light bleed around bright pixels. The intended EEVEE-Bloom replacement.
- **Fog Glow** — large soft halo around bright pixels. Atmospheric.
- **Streaks** — anamorphic-style straight rays. Direction-configurable.
- **Simple Star** — symmetrical N-pointed star (4 by default).
- **Ghosts** — lens-flare ghost reflections along an axis.

**Key parameters:**
- **Threshold** — minimum input value to trigger glare. Default ~1.0; lower → more pixels glare. **For Cycles** (linear HDR), 1.0 is sensible; for EEVEE-Next, threshold often needs lowering.
- **Mix** — −1 (only glare, no source) to +1 (only source, no glare). 0 = balanced add.
- **Size** — power-of-two falloff radius. 6–9 is normal; higher = wider bloom.
- **Iterations** (Streaks/Simple Star) — how many overlay passes.
- **Streaks count + Angle Offset** — for Streaks type.
- **Color Modulation** — chromatic dispersion across rays.

**Recipe — add bloom to an EEVEE render:**

```
Render Layers (Image) → Glare (type=Bloom, threshold=0.8, size=8, mix=0) → Composite
```

If you want to control bloom intensity independently:

```
Render Layers → ─┬─→ Mix Color (Add, factor=intensity) → Composite
                 └─→ Glare (type=Bloom, mix=-1 to isolate glare only) ─┘
```

The `mix=-1` setting outputs **only** the glare; then add it back with a controllable factor.

**Known issues:** Glare's Bloom can introduce posterization on smooth HDR gradients at low size values, and is not pixel-identical to the old EEVEE bloom. For final renders, consider rendering at higher bit depth (16-bit float) and tuning Size + Threshold in HDR.

---

## Cryptomatte V2 — Per-Object Matte Isolation

Cryptomatte gives you a perfect per-object / per-material / per-asset matte without any keying or chroma trickery. The renderer encodes hashes of object/material names into RGBA channels in dedicated passes; the compositor decodes them.

**Setup:**

1. **Enable Cryptomatte passes** — Properties → View Layer → Passes → Cryptomatte:
   - **Object** — matte per object
   - **Material** — matte per material
   - **Asset** — matte per asset (linked collection)
   - **Levels** — 6 is default; higher = better edge accuracy at more memory cost.
2. Render the scene.
3. Add **Cryptomatte V2** node. Set:
   - **Source** — Render or Image
   - **Scene** — if Render, the scene
   - **Layer** — View Layer + Cryptomatte type (Object/Material/Asset)
4. Use the **Eyedropper** in the node to click objects in the **Image Editor showing the Image socket of the Cryptomatte node** (set the Image Editor's image to the Cryptomatte node's Pick output, then sample). Click adds, Ctrl-click removes.
5. The **Matte** output is a 0–1 alpha mask of the selected objects.
6. **Cryptomatte V2 doesn't need manual pass connections** — it auto-discovers the Crypto passes from the Render Layers source. (The legacy node required wiring CryptoObject00/01/02 by hand.)

**bpy:**

```python
crypto = tree.nodes.new(type='CompositorNodeCryptomatteV2')
crypto.source = 'RENDER'
crypto.scene = scene
crypto.layer_name = "ViewLayer.CryptoObject"
crypto.matte_id = "ObjectName1,ObjectName2"  # comma-separated
```

---

## Render Passes — What Flows Into the Compositor

The compositor's power scales with what passes you enable. Each pass is an output socket on the Render Layers node when active. Configure in Properties → View Layer → Passes.

**Data passes:**
- **Combined** — the rendered RGBA image (always on).
- **Z (Depth)** — per-pixel camera-space depth. Use for fog, defocus, Z-combine.
- **Mist** — 0–1 falloff distance, configurable on World → Mist. Cheap fog.
- **Normal** — view-space normal vector per pixel. For relighting.
- **Vector** — 2D motion vector per pixel. For Vector Blur.
- **UV** — UV coordinates per pixel. For texture re-projection via Map UV.
- **Position** — world-space position (Cycles).

**Index passes:**
- **Object Index** — per-pixel object pass_index value, used with ID Mask.
- **Material Index** — same for materials.

**Light passes (Cycles, also some EEVEE):**
- **Diffuse Direct / Indirect / Color** — lets you re-balance diffuse contribution in comp.
- **Glossy Direct / Indirect / Color** — same for specular.
- **Transmission Direct / Indirect / Color** — for glass/refraction.
- **Volume Direct / Indirect** — volumetrics.
- **Emission** — emissive contribution.
- **Environment** — world background.
- **Shadow** — shadow factor.
- **AO** — ambient occlusion factor.

**Cryptomatte:**
- **Crypto Object / Material / Asset** — multi-level hash passes.

**Recombining light passes** — to reproduce Combined from passes:
`(DiffDirect + DiffIndirect) × DiffColor + (GlossDirect + GlossIndirect) × GlossColor + Transmission × TransColor + Emission + Environment`

---

## The File Output Node — Multi-Pass Disk Writing

`CompositorNodeOutputFile` writes images to disk per-frame, decoupled from Composite.

**Key behavior:**
- **One node, many sockets** — `node.file_slots.new("name")` adds an input.
- **Per-socket** — each slot has its own file path (or sub-path if Multilayer EXR), format override, color depth, codec.
- **Two modes:**
  - **Files (default)** — each socket becomes a separate file: `<base_path><socket_name>####.<ext>`.
  - **Multi-Layer EXR** — all sockets land as layers in one `.exr` file. Set `node.format.file_format = 'OPEN_EXR_MULTILAYER'`.
- **Frame padding** — `####` in the path becomes the frame number with that many digits. Default 4 digits if no `#`.

**Common pattern — per-pass EXR for downstream comp (Nuke, Fusion, [[BLENDER_WORKFLOW_RENDER_FOR_TD]]):**

```python
fout = tree.nodes.new(type='CompositorNodeOutputFile')
fout.base_path = "//renders/passes/"
fout.format.file_format = 'OPEN_EXR_MULTILAYER'
fout.format.color_depth = '32'

# default has one slot "Image" — rename or add more
fout.file_slots[0].path = "RGBA"
fout.file_slots.new("Depth")
fout.file_slots.new("Normal")
fout.file_slots.new("Vector")
fout.file_slots.new("Cryptomatte")

rl = tree.nodes["Render Layers"]
tree.links.new(rl.outputs["Image"],  fout.inputs["RGBA"])
tree.links.new(rl.outputs["Depth"],  fout.inputs["Depth"])
tree.links.new(rl.outputs["Normal"], fout.inputs["Normal"])
tree.links.new(rl.outputs["Vector"], fout.inputs["Vector"])
```

---

## Multi-View-Layer Compositing

Typical for separating background/foreground/characters into independent render layers for control:

1. Make multiple View Layers (Properties → View Layer dropdown → +).
2. Each View Layer has its own visible collections and renderer settings.
3. Add one `Render Layers` node per View Layer in the compositor.
4. Combine via:
   - **Alpha Over** (Mix Color in 4.x with `blend_type='ADD'` or Alpha Over node `CompositorNodeAlphaOver`) — for matte-based stacking.
   - **Z Combine** (`CompositorNodeZcombine`) — depth-aware merge when both layers have Z passes; respects intersections.

```
RL_Background ─┐
               ├─→ Alpha Over → Composite
RL_Characters ─┘
```

Render time scales with total View Layers; use **Disable in Render** on layers you're not composing this pass.

---

## Common Compositor Recipes

### 1. Bloom for EEVEE
```
Render Layers (Image) → Glare(type=Bloom, threshold=0.8, size=8, mix=0) → Composite
```
Single-node bloom replacement for the removed EEVEE checkbox.

### 2. Cinematic Vignette
```
Ellipse Mask (size=0.7, mask_type=NotXOR with Invert) → Blur(size=80) → Mix Color(Multiply, factor=0.7) ← Render Layers
                                                                              → Composite
```
Soft elliptical darkening of edges. Tune blur radius for falloff softness.

### 3. Color Grade — Lift / Gamma / Gain
```
Render Layers → Color Balance(LGG mode: lift teal-blue, gamma neutral, gain warm) → RGB Curves(s-curve) → Composite
```
Cinematic teal/orange grade in two nodes.

### 4. Z-Depth Fog
```
Render Layers (Depth) → Map Range(from 5→50 to 0→1, clamp on) ─┐
                                                                ├→ Mix Color(blend=Mix, image: gray fog color) → Composite
Render Layers (Image) ──────────────────────────────────────────┘
```
Linear fog from near→far. Needs Z pass enabled.

### 5. Vector Motion Blur (post)
```
Render Layers (Image + Vector + Depth) → Vector Blur(samples=32, factor=1.0) → Composite
```
Much cheaper than Cycles render-time MB; needs Vector pass enabled and no Persistent Data weirdness across frames.

### 6. Cryptomatte-Isolated Color Tweak
```
Render Layers → Cryptomatte V2 (pick: HeroObject)
       │             │
       │             Matte ─→ factor of Mix Color(Mix)
       │                       ↑
       └──────── Image ────────┴── Hue Saturation Value (Hue shift) → other input of Mix
                                                                    ↓
                                                                Composite
```
Per-object hue/saturation push without re-rendering.

### 7. Painted Mask Drives Opacity
```
Image Editor → Mask mode → paint mask "MyMask"

Mask node (mask_type='MyMask') ─→ factor of Mix Color
Render Layers ─────────────────→ image A
RGB (transparent) ─────────────→ image B
                                  → Composite
```
Animatable painted masks for hand-tuned regions.

### 8. Lens Distortion
```
Render Layers → Lens Distortion(distort=0.05, dispersion=0.01) → Composite
```
Subtle barrel + RGB dispersion for analog-camera feel. Negative distort = pincushion.

### 9. Glare + Film Grain
```
Render Layers ─┬─→ Glare(Bloom) ─┐
               │                  ├→ Mix Color(Add, factor=0.6) → Mix Color(Overlay) → Composite
               └──────────────────┘                                    ↑
Texture(Noise, animated) ────────────────────────────────────────────────┘
```
Bloom plus per-frame animated grain for organic look.

### 10. Defocus from Z (camera-aware DOF post)
```
Render Layers (Image + Depth) → Defocus(f-stop=2.8, use_camera_fstop=True) → Composite
```
Set the camera DOF target (or use Z-scale). Slow on CPU; on GPU compositor Defocus is CPU-only fallback in many versions.

### 11. Chromatic Aberration
```
Render Layers → Separate Color(RGB) ─┬─R─→ Translate(+1px) ─┐
                                      ├─G──────────────────────→ Combine Color → Composite
                                      └─B─→ Translate(-1px) ─┘
```
Per-channel pixel shift for subtle CA.

### 12. Tonemap for HDR → SDR
```
Cycles Render Layers → Tonemap(Reinhard, intensity=0, gamma=1) → RGB Curves(toe lift) → Composite
```
For high-DR Cycles renders before display transform.

---

## bpy API Surface

```python
import bpy
scene = bpy.context.scene

# 1. Enable
scene.use_nodes = True
scene.render.use_compositing = True
tree = scene.node_tree

# 2. Clear default graph (optional)
for n in list(tree.nodes):
    tree.nodes.remove(n)

# 3. Create nodes
rl       = tree.nodes.new(type='CompositorNodeRLayers')
glare    = tree.nodes.new(type='CompositorNodeGlare')
curves   = tree.nodes.new(type='CompositorNodeCurveRGB')
comp     = tree.nodes.new(type='CompositorNodeComposite')
viewer   = tree.nodes.new(type='CompositorNodeViewer')

# 4. Position (visual only)
rl.location, glare.location, curves.location, comp.location = (
    (-600, 0), (-300, 0), (0, 0), (300, 0)
)

# 5. Configure
glare.glare_type = 'BLOOM'   # 'GHOSTS','STREAKS','FOG_GLOW','SIMPLE_STAR','BLOOM'
glare.threshold = 0.8
glare.size      = 8
glare.mix       = 0.0

# 6. Link
links = tree.links
links.new(rl.outputs['Image'], glare.inputs['Image'])
links.new(glare.outputs['Image'], curves.inputs['Image'])
links.new(curves.outputs['Image'], comp.inputs['Image'])
links.new(curves.outputs['Image'], viewer.inputs['Image'])
```

### Common `type=` strings (quick reference)

| Function | `type=` |
|---|---|
| Render Layers | `CompositorNodeRLayers` |
| Image input | `CompositorNodeImage` |
| RGB / Value | `CompositorNodeRGB` / `CompositorNodeValue` |
| Composite output | `CompositorNodeComposite` |
| Viewer | `CompositorNodeViewer` |
| File Output | `CompositorNodeOutputFile` |
| Mix Color (legacy) | `CompositorNodeMixRGB` |
| Mix (unified 4.x) | `CompositorNodeMix` |
| RGB Curves | `CompositorNodeCurveRGB` |
| Hue Sat Val | `CompositorNodeHueSat` |
| Color Balance | `CompositorNodeColorBalance` |
| Gamma | `CompositorNodeGamma` |
| Bright/Contrast | `CompositorNodeBrightContrast` |
| Exposure | `CompositorNodeExposure` |
| Tonemap | `CompositorNodeTonemap` |
| Blur | `CompositorNodeBlur` |
| Bokeh Blur | `CompositorNodeBokehBlur` |
| Defocus | `CompositorNodeDefocus` |
| Glare | `CompositorNodeGlare` |
| Vector Blur | `CompositorNodeVecBlur` |
| Denoise | `CompositorNodeDenoise` |
| Lens Distortion | `CompositorNodeLensdist` |
| Cryptomatte V2 | `CompositorNodeCryptomatteV2` |
| Alpha Over | `CompositorNodeAlphaOver` |
| Z Combine | `CompositorNodeZcombine` |
| Map Range | `CompositorNodeMapRange` |
| Map Value | `CompositorNodeMapValue` |
| Color Ramp | `CompositorNodeValToRGB` |
| Combine Color | `CompositorNodeCombineColor` |
| Separate Color | `CompositorNodeSeparateColor` |
| Set Alpha | `CompositorNodeSetAlpha` |
| Translate | `CompositorNodeTranslate` |
| Transform | `CompositorNodeTransform` |
| Scale | `CompositorNodeScale` |
| Mask | `CompositorNodeMask` |

Always check by `bl_idname`: `bpy.types.CompositorNodeGlare.bl_rna.identifier`. See [[BLENDER_PYTHON_API]].

---

## CPU vs GPU Compositor

The CPU compositor has been Blender's compositor forever. The **GPU Compositor** (a.k.a. "Realtime Compositor") was introduced in 3.5 for viewport-only and has been expanding ever since:

- **3.5** — viewport-only realtime compositing.
- **4.2** — GPU compositor available for **final renders** as well; many additional nodes ported.
- **4.5** — Vector Math, Vector Rotate, Vector Mix, Value Mix, Clamp, Float Curve, Blackbody, Image Info, Image Coordinates, Relative To Pixel, all texture nodes (Brick, Checker, Gabor, Gradient, Magic, Noise, Voronoi, Wave, White Noise) added. Denoise gained GPU support.

**Where to toggle:** Properties → View Layer → Compositor (4.2+):
- **Disabled** — no compositor at all.
- **CPU** — historical compositor.
- **GPU** — GPU compositor. Falls back to CPU on unsupported nodes.

In Python: `scene.view_layers[name].compositor_device = 'GPU'` (or `'CPU'`).

**Which nodes are CPU-only?** As of 4.5, primarily:
- Defocus (often CPU-only)
- Vector Blur
- Some legacy matte nodes (Keying Screen, Plane Track Deform)
- Inpaint (CPU only)
- Some Cryptomatte ops in older versions

Unsupported nodes are marked **CPU Compositor Only** in the manual and in the node header in the editor. The GPU compositor doesn't fail — it falls back transparently to CPU for those subgraphs, but you lose realtime feedback. Look for the **incompatible-node warning** in Properties → View Layer → Compositor.

**Performance characteristics:**
- **GPU compositor is dramatically faster** for live preview — sub-frame on a modern GPU at 1080p. CPU compositor often takes seconds per frame at 4K.
- For batch render, comp time is usually << render time, so the win is mostly interactive.
- On **Apple Silicon** ([[BLENDER_APPLE_SILICON]]), GPU compositor uses Metal — generally solid in 4.5.
- VRAM: GPU compositor holds the full-resolution buffer plus working textures on the GPU. 4K HDR comp with many passes can pressure 8–16GB GPUs.

---

## Common Footguns

1. **Forgot `scene.use_nodes = True`** — graph exists but has no effect. The render output is just the raw Combined pass.
2. **`scene.render.use_compositing = False`** — same outcome at render time; comp graph ignored. Easy to set by accident via "Render Result" toggles.
3. **Composite node not connected** — saved render = raw Combined. The Image Editor shows pre-comp result silently.
4. **Using legacy `CompositorNodeMixRGB` when you wanted unified Mix** — both work in 4.x, but the 4.x unified `CompositorNodeMix` has cleaner data-type handling (vectors, floats, colors all in one node).
5. **Z-Combine alpha edges look wrong** — premultiplied vs straight alpha mismatch. Use Convert Premul / Alpha Convert before/after Z-Combine.
6. **Glare with threshold too high** — pure black output, no glare visible. Lower threshold; check render is HDR.
7. **File Output paths overwriting each other** — two sockets named "Image" both write to `Image####.png`. Always rename slots before linking.
8. **Cryptomatte returns nothing** — the matching CryptoObject/Material/Asset pass isn't enabled on the View Layer. Enable in Properties → View Layer → Passes → Cryptomatte.
9. **Defocus from Z gives black** — Z pass not enabled, or the Z input is unconnected. Add Render Layers → Defocus.Z socket.
10. **GPU compositor silently dropping a node** — fall back to CPU for that subgraph kills realtime preview. Check Properties → View Layer → Compositor for the "incompatible node" warning panel.
11. **Setting `tree.nodes['Composite'].inputs['Image'].default_value` from script** — does nothing because the socket is link-driven on render. Connect a `Render Layers` instead. `default_value` only matters when there is no link.
12. **Wrong View Layer on Render Layers node** — the dropdown silently points at the wrong VL after duplicating a graph. Re-pick after any VL rename.
13. **Mix Color factor input default of 0.5** — fresh Mix Color blends 50/50, not pass-through. Set factor or wire it.
14. **EXR Multilayer file growing huge** — every slot adds a layer at full bit depth. Drop 32-bit float to 16-bit half where lossless precision isn't needed.
15. **Color management surprise** — the Image Editor View Transform (Filmic / AgX / Standard) is applied to the **Composite** output, not the Viewer. Two viewers can look different from the saved frame if View Transform settings differ.
16. **Stale render result** — comp updates only when you re-render or when an upstream Image input changes. Editing a Glare param doesn't re-trigger render; it just re-runs comp.
17. **Compositor disabled in Render Output Properties** — the "Compositing" checkbox under Render → Post Processing toggles `use_compositing`. Easy to disable in F12-test workflows and forget.
18. **GPU compositor + Cycles** — comp runs after Cycles render; on GPU it can claim VRAM that Cycles wanted to release. Watch peak VRAM with `nvidia-smi` / `mactop`.

---

## See Also

- [[BLENDER_LIBRARY_INDEX]] — vault map
- [[BLENDER_PYTHON_API]] — bpy basics, node-tree patterns
- [[BLENDER_RENDER_CYCLES]] — passes, AOVs, color management
- [[BLENDER_RENDER_EEVEE]] — EEVEE-Next, why bloom moved to comp
- [[BLENDER_SHADER_NODES]] — shader graph (pre-render, not this)
- [[BLENDER_WORKFLOW_RENDER_FOR_TD]] — per-pass EXR for downstream tools
