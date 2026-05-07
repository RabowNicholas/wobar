# CHANGE LOG — magnet_chamber

Second polished POPX-on-WOBAR primitive after `attractor_chamber`. Built around POPX `magnetize` — particles orbiting/dancing around invisible attractor poles.

TD location: `/project1`

---

## v001 — Built (2026-05-01)

**Status:** shipped. Validates `magnetize` as the second clean POPX primitive (after `SA`). Output attrs (`P, Scale, N, Orient, Transform, Up, FullTransform, PointScale, Pivot`) carry only transform-related data, no solver-internal baggage that broke DLA/Particle/DLG today — instances cleanly via the proven SA-pattern.

**Architecture:**

```
particles (pointgenerator, sphere volume, 2200 pts)
   ↓
magnets (pointgenerator, 2 pts on X axis)
   ↓
magnets_orbit (transformPOP, ry/rz time-driven rotation — magnets dance)
   ↓
mag (POPX magnetize — Mode='spin', clean POP output)
   ↓
mag_null
   ↓
geo_render (geometryCOMP, manual numinstances=numPoints(), sphere instance, pbrMAT)
   ↓
render (HDR env + 2 palette-cycling lights + 1 cool light)
   ↓
bloom branch → mirror_flip(h) + mirror_comp → mirror_flip_v + mirror_comp_v (4-fold symmetry)
   ↓
null_out → rec_out (HAP, audio_in routed)
```

**Visual register:** mirror-symmetric pearl orb cluster with 4-fold mandala symmetry. Quadrant mirror creates ritual sigil reading. Spin axis between the two orbiting magnetic poles creates a Saturn-ring density variation. Slow camera orbit (60s) reveals the form from changing angles.

**`ctrl_master` baseCOMP — 21 custom params across 6 pages:**
- Audio: Floor, Ceil, Exponent
- Magnets: Mode (attract/repulse/spin/directional), Pole radius, Search radius, Particle count
- Material: Basecolor RGB, Metallic, Roughness, Sphere size
- Lighting: Lights intensity (multiplier), Env intensity (multiplier)
- Camera: Orbit R, Period, FOV, Elevation
- Composition: Bloom amount, Mirror toggle (controls both h and v flips)

**Single audio binding (per WOBAR pattern):**
`mag.Strength = floor + ceil * max(0, energy)^exp` — energy → spin force magnitude. Quiet sections: subtle drift. Builds: aggressive churn. Same `max(0, ...)` clamp pattern as attractor_chamber.

**Light palette cycling (palette_lights textDAT):**
Two warm-channel + cool-channel rings, non-syncing periods (70s warm, 90s cool). Form catches different hue combinations across time. Trimmed to warm/cool dyad for magnet_chamber's tighter palette (vs attractor_chamber's full 4-channel).

