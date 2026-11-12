---
title: Case File — Everyday visualizer (A$AP Rocky flip)
version: 0.1
last_updated: 2026-11-09
status: shipped — built 2026-11-07 → 11-09 with Claude over MCP; final 4K approved 2026-11-11
scope: How the Everyday full-song visualizer works — the stem pipeline, the section moves, what was tried and dropped — so the next song-driven tunnel starts from it. Parameters live in the kit card and channel table; this file holds structure, reasons and what is verified vs not.
dependencies: [[reference/blender_kit/README]] (KIT_Everyday, Everyday channels), [[reference/blender_cases/TUNNEL_V1]] (the base it grew from), [[reference/blender_cases/MAKYO]] (the other audio-locked piece), [[working/WOBAR_VISUAL_RESET]] §6 (the rules it tested), [[reference/blender_library/BLENDER_FOOTGUNS]] V-11 – V-15
---

# CASE FILE — EVERYDAY

**Track:** Nick's flip of A$AP Rocky's *Everyday*. **Act 4, pure** (driving, propulsive, "Move"; visual register *full palette activated, heavy but held*). 140 BPM with a slight swing (Nick), key measured D# minor (F# major in places), 3:39.43 = 128 bars.
**Sections:** intro 1–12 · pull-out 13–16 · drop 1 17–48 · break 49–64 · drop 2 65–112 (hats halve at 97) · outro 113–128.
**Source file:** `/Volumes/music/blender/everyday_tunnel_v1.blend` (working file; `everyday_tunnel_v0.blend` is the untouched copy of tunnel_v1). **Assets:** `everyday_assets/everyday_curves.json`. **Stems:** kick, snare, hat, low-end-no-kick, exported by Nick, same length as the master and aligned at 0. **Renders:** `renders/everyday_*` (quick previews), `renders/everyday_full_s10/` (full song, 1080p, 10 samples, pre-drop-1/outro-fix), `renders/everyday_quality_test/` (sample + 4K test).

## What it is

tunnel_v1's three nested glass tunnels with the **clock taken out**: every phase that ran on scene time (travel, spin, colour, pulse) is now a Value node set by a driver from `WOBAR_CTRL`, so the tunnel moves with the song. Black ground, muted-psychedelic glass, the 4-way kaleidoscope comp, the white vanishing light at the far end. Vertical 1080×1920 at 30 fps for previews; final 4K.

## The pipeline — the reusable part

```
4 stems ──analyze_stems.py──> everyday_curves.json (12 channels, per frame, 30 fps)
        ──bake_curves.py──> WOBAR_CTRL keys
        ──section scripts (bars → channels)──> more WOBAR_CTRL keys
        ──drivers──> TunnelWalls_AV Value nodes · EV_ColorGlass · light · orb · comp glow
```
Run order: `bake_curves → drop2_peak → break_void → break_chaos → intro_outro → drop1_outro` (all in `scripts/blender/everyday/`). Each is idempotent; the later ones rewrite drivers the earlier ones set, so re-running one means re-running the chain from there.

