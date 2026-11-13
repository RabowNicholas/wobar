# STILL TIPPIN — flip visualizer (Blender), case file

Started 2026-11-13. Act 4, full song 3:42.86 (130 bars at 140), 16:9, vocal kept out, car culture
abstract only. **State: structure built and approved in grey with fake signals; waiting on Nick's
final mix (transitions stem + kick / snare / sub / hats stems).**

## The piece
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
- Scenes: `/Volumes/music/blender/still_tippin_song_grey_v3.blend` (current; a copy of it and of `_vjloop_grey_v1` is in the repo at `blender/still_tippin/`), `_vjloop_grey_v1`,
  `_tunnel_wander_v{1,2}`, plus exploration .blends.
- Previews (with master audio): `/Volumes/music/releases/1_in_progress/flips/still_tippin/visualizer/previews/`
  (`2026-11-13_song_grey_v{1,2,3}_with_audio.mp4`, `_vj_loop_grey_20s.mp4`, `explorations/`).
- Master: `.../still_tippin/audio/still_tippin_master.wav`. Stems go in `.../audio/stems/`.

## Open
- Wire real stems: transitions envelope → chaos (replaces `CHAOS`), kick / snare / sub / hats
  onsets + envelopes → the fake `events()`; Drop 1 vowel may need the sub stem's spectral
  centroid if the "alien voice" lives in the bass filter.
- Rap-line length in the break (4 bars assumed).
- Colour pass (muted, slow, under the L2 ceiling) and whether the stretch light comes back.
- Final quality render settings (preview is 50 % / 8 samples, ~0.4 s/frame).
