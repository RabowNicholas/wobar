# CHANGE LOG — sa_1

## 2026-06-12 (session 2) — move_001 — song-long intensity build

Nick: slowly increase intensity through the song via a scalar on the audio-driven motion. `ctrl_build` (constantCHOP) outputs `build = 1.0 + Buildamount × (clamp(me.time.seconds/Songlength,0,1))²` — quadratic ease-in, starts at exactly the current tuning (1.0), reaches `1+Buildamount` by song end. Multiplied **only into the React terms** of the two audio-driven motion bindings: `sa1.Timescale` (swarm churn) and `ctrl_orbit_speed` (light orbit). Floors (`Audiofloor`/`Orbitbase`) untouched — breakdowns stay quiet all song, only peaks grow; preserves Act 3 held-tension in quiet sections while the encounter tightens toward the end. Ember left out (brightness, not motion). Dials (Audio page): `Buildamount` 0.4, `Songlength` 180 (**PLACEHOLDER** — set to real track length at Barstart alignment). Act 3 caution: kept Buildamount gentle to avoid tipping into Act 4 discharge.

### v001 — 2026-06-12
STATE: crease_sa complete first-pass system — Act 3 ENCOUNTER Rorschach attractor with full cinematic + SACRAMENT treatment. Mirrored Aizawa swarm (3000 pts, instanced metallic pearls, product-distribution sizes + wobble + per-particle size breathing on a render branch outside the solver loop), bar-clocked 4-block color system (WINE/GILT/LUCID/COMMUNION, 8 bars per block at 140 BPM) driving lights + orb albedo + mat rim, audio-integrated light orbits, block-arrival bloom pulse, ember sub-breath, lens stack (deep-focus DOF 3px, back-third fog, highlight shoulder 0.85, camera micro-drift), living void background (macro room-drift + micro eyes-closed grain, palette-locked). Nick: "really liking this." Pending: Barstart alignment to track, full-song watch, Dreamhaze.
MOVES: 18 flushed (move_001–move_018)

## 2026-06-12 — moves 014–018 — lens tuning + living void

**014–017 (tuning by Nick's eye):** DOF dialed from 10px/6 gain to deep-focus 3px/1.0 ("basically everything in focus" — settled there; whisper of blur at extremes kept as anti-CG seasoning). Fog: amount 0.35 → 0.2, then restructured with `Fogstart` 0.6 dial (`fog_level.inhigh = 1−Fogstart`; levelTOP Pre-invert runs before Range remap) so only the back 40% of the depth window fogs — front of mass clean.

**018 (living void):** solid black bg replaced. Nick's spec (asked directly): the trip void = **eyes-closed darkness + enclosed room presence**, "felt but quiet." Two noise scales — macro simplex (period 1.8, ~90s+ drift = the room's shape shifting) + micro grain (period 0.07 = closed-eye noise) — added, then lookup-forced through a SACRAMENT dark ramp (black → off-black-purple → charcoal mauve, 14% ceiling) so the void physically cannot leave palette. Post-grade bg lift 3–7% violet. `Voidlevel` dial (Composition). `bg_black` orphaned — cleanup at save.

## 2026-06-12 — move_013 — cinematic lens stack (DOF + fog + shoulder + drift)

Nick: "push the cinematic feel, almost realistic." Four moves, one stack — the image now passes through a lens:

1. **DOF:** `depth_pass` (depthTOP, reranged cameraspace 3.3–5.0, clamped) → `|depth − Doffocus| × Dofrange` mask → `dof_blur` (lumablurTOP, up to `Dofwidth` px). Focal plane at the front third of the mass; out-of-focus embers spread into bokeh discs. **Calibration lesson:** mass sits at cameraspace ~3.5–4.7, NOT the ~1.9 the Camradius dial implies (geo transforms shift it) — and unclamped void depth sampled 2924. Always grid-sample the depth pass to calibrate; never derive the rerange window from camera dials.
2. **Depth fog:** inverted clamped depth multiplied in — far side of the swarm sinks toward trip-dark. `Fogamount` 0.35.
3. **Highlight shoulder:** `level_grade.outhigh` → `Cineshoulder` 0.85 — speculars roll off instead of clipping (house "no pure whites" grade spec, was missing).
4. **Camera micro-drift:** 2-term incommensurate sin sums appended to cam tx/ty/tz (`Camdrift` 0.015) — pseudo-handheld presence, never repeats perceptibly.

