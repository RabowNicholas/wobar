---
title: Workflow — Rendering Blender Footage for Real-Time Engines
version: 1.0
last_updated: 2026-05-22
status: live
scope: Producing video / image-sequence output from Blender that will be ingested into a real-time engine (TouchDesigner, Resolume, Notch) — codec choices (ProRes, DNxHR, PNG / EXR sequence, MP4), color management (linear EXR vs sRGB MP4), alpha channel handling, frame rate matching, vertical export, the Apple Silicon-specific codec story.
dependencies: BLENDER_LIBRARY_INDEX.md, BLENDER_RENDER_CYCLES.md, BLENDER_RENDER_EEVEE.md, BLENDER_COMPOSITOR.md, BLENDER_APPLE_SILICON.md
---

# WORKFLOW — RENDERING BLENDER FOOTAGE FOR REAL-TIME ENGINES

Blender renders the **content** — the cinematic 3D environment, the animated character, the pre-rendered hero effect. The real-time engine adds the **behavior** — audio reactivity, live composition, signal play, control-surface mapping. The seam between offline render and live composite is whatever file Blender writes. Get that file right and the rest of the pipeline cooperates; get it wrong and TD shows black, washes out, plays slow, or chokes on the codec.

This file covers the bpy-driven render side of the seam: what format to pick, how to set it, how to keep color and alpha intact, and how to hand off cleanly to a real-time engine's Movie File In / Image Sequence ingestion. Target Blender is **4.2 LTS minimum, 4.5+ preferred**. Real-time engine examples reference TouchDesigner because of the existing TD library, but the same choices apply to Resolume, Notch, and Unreal MediaPlate.

**Core facts:**
- Output choice is driven by **what the downstream engine needs**, not by what Blender defaults to. The default H.264 MP4 is the worst possible choice for a real-time-engine handoff.
- Two output families: **video clips** (ProRes / DNxHR / H.264 inside QuickTime or MP4) and **image sequences** (PNG / EXR / TIFF per-frame on disk).
- Image sequences are the most robust format. Any single frame can be re-rendered, no codec drift, no decoder dependency, alpha is free with PNG / EXR.
- **ProRes** is the canonical Mac-friendly mastering codec — hardware-accelerated decode on Apple Silicon, supports alpha at the 4444 profile, lossy but visually transparent at high bitrates.
- **DNxHR / DNxHD** is Avid's equivalent. Same family role. Avoid unless a downstream NLE or facility requires it — software encode on macOS, slower than ProRes.
- **H.264 / H.265** are for distribution only. Compression artifacts (blocking, banding, mosquito noise) are invisible at normal playback but show up immediately when a real-time engine pushes the texture through Feedback, Level adjustments, or scaling.
- The Color Management View Transform (AgX / Filmic / Standard / Khronos PBR Neutral) determines whether the output file is sRGB-baked (ready for direct ingestion) or linear-float (needs a transform applied downstream).
- **Frame rate must match the destination engine project**. TD running at 60fps cannot speed up a 24fps clip — Movie File In just plays at the wrong rate. Render Blender at the destination fps.
- Aspect ratio is set by `resolution_x / resolution_y` — vertical (9:16) for TikTok / Reels, horizontal (16:9) for cinematic / film, square or 4:5 for IG feed.
- **Alpha requires a codec that supports it** — PNG, OpenEXR, ProRes 4444, TIFF with alpha. H.264, H.265, ProRes 422 (any variant), MP4 cannot carry alpha.
- Apple Silicon adds a layer: VideoToolbox provides hardware-accelerated encode for H.264 / H.265 / ProRes via macOS frameworks; Blender's FFmpeg backend uses it when the QuickTime container is selected.
- The render-output filepath in Blender uses `#` as the zero-pad token for image sequences. `frame_####.png` writes `frame_0001.png` … `frame_9999.png`. Forget the `#` and every frame overwrites the previous.
- Persistent data (`scene.render.use_persistent_data = True`) reuses BVH and scene data between frames. Big speedup for animation, but stale data can cause artifacts if geometry / materials change mid-animation.
- The compositor (cross-ref `[[BLENDER_COMPOSITOR]]`) is the last stop before the file is written. Glare, color grade, lens distortion, film grain all live there — and the Composite node output is what hits disk.

