# CHANGE LOG — iris

Audio-reactive iris portal for an Act 4/5 cusp track (Subtronics "Eyes Cut Deeper" remix, 95 BPM halftime). Started from a "[TD Drop #05] Eyes" tutorial base — twisted-torus geometry creates radial-fiber iris stroma + the inner cylinder doubles as the tunnel when camera dives through the pupil. Built directly at `/project1` (no wrapping baseCOMP), same convention as attractor_chamber / magnet_chamber.

## Locked direction (2026-05-04)

- Pure iris in void, vertical-first 720×1280.
- Stylized real-eye look in monochrome purple range — limbal ring, stroma, pupillary ruff, amber flecks for biological recognition. No anatomical brown/blue.
- Iris becomes tunnel via camera dive through pupil (no second layer).
- Drop choreography: pupil dilates + iris fibers stretch outward + light flash + camera dives. Pupil dilation timed to slow envelope (sub-bass / kick band, smoothed) — NOT chop-by-chop.
- Halo pulses slowly during low energy (~0.1 Hz breath).
- Composition: dominant scale (~65–70% frame width).
- Single audio binding per WOBAR convention: `Energy → Drive` master, internally couples to camera tz, twist3 strength, torus rady (pupil), light dimmer, halo radius.

## Move 001 — 2026-05-04

**Recolor iris palette toward stylized real-eye purple.**

- `/project1/ramp2_keys` (basecolor lookup palette) rewritten — old palette went black → magenta-purple → white → cyan-blue (hot magenta render). New palette: 7 stops, limbal-ring shadow `#0D0814` → deep eggplant `#2E1A45` → mid-purple stroma `#4F326B` → mauve ruff `#6B4D6E` → amber/tobacco fleck `#8C5C2E` (gold-fleck biology cue) → slate-violet `#8C7DA1` → bone-ash highlight `#C9BFB4`.
- `/project1/noise2.mono = True` — was pumping chromatic noise into the feedback chain, contributing to magenta cast.
- `/project1/hsvadj1.saturationmult` 1.34 → 1.05 — was amplifying the magenta band.

Result: magenta eliminated. Iris reads as deep-purple stroma with ash highlights and subtle warm flecks. Closer to "biological iris in WOBAR palette" register.

## Move 002 — 2026-05-04

**Scale iris geo toward dominant frame size.**

- `/project1/transform2.scale` 1.3 → 2.2 — iris now occupies ~50% frame width (medium-dominant). Was ~35%.

Side effect noted: light coverage dropped. light1 sits at world (0.77, 0, 9.97) with dimmer=3.5; relative illumination per surface dropped as geo grew. Render went notably darker overall, with fiber detail visible on the right side and shadow-dominant on the left. Lighting compensation needs to follow before pushing scale further or accepting current size.

## Move 003 — 2026-05-04

**Single-light symmetry + brightness pass.**

- `/project1/light1.tx` 0.77 → 0 (center horizontally)
- `/project1/light1.tz` 9.97 → 4.5 (pull closer, stronger falloff)
- `/project1/light1.ry` -4.44 → 0 (point straight at iris)
- `/project1/light1.dimmer` 3.5 → 5.5

Result: iris is now symmetrically lit, dead-centered, radial fibers clearly readable from pupil outward. Single-light modeling preserved (displacement still gets directional shading). Reads instantly as an eye.

Open notes:
- Highlights desaturate toward gray at peak brightness — light intensity is winning over the palette at ridge tops. Options for later: tint light1 cool-purple, lower the bone-ash stop in ramp2_keys, or pull dimmer to ~4.8.
- Pupil radius still small (~15% of iris diameter). Will need to grow for the dilation drop choreography later.
- Halo glow now very subtle at this brightness — re-evaluate when we add the pulse-halo move.

## Move 004 — 2026-05-04

**Tint light1 cool-violet so highlights stay in palette.**

- `/project1/light1.cr` 1.0 → 0.85
- `/project1/light1.cg` 1.0 → 0.78
- `/project1/light1.cb` left at 1.0

Result: ridge highlights now read as cool lavender/violet rather than neutral gray. Whole iris reads as a unified deep-purple monochrome palette without sacrificing the bright peaks. Trade: amber/tobacco fleck stops are now visually muted (cool light vs warm pigment) — the gold-fleck biology cue is suppressed but the radial-stroma structure is doing the iris-recognition work on its own. Acceptable.