New dials: Camera page `Camdrift`/`Doffocus`/`Dofrange`/`Dofwidth`/`Fogamount`, Post page `Cineshoulder`. Chain head now: `render → dof_blur → fog_comp → bloom_post → …`

## 2026-06-12 — move_012 — block-arrival pulse + ember sub-breath

1. **Block-arrival pulse:** `ctrl_block_pulse` (constantCHOP) computes `Blockpulse × exp(−(bars % Blockbars) × Blockdecay)` off the shared bar clock; `bloom_post.bloomintensity` multiplies in `(1 + pulse)`. Each 8-bar block announces itself with a bloom swell on bar 1 that dies by the half-bar — the structure becomes somatic. Dials (Color page): `Blockpulse` 0.6, `Blockdecay` 6.
2. **Ember breath:** `rimlight0strength` (was constant 1.4) → `Emberbase + Emberreact × pow(clamp(sub,0,2), Embercurve)` — votive glow swells with the sub-band while the form stays still. Curve 1.1 per the promoted gentle-register rule. Dials (Material page): `Emberbase` 1.4 / `Emberreact` 1.0 / `Embercurve` 1.1. Closes the standing brand-check miss ("the body is still, but everything inside is moving").

Verified at paused timeline (bar 0): pulse exactly 0.6, bloom 1.584, rim 1.535 with live sub — math consistent; decay confirmed by expression form, needs play to observe.

## 2026-06-12 — move_011 — audio-reactive light orbits

Lights already orbited at fixed wall-clock periods (47/67/60s). Now orbit speed rides energy: `ctrl_orbit_speed` (constantCHOP, `Orbitbase + Orbitreact × pow(clamp(energy,0,2), Orbitcurve)`) → `speed_orbit` (speedCHOP integrator) → `null_orbit` → all three orbiting lights read the shared phase. Integration per the promoted speedCHOP rule — speed changes never jump position (magnetize precedent). Period ratios (×0.7015, ×0.7833) and π offsets preserved, so baseline choreography is identical; drops accelerate the swing of light across the mass, breaks let it settle to the 47s drift. New Lighting dials: `Orbitbase` 0.0213 / `Orbitreact` 0.05 / `Orbitcurve` 1.5. `ty` bobs left decoupled on wall-clock; rim light static by design.

## 2026-06-12 — move_010 — orb color joins the block cycle

Nick: orbs weren't following the new light cycling. Root cause: **`Metallic=1.0`** — full metal has no diffuse, all visible color is reflection TINTED by the albedo, and the albedo was the static wine `Basecolor` dials. Every block color was being filtered through wine.

Fix: `mat.basecolor` exprs → `cycle('warm', me.time.seconds, c) × Orbalbedo` (new Material dial, 0.16 keeps current darkness); `mat.rimlight0color` (was static gilt) → `cycle('warm')` full-strength. Orb body + rim glow now walk the same 8-bar blocks as the lights — in LUCID the orbs themselves go cold silver. Absolute paths in MAT exprs (child-COMP rule). `Basecolorr/g/b` dials dormant → cleanup at save.

## 2026-06-12 — move_008 + move_009 — vignette killed; color cycling moved into the lights

**move_008:** vignette deleted entirely (4 ops + `Vignetteamount` dial), `comp_grain` rewired to `comp_ca2`. Nick's call.

**move_009:** Nick: "color should be the lights" — the bar-clock block scheme belongs in the lighting, not the post lookup. `palette_lights` rewritten: each channel is now a **12-stop concatenated block list** (WINE/GILT/LUCID/COMMUNION × 3 stops), `cycle()` signature changed to `(channel, t, comp)` with the clock inside (reads `Bpm`/`Blockbars`/`Barstart` from ctrl_master) — walks 3 stops per 8-bar block, lerping continuously through block boundaries. All 12 light color exprs updated to pass `me.time.seconds` (timeline-locked = export-true; was absTime + per-light prime periods). Channel roles: warm = block primary, cool = block undertone, earth = pewter reality-edge thread (near-constant through all blocks), pale = bone halo. Verified numerically: exact plum at bar 0, exact oxidized copper at bar 8.

