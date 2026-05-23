---
title: Cinematic Patterns — Camera Language, DOF, Motion Blur, Color Grade
version: 1.0
last_updated: 2026-05-22
status: live
scope: Camera language and finalization for cinematic-feel renders — focal length / lens choice, depth of field, motion blur, framing rules, shot types, color grading via View Transform + compositor curves, the render-cost-vs-cinematic-quality tradeoff. Lighting recipes live in BLENDER_PATTERNS_LIGHTING.md.
dependencies: BLENDER_LIBRARY_INDEX.md, BLENDER_RENDER_CYCLES.md, BLENDER_RENDER_EEVEE.md, BLENDER_COMPOSITOR.md, BLENDER_PATTERNS_LIGHTING.md
---

# CINEMATIC PATTERNS — CAMERA LANGUAGE & FINAL LOOK

"Cinematic" is not a render-engine setting. It is a stack: lens choice, depth of field, motion blur, framing discipline, aspect ratio, and a color grade that respects how real film handles highlights. A 1024-sample Cycles render through a 50mm lens with no DOF and Standard view transform looks like CG. A 128-sample EEVEE render through an 85mm lens at f/2.0 with AgX High Contrast and a 180° shutter looks like film.

This file is the camera-and-finalization side. Lighting decisions live in `[[BLENDER_PATTERNS_LIGHTING]]`. Engine-level knobs live in `[[BLENDER_RENDER_CYCLES]]` and `[[BLENDER_RENDER_EEVEE]]`. Final node-graph grading lives in `[[BLENDER_COMPOSITOR]]`.

**Core facts:**
- Blender cameras are split: `bpy.data.cameras` holds the lens/sensor/DOF data; `bpy.data.objects` of type `'CAMERA'` holds the transform that references it. Multiple camera objects can share one camera data block.
- The active render camera is `bpy.context.scene.camera` — set this before `render.render()` or Blender uses whichever was last active.
- Lens length in millimeters (`camera.data.lens`) is the primary "feel" knob. It controls perspective compression more than it controls "zoom." Wide = stretched, telephoto = flattened.
- Sensor width (`camera.data.sensor_width`) interacts with focal length to define field of view. Default is 36mm full-frame; changing this changes how a given mm focal length frames the shot.
- Depth of field is per-camera, on `camera.data.dof`. Off by default. Aperture is `aperture_fstop` — lower number = shallower DOF = more blur.
- Motion blur is engine-side, not camera-side. Both Cycles and EEVEE Next support it. Shutter value is `scene.render.motion_blur_shutter`; the 180° film standard maps to `0.5`.
- Aspect ratio comes from `scene.render.resolution_x` and `_y` — not from a camera setting. The camera frames whatever the render resolution dictates.
- View Transform (`scene.view_settings.view_transform`) determines how Blender maps HDR linear values to display range. AgX is the modern default for cinematic work in 4.0+; Khronos PBR Neutral (4.4+) is for product/PBR-accurate work.
- The Compositor handles final grade — curves, color balance, glare, lens distortion, chromatic aberration. Done after the view transform but stored in the same render output.
- "Cinematic" emerges from the combination, not any single setting. Wide-lens + shallow-DOF + 180° shutter + AgX + 2.39:1 aspect is the cliché stack; deviate deliberately.

---

## The Camera Object

A camera in Blender is two things: a data block and an object that points it somewhere.

```python
import bpy

# Create and place a camera
bpy.ops.object.camera_add(location=(7, -7, 5), rotation=(1.1, 0, 0.785))
cam_obj = bpy.context.object  # the object
cam_data = cam_obj.data        # the bpy.types.Camera datablock

# Make it the active render camera
bpy.context.scene.camera = cam_obj
```

**Switching cameras**: assign a different object to `scene.camera`. Useful for multi-angle renders from the same scene:

```python
bpy.context.scene.camera = bpy.data.objects['Camera_Wide']
bpy.ops.render.render(write_still=True)
bpy.context.scene.camera = bpy.data.objects['Camera_CU']
bpy.ops.render.render(write_still=True)
```

**Snap camera to current viewport**: `bpy.ops.view3d.camera_to_view()` — drops the active camera at the current 3D viewport vantage. Useful for "frame what I'm looking at."