**Analysis choices worth keeping** (verified in the session):
- Onsets picked on a 5 ms envelope (1 ms splits the kick's two-stage body into two hits), then back-tracked on a 1 ms envelope to the rise. Times are `index × hop / sr` — a nominal hop once faked 139.68 BPM.
- **Eased running counts** (`kick_shove`, `snare_step`, `hat_step`): each hit adds exactly 1, eased over a short window. A driver multiplies them into travel / spin without ever reversing.
- `low_slow` (attack 0.4 s, release 1.5 s) separates sections cleanly: drops ≈ 0.82, break ≈ 0.37, pull-out ≈ 0.17. It is what makes "the drop gets more psychedelic" work.
- Travel floor 0.35: the tunnel never stalls on its own; stillness is always a deliberate section move.

## Instrument mapping (became locked rule L9)

| Stem | Drives |
|---|---|
| Kick | travel push (`kick_push × kick_shove`) |
| Snare | the light: vanishing light, orb glow, comp bloom; a turn of the tunnel per hit (`spin_step`) |
| Hats | **glints** on glass rims in the in-focus depth band (18% of shapes per hat, ~4 frames). *Hats first nudged the colour roll; that made colour speed spike 7.4× in the drops and read as "snappy". Taken out (`hat_nudge` 0).* |
| Low end | travel speed and pulse (`low`, `low_acc`); psychedelic depth via `low_slow` (saturation and rim shift) |
| Vocal | **nothing** — Nick's choice, 2026-11-09 |

## The section moves

| Bars | Move | Script | Rule |
|---|---|---|---|
| 1–14 | Frame 1 is the light alone; it breathes with the sub. **The hits build the tunnel:** hats pop single shapes in, kicks/snares add whole rings, complete by bar 15. Gentle travel throughout (Nick: the intro should have light motion). | intro_outro | T3, T6 |
| 15–17 | **Held breath → lunge.** Travel stops over two beats and draws back slightly; bar 17's downbeat lunges forward in one beat (~25× normal speed) and the colour floods in at once instead of ramping. | drop1_outro | **L8** (promoted on this) |
| 49–64 | **The form breaks.** Wander (the tunnel snakes) from 49 → break shape (shapes drift off rings, each snare/kick jolts the drift) from 53 → scatter + tumble in the 61–62 kick roll → hangs nearly still in 63–64. Travel held at 50%. | break_void, break_chaos | T4 |
| 65 | **Magnetic snap** back into formation: 3 frames, overshoot through home to −0.12, settle over 9. | break_chaos | T4 |
| 65–112 | **Drop 2 = one new behaviour:** the inner layer rolls against the outer two, 1/16 turn per snare (~2.7 turns by bar 112). | drop2_peak | — |
| 97–112 | **The peak:** psychedelic depth forced to max (saturation ≈ 1.95), glints fewer and brighter — exactly where the audio thins (hats 8 → 3.5 per bar). | drop2_peak | — |
| 113–128 | **Dissipate in place:** shapes drift apart and shrink away on the hits (no flash), every motion comes to a stop by bar 127. Reveal is power-shaped (early hits take big bites) and low-passed so the last kick fill takes only the last few rings. Light alone, then **cut to black on the last kick** (frame 6573). | intro_outro, drop1_outro | T3, T6 |

**Why drop 2 needed section channels:** in the audio, drop 2a matches drop 1 hit for hit (kicks 1.38/bar, snares ≈ 0.9/bar, hats ≈ 8/bar) and the last 16 bars thin out. Stem-driven alone, drop 2 would replay drop 1 and sag at the end. Escalation had to come from bar-driven channels.

## Tried and dropped (so they are not re-proposed)

- **Break as hold + drain + void** (colour drains, blackout in 63–64): read as chrome/silver rather than dark. Nick: let the form wander instead. Still in the file behind `break_desat` / `break_dim` / `void_on` = 0.
- **Outro camera pull-out** (back out of the tunnel mouth to see it whole): read as a tidy mirrored rectangle, the least alive frame. Replaced by dissipating in place. Behind `outside_dist` = 0.
- **Light swell into drop 1** (alternative to the lunge): not chosen.
- **Grain against banding:** not needed — the light-alone frames survive a 3.5 Mbps (IG-level) encode without banding.
- **Imperfect mirror / off-white instead of pure white:** proposed under the old K1/K3 rules; Nick retired the rules instead (VISUAL_RESET §6.3 D1, D2).

## Bugs found by rendering (fixed, now footguns)

- **Smeared frames on hits** — the reveal deselected instances, so the instance count changed frame to frame and motion blur paired the wrong ones (V-14). Fix: zero-scale, never deselect.
- **Whole tunnel toggling at once / outro white-out** — the reused `Points Per Ring` counts the mesh component of a point cloud and returns 0, so every shape was "ring 0" (V-15). Reveal has its own counter now. **tunnel_v1's own copy has the same bug and the approved look depends on it** — left alone.
- New F-curves on an assigned action don't evaluate until reassignment (V-11); a driver's invalid flag sticks after the fix (V-12).

## Render

- **Quality test (2026-11-09):** at 1080p, 64 samples is within 38.5–42.6 dB of 128 (invisible); 32 is visibly grainy on glints. 4K at 32 samples, downscaled, matches 4K at 128 downscaled and is cleaner than native 1080 at 128. 4K costs ~1.5× per frame at equal samples. Glint-heavy frames (the peak) are the slowest to clean.
- **Final spec (Nick: highest quality, diminishing returns):** 2160×3840, **64 samples**, motion blur on (shutter 0.5), 16-bit PNG frames, full song. One master serves YouTube (4K upload) and IG/TikTok (downscaled). To run on the faster machine with `scripts/blender/everyday/render_final.sh` (resumable, shareable across two machines, then encodes a 4K ProRes 422 HQ master, a 4K YouTube H.264 and a 1080 social H.264). Frames came out ~36 MB each at 16-bit, ~235 GB total. **Ran 2026-11-09 → 11-11 on the M1 Max: 6,583 frames in ~37 h (~20–23 s/frame at peak), encodes ~50 min after.** Deliverables filed in the release packet (`/Volumes/music/releases/…/everyday/visualizer/`).
- Motion blur costs almost nothing in EEVEE here; samples are the cost.

## Known debts

- **Section scripts hard-code Everyday's bars and frames** (F49, F65, F97, LAST_KICK 6573…) and address the source file's object/material names. Generalise to a bar map + name map before the next piece.
- **The base conversion is not scripted:** turning `TunnelWalls` into `TunnelWalls_AV`, the psych-saturation node, the glint chain and the first drivers were built live over MCP (2026-11-07). They survive in the file and in `KIT_Everyday`, which is now the way to get them — not a script.
- Final 4K approved by Nick 2026-11-11 ("perfect"); the bar-97 peak glints read good at full quality. **Done.**
- **Deliverables (Nick, 2026-11-11):** ProRes master in the orientation the piece was made, 4K horizontal for YouTube, 1080 vertical for socials. Nothing else. Nick designs pieces to work rotated, so the second orientation is a 90° rotate of the master (Everyday: clockwise; the kaleidoscope reads the same sideways). No second render, no crop.