Lookup chain (move_007) left in place but **dormant at `Colormix=0`** — revive as a second psychedelic layer or delete at save. `Paletteperiodscale` dial now dormant (no consumers) — clean up at td-save.

## 2026-06-12 — move_007 — bar-clock SACRAMENT color scroll (psychedelic layer)

Nick: hypnotic but not psychedelic; wants color cycling mapped to song structure — one full cycle per 8 bars, then shift to the next. 140 BPM confirmed.

**Mega-ramp sliding window.** One 17-stop ramp holds 4 palette blocks end-to-end (WINE → GILT → LUCID → COMMUNION, each starting at off-black, theme arc body→ritual→waking→integration). A transformTOP window (3/16 of the ramp wide, `extend='repeat'`) slides continuously — 0.25 ramp-units per `Blockbars` bars — so each 8-bar block scrolls through one palette and the slide itself IS the shift to the next. No switching logic, no cuts. 32-bar meta-cycle.

Chain: `palette_keys` → `ramp_palette` (1024×1 rgba16float) → `xform_palette` (window) → `lookup_color` (luminance) ← `hsv_grade`; → `level_mix` (Colormix opacity) → `comp_mix` (over, swaporder) → CA stage. Clock: `me.time.seconds` (timeline-locked, export-true) × Bpm/240 → bars.

New Color page: `Bpm` 140 / `Barstart` 0 / `Blockbars` 8 / `Colormix` 0.65.