**Frame from selected**: `bpy.ops.view3d.object_as_camera()` — turns the selected object into the active camera if it's a camera, or sets the viewport to look from any selected object's transform.

**View through active camera**: `bpy.ops.view3d.view_camera()` toggles the viewport into camera view.

---

## Focal Length — The Primary Cinematic Knob

`camera.data.lens` is in millimeters. Blender defaults to 50mm. Sensor width default is 36mm (full-frame). Together these define horizontal FOV.

**Reference table** — assumes 36mm sensor:

- **8-15mm (fisheye / ultra-wide)** — heavy barrel distortion, faces stretch at edges. Use for action immersion, interior wide-establishing, dream sequences, surreal-feel. Avoid for character close-ups unless distortion is the point.
- **18-24mm (wide)** — classic establishing shot lens. Landscapes, architectural interiors, environmental context. Faces start to distort if subject fills the frame — keep characters mid-frame.
- **28-35mm (semi-wide)** — environmental portraits, documentary feel, "walk-and-talk." 35mm roughly matches human visual perspective. Good for showing character + environment together.
- **50mm (normal)** — natural perspective with no compression or distortion. Default Blender starting point. Classic photojournalism lens.
- **85mm (portrait)** — flattering facial compression. Backgrounds soften nicely at f/2.0 or wider. The cliché "character close-up" lens for a reason.
- **100-135mm (short telephoto)** — strong subject isolation, smooth background blur. Fashion, hero portraits.
- **135-200mm (telephoto)** — heavy perspective compression — background looks closer to subject than it actually is. Wildlife, paparazzi, isolating distant subjects.
- **300mm+ (long telephoto)** — extreme compression, voyeur / surveillance feel. Subject and background appear stacked on the same plane.

**Rule of thumb**: wider lens = more environment + distortion + faster apparent action. Longer lens = more compression + isolation + dreamier feel as DOF gets shallow.

```python
cam_data.lens = 85.0          # 85mm portrait
cam_data.sensor_width = 36.0  # full-frame
```

**FOV alternative**: `camera.data.lens_unit = 'FOV'` then `camera.data.angle = math.radians(45)`. Same internal calculation, different unit at the UI.

---

## Sensor Size — The Secret DOF Multiplier

`camera.data.sensor_width` (in mm). Default 36mm = full-frame. Changing this changes the field of view at a given lens mm, and changes how DOF math reads.

Common sensors:

- **36mm** — full-frame DSLR / cinema camera. Cinematic default.
- **23.5mm** — APS-C crop sensor. Common mirrorless.
- **22.3mm** — Canon APS-C variant.
- **17.3mm** — Micro Four Thirds.
- **13.2mm** — 1-inch sensor (advanced compacts, drone cameras).
- **~6mm** — phone-sized sensor. DOF goes effectively infinite at normal apertures — phone "portrait mode" fakes shallow DOF in software.

**Why this matters**: if a stylized shot is mimicking a phone-shot aesthetic (deep DOF, wide FOV at a "50mm equivalent"), a 6mm sensor + 8mm lens reads more honestly than a 36mm sensor + 50mm lens at f/22.

`camera.data.sensor_fit`: `'AUTO'` (default), `'HORIZONTAL'`, or `'VERTICAL'`. Lock this to `'HORIZONTAL'` for predictable framing across aspect-ratio changes.

---

## Depth of Field

Per-camera, lives in `camera.data.dof`. Off by default — turn on with `use_dof = True`.

```python
dof = cam_data.dof
dof.use_dof = True
dof.focus_distance = 4.5            # meters, if no focus_object
dof.focus_object = bpy.data.objects['Character']  # tracks an object
dof.aperture_fstop = 2.0            # lower = more blur
```

**Focus rules**:
- If `focus_object` is set, Blender measures distance from the camera to that object's origin every frame. Ignore `focus_distance`.
- If `focus_object` is `None`, `focus_distance` is used in meters.
- A focus_object with an origin that's not at the eye/lens of a character will focus wrong. Add an empty at the eye and use that as the focus target.