---

## Output Format Decision Tree

Pick the row that matches the downstream use, not the upstream render engine. Cycles and Eevee both feed the same render-output pipeline.

### Image Sequence — PNG

Pick when:
- You need any single frame to be re-renderable without re-rendering the whole clip.
- You need an alpha channel and want lossless compression.
- The downstream engine prefers image sequences (TD's Movie File In handles them natively).
- The render might crash partway and you want the completed frames to survive.

Cost:
- Large disk footprint. 1920×1080 RGBA 8-bit PNG = ~3–6 MB / frame depending on content. 60fps × 60s = 3600 frames = 10–20 GB.
- Slightly slower decode in TD than a video file (per-frame disk reads), but not bottleneck-level.

### Image Sequence — OpenEXR / OpenEXR Multilayer

Pick when:
- You need true HDR (16-bit half-float or 32-bit float per channel).
- You need render passes (Z-depth, normals, diffuse, emission) for downstream compositing.
- You're handing off to a Nuke / Fusion / After Effects compositor before the video encode.
- The real-time engine supports EXR (TD does, via Movie File In or TOP-side load).

Cost:
- Very large files. Multilayer EXR at 1920×1080 with 5 passes = 30–80 MB / frame.
- Slower to load — only justify EXR when you actually need the float precision or the passes.

### ProRes 4444

Pick when:
- You need a single video file with alpha.
- The target is Mac-native (TD, Resolume, Final Cut, Premiere on Mac).
- You want high quality without the disk cost of PNG sequence.

Cost:
- ~30 MB/s for 4K 30fps (≈100 GB/hour). Smaller than PNG sequence, bigger than H.264.
- Lossy but visually transparent.

### ProRes 422 HQ

Pick when:
- You need a single video file, no alpha.
- Mac-native target.
- High quality required.

Cost:
- ~20 MB/s for 4K 30fps (≈70 GB/hour).
- No alpha — pick 4444 if alpha is needed.

### ProRes 422 / 422 LT / 422 Proxy

Pick when:
- Same as 422 HQ but smaller files, less quality. 422 is the workhorse; LT is a step down; Proxy is offline-edit only.
- For real-time-engine handoff, prefer 422 HQ or higher. 422 LT and Proxy show banding in dark gradients.

### DNxHR / DNxHD

Avid's codec family. Same role as ProRes.

Pick when:
- A downstream Avid Media Composer or DaVinci Resolve session requires it.

Otherwise: use ProRes. On macOS, DNxHR software-encodes (slower); ProRes is hardware-accelerated via VideoToolbox.

### H.264 MP4

Pick when:
- Final distribution to web / social only.
- The file is the final deliverable, not an intermediate.

**Do NOT pick when:**
- The file is going into a real-time engine. H.264's compression smears motion, blocks shadows, and mosquito-noises edges — invisible on a phone, brutal under TD's Feedback TOP or Level TOP gain.

### HEVC / H.265

Same family as H.264, newer codec, better at high bitrates. Codec support in TD on macOS is inconsistent — sometimes plays, sometimes black frame. Avoid for the Blender→TD seam.

---

## Setting the Output Format in bpy

The render image-settings file-format enum lives at `scene.render.image_settings.file_format`. Valid values in Blender 4.5:

```python
'PNG'               # 8/16-bit PNG, alpha-capable
'OPEN_EXR'          # single-layer EXR, float
'OPEN_EXR_MULTILAYER'  # multi-pass EXR, float
'JPEG'              # 8-bit JPEG, no alpha
'TIFF'              # 8/16-bit TIFF, alpha-capable
'BMP'               # 8-bit BMP, no alpha
'TARGA'             # 8-bit TGA, alpha-capable
'TARGA_RAW'         # uncompressed TGA
'IRIS'              # SGI Iris
'JP2'               # JPEG 2000
'AVI_JPEG'          # AVI container, JPEG codec — legacy, avoid
'AVI_RAW'           # AVI container, uncompressed — huge, legacy
'FFMPEG'            # FFmpeg container — pick this for ProRes / H.264 / DNxHR
```

For any video output (ProRes, DNxHR, H.264, H.265), `file_format` is `'FFMPEG'`. Then:

```python
scene.render.ffmpeg.format = 'QUICKTIME'  # or 'MPEG4', 'MKV', 'WEBM', 'AVI'
scene.render.ffmpeg.codec = 'PRORES'      # or 'DNXHD', 'H264', 'H265', 'PNG', etc.
```

The `format` is the **container**, the `codec` is the **stream inside it**. QuickTime container + ProRes codec = `.mov` file with ProRes inside. MPEG4 container + H264 codec = `.mp4` file with H.264 inside.

---

## ProRes Export from bpy

The full recipe for a ProRes export:

```python
import bpy
scene = bpy.context.scene

scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'QUICKTIME'
scene.render.ffmpeg.codec = 'PRORES'

# ProRes quality / profile is exposed via ffmpeg_preset in newer Blender:
scene.render.ffmpeg.ffmpeg_preset = 'GOOD'   # 'BEST', 'GOOD', 'REALTIME'
# Audio (if needed):
scene.render.ffmpeg.audio_codec = 'AAC'
scene.render.ffmpeg.audio_bitrate = 192

scene.render.filepath = '/path/to/output.mov'
```

**ProRes profile selection.** Blender's bpy ProRes profile mapping has shifted between versions. As of 4.2 / 4.5, the codec setting is just `'PRORES'` — the profile (Proxy / LT / 422 / 422 HQ / 4444 / 4444 XQ) is controlled internally by FFmpeg defaults and is not directly exposed as a bpy enum. To control the profile precisely:

- Set codec to `'PRORES'` in bpy.
- For the most reliable 4444 (with alpha) export, set `scene.render.image_settings.color_mode = 'RGBA'` — Blender's FFmpeg wrapper picks the appropriate ProRes pixel format (`yuva444p10le`) when RGBA is requested.
- For 422 HQ (no alpha), set `color_mode = 'RGB'`.
- For finer-grained profile control (Proxy / LT vs 422 vs HQ), encode externally with ffmpeg: render PNG sequence, then `ffmpeg -i frame_%04d.png -c:v prores_ks -profile:v 3 -pix_fmt yuv422p10le out.mov`. The `-profile:v` values: 0=Proxy, 1=LT, 2=422, 3=422 HQ, 4=4444, 5=4444 XQ.

**Verification.** After render, drag the .mov into QuickTime Player → Inspector (Cmd+I). Confirm: codec = ProRes, alpha channel = "Straight" or "Premultiplied" (if 4444), frame rate, resolution.

---

## Image Sequence Export from bpy

The cleanest, most-portable handoff. Each frame is a self-contained file. Crash recovery is free.

```python
import bpy
scene = bpy.context.scene

scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'       # 'RGB' for no alpha
scene.render.image_settings.color_depth = '16'        # '8' or '16' for PNG
scene.render.image_settings.compression = 15          # 0-100, PNG compression

scene.render.filepath = '/renders/myshot/myshot_v001/frame_####.png'

scene.frame_start = 1
scene.frame_end = 240

bpy.ops.render.render(animation=True, write_still=False)
```

**Filepath padding.** The `#` characters set zero-pad width. `frame_####.png` writes `frame_0001.png` through `frame_9999.png`. `frame_##.png` writes `frame_01.png` through `frame_99.png` (and overflows after that). Use **at least 4 `#`** for any animation longer than 99 frames.

**No `#` at all = OVERWRITE.** `filepath = '/renders/frame.png'` writes every frame on top of the last. Only the final frame survives. Common footgun; check the filepath before kicking off a 4-hour render.

**OpenEXR sequence.** Same pattern, different format:

```python
scene.render.image_settings.file_format = 'OPEN_EXR'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.image_settings.color_depth = '16'        # 'half' float; '32' for full float
scene.render.image_settings.exr_codec = 'ZIP'         # 'NONE', 'PXR24', 'ZIP', 'PIZ', 'RLE', 'ZIPS', 'DWAA', 'DWAB'
```

`'OPEN_EXR_MULTILAYER'` for multi-pass EXR — pulls Z-depth, normals, diffuse, etc. into a single file per frame, readable by Nuke / Fusion.

---

## Alpha Channel

Alpha is a stack: the renderer must produce alpha, the file format must carry alpha, and the downstream engine must read alpha. Break any link in the chain and you get an opaque background or a transparent void.

**Render side:**
- `scene.render.film_transparent = True` — enables transparent background.
- The active View Layer must include the Combined pass (on by default).
- Cycles and Eevee both support film transparency.

**Format side — formats that carry alpha:**
- PNG (RGBA color mode)
- OpenEXR (RGBA)
- TIFF (RGBA)
- TGA (RGBA)
- ProRes 4444 (RGBA color mode + QuickTime container)
- WebM / VP9 with alpha (limited support, real-time-engine compatibility varies)

**Formats that DROP alpha:**
- JPEG (no alpha at all)
- H.264 / H.265 (no alpha in standard implementations)
- ProRes 422 / 422 HQ / LT / Proxy (no alpha — only 4444 carries it)
- BMP (limited)

**Verification flag (run before a long render):**

```python
import bpy
scene = bpy.context.scene
assert scene.render.film_transparent, "film_transparent is False — render will be opaque"
fmt = scene.render.image_settings.file_format
mode = scene.render.image_settings.color_mode
alpha_ok = (fmt in {'PNG', 'OPEN_EXR', 'OPEN_EXR_MULTILAYER', 'TIFF', 'TARGA'} and mode == 'RGBA')
ffmpeg_alpha_ok = (fmt == 'FFMPEG' and scene.render.ffmpeg.codec == 'PRORES' and mode == 'RGBA')
assert alpha_ok or ffmpeg_alpha_ok, f"Format {fmt} + color_mode {mode} cannot carry alpha"
```

**Visual verification:** render a single frame, open in Preview.app (Mac) or any viewer that shows the checkerboard transparency pattern. If you see solid black or solid white where the transparent area should be — the file isn't carrying alpha.

---

## Color Management

Blender's color pipeline:

1. Renderer outputs **linear-light scene-referred** float values.
2. View Transform (`scene.view_settings.view_transform`) maps that to a display-referred curve.
3. Look (`scene.view_settings.look`) optionally pushes contrast / saturation.
4. Exposure / Gamma (`scene.view_settings.exposure`, `.gamma`) apply final adjustments.
5. The output file is encoded in either the view-transformed space or the linear space, depending on format.

**View Transform options (4.2+):**
- `'Standard'` — linear sRGB. No tonemapping. Burns out highlights.
- `'Filmic'` — classic Blender filmic curve. Tames highlights, slight desaturation.
- `'AgX'` — newer default. Better neutral starting point. Handles saturated emission cleanly. Recommended for cinematic Blender→TD work.
- `'AgX Base sRGB'` / `'AgX Base Display P3'` — display-specific variants.
- `'Khronos PBR Neutral'` — physically-grounded, less stylized than AgX.
- `'Raw'` — bypasses view transform entirely; output is linear.
- `'False Color'` — diagnostic only.

**For real-time-engine handoff:**

- **PNG / JPEG / TIFF / H.264 / ProRes** — these are display-referred formats. Blender bakes the View Transform into the file. TD reads the file as sRGB by default → image looks the same in TD as it did in Blender's viewport. **Recommended path** for most Blender→TD work.

- **OpenEXR** — float, linear by default. Blender does NOT bake the View Transform unless you flip the "Save As Render" toggle. By default the EXR holds scene-referred linear values and TD has to apply a transform on its side. Choice:
  - Leave EXR linear → TD applies AgX / Filmic via OCIO LUT (advanced).
  - Bake view transform into EXR (`scene.render.image_settings.use_preview = True` or via Image-Save-As with "Save As Render" → handled differently per Blender version; verify in 4.5 by checking the actual file's gamma curve).
  - Simpler path: don't use EXR for direct TD ingestion unless you specifically need HDR / passes.

- **The "Save As Render" toggle.** Lives in the image-save settings. When ON, the View Transform is applied before write. When OFF, the file is raw linear. In bpy this is exposed via `scene.render.image_settings.view_settings` (verify the exact attribute path in 4.5 — has shifted between versions).

**Quality check.** Render the same frame as PNG and as EXR. Open PNG in Preview, drop EXR into TD as Movie File In with default settings. Compare to Blender's 3D Viewport. PNG should match the viewport. EXR will look darker and washed unless TD applies a transform.

---

## Frame Rate

```python
scene.render.fps = 60         # numerator
scene.render.fps_base = 1.0   # denominator
# Effective fps = fps / fps_base
# fps=60, fps_base=1.0      → 60 fps
# fps=24, fps_base=1.001    → 23.976 fps (NTSC film)
# fps=30, fps_base=1.001    → 29.97 fps (NTSC video)
```

**Match the destination engine.** TD's project cookrate is a fixed number, usually 60. Movie File In playing a 24fps clip in a 60fps project does NOT slow the project down — it just plays the clip 2.5× too slowly. The audio-reactive timing falls apart.

**Common target rates:**
- **60 fps** — real-time engine native, smooth motion, modern social
- **30 fps** — standard social, older platforms
- **29.97 fps** — broadcast NTSC, drop-frame
- **25 fps** — broadcast PAL
- **24 fps** — cinematic film
- **23.976 fps** — NTSC film (24 / 1.001)

**Rule of thumb:** if you don't know the destination rate, render 60fps. Downsample in the engine if needed; you can't fabricate frames you didn't render.

---

## Resolution

```python
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100   # 50 = render at half-size, 200 = double
```

**Common targets:**

| Use | Resolution |
|---|---|
| HD horizontal | 1920×1080 |
| 4K horizontal (UHD) | 3840×2160 |
| 4K cinema (DCI) | 4096×2160 |
| Vertical social (TikTok / Reels / Stories) | 1080×1920 |
| Square IG feed | 1080×1080 |
| IG 4:5 portrait | 1080×1350 |
| YouTube Shorts | 1080×1920 |
| TD M1 non-commercial cap | 1280 max on either axis |

**TD project resolution match.** If TD comp runs at 1280×1280 (the non-commercial-license cap on Mac), render Blender at 1280×1280 to skip rescale. Or render larger (1920×1920) and let TD downsample for free supersampling. Never render smaller than the TD comp — upscaling in TD just blurs.

**Resolution percentage trap.** `resolution_percentage = 50` halves the render size. A 1920×1080 setup at 50% writes a 960×540 file. Easy to leave at 50 from a test render and forget — the final file is half the expected resolution.

---

## The Apple Silicon Codec Story

Cross-ref `[[BLENDER_APPLE_SILICON]]` for the full M-series story. Render-specific facts:

- **ProRes** — hardware-accelerated encode via VideoToolbox on Apple Silicon (M1 / M2 / M3 / M4). The Media Engine (dedicated silicon, not GPU, not CPU) handles the encode. Fast — often real-time or faster than real-time for HD.
- **H.264** — VideoToolbox hardware-accelerated. Same Media Engine path. Even faster than ProRes (simpler codec).
- **H.265 / HEVC** — VideoToolbox hardware-accelerated. Faster than H.264 at equivalent bitrate.
- **DNxHR / DNxHD** — no hardware path. Software encode through FFmpeg's CPU implementation. Slower than ProRes on M-series for the same output.
- **PNG / EXR** — CPU encode (no hardware path), but per-frame work is small. Disk write speed becomes the bottleneck, not the encoder.
- **AV1** — Blender 4.2+ supports AV1 encode via SVT-AV1 (software) and via VideoToolbox AV1 encode on M3 Pro / Max / Ultra and M4. M1 / M2 software-only.

**Verification:** during a render, open Activity Monitor → Window → GPU History and CPU History. If ProRes is encoding via VideoToolbox, you'll see the "Media Engine" line spike, not just CPU.

---

## File Naming for Real-Time Engine Ingestion

TouchDesigner's Movie File In handles:
- Single video files (`.mov`, `.mp4`, `.mkv`, etc.)
- Image sequences via filename pattern (drag any frame, TD auto-detects the sequence)
- The `Play Mode` parameter selects sequential / locked-to-time / specific-frame playback.

**Rules for clean ingestion:**
- No spaces in filenames. `my shot_v001.mov` → use `my_shot_v001.mov`.
- No special characters: `/ \ : * ? " < > |`. Underscore and hyphen only.
- Zero-pad frame numbers. `frame_0001.png` not `frame_1.png` — sort order breaks at frame 10 vs frame 2 otherwise.
- Lowercase extensions. `.mov` not `.MOV` (cross-platform safer).
- No leading numbers in the basename — some sequence detectors get confused by `01_frame_0001.png`.

---

## Render Output Staging

A consistent folder structure makes batching and re-render trivial:

```
/renders/
    /[project_name]/
        /[shot_name]/
            /[shot_name]_v001/
                /frame_0001.png
                /frame_0002.png
                /frame_0003.png
                ...
            /[shot_name]_v002/
                /[shot_name]_v002.mov
```

**Conventions:**
- One folder per version. Never overwrite a previous version's renders.
- Single-file outputs (.mov) live in the version folder, named after it.
- Image sequences are inside the version folder as `frame_####.ext`.
- A `notes.txt` in each version folder is cheap and saves hours when comparing versions weeks later.

**bpy filepath pattern:**

```python
project = "myproject"
shot = "shot_01"
version = "v003"
base = f"/renders/{project}/{shot}/{shot}_{version}"

# Image sequence
scene.render.filepath = f"{base}/frame_####.png"

# Single-file video
scene.render.filepath = f"{base}/{shot}_{version}.mov"
```

---

## Long-Form Render Strategy

For a multi-minute clip (anything over ~30 seconds at full quality):

- **Always render as image sequence.** A 4-minute single-file render that crashes at minute 3 = 3 minutes of wasted compute. The same render as PNG sequence = 3 minutes of frames already on disk, resume from frame N.
- **Use `bpy.app.handlers.render_post` to save intermediate state** if the render mutates the scene (driven simulations, baked physics):

```python
import bpy
def post_frame(scene, depsgraph):
    print(f"Finished frame {scene.frame_current}")
    # Save scene state checkpoint here if needed
bpy.app.handlers.render_post.append(post_frame)
```

- **Split the frame range across multiple Blender invocations** for parallel rendering on the same machine (only worthwhile for CPU rendering; GPU is already saturating the device).
- **Use the command-line for batch rendering:**

```bash
blender --background scene.blend --python render_script.py
```

Where `render_script.py` sets the format, range, and triggers `bpy.ops.render.render(animation=True)`. Avoids the GUI overhead and is what render farms use.

- **Persistent data** — `scene.render.use_persistent_data = True` reuses BVH and scene data between frames. 2-5× speedup on animation. **Footgun:** if geometry changes per frame (simulations, shape keys mid-animation), persistent data can cache stale BVH and produce artifacts. Turn off for sim-heavy shots; turn on for camera-only motion.

---

## The Compositor as the Look Layer

Cross-ref `[[BLENDER_COMPOSITOR]]`. Most cinematic finalization belongs in the compositor, not in the 3D scene:

- **Glare** — bloom / streak / fog glow.
- **Color Balance / RGB Curves / Hue Saturation Value** — color grade.
- **Lens Distortion** — barrel / pincushion / chromatic aberration.
- **Filter / Glare** — vignette, film grain (via Mix with Noise).
- **Defocus** — variable depth-of-field if Z pass is rendered.

The compositor output Composite node is what gets written to disk. The Viewer node is preview-only. If the Composite node is disconnected or unenabled, the render goes out raw (no compositor processing).

**Verification:** in the Compositing workspace, confirm the Render Layers node → (processing chain) → Composite node connection is intact and the Composite node is enabled.

---

## bpy Snippets — Full Render Pipeline

Paste-ready. Each block is self-contained.

### Set render engine and samples

```python
import bpy
scene = bpy.context.scene

scene.render.engine = 'CYCLES'           # or 'BLENDER_EEVEE_NEXT' for 4.2+
scene.cycles.samples = 128
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPENIMAGEDENOISE'
```

### Set resolution + fps + frame range

```python
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100

scene.render.fps = 60
scene.render.fps_base = 1.0

scene.frame_start = 1
scene.frame_end = 240
```

### Set output filepath + format (PNG sequence)

```python
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.image_settings.color_depth = '16'
scene.render.image_settings.compression = 15
scene.render.filepath = '/renders/myshot/v001/frame_####.png'
```

### Enable transparent background for alpha

```python
scene.render.film_transparent = True
```

### Set ProRes 4444 (with alpha)

```python
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.ffmpeg.format = 'QUICKTIME'
scene.render.ffmpeg.codec = 'PRORES'
scene.render.ffmpeg.ffmpeg_preset = 'GOOD'
scene.render.ffmpeg.audio_codec = 'NONE'
scene.render.filepath = '/renders/myshot/v001/myshot_v001.mov'
```

### Set ProRes 422 HQ (no alpha)

```python
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.image_settings.color_mode = 'RGB'
scene.render.ffmpeg.format = 'QUICKTIME'
scene.render.ffmpeg.codec = 'PRORES'
scene.render.ffmpeg.ffmpeg_preset = 'GOOD'
scene.render.filepath = '/renders/myshot/v001/myshot_v001.mov'
```

### Set EXR Multilayer for compositor handoff

```python
scene.render.image_settings.file_format = 'OPEN_EXR_MULTILAYER'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.image_settings.color_depth = '16'
scene.render.image_settings.exr_codec = 'ZIP'
scene.render.filepath = '/renders/myshot/v001/exr/frame_####.exr'
```

### Set color management View Transform

```python
scene.view_settings.view_transform = 'AgX'     # 'Standard', 'Filmic', 'AgX', 'Khronos PBR Neutral', 'Raw'
scene.view_settings.look = 'AgX - Base Contrast'
scene.view_settings.exposure = 0.0
scene.view_settings.gamma = 1.0
```

### Trigger animation render

```python
bpy.ops.render.render(animation=True, write_still=False)
```

### Trigger single still render

```python
scene.frame_set(120)                     # set the frame first
bpy.ops.render.render(write_still=True)
```

### Pre-flight verification (run before kicking off a long render)

```python
def verify_render_settings(scene):
    r = scene.render
    flags = []
    if '#' not in r.filepath and r.image_settings.file_format not in {'FFMPEG'}:
        flags.append("filepath has no #### padding — frames will overwrite")
    if r.film_transparent and r.image_settings.color_mode != 'RGBA':
        flags.append("film_transparent=True but color_mode!=RGBA — alpha will be dropped")
    if r.image_settings.file_format == 'JPEG' and r.film_transparent:
        flags.append("JPEG cannot carry alpha")
    if r.resolution_percentage != 100:
        flags.append(f"resolution_percentage={r.resolution_percentage}% — final size will be scaled")
    if r.fps not in (24, 25, 30, 50, 60) and r.fps_base == 1.0:
        flags.append(f"fps={r.fps} is non-standard — verify against destination engine")
    return flags

for flag in verify_render_settings(bpy.context.scene):
    print("WARN:", flag)
```

---

## Handing Off to TouchDesigner — Recommended Target Settings

Three common scenarios, each with a known-working config.

### Scenario A — A "Mirror" clip the real-time engine will composite over live video

The typical Blender→TD use case. A pre-rendered effect element that TD layers on top of camera / generator output.

- **Format:** PNG sequence, RGBA, 16-bit color depth.
- **Resolution:** 1080×1920 vertical (social) or 1920×1080 horizontal (cinematic).
- **Frame rate:** 60 fps.
- **Color management:** View Transform = AgX (or AgX High Contrast for stronger grade).
- **Film transparent:** True.
- **`scene.render.use_persistent_data` = True** if scene is camera-only motion; False if simulations.
- **TD ingestion:** Movie File In, point at any frame in the sequence — TD auto-detects.

### Scenario B — A single hero shot, full-frame cinematic close-up, no alpha

A finished cinematic cut that TD just plays through — no compositing needed.

- **Format:** ProRes 422 HQ, QuickTime container.
- **Color mode:** RGB.
- **Resolution:** 3840×2160 (downsampled in TD if needed) or 1920×1080.
- **Frame rate:** 60 fps preferred, 30 or 24 if matching a specific look.
- **View Transform:** AgX High Contrast or Filmic for cinematic curve.
- **Film transparent:** False (background is part of the shot).

### Scenario C — A background plate the real-time engine will composite on top of

Static-camera or slow-camera scene that lives behind reactive foreground elements.

- **Format:** PNG sequence, RGB (no alpha needed — it's the back layer).
- **Resolution:** match the TD comp resolution exactly (1280×1280 on M1 NC license cap).
- **Frame rate:** match the TD comp cookrate (typically 60).
- **View Transform:** AgX or Filmic to match downstream grade.
- **Film transparent:** False.

---

## Common Footguns

1. **Rendering H.264 MP4 for real-time-engine ingestion** → blocky compression artifacts surface immediately under Level / Feedback / scaling. Use ProRes or PNG sequence.
2. **PNG sequence with no `#` padding in filepath** (`frame.png`) → every frame overwrites the last. Only the final frame survives. Always use `frame_####.png`.
3. **Alpha rendered but file format is JPEG** → no alpha. Pre-flight check fails silently — JPEG just drops it.
4. **Frame rate mismatch — Blender 24fps, TD 60fps** → 2.5× slow playback in Movie File In. Audio reactivity loses sync. Match the rate.
5. **ProRes 4444 selected but `film_transparent=False`** → codec supports alpha but the render produces opaque background. Container has alpha, content is solid.
6. **ProRes 422 / 422 HQ selected with `film_transparent=True`** → film is transparent but 422 codec doesn't carry alpha. Background renders as black or whatever the world background color is. Use 4444 for alpha.
7. **Resolution percentage at 50%** from a test render → final file is half size. Pre-flight check catches it.
8. **View Transform = Filmic in Blender, TD assumes Standard** → file looks washed out / dim in TD. Either re-render with Standard, or apply a Filmic-style LUT in TD.
9. **EXR rendered linear, TD reads as sRGB** → black-crushed and dim. EXR needs a view transform on the TD side, or bake it before write.
10. **Codec not supported on TD's Mac build** (rare HEVC variants, AV1 in some TD versions) → Movie File In shows black frame. Switch to ProRes.
11. **`use_persistent_data=True` with per-frame geometry changes** → stale BVH cache, artifacts that look like ghosting or wrong shadows. Turn off for simulations.
12. **Filepath with spaces or special characters** → some downstream tools fail silently (Resolume in particular). Underscore-only naming.
13. **Compositor disabled or Composite node unconnected** → render output is raw, no grade / bloom / lens distortion. Confirm the compositor chain before render.
14. **Audio codec set to MP3 in QuickTime container** → playback warning in some players. Use AAC for QuickTime, or `audio_codec = 'NONE'` if no audio.
15. **Render farm path mismatch** — `/Users/me/renders/` works locally but the farm node mounts `/mnt/render/`. Use relative paths (`//renders/`) or symlink.

---

## Related Files

- `[[BLENDER_LIBRARY_INDEX]]` — top-level vault map.
- `[[BLENDER_RENDER_CYCLES]]` — Cycles-specific render setup (samples, denoiser, light paths).
- `[[BLENDER_RENDER_EEVEE]]` — Eevee Next-specific render setup (real-time engine, screen-space effects).
- `[[BLENDER_COMPOSITOR]]` — compositor nodes; the look layer that runs after the renderer and before file write.
- `[[BLENDER_APPLE_SILICON]]` — the M-series story: GPU acceleration, VideoToolbox, Metal backend, codec hardware paths.
- `[[BLENDER_WORKFLOW_ASSET_FOR_TD]]` — companion file for non-rendered assets (geometry / point cache / Alembic / USD) handed to TD.