## Move 005 — 2026-05-04

**Open pupil baseline.**

- `/project1/torus1.rady` 0.65 → 0.5

Result: pupil grew from ~15% to ~30% of iris diameter. Surprise side effect: the inner cylinder of the twisted-torus geometry is now visible THROUGH the pupil as a bright violet glint — you can see into the tunnel-wall structure even at rest. Pro: this is literally the "iris becomes tunnel" mechanism we designed around; resting state hints at the dive depth, on-theme for "Eyes Cut Deeper." Con: less clean as pure iris-with-black-pupil read; glint shape is asymmetric. **Decision: kept rady=0.5 — Nick confirmed the resting-tunnel-hint reads as feature.**

## Move 006 — 2026-05-04

**Halo pulse — slow breath during low-energy register.**

- `/project1/ramp3.period` was constant 1.5 → set to expression `1.5 + 0.15 * math.sin(absTime.seconds * 2 * math.pi * 0.1)`. ParMode = EXPRESSION.

10-second cycle, ±10% radius modulation. Halo ring breathes slowly even before audio is wired — gives the resting state a subtle "alive eye" register.

TD expression gotcha logged: `sin()` not in expression namespace by default — must use `math.sin()`. Promotable to TD_BUILD_LOG correction tracker.

## Move 007 — 2026-05-04 (REVERTED)

Attempted warm halo tint via separate colored ring layer (`ramp_halo_tint` + `ramp_halo_tint_keys` + `comp_halo_blend` between hsvadj1 and null_out, screen blend, mauve→transparent circular gradient pulsing in sync with the existing halo).

Iterated through "over" → "add" → "screen" blend modes to dial in. Final state had cool-violet iris with warm-mauve glow ring outside it — biologically "soft skin glow around the eye."

**Reverted by Nick.** The defined ring shape competed with the iris instead of complementing it — composition felt cluttered, iris no longer cleanly floated in void. Three new ops destroyed, `hsvadj1 → null_out` connection restored. Move file deleted from `moves/`. Lesson logged: any added composition layer needs to be invisible-when-not-active or the negative space loses its weight.

## Move 007 — 2026-05-04

**Add black circle pupil mask (~80% of iris diameter).**

- `/project1/circle_pupil` (circleTOP) — solid black filled circle, transparent background, soft edge. Final params: `radiusunit=pixels`, `radiusx=radiusy=175`, `centerx=centery=0` (centered via default justify), `softness=8 pixels`, `bgalpha=0`, `fillcolor=(0,0,0,1)`. Resolution 720×1280.
- `/project1/comp_pupil` (compositeTOP) — `operand=over`. Inputs: `hsvadj1[0]`, `circle_pupil[1]`.
- Wired: `hsvadj1 → comp_pupil[0]`, `circle_pupil → comp_pupil[1]`, `comp_pupil → null_out` (replacing prior `hsvadj1 → null_out`).

Result: dilated drop-state pupil look — large clean black pupil, iris reduced to thin radial-fiber ring around it. Reads as a fully dilated eye in moment of awe / shock. Subtle glint peeks at upper-right edge from inner cylinder geometry — accepts as biological "light catching pupil rim."

Iteration history within this move:
- First attempt: `centerx=centery=0.5` with `radiusunit=fraction`. Centerunit=fraction is OFFSET from justify-center, so 0.5,0.5 placed circle in upper-right corner instead of center. Fixed to centerx=centery=0.
- Second attempt: bumped radius from 0.07 to 0.13 to 0.2 to 0.3 — circle was rendering as oval, not circle. `radiusunit=fraction` interprets radiusx as fraction-of-width and radiusy as fraction-of-height; on 720×1280 same numeric value gives 1.78× larger Y radius. Fixed to `radiusunit=pixels`.
- Final: 175px circle, soft 8px edge.

Two new TD gotchas to log:
1. `circleTOP.centerx/y` with `centerunit=fraction` is OFFSET from justify-anchor, not absolute position. Default 0,0 = at center (with center justify). Setting 0.5, 0.5 nudges by half-resolution in each axis.
2. `circleTOP.radiusx/y` with `radiusunit=fraction` is anisotropic on non-square frames. Use `fractionaspect` or `pixels` for a true circle.