**Aperture f-stop reference** (full-frame, 50mm lens, subject at 3m):
- **f/1.4** — razor-thin DOF, only eyes/eyelashes in focus. Dreamy / artistic.
- **f/2.0** — classic portrait. Face sharp, ears soft, background obliterated.
- **f/2.8** — moderate isolation. Most of head sharp.
- **f/4.0** — head and shoulders sharp.
- **f/5.6** — environmental portrait — subject sharp, background readable.
- **f/8** — full body sharp, background mildly soft.
- **f/11-f/16** — deep focus. Everything from foreground to background in.
- **f/22+** — diffraction starts to soften the whole image in real cameras; Blender doesn't simulate diffraction softening, so use sparingly for "honest" looks.

**Engine differences**:
- **Cycles**: full ray-traced bokeh. Accurate, slow. Bokeh shape, blade count, and rotation all render physically. See `[[BLENDER_RENDER_CYCLES]]`.
- **EEVEE Next**: post-process screen-space DOF. Fast, generally good, breaks on transparent edges and against background skies. See `[[BLENDER_RENDER_EEVEE]]`.
- **EEVEE Legacy** (pre-4.2 fallback): worse DOF than EEVEE Next, visible bokeh artifacts.

---

## Bokeh Shape

Bokeh is the out-of-focus highlight shape. In real cameras it follows the iris shape.

```python
dof.aperture_blades = 6              # 0 = perfect circle, 5-8 = polygon
dof.aperture_rotation = 0.0          # radians, rotates the polygon
dof.aperture_ratio = 1.0             # 1.0 = round, >1 = horizontal anamorphic oval
```

- **`aperture_blades = 0`** — perfect circles. Cleanest, most "lens-prime-ish" feel.
- **`aperture_blades = 5-9`** — polygonal bokeh. 6 and 8 are most common in real cameras. Reads as "real lens."
- **`aperture_ratio > 1.0`** — horizontal ovals. Anamorphic lens feel. Cinematic wide-format signature. Common values: 1.3, 1.6, 2.0.
- **`aperture_ratio < 1.0`** — vertical ovals. Rare in real life, unsettling on purpose.

Cycles renders this physically. EEVEE Next approximates it in screen-space.

---

## Motion Blur

Engine-side, controlled on the scene render settings. Both Cycles and EEVEE Next support it.

```python
scene = bpy.context.scene
scene.render.use_motion_blur = True
scene.render.motion_blur_shutter = 0.5            # 180° film shutter — the cinematic default
```

**The 180° shutter rule**: in physical cameras, the shutter is open for half of each frame's duration. At 24fps that's 1/48s of exposure per frame. In Blender, `shutter = 0.5` = "half the frame's duration." This is the cinematic-standard motion blur amount.

**Shutter values in practice**:
- **0.1-0.2** — minimal blur. CG-feel, sharp action, 60fps-style. Use for stylized / animated looks where frame-stepping clarity matters.
- **0.3** — sharper than cinema. Vertical / TikTok content where rapid scroll demands sharp frames.
- **0.5** — 180° rule. Classic cinema. Default for cinematic work.
- **0.7-1.0** — heavier blur. Dreamy, drugged, action-blurred. Movement smears across frames.
- **1.0+** — full open shutter. Movement carries through entire frame. Pre-cinema documentary feel.

**Engine specifics**:
- **Cycles**: full geometric motion blur. Each frame samples the time interval. ~2× render time hit. See `[[BLENDER_RENDER_CYCLES]]`.
- **EEVEE Next**: post-process motion blur using motion vectors. Much faster, less accurate on extreme motion. Good for most cinematic work. See `[[BLENDER_RENDER_EEVEE]]`.

**Common gotcha**: `use_motion_blur = True` but `shutter = 0` = no blur, silently. Always set both.

---

## Rolling Shutter

Cycles-only. Simulates CMOS sensor scan effects — vertical lines lean when the camera pans fast, propellers warp into curves.

```python
scene.render.motion_blur_position = 'CENTER'         # 'START' / 'CENTER' / 'END'
scene.render.motion_blur_rolling_shutter_type = 'TOP'  # 'NONE' / 'TOP'
scene.render.motion_blur_rolling_shutter_duration = 0.1
```

Subtle, but real for stylized realism — "shot on a phone / DSLR" vs "shot on a global-shutter cinema camera" reads different to a trained eye. Off by default in most cinematic looks; on for documentary / drone / handheld stylization.

---

## Aspect Ratios

