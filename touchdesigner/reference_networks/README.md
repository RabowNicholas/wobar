# Reference Networks

Structural examples for WOBAR TD builds. Each entry documents a working node chain and the taste decisions behind it. When building a new network, find the closest structural match here first — propose the new build as a diff against it rather than from scratch.

**To add a new entry:** drop a PNG export of the network into this folder alongside this file, then fill in the template below. Screenshot filename must match exactly what you dropped in.

---

## Template

```
### [Network Name]
Screenshot: `filename.png`
Act: Act N / NAME
What it does: One sentence — the visual output and its primary audio driver.

Node chain:
​```
[OP name] ([type]) — key parameter
  ↓
[OP name] ([type]) — key parameter
  ...
​```

Taste decisions:
- Bullet 1 — structural choice and why
- Bullet 2 — parameter value and what it prevents
- Bullet 3 — ordering decision and its perceptual consequence

Known non-working variations:
- What was tried → why it fails
```

---

## Entries

---

### Act 1 Breath Circle
Screenshot: `act1_breath_circle.png`
Act: Act 1 / INVOCATION
What it does: Soft-edged circle with sub-bass-driven radius and LFO breath rhythm (~70 BPM), cropping generative content to a portal shape.

Node chain:
```
lfo_breath (LFO CHOP)   sub_lag (Lag CHOP)
  ↓ rate 1.0–1.33 Hz      ↓ up 0.05s / down 0.30s
math_breath (Math CHOP) — remap 0→1 to 0.35→0.55
  ↓
circle1 (Circle TOP) — radius driven by CHOP export, softness 0.25–0.40
  ↓
[content source]  →  comp_crop (Composite TOP, Inside) ← circle1 (Input 2)
                           ↓
                       null_out (Null TOP)
```

Taste decisions:
- `Composite Inside` (not `Multiply`) for the crop — Inside uses the circle's alpha channel directly, so the edge softness lives entirely in the Circle TOP and can be audio-reactive without affecting the content brightness. Multiply bleeds circle edge brightness into content, which warms highlights uncontrollably.
- Sub-bass drives both `radiusx`/`radiusy` (size breath) and `softness` (edge sharpness) simultaneously — at high sub-bass the portal blooms open AND gets a harder edge, which reads as the circle "inhaling" rather than just scaling.
- LFO CHOP drives the long breath arc (1.0–1.33 Hz = 60–80 BPM); sub-bass Lag CHOP adds the audio transient layer on top. Two separate drivers prevent the breath from disappearing when audio is absent.

Known non-working variations:
- `Composite Multiply` instead of `Inside` → circle edge tints content near the boundary; warm highlights appear at breakdown when softness increases. Not Act 1 — reads as a glow leak, not a portal edge.
- Driving `softness` from `energy` instead of `sub_bass` → energy is highest at melodic breakdowns (wide-band), so the edge blurs most during the calm sections and sharpens at drops — opposite of the intended behavior. Sub-bass is the right driver.
- Single combined driver (LFO + sub summed before export) → at silence the breath stops entirely; the circle looks static. Two separate drivers keep breath alive even when track goes quiet.
- `radius` > 0.55 — circle bleeds past frame edges on portrait 720×1280. Cap at 0.52.

---

### Act 3 Tunnel + Partial Mirror
Screenshot: `act3_tunnel_mirror.png`
Act: Act 3 / CONFRONTATION
What it does: Inward-scrolling feedback tunnel with 85–90% horizontal mirror symmetry and noise-driven displacement, cold palette only, transient-triggered glitch.

Node chain:
```
[content source] (e.g. glslTOP or Noise TOP)
  ↓
hsv_desat (HSV Adjust TOP) — satmult 0.15, valuemult 0.80
  ↓
feedback1 (Feedback TOP) — targetop = null_out
  ↓
xform_tunnel (Transform TOP) — sx/sy 0.978, rotate 0.3°, bgcolor black
  ↓
lvc (Level TOP) — opacity (Post) 0.93, pixel format rgba16float
  ↓
flip1 (Flip TOP) — flipx on
  ↓
lvc_flip (Level TOP) — opacity 0.875 (the 87.5% mirror weight)
  ↓
comp_mirror (Composite TOP, Over) ← lvc output (Input 1) + lvc_flip (Input 2)
  ↓
disp_glitch (Displace TOP) ← noise_glitch (Noise TOP, displaceweight driven by transient)
  ↓
null_out (Null TOP)   ← feedback1 targetop points here
```