Both promotable to TD_BUILD_LOG correction tracker.

## Failed biological experiments (between move 007 and 008)

Two attempts to push iris into "real eye" territory that didn't land and were reverted:

**Catchlight (small bright reflection in pupil)** — Created `circle_catchlight` + `comp_catchlight` between comp_pupil and null_out. Caught a TD gotcha: `circleTOP.premultrgbbyalpha=True` (default) caused the catchlight to be invisible in `over` composite at small sizes (visible at 200px+ as solid white, invisible at 22-35px). Setting `premultrgbbyalpha=False` made it visible but positioning kept overlapping with existing inner-cylinder glint. After multiple iterations couldn't get a clean readable catchlight. Cleaned up — destroyed both ops, restored direct comp_pupil → null_out wiring. Logged the premultrgbbyalpha gotcha to TD_BUILD_LOG.

**Wet PBR surface** — Tried roughness 1.0 → 0.25 → 0.5 → 0.7 → 0.88 with metallic 1.0 → 0.15 → 0. All resulted in mirror-finish blowout because `light1.dimmer = 5.5` (boosted earlier for larger geo) overpowered any glossy surface into plastic-mirror look. Real wet eye PBR would need light dimmer dropped to ~3.0 first. Reverted to defaults (roughness=1.0, metallic=1.0).

Both reverts done in-place — no move files written for these experiments.

## Move 008 — 2026-05-04

**Limbal ring overlay (dark band at iris outer edge).**

- `/project1/circle_limbal` (circleTOP) — circular ring shape using borderwidth (no fill). Final params: `radiusunit=pixels, radiusx=radiusy=165, borderwidth=25, borderr/g/b=0, borderalpha=1, fillalpha=0, bgalpha=0, softness=6, premultrgbbyalpha=False`. Resolution 720×1280.
- `/project1/comp_limbal` (compositeTOP) — `operand=over`. Inputs: comp_pupil[0], circle_limbal[1].
- Wired: `comp_pupil → comp_limbal[0]`, `circle_limbal → comp_limbal[1]`, `comp_limbal → null_out`.

Result: subtle darkening at the iris outer edge, but doesn't read as a clean defined limbal ring — competes with the iris's natural alpha falloff to dark void. Effect is barely visible. Honest assessment: post-render composite overlays are fighting the geometric texture chaos. Limbal ring isn't doing much; left in the network for now (negligible visual impact, easy to revert later if desired).

## Move 009 — 2026-05-04

**Iris boundary mask — contain feedback trails within iris circle.**

Diagnosis: feedback chain (`comp4 → feedback1 → displace1 → level4 → comp4`) was pushing iris content outside the iris radius over many frames. The geo rotation (`geo1.rz = absTime * -5`) plus iterative displacement made trails extend downward and outward indefinitely. `comp4.operand=maximum` doesn't fade RGB so trails persisted.

Fix: insert circular multiplicative mask after comp4 so both forward path AND feedback loop only see iris-bounded content. Anything pushed outside the iris radius gets multiplied by zero each frame.

- `/project1/circle_iris_bound` (circleTOP) — solid white-filled circle (the multiply mask). `radiusunit=pixels, radiusx=radiusy=230, fillcolor=(1,1,1,1), bgalpha=0, softness=20, premultrgbbyalpha=False`.
- `/project1/comp_iris_bound` (compositeTOP) — `operand=multiply`. Inputs: comp4[0], circle_iris_bound[1].
- Rewiring: `level5[0]` was `comp4`, now `comp_iris_bound`. `feedback1.par.top` was `comp4`, now `comp_iris_bound`. Both forward and feedback paths now read the bounded version.

Result: trails INSIDE the iris are preserved (motion blur, fluid afterimage feel) but cannot escape the iris boundary. Iris reads as a contained eye. Bottom tail gone. Soft 20px edge fade keeps the boundary natural.

## Move 010 — 2026-05-04

**Fix: comp_pupil swaporder — pupil mask was BENEATH the iris this whole time.**

Investigation triggered by Nick asking what was causing inside-pupil bright spots. Initial diagnosis was that the bright crescents were the inner cylinder of the twisted-torus geometry visible through the natural donut hole. Tested `pbr1.cullface = backfaces` to remove the back side — didn't work because the inner cylinder is still front-facing on the twisted geo. Reverted.