**Why this works (after today's failures):**
The POPX module screening method validated today: `magnetize` was placed and its output `pointAttributes` listed BEFORE committing to a build. Output had only transform-relevant attrs (no `PartId, PartForce, Density, Parent, iNumChildren`) — confirming it was safe for the geo COMP instancing path. Future POPX builds: always screen attrs first.

**Move file:** `moves/move_001.json`.

---

## v002 — Built (2026-05-01)

**Status:** shipped variant. Same magnetize core as v001 but pivoted aesthetic to **inside-the-tesseract / Cooper-in-4D / wireframe psychedelic**. Different visual register, same TD plumbing.

**Pivot from v001:**
- v001: pearl orb cluster, lit from outside, mirror mandala-of-spheres
- v002: white wireframe cubes, camera INSIDE the cluster, tumbling POV with chromatic aberration, scale-pulsed warp through geometry

**Key architectural additions vs v001:**

1. **Cube template instead of sphere:** `boxSOP` source → `wireframeSOP` (radius=ctrl.Wireradius) → `convertSOP totype='poly'` (CRITICAL — wireframe alone breaks geometryCOMP instancing; convertSOP polygonization fixes it). The `convert` step took multiple attempts; without it the wireframe instances at numinstances=1 only.

2. **Per-cube rotation + scale variation:** `randomPOP` chain after `mag_null` writes `Rotate` (3-comp 0-360°) and `ScaleRand` (1-comp 0.6-1.4). geo_render reads `instancerx/y/z = 'Rotate(0/1/2)'` and `instancesx/y/z = 'ScaleRand'`. Cubes tumbled at varying angles + sizes — breaks the rigid grid feel into organic crystalline lattice.

3. **Inside-POV camera:** `Camradius=0.1, Camfov=80, Camelev=0` — camera at center of the cube cluster, wide-angle perspective, Cooper-in-tesseract feel. Required dropping ctrl.Camradius.min to 0 (was 0.5).

4. **Camera tumble:** `cam.rz = absTime * Tumblespeed`, `cam.rx = 8 * sin(absTime * 2π/23)`. POV swirls slowly. Toggleable via ctrl.Tumbleenable.

5. **Scale-pulse warp:** `geo_render.scale = Pulsebase + Pulseamp * sin(t * 2π/Pulseperiod)`. Smooth in/out breathing (avoided sawtooth — snap-back was jarring). 12s default period, range 0.6-2.4. Particles appear to fly past camera in waves.

6. **Chromatic aberration chain:** `trail_comp` → 3 levelTOPs (R-only, G-only, B-only via highg/highb=0 patterns) → 2 transformTOPs (R shift left by `-Caoffset`, B shift right by `+Caoffset`, G stays center) → composite ADD x2 → null_out. Manual RGB split since TD has no native chromatic-aberration TOP. Default offset 0.008 (≈8px in 1024 frame).

7. **Hue rotation:** `hsvadjustTOP` with `hueoffset = (t * Huerate) % 1.0` when enabled. Default OFF for v002 (white wireframes have zero saturation, hue rotation doesn't shift them; only useful if material is given a tinted base color first).

8. **Mirror compositing — 4-fold (h+v):** `mirror_flip(h) → mirror_comp` then `mirror_flip_v → mirror_comp_v` for full quadrant symmetry. Mandala/sigil register.

**Rendering:**
- White constant material (`r=g=b=1, alpha=1`)
- Black bg (`render.bgcolora=1`)
- HDR env at low dimmer (0.3) since constantMAT doesn't read PBR but env affects bloom
- Bloom branch tuned mild (size=20, brightness=0.5)
- Trail feedback active (decay -0.15) for slight smear/depth — not aggressive enough to wash out

**`ctrl_master` updates — added "Effects" page (9 new params total = 30 across 7 pages):**
- Caoffset (0..0.04, default 0.008)
- Tumbleenable (toggle, default ON)
- Tumblespeed (0..30, default 6)
- Pulseamp (0..2, default 0.9)
- Pulseperiod (1..60, default 12)
- Pulsebase (0.3..4, default 1.5)
- Hueenable (toggle, default OFF)
- Huerate (0..0.1, default 0.017 ≈ 60s/cycle)
- Wireradius (0.0005..0.02, default 0.0015)

**Visual register:**
Cooper-in-4D-tesseract / inside-the-cathedral-of-wireframes / chromatic warp through architectural lattice. Pure white edges with red/cyan ghost ofsets, mirror-symmetric mandala, smooth scale pulse making cubes fly past viewer continuously, slow camera tumble.

**Why this looks works after today's failures:**
- Wireframe instancing required the `wireframeSOP → convertSOP polygonize → instance` chain (without convert, only 1 instance renders)
- POPX magnetize stayed as the proven core — clean POP attrs, 80→25 instances tunable
- All new visual is post-render TOP work, not POP plumbing — clean rendering pipeline
- Inside-POV (`Camradius=0.1`) creates immersive perspective without breaking instancing

**Move file:** `moves/move_002.json`.

---