Aspect comes from `scene.render.resolution_x` and `_y`. The camera doesn't store an aspect.

**Reference resolutions**:

- **16:9 (1920×1080)** — modern broadcast / YouTube / monitor default. Safe everywhere.
- **2.35:1 (Cinemascope, 1920×817)** — classic widescreen cinema. Bands above and below frame the eye.
- **2.39:1 (Anamorphic flat, 1920×804)** — modern wide cinema. Almost identical to 2.35:1.
- **1.85:1 (Academy flat, 1920×1038)** — modern theatrical standard. Slightly less wide than 2.39.
- **4:3 (1440×1080)** — academy/vintage. Period-piece / nostalgia feel.
- **9:16 (vertical, 1080×1920)** — TikTok / Reels / Stories. Critical for short-form. Compose for the center vertical strip — sides get cropped on some platforms.
- **4:5 (Instagram feed, 1080×1350)** — Instagram portrait feed. The "default" IG mobile shape.
- **1:1 (Square, 1080×1080)** — legacy Instagram, feed-agnostic, art-printable.
- **2.76:1 (Ultra Panavision)** — very wide, period epic.

```python
# 2.39:1 anamorphic flat
scene.render.resolution_x = 1920
scene.render.resolution_y = 804
scene.render.resolution_percentage = 100
```

**Composition for vertical**: 9:16 changes everything. Wide lenses on 9:16 stretch the top and bottom dramatically. Avoid wider than 24mm for human subjects in vertical unless distortion is the point.

---

## Resolution and Downsampling

Strategy: render at 2× target delivery resolution, downsample in compositor for cleaner edges and smoother DOF transitions.

```python
# Render at 2× delivery, downsample in compositor
scene.render.resolution_x = 3840
scene.render.resolution_y = 2160
scene.render.resolution_percentage = 100
# Then in compositor, Scale node to 0.5
```

`resolution_percentage` is a global multiplier — set to `25` for quick previews while keeping the "true" resolution in `resolution_x/y`. Set to `100` for final.

DOF transitions especially benefit from 2× rendering — the gradient between in-focus and out-of-focus regions resolves more smoothly. Same for thin geometry against bright backgrounds (hair, foliage, wire-frame structures).

See `[[BLENDER_COMPOSITOR]]` for the downsample node setup.

---

## Framing Rules

These are conventions, not laws. Break them deliberately.

**Rule of Thirds**: divide the frame into 9 equal cells with two horizontal and two vertical lines. Place key subjects on the intersections. Eyes of a portrait subject usually sit on the top horizontal third-line.

Blender shows a thirds guide overlay on the camera object:
```python
cam_data.show_composition_thirds = True
cam_data.show_composition_golden = True       # Golden ratio overlay
cam_data.show_composition_center = True       # Center cross
cam_data.show_composition_harmony_tri_a = True  # Triangle harmony guides
```

**Golden Ratio (1.618)**: more elegant alternative to thirds. Phi-grid overlay; subject sits on spiral focal points.

**Headroom**: space above the subject's head. Too much = subject looks small / sad. Too little = subject feels cramped / aggressive. Tight close-ups deliberately crop the top of the head — full headroom on a CU reads as snapshot, not cinema.

**Lookspace / nose-room**: when subject looks left or right, leave more space on the side they're looking toward. Symmetric framing of a side-glancing subject feels wrong without you knowing why.

**The 180° line / axis of action**: in a two-shot or shot/reverse-shot, keep the camera on one side of the imaginary line connecting the subjects. Crossing the line flips the spatial relationship and disorients the viewer.

**Camera height**:
- **Eye-level** — neutral, observational. Default.
- **High-angle** (camera above subject, looking down) — diminishes subject. Vulnerability, weakness, childlike.
- **Low-angle** (camera below, looking up) — empowers subject. Threat, heroism, scale.
- **Dutch tilt** (rolled camera) — disorientation, mental instability, action chaos. Rotate camera object on local Y by 5-15°.

---

## Shot Types — Reference

