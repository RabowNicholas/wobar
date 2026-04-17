---
title: Feedback TOP Patterns
version: 1.0
last_updated: 2026-04-16
status: live
scope: Feedback TOP recipes — trails, tunnels, zoom, generative feedback, decay, bloom-like effects.
dependencies: TD_LIBRARY_INDEX.md, TD_OPERATORS_TOP.md, TD_EFFICIENT_NETWORKS.md
---

# FEEDBACK TOP PATTERNS

Feedback is TD's most powerful visual mechanic. Every trail, tunnel, generative smear, and organic-looking motion draws from the same base pattern: **current frame composited with last frame, transformed a bit each frame**.

---

## The Core Loop

```
Source TOP ──► Composite (Over, Background = Source, Foreground = Feedback output)
                       │
                       └──► Null ("null_frame") ──► [downstream post]
                               ▲
                               └── Feedback TOP ◄── Transform ◄── Level (opacity < 1)
```

Read the loop this way:
1. Feedback TOP reads last frame's output (from Null "null_frame").
2. Level TOP attenuates it (opacity 0.95).
3. Transform TOP nudges it (scale, rotate, translate).
4. Composite mixes current Source with this attenuated, transformed last frame.
5. Composite's output goes through Null "null_frame" — which becomes last frame's output for the next cook.

---

## The Three Critical Parameters

### 1. Level TOP opacity (decay)
- 1.0 = no decay, trail grows forever → goes white (see `TD_FOOTGUNS.md` §A1).
- 0.98 = slow decay, long trails.
- 0.95 = medium decay — most common.
- 0.85 = fast decay, short tails.
- 0.0 = no feedback at all.

### 2. Transform TOP parameters (shape of motion)
- **Scale > 1** = zoom out (trails grow away from center).
- **Scale < 1** = zoom in (tunnel into center).
- **Translate XY** = directional wipe (trails fly left/right/up/down).
- **Rotate Z** = spiral (rotating zoom).

### 3. Composite mode (how source meets feedback)
- **Over** = source replaces feedback where alpha > 0 (crisp trails).
- **Add** = source + feedback (brightening, risks blowout without low opacity).
- **Screen** = lighten-only (glow aggregation).
- **Max** = keep brightest pixel per location (hard edges preserved).
- **Multiply** = darken source by feedback (rare; use for masking effects).

---

## Pattern 1 — Basic Trails

```
Source (e.g., Circle TOP moving) ──► Composite (Over) ──► Null "null_frame"
                                            ▲
                                            └── Feedback ◄── Level (opacity 0.95) ◄── Null "null_frame"
```
- Source draws on top of fading previous frames.
- Adjust opacity for trail length.

---

## Pattern 2 — Tunnel / Zoom

```
Source ──► Composite (Over) ──► Null "null_frame"
                 ▲
                 └── Feedback ◄── Level (0.98) ◄── Transform (Scale = 1.02) ◄── Null "null_frame"
```
- Each frame, the previous frame is scaled up 2%. Over many frames, the image blooms outward into a tunnel.
- **Scale > 1** = tunnel pushing outward.
- **Scale < 1** = tunnel pulling inward.

---

## Pattern 3 — Spiral

```
Transform (Scale = 0.99, Rotate Z = 1°) in the loop.
```
- Combines rotation + scale for a rotating inward spiral.
- Tune rotation for chirality (left / right handed spiral).

---

## Pattern 4 — Directional Streaking

```
Transform (Translate X = 0.005) in the loop.
```
- Feedback drifts right every frame — streaks/lines to the right.
- Opacity 0.9 for short streaks; 0.99 for long comet tails.

---

## Pattern 5 — Generative Smear (Displacement Feedback)

Displace TOP inside the feedback loop adds organic flow:
```
Null "null_frame" ──► Level ──► Displace (displacement map = Noise TOP) ──► Feedback
```
- Noise TOP slowly changing + Displace TOP inside the loop = flowing, organic trails.
- Tune Displacement magnitude for subtle vs chaotic.

---

## Pattern 6 — Feedback + Blur (Bloom-style)

```
Feedback ◄── Level (0.95) ◄── Blur TOP (small radius) ◄── Null "null_frame"
```
- Each frame, previous frame gets slightly blurred before being composited back.
- Produces a glowing, ethereal feel.
- Cost increases with blur radius — downsample the feedback branch to half res.

