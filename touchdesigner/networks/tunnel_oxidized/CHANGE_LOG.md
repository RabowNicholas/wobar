# CHANGE LOG — tunnel_oxidized

The first build of the visual reset (`working/WOBAR_VISUAL_RESET.md` §4). Proof of the
constant: **a tunnel inward** — full-frame, hypnotic, slow, desaturated, material,
grainy, imperfect-mirror. Material variable for this piece = oxidized cool metal
(Act 2 / DESCENSION affinity).

---

## move_001 — 2026-07-14 — initial build (no audio wired)

**Built:** 2D polar material tunnel in a glslTOP (IQ `1/r` map), portrait 720×1280,
per spec §4. `/project1` was empty at move start — built from scratch, no wrapping
baseCOMP (matches down_bad_3stack / iris_2 / eyes_cut_deeper convention).

Chain:
```
text_tunnel (textDAT = the .frag)
   ↓ pixeldat
glsl_tunnel (glslTOP) — outputresolution=custom 720×1280, format=rgba16float
   ↓
hsv_desat (hsvadjustTOP) — saturationmult 0.6
   ↓
comp_grain (compositeTOP, screen) ← res_grain (resolutionTOP 720×1280) ← noise_grain (noiseTOP randomgpu, 360×640, mono, aspectcorrect, amp 0.08, seed=absTime.frame)
   ↓
comp_vignette (compositeTOP, multiply) ← circle_vignette (circleTOP, radius 1.05 fractionaspect, softness 0.45, bg floor 0.35)
   ↓
null_out (nullTOP)
```

`ctrl_scene` (baseCOMP, custom page "Scene"): `Scrollspeed` 0.06 · `Mirroramt` 0.88
· `Foldcount` 6.0 · `Brightness` 1.3.

**Deviations from spec §4 — and why:**

- **`level_desat (levelTOP, satmult ~0.6)` → `hsv_desat (hsvadjustTOP, saturationmult 0.6)`.**
  `levelTOP` has no saturation parameter of any kind; `satmult` is an `hsvadjustTOP`
  par (`saturationmult`). Spec named the wrong operator. Verified against the live
  levelTOP par dump before substituting.
- **Uniforms bind on the glslTOP VECTORS page, not the color page.** `WOBAR_TWOZERO_GUIDE.md`
  claims "float uniforms live on the color page" (`color0name`/`color0rgbr`) — that is
  wrong. The color page carries vec4 *color* uniforms; scalar floats bind via
  `vec0name` / `vec0valuex`. Guide needs correcting.
- **`lookup_ramp` + `ramp_metal` skipped.** Spec marks it "optional palette lock"; the
  shader already renders inside the palette as vec3 constants, and AGENT_RULES §Color
  says skip the Lookup when the source is already in-palette.
- **`audio_ref` not wired** (spec: "optional for first look"). No `base_audio_react`
  exists in this project — it lives in the down_bad network, and the rule is don't
  duplicate the audio pipeline. Uniforms guard to 0; the time-based brightness breath
  keeps the piece alive without it.

**Shader fixes (synced back to `touchdesigner/glsl/tunnel_oxidized.frag`):**

- **The seven `uniform float` declarations were missing entirely.** The file used
  `uTime`/`uSubBass`/etc. undeclared — a hard GLSL compile error. Added.
- **`uTime` = `absTime.seconds`, NOT `me.time.seconds`.** Tried `me.time.seconds` first
  (reasoning from the promoted "absTime drifts" rule) — wrong here: the timeline loops,
  so `me.time.seconds` sawtooths (read 0.35s at frame 22 while the tunnel had run 4.4s)
  and would hard-jump the scroll back on every loop. An infinite inward scroll must
  never rewind — same class as a noise/grain seed, which is exactly the carve-out the
  rule names. Spec was right.
- **Audio guard needed an existence check.** Spec's
  `op('audio_ref')['sub_bass'] if op('audio_ref').numChans>0 else 0` raises
  AttributeError on None when `audio_ref` doesn't exist — which is precisely the
  no-audio case the guard is for. Corrected to
  `if (op('audio_ref') and op('audio_ref').numChans>0)`.

**Corrections made mid-build:**

