---
title: WOBAR Blender Kit — Parts Library
version: 0.2
last_updated: 2026-11-09
status: live
scope: The reusable, verified parts pulled out of finished WOBAR Blender pieces, stored as Blender assets you can append. One card per part — what it is, what it needs, what to set, what bites. The analog of touchdesigner/reference_networks, except the parts are real assets to append, not files to compare against.
dependencies: [[reference/blender_library/BLENDER_FOOTGUNS]], [[reference/blender_cases/TUNNEL_V1]], [[reference/blender_cases/MAKYO]], [[reference/blender_cases/EVERYDAY]]
---

# WOBAR BLENDER KIT

**Start every new visualizer by checking this kit before building anything.** A part here is tested; rebuilding it from memory is not.

## Where it lives

| What | Path |
|---|---|
| Library file | `/Volumes/music/blender/wobar_kit/wobar_kit.blend` (Blender 5.2.3, ~4.0 MB). v0.1 kept beside it as `wobar_kit_v0.1_backup.blend` |
| Catalogs | `/Volumes/music/blender/wobar_kit/blender_assets.cats.txt` — WOBAR / Tunnel · MAKYO · Everyday · Control · Compositor · World · NodeGroups |
| Build + verify scripts | `scripts/blender/kit/` — `prep.py` (source → partial), `assemble.py` (partials → library), `verify_kit.py`, `imgdiff.py` |

Binaries live on the drive, text lives in git. **Registered 2026-11-07** in Preferences → File Paths → Asset Libraries as **"WOBAR Kit"**, import method **Append** (Append (Reuse Data) is not offered for user libraries in 5.2; FOOTGUNS V-10). It shows in the Asset Browser on any file while the drive is mounted.

**Asset Browser caveat for MAKYO parts:** each dragged-in part appends its own copy of the control empty as a dependency, so two parts give `WOBAR_CTRL` + `WOBAR_CTRL.001` and split the drivers. That's expected from Append and the script behaviour, but not yet observed in the UI. For MAKYO parts, use the script below with every part plus `KIT_CTRL` in one load. The Browser is fine for the tunnel, worlds and compositors.

Append by script:

```python
with bpy.data.libraries.load("/Volumes/music/blender/wobar_kit/wobar_kit.blend", link=False) as (src, dst):
    dst.collections = ["KIT_Tunnel"]          # top-level KIT_ collections; children come along
    dst.worlds = ["TunnelWorld"]; dst.node_groups = ["TunnelComp"]
for c in dst.collections: bpy.context.scene.collection.children.link(c)
scene.world = bpy.data.worlds["TunnelWorld"]
scene.compositing_node_group = bpy.data.node_groups["TunnelComp"]   # 5.x location (FOOTGUNS V-7)
```

**Append, don't link**, unless the piece should follow later kit changes. Edits to an appended part stay in the piece.

## Verification record (2026-11-07, Everyday added 2026-11-09)

How "verified" was earned, so it isn't taken on faith:
- **Integrity:** all 8 Object/Collection Info references resolve inside the kit; all 87 drivers target `WOBAR_CTRL`; no action has users; no sound; only `KIT_` collections.
- **Tunnel:** `KIT_Tunnel` appended into an empty scene, frame 100 rendered at 20%, diffs **0.000/255** against `tunnel_v1.blend` frame 100.
- **MAKYO:** all MAKYO parts plus `KIT_CTRL` appended into an empty scene, the control empty set from `makyo_curves.json` at frame 900. Instances **ShardStream 3000 / HatDust 7000**, identical to `makyo_intro.blend`, and the render diffs **0.13/255**.
- **2026-11-09 rebuild (v0.2, adds Everyday):** integrity clean, **194 drivers, all on the one `WOBAR_CTRL`**. Regression: tunnel still **0.000/255**, MAKYO **0.074/255** with the same instance counts.
- **Everyday:** `KIT_Everyday` + `KIT_CTRL` + `EverydayWorld` + `EverydayComp` swapped into the source file in place of its own parts, control values copied at the frame, all driven values identical (checked one by one at frame 5000). Render diff **10.4/255 at 8 samples, 3.0/255 at 64 samples** (frames 300 / 3150 / 5000 at 8 samples: 6.6 / 7.0 / 10.4). The gap is sampling noise, not a mismatch: same-scene renders are bit-identical, the diff is speckle on edges and glints with no shift or colour change, and it falls with the square root of the sample count. EEVEE seeds some noise per object, and the kit renames objects. `scripts/blender/kit/verify_everyday.py`.
- **Not exercised:** the ShardStream simulation over time (break history from frame 1). Both sides jumped straight to frame 900. Bake from frame 1 before trusting breaks.