---

## Pattern 7 — Audio-Driven Feedback Parameters

Drive Transform's Scale or Translate from audio:
```
null_audio_sub ──► Math (range to 0.99–1.02) ──► Transform Scale
```
- Bass pushes the tunnel outward.

Drive Level opacity from audio:
```
null_audio_overall ──► Math (invert: 1 - x) ──► range to 0.85–0.98 ──► Level opacity
```
- Louder audio = faster decay = tighter trails.

---

## Pattern 8 — Frame-Buffered Trail (Cache-based)

Alternative to Feedback TOP — use Cache TOP:
```
Source ──► Cache TOP (N frames) ──► Cache Select (index = current - N) ──► Composite with current
```
- Hard-edged, discrete trails at N-frame delay.
- Less blurry than feedback but more memory-intensive.

---

## Pattern 9 — Dual Feedback Layers

Two independent feedback systems composited:
```
Layer A: fast feedback (opacity 0.9, zoom 1.01) — short punchy trails
Layer B: slow feedback (opacity 0.99, rotate 0.5°) — long rotating ambience

Composite (Layer A over Layer B) ──► Out
```
Use for: crisp motion on top of atmospheric background motion.

---

## Pattern 10 — Feedback Resolution Downsampling

Feedback at full resolution is expensive. Downsample:
```
Source (at 1280²) ──► Resolution TOP (640²) ──► feedback chain at 640² ──► Resolution TOP (1280²) ──► Out
```
- 4× cheaper feedback.
- Slight softness — usually aesthetic-positive.
- Match internal ops to same resolution to avoid per-frame resize.

---

## Pattern 11 — Post Only Post-Feedback

Put expensive post (Bloom, Chromatic, Film Grain) **after** the feedback exit Null, not inside the loop:
```
Null "null_frame" ──► Bloom ──► Chromatic ──► Level ──► Out
```
- Post runs once per frame on the composited result.
- Keeps feedback loop itself minimal and fast.

---

## Pattern 12 — Reset / Refresh

Clear feedback on demand:
```
Button COMP → triggers Feedback TOP → Reset pulse parameter.
```
Or add a Constant TOP (black) in series and blend via Cross TOP to fade to black before resuming.

---

## Pattern 13 — Feedback for Noise Accumulation

Feedback can integrate noise over time:
```
Noise TOP (slowly changing) ──► Composite (Add, low opacity) ──► Null "frame"
                                       ▲
                                       └── Feedback ◄── Level (0.98) ◄── Null "frame"
```
- Produces a slowly-swirling buildup of noise, never identical twice.
- Good for abstract backgrounds.

---

## Pattern 14 — Feedback with Color Shift

Shift hue each frame:
```
Null "null_frame" ──► HSV Adjust (small Hue Shift) ──► Level ──► Feedback
```
- Trails progressively shift in color — rainbow smears.

---

## Common Feedback Failures (cross-ref)

- **Going white**: opacity too high. See `TD_FOOTGUNS.md` §A1.
- **Going black**: composite mode wrong or opacity too low. See §A2.
- **Pixelated**: resolution mismatch. See §A3.
- **Sluggish 1-frame lag**: by design. See §A4.

---

## Feedback Performance

- Bandwidth-bound: each frame = read + write of the full texture.
- 1280²@16-bit RGBA = ~26MB per frame. At 60fps that's 1.5GB/s bandwidth on the GPU for read + write.
- **Downsample before feedback is the single biggest perf win** — see Pattern 10.
- Pixel format 8-bit RGBA halves the bandwidth vs 16-bit (but flattens HDR).
- Keep feedback loops tight — Level + Transform + Composite + Feedback. Every extra op inside the loop multiplies cost.

---

## Brand Note

Wobar uses feedback in specific ways per act — tunnels for Act 3, radial expansion for Act 4, gentle circles for Act 1. Brand-specific parameter ranges live in `WOBAR_TD_REFERENCE.md` and act shader code in `WOBAR_GLSL_PATTERNS.md`. This file is the mechanics; those files are the taste.

---

## Reading This File

The Core Loop and Three Critical Parameters are must-know. Patterns 1–14 are recipes — use whichever matches the need. Performance section applies to all of them.