- **Extreme wide / establishing (EWS / WS)** — full scene context. Subject is small in frame. 18-24mm lens, deep DOF, environmental.
- **Wide shot (WS)** — full body, environment readable. 24-35mm lens.
- **Medium wide (MWS)** — knees-up. 35-50mm lens.
- **Medium shot (MS)** — waist-up character. 50mm lens. The workhorse conversational shot.
- **Medium close-up (MCU)** — chest-up. 50-85mm lens.
- **Close-up (CU)** — head and shoulders. 85mm lens at f/2.0-2.8.
- **Extreme close-up (ECU)** — face, eye, mouth, single detail. 85-135mm lens, f/2.0+. Very intimate or very tense.
- **Two-shot** — two subjects in frame. 35-50mm lens. Often paired with OTS reverses.
- **Over-the-shoulder (OTS)** — foreground character's shoulder/head frames a subject across. 50-85mm, focus pulled to the far subject.
- **Insert** — close-up of an object the character is touching/using. 50-100mm.
- **Cutaway** — non-character context shot. Any focal length, used in editing for pacing.
- **POV shot** — camera positioned as a character's eyes. 35-50mm to feel natural.

---

## Camera Movement

Static cameras are fine — most cinema has more static than moving shots. When movement is wanted, use one of these patterns.

**Keyframed location/rotation** — simplest. Animate `cam_obj.location` and `cam_obj.rotation_euler` directly on the timeline.

**Follow Path constraint** — camera rides a Bezier or NURBS curve.

```python
# Add curve, then constrain camera to it
constraint = cam_obj.constraints.new('FOLLOW_PATH')
constraint.target = bpy.data.objects['CameraPath']
constraint.use_curve_follow = True   # camera rotates along the curve's tangent
```

Then in the curve's Object Data Properties → Path Animation, set `path_duration` (in frames) and animate `eval_time`.

**Track To / Damped Track** — lock camera rotation onto a subject.

```python
track = cam_obj.constraints.new('TRACK_TO')
track.target = bpy.data.objects['Subject']
track.track_axis = 'TRACK_NEGATIVE_Z'   # camera looks down -Z
track.up_axis = 'UP_Y'
```

Damped Track is the smoother, less twitchy version — use it for organic following.

**Camera shake** — parent the camera to an empty, add an F-curve Noise modifier on the empty's rotation channels:

```python
empty = bpy.data.objects.new('CamShake', None)
bpy.context.collection.objects.link(empty)
cam_obj.parent = empty

# In the F-curve editor on the empty's rotation channels, add Noise modifier
# Strength 0.05, Scale 5 = subtle handheld
# Strength 0.3, Scale 10 = action chaos
```

**Steady-cam push** — combine Follow Path on a curve (slow forward motion) with subtle noise on rotation (handheld bob). Reads as a real operator walking with a stabilized rig.

**Crane / boom move** — Follow Path on a vertical curve, with Track To locked on subject. Camera rises while subject stays framed.

---

## View Transform — How HDR Becomes Display

`scene.view_settings.view_transform` maps linear HDR render values into the 0-1 display range. This is the single biggest "look" choice after lens and DOF.

- **Standard** — no tone mapping. Linear-to-sRGB only. Highlights clip hard. Avoid for cinematic. Use only for technical / debugging / matte passes.
- **Filmic** — Blender's previous default (pre-4.0). Strong filmic curve, good shadow detail, but emission gets clamped — bright magic / neon / fire goes muddy at peaks.
- **AgX** — Blender 4.0+ default. Modern recommended for cinematic. Better hue retention through highlights than Filmic, emission stays punchy, blue lights stay blue at high intensity (Filmic shifts them toward white/cyan). Use this unless you have a specific reason not to.
- **Khronos PBR Neutral** — Blender 4.4+. Aimed at PBR-accurate product / CAD work. Preserves perceived saturation and brightness fidelity vs. material values. Less stylized than AgX. Use for product renders, asset showcase, "honest" material representation.
- **False Color** — debug. Maps brightness to a color ramp. Use to spot blown highlights.
- **Raw** — no transform. Debug only.

**Look sub-setting** (available on Filmic and AgX):
- **Very High Contrast**
- **High Contrast** — punchy, cinematic default for many shots
- **Medium High Contrast**
- **Medium Contrast** — base
- **Medium Low Contrast**
- **Low Contrast** — flat, gradeable in compositor
- **Very Low Contrast** — log-like, maximum grade headroom

Strategy: pick contrast based on grading intent. If grading heavily in compositor, use Medium Low or Low — preserves dynamic range. If shooting "to print," use High Contrast — bake the look in.

