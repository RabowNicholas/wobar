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

## Feedback CHOP — state in the CHOP graph

`feedbackCHOP` is the CHOP-domain analog of feedbackTOP but with a **completely different API** (verified by inspecting the op's par list):

- **No target par at all.** No `par.top`, `par.chop`, `par.target` — feedbackCHOP samples ITS OWN INPUT, not an external target. Whatever you wire into input[0] is what gets delayed.
- **`par.output` mode** (default `'previous'`) controls what comes out:
  - `'previous'` — input's previous frame (1-frame delay) ← the most common use
  - `'shift'` — multi-frame delay buffer
  - `'sample'` — sample input at a specific frame
- **`par.delta`** — frame offset for sample/shift modes
- **`par.reset` / `par.resetpulse`** — clear the buffer
- Pattern: `current_value_chop → feedback → [now you have previous_value_chop on output]`
- Combine current and previous in downstream ops (mathCHOP, expressionCHOP, logicCHOP) for edge detection, hysteresis, derivatives, change detection.

### CHOP-feedback auto-reset rig (POPX `curve advection.toe` canonical)

When a simulation needs to AUTO-RESET based on its own state — not just a manual button — combine state derivation (POP→CHOP), threshold detection, hysteresis (feedbackCHOP), and OR-gated triggers:

```
analyzePOP (numpointsvertsprims=True)        ← count current sim state
    │
    ▼
poptoCHOP (attribscope='NumPoints')           ← extract count as CHOP sample
    │
    ▼
expressionCHOP (expr0: 'me.inputVal > op("constant1")["maxPoints"]')
    │                                         ← threshold check → 0 or 1
    ▼
feedbackCHOP                                  ← previous frame's threshold result
    │                                           (hysteresis / state remembering)
    ▼
logicCHOP.in2     (chopop='or')               ← combine ALL trigger sources
buttonCOMP (display=False) ──▶ logicCHOP.in0
keyboardinCHOP ─────────────▶ logicCHOP.in1
    │
    ▼
triggerCHOP (attack/decay/sustain/release = 0)
    │                                         ← clean edge pulse
    ▼
renameCHOP                                    ← rename to 'reset' for clarity
    │
    ▼
reset (nullCHOP)                              ← THE convergence point
```

The `reset` nullCHOP is then **referenced via expression** by every op that needs to reset:
```python
flow1.par.Reset.expr = "op('reset')['reset']"
speed1.par.resetpulse.expr = "op('reset')['reset']"
# ... any other op that should reset on the same trigger
```

**Why the hysteresis?** Without `feedbackCHOP` in the chain, the threshold-trigger would fire continuously while the condition is true (every frame the count exceeds maxPoints), causing repeated resets. With feedbackCHOP, downstream logic can detect EDGES — "fire reset only on the frame where count CROSSES the threshold" — by comparing current vs previous.

**Why a hidden button?** `buttonCOMP.par.display=False` makes it invisible in the UI but still triggerable programmatically (via Python `button.click()` or panel hover detection). Combined with `keyboardinCHOP` and the auto-trigger via OR-gate logic, you get: manual trigger + hotkey + automatic state-based all converging to the same reset pulse, with no visible UI clutter.

---

## Common Feedback Failures (cross-ref)

- **Going white**: opacity too high. See `TD_FOOTGUNS.md` §A1.
- **Going black**: composite mode wrong or opacity too low. See §A2.
- **Pixelated**: resolution mismatch. See §A3.
- **Sluggish 1-frame lag**: by design. See §A4.

---

## Cook-Loop-Safe Feedback Wiring (canonical pattern)

**This section is `feedbackTOP`-specific. For `feedbackCHOP`, see the "Feedback CHOP" section above — it has a completely different API (no target par, just sample its own input).**

When the feedback target itself appears downstream of the feedback in the cook graph (the common case: feedback feeds a composite whose previous frame the feedback wants to sample), a naive wiring creates a circular cook dependency. TD detects this and errors with "Not enough sources specified" or a red cook-loop warning.

**Wrong (creates the loop):**
```
feedback.par.top = composite_target
feedback.input[0] ◄── composite_target  ← same op = circular dep
```

**Right (canonical, breaks the loop):**
```
feedback.par.top = composite_target   ← samples its PREVIOUS frame (not current)
feedback.input[0] ◄── source_op        ← a DIFFERENT op (typically the upstream
                                          source feeding the composite) that has
                                          no dependency on feedback. Provides
                                          format/resolution/init only — its value
                                          is overwritten by par.top's previous-frame sample.
```

**Why:** feedbackTOP's `par.top` is specifically designed to break the cook dependency by sampling the previous frame (not the current). The input[0] wire is required by TD for format/init resolution but doesn't have to be the same op as par.top — and **must not be**, or the safety is defeated.

**Canonical example:** POPX `dla.toe` post chain has `render → ssao → cross ← feedback`. Feedback wires: `par.top = cross` (samples cross's prev frame for the trail), `input[0] = ssao` (the source that ALSO feeds cross — no feedback dependency, safe). The trail accumulates frame-over-frame without a cook loop.

**Reference:** WOBAR base_current smoke layer (VILOS) uses the same pattern. Documented also in `TD_FOOTGUNS.md` failure modes.

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
