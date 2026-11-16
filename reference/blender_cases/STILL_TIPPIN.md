# STILL TIPPIN — flip visualizer (Blender), case file

Started 2026-11-13. Act 4, full song 3:42.86 (130 bars at 140), 16:9, vocal kept out, car culture
abstract only. **State (2026-11-16): look locked as v5 — `still_tippin_song_v5.blend`, no audio
modulation. Next is motion from the real stems (transitions + kick / snare / sub / hats); none exist yet.**

## The look — v5, locked 2026-11-16 (supersedes the grey membrane below)
Built by `song_preview.py` (switch dicts at the top of the file; every value below lives there).
- **Form:** the tunnel is a **ribbed coil** (Nick: "too organic" → more hypnosis): rings every 0.6 m with
  flat tops, spacing that breathes ±50 % over 12 m, organic lumps at 30 %, plus **self-similar ribbing**
  (the rib profile again at 1/4 and 1/16 scale, as shader bump). Concentric rings read as a target/eye
  on axis, so the camera **rides 0.7 m off the centre line**, the side drifting one way.
- **Paint:** **oxblood candy over light gold flake**, violet pearl flip, clear coat (Nick named classic
  car red, metallic, pearlescent, "flake like a real car"; then darker — oxblood, gold highlights).
- **Light:** night. The clear coat reflects a suburban road at night with one street lamp (Poly Haven
  `street_lamp`) that the camera never sees and that lights nothing; a specular-only, shadowless key
  light sits where that lamp is (strength 10). Headlamp fills stay. Exposure −0.6; bloom on hot spots
  only (threshold 2, size 0.2 — larger milks the throat). Coat reflection fades out by 22 m so the
  throat stays black.
- **Arrangement (the psychedelia):** **red = the rap, pearl = the drops.** Intro, rap and break are
  oxblood; Drop 1 and Drop 2 turn into a **depth pearl** — hue depends on distance from the viewer
  (cherry → violet → copper → gold, one cycle per 14 m), impossible for real paint. The pearl rolls up
  the throat over the bar before each drop and **reaches the lens on the downbeat**; it recedes at
  the outro. Psychedelia came from contrast and arrival, not added effects.
- **Drop 2 = liquid-metal melt:** ribs melt to 30 %, lumps flow back in at 1.2×, star folds off, an
  oval fold twists with the wring, squeeze halved, camera eases toward the axis (0.25 m) and a soft
  radius floor (1 m) keeps the wall off the lens. Snaps back at 113. The 5-lobe "starfish" it forms
  at speed is accepted (Nick: "starfish is fine").
- **Speed:** all section speeds ×1.5 (Nick: "move more quickly through the tunnel").
- **Brand-check exceptions, deliberate:** gloss metallic everywhere breaks the matte fundamental —
  matte was tested and turned the oxblood bronze/milky, so gloss stays and restraint comes from night
  and darkness instead. Grain belongs in the final grade.
- **Brand check (2026-11-16, 5/10 Act 4):** the two criticals are motion, not look — still water (no
  real reactivity) and hypnotic instead of driving. Both wait on the stems.

## Motion decisions 2026-11-14 → 16
- **The no-sway rule is dropped** (Nick, 2026-11-16) — roll may go both ways.
- **Not chosen, all built behind switches and rejected:** per-hit mapping on fake signals (sun steps
  per snare, flake glints on hats, sub breathing; tight and swell — "feels forced"); tempo-lock (ribs
  pass the lens on the grid) + trunk rattle from the master's sub; a **water slide** (corkscrews,
  plunges, gravity speed, a pendulum rider that banks up the walls). Fake hits can't be judged —
  motion gets judged against the real stems only.
- Psychedelia tried and not chosen: tracers, time-lapse sky, heat-reactive paint, chameleon /
  oil-slick / impossible-sky pearls, lace candy (reads as veins/crackle), recursion (mock only).

## The piece (grey membrane, 2026-11-13 — the base v5 grew from)
**A winding membrane tunnel you travel down.** Camera inside a long tube on a wandering spine,
looking a few metres ahead along it, rolling slowly in **one direction only** (Nick: no sway).
Grey while motion is locked; colour comes last.

**Lighting (Nick, 2026-11-13):** headlamp only — a fill on the camera + a shadowless, no-specular
fill 5.5 m ahead (closer blows out the near walls). **No core light on this track** — a deliberate
exception to WOBAR_VISUAL_RESET L10. The "wall lights itself where stretched thin" layer was built
and is **off for now** (Nick); the snare = light rule is carried by a **headlamp flash** instead.