**Exposure** — `scene.view_settings.exposure`, in stops. Global brightness without re-rendering. +1.0 = 2× brighter. Useful for matching multiple shots to a reference brightness post-render.

```python
scene.view_settings.view_transform = 'AgX'
scene.view_settings.look = 'AgX - High Contrast'
scene.view_settings.exposure = 0.0
scene.view_settings.gamma = 1.0
```

---

## Color Grading in the Compositor

Final grade lives in the Compositor (`scene.use_nodes = True`, then build the node tree). The cinematic chain:

**Render Layers → RGB Curves → Color Balance → Hue/Saturation/Value → Lens Distortion → Glare → Composite**

- **RGB Curves** — per-channel and master tone curves. The single most powerful grading tool. S-curve master = contrast. Lift the toe of the blue curve = warm shadows. Pull down the head of the red curve = cyan highlights.
- **Color Balance** — three-way grade: Lift (shadows), Gamma (midtones), Gain (highlights). Industry-standard control mapping. Drag the color wheels to push tone in shadows vs midtones vs highlights.
- **Hue/Saturation/Value** — global saturation pull-down is the most-used cinematic move. Real film is less saturated than CG. Saturation 0.85-0.95 is a common cinematic baseline.
- **Lens Distortion** — adds slight barrel distortion + chromatic aberration. Aberration of 0.005-0.015 = "real lens," more = stylized.
- **Glare** — Fog Glow (subtle bloom) or Streaks (anamorphic). Threshold high (1.0+) so it only catches genuine highlights. Mix at 0.2-0.5, not full.
- **Vignette** — multiply with a Mask of a soft ellipse, or use Ellipse Mask node. Subtle (0.85 in corners) = polished. Heavy = stylized.

See `[[BLENDER_COMPOSITOR]]` for the full node-by-node graph and downsampling chain.

**Lift / Gamma / Gain quick reference**:
- **Lift** (shadows) — push warm-cool here for "cool shadows" looks (teal/cyan)
- **Gamma** (midtones) — push warm here for skin / hero subject
- **Gain** (highlights) — push warm/cool here to set highlight temperature

Teal-and-orange = cool lift + warm gain. The most-copied modern blockbuster grade.

---

## Cinematic Recipes

Paste-ready shot setups. Adjust lighting per `[[BLENDER_PATTERNS_LIGHTING]]`.

**Cinematic establishing shot**
- Lens: 24mm
- Sensor: 36mm full-frame
- DOF: on, f/4.0, focus on midground subject
- Aspect: 2.39:1 (1920×804)
- Motion blur: shutter 0.5
- View transform: AgX High Contrast
- Engine: Cycles, 512 samples, see `[[BLENDER_RENDER_CYCLES]]`

**Portrait close-up**
- Lens: 85mm
- DOF: on, f/2.0, focus_object = eye empty
- Aperture blades: 6
- Aspect: 16:9 or 4:5
- Motion blur: shutter 0.5
- View transform: AgX Medium Contrast (preserves skin)

