# CHANGE LOG — eyes_cut_deeper_pop_mirror

Third visualizer for the Subtronics "Eyes Cut Deeper" remix (cusp 4→5 register, "heavy and beautiful"). Counter-programs to the existing iris_2 (intimate close-up, drawn pupil overlay) and eyes_cut_deeper grid (4-cell macro-eye fragmentation). This third take uses POPX particles to form an eye-suggestive bilateral mirror — "two intelligences meeting / Three Versions meeting at the mirror" framing from the brand visual identity refresh.

Built directly at `/project1` (no wrapping baseCOMP, per attractor_chamber v002 pattern). Reuses canonical SA + sphere instancing from `attractor_chamber/move_001.json` and HDR cinematic post chain from `iris_2`. New work in this build is the bilateral side-by-side mirror layout, the cusp 4→5 light palette weighting, and the HDR post (vs attractor_chamber's grain-add atmospheric).

---

## Move 001 — SA pipeline + sphere instancing + audio binding (canonical lift)

2026-05-07.

Built the foundation: POPX SA chain (pointgen1 → sa1 Aizawa advect → null_pop_out) with audio-bound Timescale, sphere instancing via geo_attractor with manual count + P(N) attribute reads, basic camera + temporary single light + render TOP for verification.

**Core pipeline:**
```
pointgen1 (3000 pts) → sa1 (Aizawa, advect, Timescale audio-bound)
  → null_pop_out → geo_attractor (instancing on, manual 3000)
    └─ sphere_template (sphereSOP, radius 0.02)
  → render_attractor (720×720) ← cam_attractor (tz=5) + light_test (temp)
```

**Audio binding (single — proven attractor_chamber pattern):**
```
sa1.Timescale = ctrl_master.par.Audiofloor + ctrl_master.par.Audioceil × pow(max(0.0, ctrl_master.par.Energy), ctrl_master.par.Audioexp)
```
Defaults: floor=0.1, ceil=2.0, exp=1.5. Energy 0→1 maps Timescale 0.1→2.1.

**Source:** POPX SA module copied from `third_party/POPX/POPX_Examples_1_3_0/examples/strange attractors.tox`. Cleared orphan `parent.Example`/`parent.POPX` expressions on sa1.Startpulse and sa1/feedback1.startpulse.

**Gotchas hit + handled:**
- `geometryCOMP` auto-torus killed render — destroyed before placing sphere_template
- `sphereSOP.par.rad` doesn't exist; correct is `radx/rady/radz`
- Instance count: `oplength` mode reads 1 from POPX null — must use `instancecountmode='manual'` + `numinstances=3000` (or expression on `numPoints()`)
- `par.instancing` master toggle was OFF; required True to actually multiply
- Instance attribute syntax: `'P(0)'`/`'P(1)'`/`'P(2)'` (parens), NOT brackets
- `renderTOP.par.geometry` is a glob PATTERN — `'geo_attractor'` works, `/project1/geo_attractor` silently fails (per existing gotcha)

**Verification:**
- 3000 spheres render in expected 3D distribution
- Energy slider drives Timescale through expected range
- 0 hard errors; remaining warnings cosmetic (POPX-internal sync to old user paths)

**Next:** move_002 — replace `light_test` with 4 palette-cycling lights (cusp 4→5 weighting: deep purple, wine magenta, bronze patina, oxidized teal) + add centroid tracker for cam lookat (Aizawa's mass-center wanders).

---

## Move 002 — 4 palette-cycling lights + centroid tracker

2026-05-07.

Replaced `light_test` with 4 lightCOMPs cycling between paired colors over prime-period intervals (47/67/53/60s). Cusp 4→5 palette weighting:

| Light | Position | Color A → Color B | Period |
|---|---|---|---|
| `light_wine` | (3, 1, 2) | wine magenta `#5A0F41` ↔ muted magenta `#B34E8F` | 47s |
| `light_petrol` | (-3, 1, 2) | petrol `#2C4554` ↔ oxidized teal `#1E505A` | 67s |
| `light_bronze` | (3, -1, -2) | bronze patina `#5A5240` ↔ oxidized copper `#6F4E3A` | 53s |
| `light_purple` | (-3, -1, -2) | deep purple dark `#190028` ↔ deep purple highlight `#5A0F78` | 60s |

Color cycle expression on each `cr/cg/cb` par:
```
a + (b-a) * (0.5 + 0.5 * sin(absTime.seconds * 2π / period))
```

`render_attractor.par.lights = 'light_*'` (glob pattern matches all 4).

**Centroid tracker** added (`centroid_tracker` executeDAT) — `onFrameStart` callback reads `null_pop_out.points('P')`, computes mean, EMA-lerps `lookat_target.tx/ty/tz` (alpha=0.04, ~0.4s time constant at 60fps). Aizawa's mass-center wanders; fixed lookat causes drift. Camera `par.lookat = lookat_target` makes the camera follow the cloud's actual center, even as the chaotic distribution shifts.

**Gotcha hit:** `lightCOMP` color params are `cr/cg/cb` not `lightcolorr/g/b`. `baseCOMP` has no `tx/ty/tz`; used `geometryCOMP` (with render/display=False) as the empty-transform anchor for the lookat target.

**Cusp 4→5 register check:** all 4 light pairs sit in the heavy palette range (no light/bone/amber/cream colors that would pull toward Act 1 or 5 register). Cycling between two-step ranges (within the same color family) keeps the visual mood consistent — no jarring color shifts, just slow temperature breathing.

**Verification:**
- Render shows particles lit in dusty wine/petrol/bronze/purple tones
- `lookat_target` updates from (0,0,0) toward computed centroid as SA evolves
- 0 hard errors

**Next:** move_003 — bilateral mirror layout. Render at 720×720 square → flipTOP horizontal → side-by-side composite into 720×1280 portrait canvas with invisible centerline seam.

---

## Move 003 — Bilateral mirror layout

2026-05-07.

Built the side-by-side mirror composition. Single 720×720 render flipped horizontally, both halves placed at left/right of 720×1280 portrait canvas.

```
render_attractor (720×720)
  ├─→ xform_left (sx=sy=0.5, tx=-0.25 frac) → 720×1280 with cloud at left half
  └─→ flip_horizontal → xform_right (sx=sy=0.5, tx=+0.25 frac) → 720×1280 with cloud at right half
      ↓                                                            ↓
      └────────────────→ comp_mirror (add) ←─────────────────────┘
                            ↓
                     null_mirror_out (720×1280)
```

Each cloud is 360×360 in the 720×1280 canvas (50% scale of square render). 280px black bars top + bottom give cinematic letterbox. Invisible seam at canvas centerline because `extend='zero'` produces black outside the source area for both transforms.

`compositeTOP operand='add'` — non-overlapping halves, so add and over behave identically.

**Open question:** clouds are small relative to canvas. Will revisit scale after HDR post (move_004) — the bloom + crushed blacks may make 360×360 feel right, OR we may bump scale up.

**Next:** move_004 — HDR cinematic post chain (hsv_mute + level_post + bloom_post), lifted from iris_2 final params.

---

## Move 004 — HDR cinematic post chain

2026-05-07.

Replaced attractor_chamber's grain-add atmospheric with iris_2's proven HDR chain. The "burning embers" luminous look — crushed blacks + bloom halo — locks the cusp 4→5 register: heavy via dark crush, beautiful via bloom on cycling-color particles.

```
comp_mirror → hsv_mute (sat 0.78) → level_post (crushed blacks/S-curve) → bloom_post (HDR inputplusbloom) → null_mirror_out
```

Final params (lifted directly from iris_2 final tuning — proven for cusp 4→5):

| Op | Param | Value |
|---|---|---|
| `hsv_mute` | saturationmult | 0.78 |
| `level_post` | inlow | 0.06 (crushed blacks) |
| `level_post` | inhigh | 0.95 (rolled highlights) |
| `level_post` | contrast | 1.18 |
| `level_post` | gamma1 | 0.92 (cinematic S-curve) |
| `bloom_post` | bloomthreshold | 0.4 |
| `bloom_post` | bloomintensity | 1.1 |
| `bloom_post` | maxbloomradius | 0.22 |
| `bloom_post` | bloomscurve | 0.75 |
| `bloom_post` | pregamma | 1.1 |
| `bloom_post` | output | `inputplusbloom` |

Also fixed letterbox: set `xform_left.par.bgcolora = xform_right.par.bgcolora = 1.0` so the 280px black bars top+bottom render as solid opaque black instead of TD's transparent-checkerboard indicator.

**Visual check at Energy=0.85:** Aizawa starts sculpting the cloud into its characteristic torus. The bilateral mirror creates a butterfly / two-halves-of-iris reading with internal density variation. Particles glow with bloom halos in the dusty wine/petrol/bronze/purple palette.

**Brand register check (cusp 4→5 "heavy and beautiful"):**
- HEAVY: crushed blacks dominate, deep purple foundation reads as gravity ✓
- BEAUTIFUL: HDR bloom on cycling-color particles ✓
- HEART OPENING at drops: Aizawa torus sculpts as Timescale rises with Energy ✓
- HARD-WON SOFTNESS: 5-second energy release will give residual-motion decay (when audio is wired)

**Next:** move_005 — record_out (moviefileoutTOP) + drop in base_audio_v001.tox + bind Energy to audio_master/smooth_out['energy']. Final tuning + close-out.

---

## Move 005 — Audio wiring + record_out (close-out)

2026-05-07.

Loaded canonical `base_audio_0_1.tox` as `audio_master` (8 channels: sub_bass, bass, mid, high, energy, sub_pressure, growl, transient). Bound `ctrl_master.par.Energy.expr` to `op('audio_master/smooth_out')['energy']` — the SA Timescale audio expression now reads live audio analysis.

Created `record_out` (moviefileoutTOP) at the end of the chain:
- input via `input0top = '/project1/null_mirror_out'` (moviefileoutTOP uses input0top param, not connector wire)
- output 720×1280 portrait, h264, yuv420, mp4 container, high quality
- audiochop = `'/project1/audio_master/audio_in'` (raw 44100Hz, NOT smooth_out — entry 32 in correction tracker, promoted)
- file: `touchdesigner/networks/eyes_cut_deeper_pop_mirror/exports/eyes_cut_deeper_pop_mirror_v001.mp4`

**Build complete.** Network ready to render.

**Render workflow:**
1. Set `audio_master/audio_in.par.file` to the song mp3/wav
2. Pulse `audio_in.par.cuepulse` to seek to start
3. Toggle `record_out.par.record` ON
4. Let song play through (~275s for Eyes Cut Deeper)
5. Toggle `record_out.par.record` OFF
6. mp4 lands at the configured file path

**Final ctrl_master state (Audio page):**
- `Energy` (live audio-bound expression)
- `Audiofloor` = 0.1
- `Audioceil` = 2.0
- `Audioexp` = 1.5

**Final network inventory (~16 ops at /project1):**
- ctrl_master, audio_master (loaded)
- pointgen1 → sa1 → null_pop_out (POPX SA chain)
- geo_attractor (with sphere_template child)
- 4 lights (light_wine/petrol/bronze/purple) — palette cycling
- cam_attractor + lookat_target + centroid_tracker
- render_attractor (720×720 single-eye render)
- xform_left, flip_horizontal, xform_right, comp_mirror (bilateral mirror)
- hsv_mute, level_post, bloom_post (HDR cinematic post)
- null_mirror_out → record_out

**Brand check (cusp 4→5 "heavy and beautiful"):**
- HEAVY: crushed blacks, deep purple foundation, bilateral symmetry as gravity ✓
- BEAUTIFUL: HDR bloom on cycling-color particles, dusty wine/petrol/bronze/purple palette ✓
- HEART OPENING at drops: SA Timescale surges with energy, particles advect into Aizawa torus; bilateral mirror amplifies the "two halves meeting" gesture ✓
- HARD-WON SOFTNESS: 5-second energy release in audio analysis chain → slow wind-down decay after drops ✓

Counter-programs cleanly to the existing iris_2 (intimate close-up, photoreal) and eyes_cut_deeper grid (4-cell macro fragmentation) — third visual identity for the same song's release window.

---

## Move 006 — Fix: SA integration not running (parent.POPX expression)

2026-05-07.

**Problem:** Cloud particles weren't moving despite `sa1.par.Play=True` and `Timescale=1.0`. Sampling positions over 30 frames showed zero delta. SA was loaded and configured but not actually advecting.

**Root cause:** During move_001 cleanup, I cleared `sa1/feedback1.par.startpulse.expr` because it referenced `parent.POPX.par.Startpulse` and the example container was being deleted. Looked like an orphan reference — but it was actually CORRECT. `sa1.par.parentshortcut = 'POPX'` makes `parent.POPX` resolve to sa1 itself from inside the COMP. The expression was forwarding `sa1.Startpulse` to `feedback1.startpulse` (the actual integrator), which is what kicks off continuous integration after Initialize.

**Fix:**
```python
sa1/feedback1.par.startpulse.expr = "parent.POPX.par.Startpulse"
sa1.par.Initializepulse.pulse()
sa1.par.Startpulse.pulse()
```

Also added a Pulse page on `ctrl_master`:
- `Pulsebase` (0.025) — silence sphere radius
- `Pulsegain` (0.05) — peak addition (max radius 0.075)
- `Pulsecurve` (1.5) — exponent

`sphere_template.par.radx/y/z.expr = Pulsebase + Pulsegain × pow(max(0, Energy), Pulsecurve)`. Particles grow with energy.

Bumped audio defaults so cloud is always visibly evolving (not just at peaks):
- `Audiofloor` 0.1 → 1.0 (active drift at silence)
- `Audioceil` 2.0 → 1.5 (peak Timescale 2.5)

**New gotcha for TD_BUILD_LOG correction tracker:**
> POPX modules use `parent.<shortcut>` references internally (e.g. `parent.POPX.par.Startpulse` from `feedback1` inside `sa1`). The shortcut comes from the parent COMP's `par.parentshortcut` setting (POPX modules ship with `parentshortcut='POPX'`). Expressions like `parent.POPX.par.X` look orphan-style but are CORRECT — they resolve via parentshortcut. **Do NOT clear them when copying POPX modules to a new project — that breaks the internal pulse/start chain.** If they error on first eval, fix by copying the module to a target where parent shortcut RESOLVES (often: leave the module where it is, or destroy + recreate the chain that references the original parent).

**State:**
- SA is integrating continuously
- Energy slider drives Timescale (1.0 → 2.5) AND sphere radius (0.025 → 0.075)
- Audio still unwired — manual Energy slider for testing
- Network ready for audio re-bind when Nick is ready