Taste decisions:
- Mirror weight at 0.875 (not 1.0, not 0.5) — 85–90% symmetry means the flip composite is nearly but not perfectly even. The seam between left and right halves is faintly visible at oblique angles. Perfect symmetry (`lvc_flip opacity = 1.0`) reads as a digital artifact; the flaw is structurally intentional for Act 3.
- Feedback Level TOP (`lvc`) opacity 0.93 is higher than Act 2 (0.89–0.91) — Act 3 wants longer trails that accumulate into tunnel depth. Lower opacity kills the depth illusion; the tunnel reads as a single-layer pattern instead of an infinite corridor.
- `xform_tunnel` scale 0.978 (not 0.98+) — slightly tighter inward pull than Act 2 spiral. The tunnel closes faster, which reads as the space getting less navigable. Combined with the partial mirror, the viewer feels the geometry is working against them.

Known non-working variations:
- `instancepop` / `instanceop` on Geometry COMP → single dot at origin. These modes do NOT do position-based instancing. Only Script CHOP bridge works.
- `op('../torus_sop')` in Script CHOP callbacks → None. Script CHOP `op()` resolves at parent COMP scope — use `op('torus_sop')` (no `../`).
- Wiring feedbackTOP input[0] directly to null_out → cook dependency loop on comp_main. Wire a black constantTOP as seed; par.top captures null_out asynchronously.
- MAT expressions `op('../../sel_audio')` inside geo COMP → None. Use absolute path `/project1/base_act2_particles/sel_audio`.

---

### Act 2 Descension Vortex (POP torus instancing)
Screenshot: *(no export yet)*
Act: Act 2 / DESCENSION
What it does: 720-sphere torus viewed overhead, rotating inward with feedback spiral trail accumulation. Rotation speed and noise amplitude driven by bass/sub_bass. Act 2 teal palette via lookup ramp.

Node chain:
```
torus_sop (Torus SOP) — radx 1.2, rady 0.08
  ↓
noise_sop (Noise SOP) — amp expression-driven by sub_bass

pos_chop (Script CHOP) — reads torus_sop.points, outputs tx/ty/tz × 720 samples
  ↓
geo_particles (Geometry COMP)
  ├─ sphere_template (Sphere SOP, radx 0.03, render=True)
  ├─ mat_particles (Constant MAT, Act 2 teal, applypointcolor=True, abs path audio exprs)
  └─ instancing: instancetop=pos_chop, instancetx/ty/tz = 'tx'/'ty'/'tz'

cam_main (Camera COMP) — tx 0, ty 3.5, tz 0.8, rx -78°, fov 55
light_key (Light COMP) — distant, white

render_main (Render TOP, 720×1280)
  ↓
hsv_desat (HSV Adjust TOP) — saturationmult 0.85
  ↓
level_main (Level TOP) — brightness1 expression: 1.2 + energy * 0.5
  ↓
comp_main (Composite TOP, Over) ← [input 1] level_trail
  ↓
lookup_act2 (Lookup TOP) ← ramp_act2 (Ramp TOP, 256×1, horizontal)
  ↓
null_out (Null TOP)
  ↑ par.top targets here
black_seed (Constant TOP, 720×1280, black) → feedback_main (Feedback TOP)
  ↓
xform_spiral (Transform TOP) — sx/sy 0.993, rz expr: absTime.seconds*22*(1+bass*2)
  ↓
level_trail (Level TOP) — opacity 0.82
  ↓ (→ comp_main input[1])
```

Taste decisions:
- Script CHOP bridge (not POP instancing) — `instancepop` and `instanceop` on Geometry COMP are broken for position-based instancing in TD 2025. Script CHOP reading SOP points is the only working path.
- Camera rx -78° (near-overhead) — transforms the horizontal torus ring into a near-circle filling the portrait frame. Gives the "looking down into the vortex" portal depth.
- level_trail opacity 0.82 (not 0.93 like Act 3) — tighter decay creates a shorter spiral coil, which reads as "falling inward" rather than a deep tunnel. Act 2 is about descent, not infinite depth.
- feedbackTOP seed = black constantTOP (not null_out wire) — direct wire creates cook dependency loop. Black seed gives a clean first frame before feedback accumulates.
- Absolute paths in MAT expressions — relative `op()` inside child COMP context returns None.

Known non-working variations:
- `instancepop` / `instanceop` on Geometry COMP → single dot at origin. These modes do NOT do position-based instancing. Only Script CHOP bridge works.
- `op('../torus_sop')` in Script CHOP callbacks → None. Script CHOP `op()` resolves at parent COMP scope — use `op('torus_sop')` (no `../`).
- Wiring feedbackTOP input[0] directly to null_out → cook dependency loop on comp_main. Wire a black constantTOP as seed; par.top captures null_out asynchronously.
- MAT expressions `op('../../sel_audio')` inside geo COMP → None. Use absolute path `/project1/base_act2_particles/sel_audio`.

---

### Act 3 Tunnel + Partial Mirror
Screenshot: `act3_tunnel_mirror.png`
Act: Act 3 / CONFRONTATION
What it does: Inward-scrolling feedback tunnel with 85–90% horizontal mirror symmetry and noise-driven displacement, cold palette only, transient-triggered glitch.