**Wide vertical (TikTok / Reels)**
- Lens: 24mm (avoid wider, faces stretch)
- Aspect: 9:16 (1080×1920)
- DOF: off or f/8 (deep — phones don't blur)
- Motion blur: shutter 0.3 (sharp for scroll readability)
- View transform: AgX High Contrast
- Render: full quality, then check on a phone — vertical reads wildly different from desktop preview.

**Product / commercial**
- Lens: 50mm (or 100mm for "luxury" compression)
- DOF: on, f/5.6-8, full product in focus
- Aspect: 1:1 or 4:5 depending on platform
- Motion blur: off (product shots are usually static)
- View transform: Khronos PBR Neutral (or AgX Medium) for accurate material color
- White background, see `[[BLENDER_PATTERNS_LIGHTING]]` softbox setup.

**Dramatic interior**
- Lens: 35mm
- DOF: on, f/2.8
- Aspect: 2.39:1
- Motion blur: shutter 0.5
- View transform: AgX High Contrast
- Low-key lighting from `[[BLENDER_PATTERNS_LIGHTING]]`, single key with strong shadows

**Action / dream blur**
- Lens: 50mm
- DOF: on, f/2.0
- Motion blur: shutter 0.7-1.0
- View transform: AgX High Contrast or Filmic High Contrast
- Compositor: chromatic aberration 0.015, slight glare Fog Glow

**Macro / extreme close-up**
- Lens: 100-135mm
- DOF: on, f/4-5.6 (razor-thin at macro distance — be conservative)
- focus_object on a vertex empty at the exact detail point
- Aspect: 16:9 or 4:5
- View transform: AgX Medium
- Tripod the camera — handheld noise is too much at macro

**Architecture / wide environmental**
- Lens: 18-24mm
- DOF: off or f/16 (everything in)
- Aspect: 16:9 or 2.39:1
- Motion blur: off for stills, 0.3 for slow drone-style move
- View transform: AgX Medium Contrast
- Strong sky / HDRI lighting from `[[BLENDER_PATTERNS_LIGHTING]]`

**Anamorphic-style hero shot**
- Lens: 40mm
- DOF: on, f/2.0
- aperture_ratio: 1.8 (horizontal oval bokeh)
- Aspect: 2.39:1
- Motion blur: shutter 0.5
- View transform: AgX High Contrast
- Compositor: streak glare horizontal, subtle blue tint

---

## The bpy API — Paste-Ready Camera Setup

```python
import bpy
import math
from mathutils import Vector

def setup_cinematic_camera(name='Cam_Hero', location=(7, -7, 5),
                           target_location=(0, 0, 1), lens=50,
                           fstop=2.8, sensor_width=36,
                           aspect=(1920, 804)):
    # Create camera
    cam_data = bpy.data.cameras.new(name)
    cam_obj = bpy.data.objects.new(name, cam_data)
    bpy.context.collection.objects.link(cam_obj)

    # Position
    cam_obj.location = location

    # Aim at target via empty + Track To
    target = bpy.data.objects.new(name + '_target', None)
    target.location = target_location
    bpy.context.collection.objects.link(target)
    track = cam_obj.constraints.new('TRACK_TO')
    track.target = target
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'

    # Lens / sensor
    cam_data.lens = lens
    cam_data.sensor_width = sensor_width
    cam_data.sensor_fit = 'HORIZONTAL'

    # DOF
    cam_data.dof.use_dof = True
    cam_data.dof.focus_object = target
    cam_data.dof.aperture_fstop = fstop
    cam_data.dof.aperture_blades = 6

    # Scene resolution + active camera
    scene = bpy.context.scene
    scene.render.resolution_x = aspect[0]
    scene.render.resolution_y = aspect[1]
    scene.render.resolution_percentage = 100
    scene.camera = cam_obj

    # Motion blur (180° rule)
    scene.render.use_motion_blur = True
    scene.render.motion_blur_shutter = 0.5

    # View transform
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - High Contrast'
    scene.view_settings.exposure = 0.0

    return cam_obj, target


# Usage
cam, target = setup_cinematic_camera(
    name='Cam_Portrait',
    location=(3, -3, 1.6),
    target_location=(0, 0, 1.65),  # eye level
    lens=85,
    fstop=2.0,
    aspect=(1920, 1080)
)

# Render current frame
bpy.ops.render.render(write_still=True)
```

**Switching between cameras for multi-angle render**:
```python
for cam_name in ['Cam_Wide', 'Cam_MS', 'Cam_CU']:
    bpy.context.scene.camera = bpy.data.objects[cam_name]
    bpy.context.scene.render.filepath = f'//renders/{cam_name}_'
    bpy.ops.render.render(write_still=True, animation=False)
```

**Add F-curve noise for camera shake**:
```python
# Assumes cam_obj has at least one rotation keyframe
fc = cam_obj.animation_data.action.fcurves.find('rotation_euler', index=0)
noise = fc.modifiers.new('NOISE')
noise.strength = 0.05
noise.scale = 5.0
```

---

## Render Cost vs Cinematic Quality

Cinematic settings are expensive. Know what each costs.

| Setting | Cost multiplier (Cycles) | Cost multiplier (EEVEE Next) |
|---|---|---|
| Motion blur | ~2× | ~1.2× |
| DOF | ~1.3-1.5× | ~1.1× |
| Volumetrics | 1.5-3× | 1.3× |
| Samples 256 → 1024 | ~4× | n/a (TAA-based) |
| Caustics on | ~1.5× | n/a |
| Render at 2× downsample | ~4× | ~4× |

**Stacked cinematic** (motion blur + DOF + volumetrics + 1024 samples + 2× resolution) on Cycles can hit 20-30× the cost of the same scene without them. Plan accordingly.

**Draft → final workflow**:
1. **Draft pass** — disable motion blur, disable DOF, samples = 64-128, resolution 50%. Confirm framing, lighting beats, animation timing.
2. **Mid pass** — enable DOF, samples = 256, resolution 75%. Confirm grade direction, check edges.
3. **Final pass** — enable motion blur, samples = 512-1024, resolution 100% (or 2× with downsample). Render farm if available.

For Cycles render-cost detail see `[[BLENDER_RENDER_CYCLES]]`. For EEVEE specifics see `[[BLENDER_RENDER_EEVEE]]`. For rendering specifically to feed TouchDesigner, see `[[BLENDER_WORKFLOW_RENDER_FOR_TD]]`.

---

## Common Footguns

1. **Wide lens on a character close-up** — 24mm on a face → nose enlarged, ears receding, distorted "fish-eye portrait" effect. Use 50mm minimum for character CUs, 85mm preferred.
2. **DOF focus_distance way too close** — set focus to 0.5m when subject is at 5m → everything behind 0.5m is blurred to noise. Always use focus_object if subject can move, and double-check focus_distance values.
3. **Motion blur on but shutter is 0** — `use_motion_blur = True` and `motion_blur_shutter = 0.0` = no blur. Silent failure. Set shutter explicitly to 0.5 for cinematic.
4. **AgX killing emission punch** — emission materials look duller in AgX than Filmic because AgX preserves hue at high intensity. Compensate by increasing emission strength 2-3× from Filmic values, or use AgX High Contrast Look.
5. **9:16 vertical rendered as 16:9 letterbox** — set `resolution_y` larger than `resolution_x` for vertical. The camera frame in the viewport will flip orientation. Don't crop a 16:9 to 9:16 in post — render natively.
6. **Resolution percentage stuck at 50%** — left over from draft preview. Always confirm `scene.render.resolution_percentage = 100` before final render.
7. **Sensor width default doesn't match reference camera** — mimicking iPhone footage with default 36mm sensor + 8mm lens gives wrong perspective. iPhone main camera is ~7mm sensor; set sensor_width accordingly.
8. **Filmic emission clamp creating hot blobs** — bright lights blow out into shapeless white circles on Filmic. AgX handles this better. If sticking with Filmic, lower emission strength and add bloom in compositor instead.
9. **DOF in EEVEE Next breaking on transparent / sky edges** — screen-space DOF can't see what's behind alpha edges. Composite renders separately (subject + background passes) and blur per-pass, or use Cycles for shots with significant transparency.
10. **focus_object at object origin, not at the eye** — origin of a character might be at the feet. Use an empty parented to the head bone or eye vertex as the focus target.
11. **Track To causing camera roll** — set `up_axis = 'UP_Y'` and verify. If camera spins on rotation when subject moves, the up vector is wrong.
12. **Rendering with no active camera** — `scene.camera = None` raises an error on render. Always set `scene.camera` before `render.render()`.
13. **Color grade applied in viewport but not in render** — view transform applies, but compositor nodes only run if `scene.use_nodes = True`. Confirm before final render.
14. **Aspect ratio mismatch between viewport and render** — viewport in 16:9 but render set to 9:16 → composition in viewport will lie. Always toggle camera view (`view_camera()`) and confirm framing in the final aspect.

---

## Cross-Refs

- Lighting recipes per shot type → `[[BLENDER_PATTERNS_LIGHTING]]`
- Cycles engine settings (samples, denoiser, motion blur internals) → `[[BLENDER_RENDER_CYCLES]]`
- EEVEE Next engine settings (TAA, screen-space DOF, motion blur) → `[[BLENDER_RENDER_EEVEE]]`
- Compositor grade chain (curves, color balance, glare, downsample) → `[[BLENDER_COMPOSITOR]]`
- Rendering outputs for TouchDesigner ingest → `[[BLENDER_WORKFLOW_RENDER_FOR_TD]]`
- All Blender reference files → `[[BLENDER_LIBRARY_INDEX]]`
