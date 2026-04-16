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
- `Flip TOP` after `comp_mirror` (flipping the composited output) → the seam lands at center and is perfectly straight — worse than full symmetry. The flip must happen before the composite to bury the seam inside the overlap.
- `Displace TOP` always on (displaceweight constant 0.05) → glitch becomes ambient texture and stops reading as a peak trigger. Displaceweight must come from `transient` so it fires sharply on note attacks and is nearly zero at breakdown.
- Any warm color in content source → Act 3 rule violation. If content source includes warm tones (e.g. from a Noise TOP with default HSV), add a second HSV Adjust TOP after desat targeting orange (hue 20–40°, satmult 0.0) before the feedback entry point. The feedback loop will amplify any warm tones that make it past desat.
- `sx`/`sy` = 1.0 exactly → no inward motion, feedback accumulates in place and immediately whites out.