- First vignette pass (radius 0.78, softness 0.85, black bg) read as a **spotlight, not
  a vignette** — multiply crushed the frame to near-black. Softness 0.85 collapses the
  circle to a center blob. Fixed: radius 1.05, softness 0.45, and a **0.35 grey bg floor**
  so multiply darkens the edge rather than killing it. The shader already carries its own
  fog vignette, so the node vignette only needs to be a gentle top-up.

**Verified:** 0 errors / 0 warnings across `/project1`. `null_out` = 720×1280.
Perf: `glsl_tunnel` 0.76 ms CPU, 0.0 ms GPU, cook budget 0.1% — the low fps badge
during the session was TD idling unfocused, not a cost problem. Spec's "cheapest on M1"
claim holds.

**Open / next:**
- Not yet saved to `.tox` (no checkpoint — `td-save` not run).
- Material is legible but reads soft/cloudy rather than hard oxidized metal — the fbm is
  gentle. Taste call for Nick.
- Audio unwired at this move — closed in move_002.

---

## move_002 — 2026-07-14 — audio wired (song: `kekkai-2--6-17.mp3`, 4:34, 16458 frames @ 60fps)

Track chosen; Nick set the timeline to 16458 and recorded the full song through
`null_audio` → `rec_audio` (8 chans × 16458 samples). Modulation sources picked from the
recording per the **record-first-then-map** rule, not by feel.

### What the recording said

Song structure (energy, 8s blocks): intro 0:00–0:24 → build → **drop 1 (0:56–2:00)** →
**breakdown (2:00–2:24, energy 0.084)** → rebuild → **drop 2 (2:56–3:52)** → outro decay.

Percentiles (raw, as recorded off `null_audio`):

| chan | p10 | p50 | p90 | p95 | max | crest p99/p90 |
|---|---|---|---|---|---|---|
| sub_bass | 0.2784 | 0.4988 | 1.0552 | 1.0794 | 1.2088 | **1.05** |
| bass | 0.1922 | 0.4809 | 0.6147 | 0.6520 | 0.9749 | 1.30 |
| mid | 0.0998 | 0.1663 | 0.2107 | 0.2225 | 0.3080 | 1.21 |
| high | 0.0198 | 0.0303 | 0.0401 | 0.0435 | 0.0613 | 1.28 |
| energy | 0.1002 | 0.4974 | 0.7631 | 0.7980 | 1.0024 | 1.15 |
| sub_pressure | 0.0105 | 0.0368 | 0.1402 | 0.1501 | 0.1942 | 1.17 |
| growl | 0.3517 | 0.7826 | 1.0364 | 1.0919 | 1.6335 | 1.24 |
| transient | 0.0345 | 0.1102 | 0.2994 | 0.3599 | 0.6203 | **1.59** |

**Correlation matrix killed half the channels:**
- `sub_pressure` ≈ `sub_bass` → **r = 0.97**. Duplicate.
- `growl` ≈ `bass` → **r = 0.98**. Duplicate.
- `bass`/`mid`/`growl` cluster at r = 0.83–0.98.
- `transient` is the ONLY independent axis (max r = 0.53, vs energy).

**`high` is a trap on this track.** Percentiles look usable (2× range) but across sections
it is flat — breakdown 0.029 vs drop 0.033 = **1.14×**, against energy's **8.2×**. Its
variance is hat texture, not arrangement, and normalizing it needs **gain 49.4** (a 49×
noise amplifier). Unused.

### The three sources + normalization

`preoff = -p10`, `gain = 1/(p_hi - p10)`; `p_hi` = p90 steady, **p95 for spiky transient**:

| chan | preoff | gain | curve | drives |
|---|---|---|---|---|
| `sub_bass` | −0.2784 | 1.287 | **1.2** | bore breathing (weight) |
| `energy` | −0.1002 | 1.508 | 1.5 | brightness breath (section macro) |
| `transient` | −0.0345 | 3.073 | 2.5 | specular flare (attack) |

**`sub_bass` curve dropped 2.5 → 1.2.** Its crest is **1.05** — compressed and sustained,
not spiky. At 2.5 the normalized median lands at 0.043, so the bore would sit shut except
at drops. AGENT_RULES: choose the curve from the recorded percentiles, not by feel; and
Act 2 wants walls breathing WITH the bass, continuously. Curve 2.5 stays on `transient`,
where it IS correct — there we want only peaks.

### Built