**Verified:** window mapping confirmed numerically via `TOP.sample()` before wiring (tx semantics: output-fraction units, S = −tx × 0.1875). Floor-lift during block transitions (shadows briefly carry the outgoing block's bright stops) is intended — color flowing through the form. `Barstart` aligns bar 0 to the track's downbeat at render time.

## 2026-06-12 — move_005 — render branch + wobble + size breathing (variation options B+C)

The architecture move: `sa1.Pointsupdatepop` reads `null_pop_out` (solver advects from its own output), so any in-loop variation would accumulate into trajectories and smear the attractor. Built a **visual-only render branch** outside the loop: `null_pop_out → noise_wobble → noise_breath → null_render_out`, `geo_attractor.instanceop` repointed to `null_render_out`. Solver and centroid tracker stay on the clean null.

- `noise_wobble` (noisePOP perlin4d, period 0.15): adds animated micro-displacement to P — each sphere trembles around its true path. `t4d` carries time (field evolves in place, no directional scroll). Dials: `Wobbleamp` 0.008, `Wobblespeed` 1.0.
- `noise_breath` (noisePOP perlin4d, period 0.2): multiplies ScaleRand by 1.0 ± `Breathvar` — individual spheres swell/shrink independently and slowly. Dials: `Breathvar` 0.15, `Breathvarspeed` 0.5.
- 4 new dials on existing Form page.

Verified: wobble delta ≈ amp on live points; render-branch ScaleRand 0.29–2.07; solver ref unchanged; 60fps. Act 3 note: this is the geometry-level "the body is still, but everything inside is moving."

## 2026-06-12 — move_004 — size distribution reshape (variation option A)

Nick: instances read uniform in shape and path. Option A (cheapest test): second randomPOP `random_scale2` chained after `random_scale`, `combineop='mult'` into `ScaleRand` → product of two uniforms = organic skew (many small, rare large "stones"). Verified: min 0.31 / max 1.95 / mean 0.96; 25% under 0.7, 9% over 1.5. Inside the SA feedback loop is safe here because both randomPOPs are deterministic per point and re-set/mult each cook — no accumulation.

**New gotcha (logged):** randomPOP `combineattrscope` defaults to **'P'** — with `combineop='mult'` the random value multiplied against POSITION (signed!), driving ScaleRand to −1.77..2.07. Always set `combineattrscope` to the target attr when using mult/add.

Held for next: branch-after-null_pop_out architecture for visual-only variation (wobble noisePOP, per-particle size breathing), velocity-coupled size via unused `LenVel`.

## 2026-06-12 — move_003 — halo backlight + cosmetic polish batch

1. **Halo backlight (light_back revival).** The orphaned bone-pale backlight rejoined `render.par.lights`, dimmer cut 5.5×→1.5× (rims, doesn't flood), `soft2d` shadows + `shadowcasters='geo_attractor'`. Pale glow behind the mass = corrupted-halo register — religious vocabulary in pure light. Now 2 shadow-mapped lights; fps holds 60.
2. **Micro-CA (nostalgic/analog register).** 7-op manual chain (TD has no native CA): hsv_grade → 3× channel-isolate levelTOPs → ±tx transformTOPs on R/B → 2× add composites. `Caoffset` dial in PIXELS (expr ÷720). Default shipped at **1.0px** — 2px doubled every point-source ember and read anaglyph; on glint-dense content the brand's 1–3px range should sit at the bottom.
3. **Radial vignette.** `vignette_keys` tableDAT → rampTOP (radial, `fitaspect='fitvert'` for true circle on portrait) → levelTOP `outlow = 1 - Vignetteamount` → multiply composite. Candlelit-room falloff. `Vignetteamount` 0.35.
4. **Grain blend add → screen** per the canonical post template.

Final post chain: `render → bloom_post → mirror → comp_bg → level_grade → hsv_grade → CA → vignette → grain(screen) → null_out`. New Post dials: `Caoffset` 1.0, `Vignetteamount` 0.35.

## 2026-06-12 — move_002 — SACRAMENT color register

Song theme (Nick): psychedelic trip processing religious trauma — "am I dreaming?" → recognition that this is reality, the past must be faced. Color direction chosen to carry that without figuration: **communion wine + tarnished gilt**.

- `palette_lights` rewritten from the all-red register: **warm** → votive gilt (brass ochre `#B89958`, oxidized copper `#6F4E3A`, burnt amber, dried tobacco — warmth that disturbs per Act 3 affinity rule), **cool** → sacramental wine (wine magenta `#5A0F41`, plum, muted magenta, deep purple mid), **earth** (rim light) → pewter/tarnished-silver/ash — the cold "this is reality" lucidity edge, **pale** → bone/ash.
- Mat base albedo wine-biased: (0.039, 0.009, 0.011) → (0.048, 0.010, 0.032).
- Mat rimlight: magenta-pink (0.55, 0.18, 0.42) → tarnished gilt (0.55, 0.32, 0.16).

Concept note: gilt votives burning inside a body of communion wine, witnessed in trip-dark, mirrored back. Held idea (not built): `Dreamhaze` choreography dial — soft bloom/sat early (dream), grade hardens at the realization moment (awake) via keyframe-table pattern.

## 2026-06-12 — move_001 — post chain realism upgrade (crease_sa, Act 3 ENCOUNTER)

Brand-check session flagged the post chain as the realism gap. Three approved moves landed as one move:

1. **Threshold bloom.** Manual bloom chain (`blur_bloom` 32px full-frame blur → `level_bloom` → `comp_bloom` screen) bloomed the entire frame — uniform milky haze, lifted blacks, classic CG giveaway. Replaced with native `bloom_post` (bloomTOP, `output='inputplusbloom'`, threshold-driven so only ember cores and speculars glow). Threshold on new `Bloomthresh` dial; intensity rides existing `Bloomamount` (×0.5 → ≈1.0 at current setting, inside the 0.7–1.1 canonical range).
2. **Cinematic tone stage.** `comp_bg → level_grade → hsv_grade → comp_grain`. Crushed blacks / S-curve gamma / contrast / sat-trim per the established WOBAR post template (down_bad_3stack, iris_2). All four on dials.
3. **Soft shadows.** `light1` (warm orbiting key) `shadowtype='soft2d'`, `shadowcasters='geo_attractor'` — inter-sphere occlusion so the cluster reads as mass, not floating balls.

New ctrl_master **Post page**: `Bloomthresh` 0.5, `Cineblacks` 0.05, `Cinegamma` 0.92, `Cinecontrast` 1.18, `Cinesat` 0.9.

**Why:** Act 3 register check scored 8/10 but "doesn't feel realistic enough" — diagnosis ranked threshold-less bloom, missing grade, and missing occlusion as the top three causes. Depth-fog/DOF (gap 3) deliberately deferred.

**Deliberately NOT done:** `light_back` remains orphaned (exists, palette-bound, dimmer 5.5×, absent from `render.par.lights`) — re-adding a hot pale light would shift the tuned look; Nick to decide. Grain still `add` blend (template uses screen) — minor, untouched.
