# CHANGE LOG — mercury_womb

Act 4 Phase 1 visualizer (Physical Discharge — heavy halftime, swing drums, 808s, body-feel). Built for a "Down Bad" remix (Dreamville / J Cole) with full vocals preserved; lyric/word overlays are added in post (AE/Premiere), not in TD.

**Creative direction (locked):** the WOMB. We are inside a narrow chamber of black mercury. Walls press in, breathe with the bass. One sustained shot — camera moves slowly forward through the passage; sometimes it widens, sometimes tightens. Reflective surfaces (mirror/encounter lens) play with iridescent desat-purple highlights. Music-video treatment, not loop-feel.

Register: **held by a body.** Distinct from cusp 4→5 work (`iris_2`, `eyes_cut_deeper_pop_mirror`) which open the heart. This visual presses in, makes the music physical.

TD location: `/project1`

Source plan: `~/.claude/plans/i-made-a-remix-wondrous-pearl.md`

---

## v001 — In progress (2026-05-21)

**Build path:** SOP tube/lofted-curve geometry + GLSL/noise displacement + PBR reflective MAT + HDRI environment + slow forward camera + cinematic post chain. NOT raymarched SDF (TD-FTE-hostile) and NOT POPX soft-body fluid (too heavy, hard to camera-relate).

**Reference networks (diff-against, per Rule 0b):**
- `magnet_chamber/` v002 — inside-POV camera (Camradius=0.1, Camfov=80), slow tumble, manual CA recipe
- `attractor_chamber/` v002 — black PBR + HDRI + 4-light rig + recorder wiring + ctrl_master pattern
- `iris_2/` — single sustained shot pacing, per-channel CHOP normalization, HDR bloom + cinematic level grade
- `act2_ferrofluid_sphere.toe` — reflective black PBR + 3-light iridescent rig (120° hue offset)
- DO NOT mimic: `act2_tunnel/` — same word, entirely different register (intimate/organic/mercury vs vast/geometric/particle)

**Architecture (target):**
```
SOP CHAIN:
  tube_sop (high col/row counts) → noise_sop (audio-amp-driven) → subdivide_sop
  → geo_walls (Geometry COMP, mat_mercury PBR black/metallic + iridescent)

RENDER:
  env_hdri + 4 lights (orbit, palette-cycle) + cam_inside (Camradius=0.1, Camfov ~60–80, tz forward)
  → render_main (720×1280, AA on)
  → manual CA (3 levelTOP + 2 transformTOP)
  → inputplusbloom (threshold 0.4, intensity 1.1)
  → level_cinematic (crushed blacks, S-curve gamma)
  → hsv_desat (sat ~0.80)
  → grain (simplex2d, ~0.08 opacity)
  → null_out → moviefileout (h264 yuv420 mp4, audio from audiofileinCHOP @44100)

AUDIO:
  base_audio (canonical 8-channel split)
  → per-channel normalization (iris_2 pattern from rec_audio stats)
```

**Audio reactivity (single primary + sparse seconds):**
| Channel | Maps to | Curve |
|---|---|---|
| `bass` | Wall displacement amplitude (primary) | `floor + ceil * max(0, bass)^1.5` |
| `transient` | Sharp displacement spike (gated) | `transient^2.5`, lag-gated |
| `energy` | Iridescent intensity | `energy^2` |
| `sub_pressure` | Camera tz speed micro-modulation (±5%) | linear, tiny |

NOT mapped: camera forward speed (sustained shot is the anchor), color cycle (palette stays in foundation), CA offset (ambient atmosphere, not effect).

**Open decisions (resolved during build):**
1. Network name: `mercury_womb` (preserves creative anchor + substance)
2. Wall topology: lofted curve (twists, widens/tightens) over straight tube — more variation across full track
3. HDRI: borrow attractor_chamber setup first, swap if too bright
4. Iridescent palette weighting: mauve/deep-purple/bronze-patina for Phase 1 (vs. brighter mirror-metallics for cusp work)
5. Pearl/anchor object: NO for v001 — pure environment per direction

**Risks to watch:**
- "Tunnel" drift toward act2_tunnel register — keep walls intimate, organic, smooth-curved
- HDRI bleed making reflections busy — use dim low-detail env
- Audio over-mapping — resist binding more than the table above
- Lyric post-compositing legibility — avoid sustained mid-grey luminance band

**Build status:** workspace folder created, CHANGE_LOG drafted. TD build pending — one step at a time per Nick.

---