---

## Parts

### `KIT_Tunnel` — WOBAR / Tunnel
Three nested `TunnelWalls` tunnels (`Tunnel`, `Tunnel_Mid`, `Tunnel_Inner`) + `VanishingLight`, `VanishingOrb`, `TunnelCam`, and the child `KIT_Tunnel_Shapes` (instance sources, hidden from render). Defaults reproduce `tunnel_v1` exactly.
- **Needs:** `TunnelWorld` + `TunnelComp` for the full look; render 1080×1920, 30 fps, **Standard** view transform, frames 1–206.
- **Loops every `Loop Frames` (206).** Keep scene length equal to it, or a multiple of it.
- **Shape swap:** one node in `TunnelWalls` (`Shape Source`, an Object Info) sets the repeated shape for **all three tunnels at once**. The shape is a node value, not a per-object setting. Kit default is `Shape_GlassSolid`; the others are `Shape_Cube`, `Shape_Sphere`, `Shape_Pill`, `Shape_GlassPill`, `Shape_RoundedSquare`, `Shape_RoundedSquareWire`.
- **Key inputs:** Width/Height (tunnel cross-section), Rings / Ring Gap / Rings Per Loop (density and speed), Fade In Until / Shrink From / Gone At (distances where shapes appear, shrink, vanish), Color Offset (layers kept off-phase at 0 / 0.33 / 0.66), Spiral Arms, Pulse Amount / Pulse Wavelength, Field Scale / Field Drift. Round Rings / Face Centre / Ring Spin came from the rounded-squares variant; **off = tunnel_v1**.
- **Not audio-reactive.** Everything runs on scene time.

### `KIT_CTRL` — WOBAR / Control
The `WOBAR_CTRL` empty. **Every audio-driven part reads only this object.** It was MAKYO_CTRL, renamed; the drivers followed the rename. It ships with **no keyframes**: signal channels neutral, tuning constants as MAKYO shipped them.
- **Append it in the same `libraries.load` call as the MAKYO parts.** A MAKYO part appended alone brings `WOBAR_CTRL` along as a driver dependency, and a second load of `KIT_CTRL` then creates `WOBAR_CTRL.001`, which splits the drivers across two empties (verified 2026-11-07). One load, every part plus `KIT_CTRL`.
- Channel contract: see **Control Channels** below.

### `KIT_MAKYO_Shards` — WOBAR / MAKYO
`ShardStream`: 3000 mirror shards on a looping stream past the camera, broken by kicks inside a break zone, with a hit-glow attribute (`hitglow`) read by the shard materials. Children: `KIT_MAKYO_ShardKit` (24 shard meshes), `KIT_MAKYO_FracPieces` (255 fracture pieces), `KIT_MAKYO_FracTables`. All hidden from render, which is still instanced (FOOTGUNS V-8).
- **Simulation zone.** Bake (`object.simulation_nodes_cache_bake`) from frame 1 before rendering; the MAKYO render script re-bakes every launch.
- **Reads:** `stream_base`, `kick_acc`, `kick_surge`, `kick_on`, `vortex_acc`, `vortex_turn`, `vortex_on`, `kick_idx`, `kick_vel`, `break_on`, `sec_density`, `intact`.
- **How breaks fire** (from setting and attribute names; physics not stepped through): a new `kick_idx` value is a new kick, `Break Chance` (0.3) of shards inside `Break Zone` break into `Fragments`, and they glow for `Hit Glow Time`.

### `KIT_MAKYO_Dust` — WOBAR / MAKYO
`HatDust`: 7000 specks on the same stream logic, driven by hats. Source speck `K_speck` sits in the hidden child `KIT_MAKYO_DustSrc`.
- **Reads:** `hat_idx`, `hat_env`, `hats_on`, `dust_density`, `hat_bright`, `intact`, `vortex_*`, `stream_base`, `kick_*`. Density is `dd * (0.6 + 0.8*hat_bright) * (1 - intact)`, so dust is off while the mirror is intact. That's the makyo_intro version of the driver.
- The intro's pre-drop hide keyframes were **stripped** (song-specific); the `(1 - intact)` term does the same job from the control channels.