`base_audio_react` (baseCOMP, `/project1`) — the rule's canonical shape, per band:
`selectCHOP` (absolute path, cross-COMP CHOP wiring fails silently) → `mathCHOP`
(preoff→gain) → `renameCHOP` (`_n`) → `merge_n` → `null_out`. Publishes `sub_bass_n`,
`energy_n`, `transient_n`. **`base_audio` itself untouched** — `base_audio_react` is a
downstream stage, no duplicate audio pipeline.

Shader: added `uniform float uTransient`; `uEnergy` **is now actually used** (it was
declared, bound, and dead in move_001 — the compiler stripped it, so the binding was a
silent no-op); curves per table above; `glintLo = 0.87 - tr*0.22` (floors at 0.65, so
smoothstep edge order is always safe) and specular gain `0.6 + tr*0.5`; brightness breath
is now `mix(breathLfo, 0.40 + en*1.25, step(0.001, uEnergy))` — the LFO still carries it
when no audio is present, so it never goes dead.

### Verified numerically (not by scrubbing)

`base_audio` has lag CHOPs, so a jumped timeline gives wrong lag state (the paused-state
trap in the debug log). Verified by replaying `rec_audio` through the shader math instead:

| window | sub_n | en_n | tr_n | bore | breath |
|---|---|---|---|---|---|
| intro | 0.076 | 0.081 | 0.141 | 0.917 | 0.459 |
| build | 0.327 | 0.438 | 0.322 | 0.995 | 0.805 |
| **drop 1** | 0.763 | 0.919 | 0.482 | 1.160 | **1.507** |
| **breakdown** | 0.035 | 0.002 | 0.097 | 0.907 | **0.400** |
| **drop 2** | 0.824 | 0.877 | 0.372 | 1.184 | **1.444** |
| outro | 0.085 | 0.042 | 0.133 | 0.920 | 0.417 |

Breath swings **3.8×** breakdown→drop; bore opens 30%; `en_n` bottoms at 0.002 in the
breakdown. Transient gating: **0%** of breakdown frames clear tr_n 0.5, vs 43.5% (drop 1)
and 28.7% (drop 2), saturating at peaks (glintLo → 0.65 = full flare). 0 err / 0 warn.

### New findings for the reference docs

- **`ctrl_norm` normalizes to MAX and shares one `band_max` (0.32) across all four bands.**
  That's the outlier-driven antipattern AGENT_RULES calls out, and it's why sub reaches
  1.2 while high never clears 0.06 — the bands are not individually normalized. Left alone
  (energy/growl remaps depend on it); `base_audio_react` corrects downstream with per-band
  percentiles. Worth revisiting at the source.
- **glslTOP `par.vec` is NOT a uniform count** — reads 0, setting it is a no-op. The
  `vecN*` blocks are addressable directly. TWOZERO_GUIDE updated.
- **"Uniform X is not assigned" can be a STALE warning** — clears on force-cook of the DAT
  + glslTOP. Verify with `.warnings()`, not the badge.
- **Re-hit the exec_server nested-scope failure** (`NameError` on a `def` helper referencing
  an outer var) despite the rule being explicit. The rule is right; I wrote a helper anyway.

---

## move_003 — 2026-07-14 — lateral drift (the constant movement)

Nick: "add constant movement to the tunnel." Offered roll / lateral drift / faster-nonlinear
scroll / fold evolution — **chose lateral drift.**

**Why the tunnel read static in the first place (worth keeping):** the `1/r` map makes the
scroll nearly invisible where the eye goes. Feature velocity is `dr/dt = bore*uScroll/depth^2`,
so at the frame edge (depth ~1) features move ~0.054 NDC/s across a 2-unit frame (~2.7%/s),
while at the vanishing point (depth ~45) it is **~2000x slower** — effectively frozen. That
is inherent to the projection, not a tuning miss. Raising `uScroll` cannot fix the centre;
it just makes the edges rush.

**Built:** `uDrift` uniform + `ctrl_scene.Driftamt` (default 0.15, range 0–0.5). Two
incommensurate sine pairs per axis (periods ~38/62 s in x, ~49/80 s in y) so the path never
retraces inside the 4:34 track. **Applied in NDC BEFORE the aspect squeeze** — added after
it, the same value reads ~1.8x wider horizontally than vertically (uv.x is scaled by
720/1280 = 0.5625). Time-driven, never audio: this is the constant, not a reaction.