**Instrument map (L9):** kick = push (camera surge; Drop 1 opens the throat; Drop 2 adds a twist
step; in drops it also punches the lens wider) · snare = light (headlamp flash) · sub = intensity
(depth of the section's deformation) · hats = detail (fine wall shiver, never the shape).

**Transitions stem (Nick's plan):** the scene falls into **chaos** with transitions energy — risers
pre-drop and between sections. Chaos = whip bends baked into the spine where the camera will be,
wall boil, lens widening/breathing (close/far confusion), roll speeds up (still one way), travel
accelerates. Ends with a ~0.2 s release tail, not a dead cut. **No held breath before either drop**
(Nick: "the rap leads right into the drop").

## Structure (bars) — approved state
| Bars | Section | Tunnel / motion |
|---|---|---|
| 1–16 | intro | calm, stable glide; riser 13–16 at ~half strength |
| 17–32 | rap (not dubstep yet) | steady "normal" tunnel; long riser 25–32 builds into the drop |
| 33–64 | **Drop 1 — talking throat** (approved) | cross-section forms vowels per 8th on a bouncy spring (formant / "alien voice"); fast travel, big wander |
| 65–80 | break — same rap line repeated | camera passes through the **same 8.9 m stretch once per 4-bar line**, roll locked so passes line up, wall mutates slowly across repeats; riser 77–80 tears it into Drop 2 |
| 81–112 | **Drop 2 — wring** (approved; energy raised in v3) | roll locks, tube twists against it, each kick adds a jolting twist step: 81 tighten, 89 snap + tighten harder, 97–104 long unwind (master's highs dip), 105 hardest wring the other way |
| 113–129 | **outro — snap back** (approved) | back to the steady glide; fades to black |

Nick's verdicts: Drop 1, Drop 2, outro "really great" (v1). Intro + old break rejected (intro didn't
build — fixed with transitions chaos; break "forms breaking" widening rejected — replaced by the
repeated-line pass). v3 answered "transitions a little choppy" (all section channels smoothed,
kicks added back on top) and "drop 2 doesn't have enough energy". **v3 not yet reviewed.**

Assumed, unconfirmed: rap line = 4 bars; riser positions (13–16, 25–32, 77–80, 111–112) are
placeholders read off the master's energy map; fake halftime pattern (kick beat 1 + "and" of 3
every other bar, snare beat 3, hats 8ths / 16ths in drops, hats out 97–104).

## Also built
- **VJ loop** (`vj_loop.py`): 20 s seamless grey loop, periodic spine + wall (period 36 m),
  holonomy-corrected frame, exactly one roll turn per loop. Verified frame 601 == frame 1 (mean
  pixel diff 8e-5). 20 s is not bar-locked (~11.7 bars at 140; 8 bars = 13.71 s if needed).
  Audio on a loop must move walls/light only — travel speed changes break the closure.

## Rejected this session (don't re-propose)
- Swanga spoke cones — read as a mandala / wheel on-axis.
- Candy-paint body panel + liquid surface (wave-equation heightfield) — "hypnotic but not psychedelic".
- Moiré (multi-sheet Shepard descent, then two bold gratings) — "a shimmering texture", then "can't carry a whole song".
- Static membrane chamber with a pinch — a centred hole reads as an eye (same pareidolia as ATEM).
- Fast contour colour bands — "moves too quickly through the colours"; colour returns last and slow.
- Break as "form breaks" (tunnel widens and loosens) — Nick didn't like it.
- Held breath before the drops.
- Regular symmetric wall folds (cos 5θ) and whole-sector glow — read as a star / pinwheel down the axis.

## Files
- Scripts: `scripts/blender/still_tippin/` — **current: `song_preview.py`** (needs `chamber.py`
  exec'd first for `_col`), `vj_loop.py`, `tunnel_wander.py` (+ the explorations).
  Run: `exec(chamber.py); exec(song_preview.py); build_song()` → keyed per frame, renders headless.
- **Current: `/Volumes/music/blender/still_tippin_song_v5.blend`** (built from v3 by `song_preview.py`;
  `_grey_v4` = the sunny version, `_grey_v4_pre_arr` = before self-similar ribs + arrangement).
  Assets: `still_tippin_assets/` (`street_lamp_2k.hdr`, `abandoned_tank_farm_03_2k.hdr`,
  `sub_env_master.json` from `sub_env_master.py`).
- Older scenes: `/Volumes/music/blender/still_tippin_song_grey_v3.blend` (a copy of it and of `_vjloop_grey_v1` is in the repo at `blender/still_tippin/`), `_vjloop_grey_v1`,
  `_tunnel_wander_v{1,2}`, plus exploration .blends.
- Previews (with master audio): `/Volumes/music/releases/1_in_progress/flips/still_tippin/visualizer/previews/`
  (`2026-11-13_song_grey_v{1,2,3}_with_audio.mp4`, `_vj_loop_grey_20s.mp4`, `explorations/`).
- Master: `.../still_tippin/audio/still_tippin_master.wav`. Stems go in `.../audio/stems/`.

## Open
- Wire real stems: transitions envelope → chaos (replaces `CHAOS`), kick / snare / sub / hats
  onsets + envelopes → the fake `events()`; Drop 1 vowel may need the sub stem's spectral
  centroid if the "alien voice" lives in the bass filter.
- Rap-line length in the break (4 bars assumed).
- Motion against the real stems — the brand check's two criticals (still water; hypnotic, not
  driving). Kick → travel push is the first thing to try. `AUDIO`, `AMOD`, `TEMPO`, `RATTLE`, `SLIDE`
  stay in the script as switches, all off.
- Depth pearl bands deep in the throat (many 14 m cycles squeeze into a few pixels → rainbow
  contours); fix by holding the colour past ~20 m. Not done yet.
- Final quality render settings (preview is 50 % / 16 samples), motion blur, grain in the grade.