### `KIT_MAKYO_Mirror` — WOBAR / MAKYO
`MirrorPieces` (`MirrorShatter`: mesh-island shatter toward camera at `Drop Frame`), `MirrorCracks` (crack light), `IntactMirror`.
- **Set `Drop Frame` per song** (modifier input; MAKYO = 824).
- **Hard-coded frame, fix before reuse:** the `MirrorCracks` scale driver is `1.0 if frame < 827 else 0.0`, and the `KickRim` energy driver (in `KIT_MAKYO_Light`) multiplies by `(frame >= 827)`. Both are literal MAKYO frames, 3 frames after the 824 drop, and they **won't follow a new drop**. Rewrite them to read the control empty (e.g. `intact`) or a `drop_frame` property.
- **Reads:** `crack`, `intact`, `snare*`, `kick_flash`, `kick_light`, `kick_on`, `drop_flash`.

### `KIT_MAKYO_Light` — WOBAR / MAKYO
`Core` (white emission sphere, scale `2.6 * sec_core`), `CoreLight` (point, 3e6 × light level), `Halo` (hidden in MAKYO), `Haze` (volume cube), `KickRim` (area light, rust `#C07950`).
- **The light level is the snare.** One expression feeds core light, core emission (squared), haze glow, mirror edges and crack light: `floor + (1-floor) * max(snare, kick_light*kick_flash*kick_on, drop_flash)`, falling back to 1.0 when `snare_on` is 0.
- Rust gradient on edges/haze/halo; see [[reference/blender_cases/MAKYO]] § Colour.

### `KIT_MAKYO_Cam` — WOBAR / MAKYO
`MakyoCam`, 28 mm, at origin looking +Y, with kick jolt drivers: x/z offset `0.015 * jolt * kick_on`, roll `0.25° * jolt_r * kick_on`.

### `KIT_Everyday` — WOBAR / Everyday
The audio-reactive tunnel from Everyday: `EV_Tunnel`, `EV_Tunnel_Mid`, `EV_Tunnel_Inner` on **`TunnelWalls_AV`**, `EV_VanishingLight`, `EV_VanishingOrb`, `EverydayCam`, hidden child `KIT_Everyday_Shapes` (`EV_Shape_*`). Names carry `EV_` because they clash with `KIT_Tunnel`. Use with `EverydayWorld` + `EverydayComp` and `KIT_CTRL`, in one `libraries.load`.
- **`TunnelWalls_AV` = `TunnelWalls` with the clock taken away.** The Loop Phase links are replaced by Value nodes (`TravelPhase`, `SpinPhase`, `ColorPhase`, `PulsePhase`, `PulseGain`) that drivers set from the control empty, so motion follows the song, not scene time. Plus two stages before `Shapes On Walls`:
  - **Chaos Offset:** wander (the tunnel snakes, rings move together), shape (3D noise pushes shapes off rings), scatter (random direction per shape) and tumble (extra rotation). All zero unless driven. Colour is stored before it, so shapes keep their colour.
  - **Reveal:** per-ring and per-shape keys against `reveal_r` / `reveal_h`; shapes grow in / shrink out with an overshoot (`pop`). Hidden shapes are **zero-scale, never deselected** (FOOTGUNS V-14). Uses its own point-cloud `Reveal Points Per Ring` (V-15).
- **`EV_ColorGlass`:** the Muted Psychedelic ramp → `Psych Saturation` (sub-section intensity, peak, flood, break drain) → rim shift; hat **glints** on rims in the in-focus band; a warm **appear flash** (`pop`); `Void Mix` to black (void, cut).
- **Light:** `EV_VanishingLight` and `EV_OrbGlow` follow the snare (L9), breathe with the sub in the intro, go to 0 on `cut`. `EverydayComp` bloom strength follows the snare.
- **Neutral as shipped:** every song channel 0 except `reveal_r` / `reveal_h` = 1, so the whole tunnel shows; tuning constants as Everyday shipped them. **Not a loop**, nothing moves until channels are baked.
- **The section moves are scripts, not parts:** `scripts/blender/everyday/` (drop2_peak, break_void, break_chaos, intro_outro, drop1_outro). They hard-code Everyday's bars and address the **source file's names** (`Tunnel_Inner`, `ColorGlass`, `OrbGlow`, `VanishingLight`); against the kit part those are `EV_*`. Generalising them (bar map + name map as arguments) is the next piece's first job. See [[reference/blender_cases/EVERYDAY]].