Drift path measured over the song at Driftamt 0.15: max radial excursion 0.189 NDC (frame
half-height = 1.0), mean centre speed 0.012 NDC/s, only 1.0% of samples near-stalled — it
wanders continuously and never parks. Note the centre speed is ~4.5x *slower* than the
edge-scroll; the `1/r` magnification near the centre is what makes it read anyway. If it
reads too subtle, `Driftamt` is the dial.

**(Superseded by move_004/005 — the shader was rewritten. Kept for the reasoning.)**

**FOUND — highlight clipping at drops (RESOLVED in move_004 via a soft-knee tonemap).** The first screenshot with
audio live at a drop (`uEnergy` 0.94) shows large flat BONE-capped regions. Chain math:
`uBrightness 1.3 x breathAud (0.40 + en^1.5 * 1.25 -> 1.65 at en=1) = ~2.15x` peak, and
`PEWTER 0.58 * 2.15 = 1.25` — far past BONE (0.78), so `min(col, BONE)` flat-clips. The
no-pure-white law holds, but the material texture is lost at exactly the moments that matter
most, and material walls are the thesis of the reset. **This predates the audio** — the old
LFO breath peaked at 1.66, so `1.3 * 1.66 = 2.16` would clip too; move_001's screenshot just
happened to catch breath ~1.0. Candidate fixes: drop `Brightness` default 1.3 -> ~0.85, or
narrow `breathAud` to `0.40 + en * 0.9`, or soft-knee the cap instead of `min()`.
*(RESOLVED in move_004: soft-knee tonemap.)*

---

## move_004 — 2026-07-14 — v2 RAYMARCH rebuild (v1 rejected)

Nick: *"this doesn't read as professional visualizer. this reads as cheap audio visualizer."*
He was right, and `WOBAR_VISUAL_RESET` **D1 predicted it verbatim** — *"strip the palette and
the 10 shaders are stock Milkdrop/Resolume."* v1 WAS the thing the doc warned about; the
palette was doing all the work. Offered raymarch / 2D-surface / kill-mandala-only /
re-approach → **"raymarch it properly."**

### The three faults in v1 (named so they never recur)
1. **It was a mandala.** Six-fold centred radial symmetry = the Winamp/Milkdrop form.
   `Mirroramt 0.88` does not rescue it — 88% of a mandala is still a mandala, and the seam
   reads as sloppiness, not intent. K4/OBSCURA means *reflection geometry*, not a rosette.
2. **fbm clouds are not a material.** Isotropic soft noise = smoke. §3's first strike-column
   entry is "material walls, tactile surface". Naming the file `oxidized` didn't make it so.
3. **No light.** Colour ramped straight off a scalar noise IS the cheap-visualizer technique.
   Metal reads via specular response across a normal field. v1 faked it with a `smoothstep`
   threshold called `glint`, which is why it looked like backlit fog.

Root cause: **the method was the ceiling.** Spec §4 claimed 2D polar "beat raymarch on every
WOBAR requirement" — wrong on the one that mattered. A 2D polar map has no normals, no
parallax, no lighting; it can approximate a shape but never a surface. It bought cheapness
(0.76 ms, 0.1% budget) and paid in exactly the currency the reset is about.

### THE BIG ONE — `audio_out` had `cookalways = True`; project was at fps 0 ALL SESSION
Documented in `WOBAR_TWOZERO_GUIDE` limitations the whole time. Measured **68.6 ms/cook,
1223 ms/s CPU = 7352% of budget**, holding fps at 0. `cookalways=False` → **fps 60 instantly**.
**It does NOT appear in `td_get_operator_info` nonDefaultPars** (Common-page par), so it hid
from every inspection. Every aesthetic judgement before this was made on a crippled machine.
Symptom to recognise: fps 0 + near-idle GPU + one CHOP dominating `td_get_perf` cpu/s.

### Two traps found while rebuilding
- **Killing `kaleido()` was NOT enough.** I put angular plate seams in the wall; on a tube
  they project as straight spokes from the vanishing point — the rosette rebuilt in 3D. **ANY
  angular repeat on a tube does this, by projection.** Now: ring welds only; all angular
  structure is irregular (corrosion/pitting) by construction.