Node chain:
```
[content source] (e.g. glslTOP or Noise TOP)
  ↓
hsv_desat (HSV Adjust TOP) — satmult 0.15, valuemult 0.80
  ↓
feedback1 (Feedback TOP) — targetop = null_out
  ↓
xform_tunnel (Transform TOP) — sx/sy 0.978, rotate 0.3°, bgcolor black
  ↓
lvc (Level TOP) — opacity (Post) 0.93, pixel format rgba16float
  ↓
flip1 (Flip TOP) — flipx on
  ↓
lvc_flip (Level TOP) — opacity 0.875 (the 87.5% mirror weight)
  ↓
comp_mirror (Composite TOP, Over) ← lvc output (Input 1) + lvc_flip (Input 2)
  ↓
disp_glitch (Displace TOP) ← noise_glitch (Noise TOP, displaceweight driven by transient)
  ↓
null_out (Null TOP)   ← feedback1 targetop points here
``` (flipping the composited output) → the seam lands at center and is perfectly straight — worse than full symmetry. The flip must happen before the composite to bury the seam inside the overlap.
- `Displace TOP` always on (displaceweight constant 0.05) → glitch becomes ambient texture and stops reading as a peak trigger. Displaceweight must come from `transient` so it fires sharply on note attacks and is nearly zero at breakdown.
- Any warm color in content source → Act 3 rule violation. If content source includes warm tones (e.g. from a Noise TOP with default HSV), add a second HSV Adjust TOP after desat targeting orange (hue 20–40°, satmult 0.0) before the feedback entry point. The feedback loop will amplify any warm tones that make it past desat.
- `sx`/`sy` = 1.0 exactly → no inward motion, feedback accumulates in place and immediately whites out.

---

### Glass Orb (nested POPX shells, audio-reactive)
Screenshot: *(no export yet)*
Act: Act 2 / DESCENSION
What it does: Three nested translucent-glass shells of magnetized facets, each tumbling on a Lissajous integral of its own audio band (bass→outer, mid→middle, high→inner), with a drop-gated feedback "melt" and a cool-band hue-cycling environment. Camera sits at center — the nested depth reads as a frequency tunnel. Network: `magnetize` (`/example`).

Node chain:
```
box1 (boxPOP, shard) + pointgen1>attribute1>noise1 (wander poles)
  ↓
instancer1 (POPX spherical) — Scale=Orbsize, Freq=Facetcount
  ↓
magnetize1 (POPX) — Affectrot, Aimweight=Glintturn (pole-aim glints)
  ↓
transform/color_modifier1 → geo2 (inner ×1) / geo2_mid (Midscale) / geo2_large (Outerscale)
   each geo rx/ry/rz = spin_angles[band] * Lissajous_ratio % 360

base_audio.smooth_out (bass/mid/high) → spin_speeds (constantCHOP: base*(1+band*react))
  ↓
spin_angles (speedCHOP — INTEGRATES speed → continuous angle)

hdri_env → env_down (resTOP 512) → hsv_cycle (cool-band hue) → env_obsidian (IBL light)
mat_obsidian (pbrMAT — translucent: alpha<1, blending, alphafront/alphaside fresnel)
  ↓
render1 (transparent, sortedblending) + cameraViewport + lights
  ↓
comp_bg → bloom → grade(+cool tint) → feedback MELT (drop-gated) → vignette → grain → switch_post → out1
```

Taste decisions:
- 3 shells are SCALED COPIES of one POP (geo COMP scale), not 3 sims — cheap. They read as distinct LAYERS via independent MOTION (parallax), not density: each tumbles at a different audio-driven rate. Density alone can't separate them — from inside, a sparse shell shows only ~12 facets in the FOV.
- Rotation is INTEGRATED through a speedCHOP, never `band` multiplied into `absTime*speed` — the latter jumps when the band changes. Integration gives smooth audio-driven accel/decel.
- The melt is drop-GATED (`clamp(0,(energy-gate)*sens)`) — verses stay clean, only drops dissolve. Keep it a dissolve (surrender / Act 2), not an explosion (release / Act 4).
- Cool-band hue cycle + Saturation ~0.45 keeps the psychedelia on-brand (Act-2 blue/teal); full-spectrum rainbow is off-brand. The glass is NEUTRAL — color comes from the env, not the material. *(Starting point, not a hard rule.)*

Known non-working variations:
- Pole-aim orientation does NOTHING on a flat grid (all normals +Z) — needs a curved surface (the sphere) for the magnetize aim to engage.
- DOF on the translucent shards is not viable — alpha-blended/instanced geo writes no clean depth (depthTOP, drawdepthonly, opaque-material override all failed).
- Animating the env map re-bakes IBL every frame at ~142 ms unless `envlightmapprefilter='off'` + env map downsampled to ~512.
- `sin`/`cos` in hue/spin expressions → `NameError` — use `math.sin` or an `abs`-based triangle/smoothstep.