### Worlds and compositors
- `TunnelWorld`: Light Path mix; the camera sees black, lighting sees white.
- `MakyoWorld`: camera sees patina `#5C7470` at strength 0.004 (reads as black); reflections and lighting see the HDRI at `/Volumes/music/blender/makyo_assets/hdri/metro_noord_2k.hdr`, an **absolute path**, not packed.
- `TunnelComp`: Glare (Bloom, threshold 0.45, strength 0.6) → flip X + split → flip Y + split. That's the 4-way kaleidoscope.
- `EverydayWorld`: tunnel world (camera sees black).
- `EverydayComp`: `TunnelComp` with the Glow strength driven by the snare (`0.6 * (glow_floor + glow_depth * snare)`).
- `MakyoComp`: two Bloom passes (threshold 20 / strength 0.2 and threshold 2 / strength 0.25) mixed.

### Node groups (also marked individually)
`TunnelWalls`, `TunnelWalls_AV` (Everyday), `WireTubes` (edges → tubes, `Wire Radius`), `ShardStream`, `HatDust`, `MirrorShatter`, for building new parts. **They reference kit objects** (shapes, shard kit, fracture tables), so appending a node group alone leaves those references to bring in yourself. Prefer the collection parts.

---

## Control Channels — the contract

**One control object for the whole kit.** Since v0.2 `WOBAR_CTRL` carries both MAKYO's and Everyday's channels; `assemble.py` merges a later part's control empty into it (copies missing channels, remaps users, deletes the duplicate) and reports any same-name channel with a different value (none so far). The MAKYO table comes first, then Everyday's.

What `WOBAR_CTRL` carries. A new song's analysis has to produce these names, per frame, as custom-property keyframes on the empty. MAKYO's came from `makyo_assets/makyo_curves.json` (per-frame, 30 fps). The JSON matched the baked keys exactly at frames 1/900/2400.

| Channel | Kind | Meaning (MAKYO) |
|---|---|---|
| `kick_idx` | int, non-decreasing (0–171) | running kick count; a change = a new kick |
| `kick_vel` | 0–1 | velocity of the current kick |
| `kick_acc` | non-decreasing (0–161) | kick-driven stream push (× `kick_surge`) |
| `kick_flash` | 0–1 decay | kick light flash |
| `snare` | 0–1 envelope | **master light level** |
| `hat_idx` / `hat_env` / `hat_bright` | int non-decreasing (0–431) / 0–1 / 0–0.81 | hat count, hat envelope, hat brightness |
| `low` | 0–1 | low-end level (carried, **read by no driver**) |
| `vortex_acc` | non-decreasing (0–152) | stream rotation (÷ `vortex_turn`, × 2π) |
| `stream_base` | non-decreasing (1–4910) | baseline stream travel |
| `sec_density` / `sec_glow` / `sec_core` | 0/1 · 0.15–2.23 · 0.6–1.7, per section | stream on/off, haze glow multiplier, core size multiplier |
| `intact` / `crack` / `drop_flash` | 0/1 · 0.12–0.9 non-decreasing · 0–1 | mirror intact (pre-drop), crack opening, drop flash |
| `jolt_x` / `jolt_z` / `jolt_r` | −1–1 | camera shake per kick |
| `break_on` | 0/1 | shard breaking enabled |

Switches and tuning constants (not per-frame): `snare_on`, `kick_on`, `hats_on`, `vortex_on` (per-system mute), `snare_floor` 0.08, `kick_surge` 7.5, `vortex_turn` 12, `dust_density` 0.08, `kick_light` 0.35, `kick_rim` 4000 (declared as driver variable `kr` on KickRim but **not used** in its expression, which hard-codes 8000).

`makyo_curves.json` also carries `sec_speed` (0.3–1.1), `drop_frame` (824) and `st_drop`. None of them is a property on the control empty; `sec_speed` was never wired.

### Everyday channels (from `scripts/blender/everyday/analyze_stems.py` + the section scripts)

Stem analysis (`everyday_curves.json`, 30 fps, 6583 frames; ranges measured on the baked file):

| Channel | Kind | Meaning |
|---|---|---|
| `kick_idx` / `snare_idx` / `hat_idx` | int, non-decreasing (0–160 / 0–104 / 0–746) | running hit counts |
| `kick_flash` / `snare` / `hat_env` | 0–1 decay | envelopes on the **onset**; `snare` is the master light (L9) |
| `kick_shove` / `snare_step` / `hat_step` | non-decreasing | eased hit counts: each hit adds exactly 1 → travel push, spin step |
| `low` | 0–1.2 | low end (no kick), normalised to drop level → pulse gain |
| `low_slow` | 0–1 | the same at section speed (attack 0.4 s, release 1.5 s) → psychedelic intensity |
| `low_acc` | non-decreasing (0–161) | integral of travel speed (floor 0.35 + low) |

Section channels (baked by the scripts from bar numbers and the channels above):