- **A diffuse-weighted pipe renders BLACK.** The wall normal is RADIAL; a camera lamp shines
  AXIALLY; so `dot(n,ld) ~ 0` over the whole wall regardless of lamp brightness. Real pipes
  read via proximity + grazing specular/fresnel. The first raymarch pass was near-black for
  exactly this reason. The lamp also moved off-axis — an on-axis lamp gives concentric
  symmetry, i.e. the rosette creeping back a third time.

**Cost: 0.21 ms GPU/cook, 0.8% of budget.** Marching the SMOOTH SDF (no noise) and applying
material as a BUMP at the hit point — rather than displacing the SDF — is what bought that:
~30 noise evals/pixel instead of ~350M/frame. Also: soft-knee tonemap
`(1 - exp(-col*uBrightness)) * BONE` replaces `min(col, BONE)`, fixing the move_003 flat-clip.

---

## move_005 — 2026-07-14 — v3 ALIVE: lamps + haze + breathing walls

Nick: *"this is better. how can we bring life to the shader now."* Diagnosis: it was a place,
but **nothing happened in it** — homogeneous (every metre identical), light welded to the
camera (nothing sweeps or passes), audio moving only global scalars (reads as "the image got
brighter", not "the place responded"), and a vacuum (no atmosphere). Nick picked all three of
passing lamps / volumetric haze / breathing walls.

**`uTime` → `me.time.seconds` (song time).** Beat-sync is impossible on `absTime` — wall-clock
has no relation to the playhead. The timeline is now 16458 frames = exactly the track, so
`me.time.seconds` IS song position and runs monotonic across a full render; when it wraps, it
wraps because the song restarted. **v1's `absTime` choice was correct AT THE TIME** (the
timeline was then 600 frames, looping every 10 s, which sawtoothed the clock). The right
answer changed when the timeline changed.

**BPM = 140, confirmed by Nick.** Auto-detection FAILED and should not be retried on this
signal: `transient` is already lagged/filtered, so onsets are smeared. Raw autocorrelation's
global max was a bogus **200 BPM** — purely the monotonic decay of a smoothed envelope, not a
beat. Onset-flux autocorrelation gave an ambiguous 133/144, and a phase-aligned comb put every
candidate inside noise (0.0155 vs 0.0153). Beat-sync needs the EXACT value: **1% off drifts a
full beat in 40 s**, which would look worse than no sync. Lesson: ask the producer, or analyse
RAW audio — never a lagged analysis channel.

**Passing lamps.** Recessed in the wall at `mod(z, spacing)`, spiralled by the **golden angle**
so they never line up into a rail (a fixed angle = a straight stripe; a regular angular pattern
= the rosette trap again). **Spacing derives from TIME, not distance** — `gSpacing = gSpeed *
uLampSecs` — so they stay beat-locked at any Scrollspeed. `Lampbeats = 8` (2 bars @140 =
3.43 s → 2.06 units): at 4 beats spacing is ~1.03 units against radius ~1.0, which reads as a
continuous strip rather than discrete lamps passing. Each lamp rakes a moving highlight across
the bump — which is what finally reveals the pitting a static lamp left invisible.

**Volumetric haze.** 20 steps along the primary ray, lamp-lit fog, single-octave `noise()`
(not `fbm` — this loop runs 20x/pixel). **First pass washed the frame to milk**: lamps repeat
every ~2 units down a 45-unit corridor, so `L` is roughly CONSTANT along the whole ray, and at
extinction 0.06 the integral came to ~4.6 — brightest at the FAR end, i.e. the void inverted
into a glowing tube. Fixed with extinction 0.20 + a 0.08 density scale, making haze a
near-field effect: shafts around close lamps, blackness beyond.

**Walls breathe.** Travelling axial swells in the **SDF** (not the bump), `sub * 0.16`, so the
silhouette, parallax and lamp highlights all flex with the bass. §3 asks for "walls breathe
with the bass" — scaling the bore radius uniformly (v1/v2) is a BORE, not breathing. Axial
only: an angular swell term would reintroduce radial symmetry. Cheap (2 sins), Lipschitz ~0.07,
so the 0.7 march factor stays safe.

**Cost: 0.2% of budget, fps 60.** `audio_out` now 0.0015 ms/cook vs 68.6 pre-fix.

**Open:** still reads greyer than "oxidized metal" — environment reflection (sample a gradient
along the reflect vector, weight by fresnel; ~6 lines, near-zero cost) remains the untaken
lever, since metal reads as metal by reflecting a world. Not yet `.tox`-saved.