Then tested bumping `circle_pupil.radiusx/y` from 175 → 210 → 230 → 250 to cover the glints. None worked — the dark area in the rendered output was MUCH smaller than the set radius. Verified circle_pupil standalone rendered correctly (e.g. 230 radius → ~230px black circle). Therefore the composite was the issue.

Root cause: in compositeTOP with `operand=over` and `swaporder=False` (default), **input 0 is rendered ON TOP of input 1**, not the other way around. So `hsvadj1` (iris, input 0) was always being drawn over `circle_pupil` (black mask, input 1) — the iris fibers were on top of the pupil mask, not the other way around. The bright crescents weren't bleeding through the mask — the mask was simply BEHIND them.

Fix:
- `/project1/comp_pupil.swaporder` False → True (flips input render order)
- `/project1/circle_pupil.softness` 8 → 10 (slightly softer edge for natural blend)
- Radius restored to 175 (same as move 007). With proper masking now active, 175 covers most of the inner crescents while preserving a generous iris ring.

Result: clean black pupil at center, iris fibers radiating around it. The tiny bit of bright crescent that peeks at the pupil edge reads as the natural pupillary ruff (anatomical inner-iris ring) — biological accent rather than artifact.

This pattern (compositeTOP over: input 0 on top by default) is now logged in TD_BUILD_LOG correction tracker.

## Move 011 — 2026-05-04

**Expose pupil radius as parameter on ctrl_master baseCOMP.**

First param of the master control dashboard that will host all tunable iris controls (audio bindings come later).

- `/project1/ctrl_master` (baseCOMP) created at nodeX=-800, nodeY=400. Custom page `Pupil` with custom param `Puprad` (Float, default 175, normRange 0-350, clamped min 0, max 1000).
- `/project1/circle_pupil.radiusx` mode CONSTANT 175 → EXPRESSION `op('/project1/ctrl_master').par.Puprad`
- `/project1/circle_pupil.radiusy` mode CONSTANT 175 → EXPRESSION (same)

Pattern matches attractor_chamber / magnet_chamber `ctrl_master` convention. As more controls are exposed (camera dive, twist strength, color, etc.) they'll be added as additional custom params/pages on this same baseCOMP.

## Move 012 — 2026-05-04

**Iris-over-video composite (v1) + expose position controls.**

New parallel branch that composites our iris over a real-eye video for an "alien-eye" look. Video: `wobar_macro_of_female_eye_centered_in_frame...mp4` (464×832, 121 frames, blue iris with multiple slow blinks).

**Composite chain:**
- `/project1/xform_iris_replace` (transformTOP) — scales our 720×1280 null_out to 0.42, positions over video iris, output resolution 464×832 to match video.
- `/project1/mask_iris_video` (circleTOP) — soft circle (radius 102, softness 8) at video iris position, defines iris-shaped area.
- `/project1/comp_iris_masked` (compositeTOP, multiply) — applies mask to scaled iris.
- `/project1/comp_video_replace` (compositeTOP, over with swaporder=True) — masked iris over video.
- `/project1/null_video_replace_out` — final 464×832 output.

**ctrl_master Replace page added:**
- `Irisx` (Iris X position offset, default 18, slider ±200)
- `Irisy` (Iris Y position offset, default -60, slider ±200)

Both params bound to `xform_iris_replace.tx/ty` AND `mask_iris_video.centerx/centery` so the iris and its mask move together when tuned.

v1 status: iris replacement is working — purple WOBAR iris sits dramatically over the natural blue iris, dilated pupil reads as alien. v1 doesn't yet handle blinks (our iris currently shows over the eyelid during closure). Next iteration will add a lash/lid extraction layer to make our iris disappear under the closing eyelid as Nick requested.

## Move 013 — 2026-05-04

**Expose Irisscale on ctrl_master.**

- `Irisscale` (Float, default 0.42, slider range 0.1-1.0, hard min 0.01) added to `ctrl_master.Replace` page.
- `xform_iris_replace.sx` and `.sy` bound to `Irisscale` directly.
- `mask_iris_video.radiusx` and `.radiusy` bound to `Irisscale * 243` (the ratio that preserves alignment between iris content and mask boundary at the calibration point).

Now position (Irisx, Irisy) and size (Irisscale) are all tunable live from ctrl_master.