| Channel | Script | Meaning |
|---|---|---|
| `shear`, `peak` | drop2_peak | inner-layer counter-roll steps from drop 2; bar-97 peak 0→1 |
| `brk`, `brk_acc`, `void` | break_void | break hold (travel share removed), void (off via `void_on`) |
| `c_wander` / `c_shape` / `c_scatter`, `chaos_t` | break_chaos | chaos layers (overshoot to −0.12 on the snap back); noise time with hit jolts |
| `reveal_r` / `reveal_h`, `intro_mask`, `outside`, `cut` | intro_outro | ring / shape reveal; intro gate; camera pull-out (off: `outside_dist` 0); cut to black |
| `xhold_acc`, `kick_hold`, `snare_hold`, `ostop_t`, `lunge`, `flood`, `dissolve`, `outro_t` | drop1_outro | held-breath and outro stops subtracted from travel / kicks / spin / clock; lunge; colour flood; outro drift |

Tuning constants (Everyday values): `travel_rate` 0.18 · `kick_push` 0.05 · `spin_rate` 0.0728 · `spin_step` 1/24 · `color_rate` 0.0874 · `hat_nudge` 0 · `pulse_rate` 0.17 · `pulse_base` 0.75 · `pulse_depth` 0.5 · `light_floor` 0.85 · `light_depth` 0.45 · `glow_floor` 0.9 · `glow_depth` 0.35 · `psych_lo` 0.4 · `psych_span` 0.45 · `sat_depth` 0.6 · `rim_depth` 0.6 · `glint_frac` 0.18 · `glint_strength` 5 · `glint_focus` 16 · `glint_band` 8 · `inner_shear` 1/16 · `peak_sat` 0.35 · `peak_rim` 0.4 · `peak_glint_frac` 0.5 · `peak_glint_gain` 0.6 · `break_hold` 0.5 · `wander_amp` 3 · `shape_amp` 1.6 · `scatter_amp` 4 · `tumble_amp` 3 · `chaos_snare` 0.35 · `chaos_kick` 0.2 · `reveal_soft` 0.005 · `pop_amp` 0.6 · `pop_glow` 1.5 · `light_sub` 0.8 · `lunge_amt` 0.5 · `lunge_pull` 0.12 · `dis_shape` 1.2 · `dis_scatter` 3 · `dis_tumble` 1 · `dis_rate` 0.15. Switches: `void_on` 0, `break_desat` 0, `break_dim` 0, `outside_dist` 0.

**Gap:** no vocal channel (Everyday kept the vocal out by choice, 2026-11-09). A vocal-led piece needs new channels (e.g. `vocal_env`, `vocal_onset`) added to the analysis and to this table before any part reads them.
**Verified 2026-11-09:** `makyo_curves.json` is generated from `makyo_stems.json` (from `scripts/post/makyo_stems.py`: same keys and file time, not re-run) by `scripts/post/makyo_bake.py`; a re-run to a scratch path reproduced it exactly.

---

## Rebuilding the kit

```
B="/Applications/Blender 5.2.app/Contents/MacOS/Blender"     # NOT Blender.app — that is 4.5 (FOOTGUNS V-1)
"$B" -b --factory-startup /Volumes/music/blender/tunnel_v1_rounded_squares.blend -P scripts/blender/kit/prep.py -- tunnel part_tunnel.blend
"$B" -b --factory-startup /Volumes/music/blender/makyo_intro.blend               -P scripts/blender/kit/prep.py -- makyo  part_makyo.blend
"$B" -b --factory-startup /Volumes/music/blender/everyday_tunnel_v1.blend   -P scripts/blender/kit/prep.py -- everyday part_everyday.blend
"$B" -b --factory-startup -P scripts/blender/kit/assemble.py -- wobar_kit.blend part_tunnel.blend part_makyo.blend part_everyday.blend
"$B" -b wobar_kit.blend -P scripts/blender/kit/verify_kit.py -- integrity wobar_kit.blend out/
"$B" -b /Volumes/music/blender/everyday_tunnel_v1.blend -P scripts/blender/kit/verify_everyday.py -- wobar_kit.blend out/ 5000
```
Build into a scratch folder, verify, then copy over the drive copy. Never write the library in place. **Part order matters:** MAKYO before Everyday, so the kit `WOBAR_CTRL` is MAKYO's and Everyday's merges into it.

## Adding a part

A part enters the kit only when (1) it is a top-level `KIT_` collection holding the host object plus everything its node groups reference, (2) its song-specific keyframes are stripped and every driver reads `WOBAR_CTRL`, and (3) a render-diff against its source file is logged in the verification record above.
