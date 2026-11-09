---
title: Case File — MAKYO visualizer
version: 0.1
last_updated: 2026-11-07
status: live — reverse-engineered from the files; Nick's build log not yet merged
scope: How the MAKYO full-song visualizer works — the audio pipeline, the event structure, the light logic — so the next song-driven piece starts from it. Parameters live in the kit cards; this file holds structure and what is known vs inferred.
dependencies: [[reference/blender_kit/README]] (KIT_MAKYO_*, KIT_CTRL, Control Channels), [[reference/blender_library/BLENDER_FOOTGUNS]], [[working/WOBAR_ACTIVE]] § MAKYO, [[working/WOBAR_VISUAL_RESET]] §8 (Rust preset)
---

# CASE FILE — MAKYO

**Track:** MAKYO, Act 3 original, 140 BPM. Concept and title reasoning live in [[working/WOBAR_ACTIVE]] § MAKYO (*ego eating itself*; 魔境, with the 魔鏡 magic-mirror homophone never printed).
**Source files:** `/Volumes/music/blender/makyo_final.blend` (Nov 3 22:29) and `makyo_intro.blend` (Nov 4 09:23, the later save). Shard look-dev: `makyo_shards_v0`–`v6` (Nov 3). Assets: `makyo_assets/` (stems JSON, curves JSON, HDRI). Renders: `renders/makyo_final/` (5452 frames), `makyo_final_intro/`, `makyo_final_old_intro/`, `makyo_breakdown_f2100-2950.mp4`, `makyo_wip_f2181.mp4`. Render script: `renders/makyo_render_final.py`, a copy of `wobar/scripts/blender/makyo_render_final.py`, which is on the other machine.

## What it is

A **full-song, audio-locked vertical piece**: 2160×3840, 30 fps, 5452 frames (3:01.7), EEVEE with motion blur, AgX. The master WAV sits in the sequencer (`MAKYO_master`, frames 1–5452) for sync. Near-black void, copper/rust light, one white-hot core far down +Y.

**Event structure:**
1. **Frames 1–823, the held mirror.** A dark cracked mirror (`IntactMirror` / `MirrorCracks`) holds 14 units in front of the camera. Crack light follows `crack` (0.12 rising to 0.9, which it reaches at frame 753 and holds) and the snare.
2. **Frame 824, the drop** (bar 17 downbeat at 140 BPM). `MirrorShatter` throws the mirror's mesh islands toward camera (creep, then burst). `intact` goes 1 → 0 at exactly frame 824 and never returns, and `sec_density` goes 0 → 1 on the same frame. Everything gated on either turns on.
3. **After the drop, the stream.** 3000 shards (`ShardStream`) and 7000 dust specks (`HatDust`) flow past on a looping stream around the core. Kicks push the stream (`kick_acc × kick_surge`), break shards, and jolt the camera. Hats feed the dust. Arrangement sections set density, glow and core size.

## The audio pipeline — the reusable part

```
makyo_stems.json   per-bar analysis (bpm 140, bar 1.714 s): kick/snare/hat counts, low_db, low_sus, pitch range, hat_hz, master_db
      ↓ scripts/post/makyo_bake.py (verified 2026-11-09: re-run to a scratch path, output identical to the file on the drive)
makyo_curves.json  per-frame curves, fps 30, 5452 frames, 23 channels + drop_frame 824
      ↓ baked as keyframes (5452 keys per channel)
MAKYO_CTRL empty   custom properties = the channels  (kit: WOBAR_CTRL, keys stripped)
      ↓ 87 drivers
every moving value in the scene
```
**Verified:** the baked keys equal the JSON exactly at frames 1 / 900 / 2400. The channel contract, with measured ranges, is the kit README's Control Channels table.

**Design choices worth keeping** (the patterns are in the file; the *why* in the last two bullets is Claude's read, not a reason Nick stated):
- **One control object.** Every driver in the file reads one empty, so a new song means re-baking one object, with no part rewired.
- **Per-system mutes and tuning on the same empty** (`*_on`, `snare_floor`, `kick_surge`, `vortex_turn`, `kick_light`), so look and feel can be tuned without touching node trees.
- **Event indices, not triggers.** `kick_idx` and `hat_idx` are running counts. A node group detects a new event when the index changes, which survives frame jumps and motion-blur sub-frames better than a 0/1 pulse.
- **Accumulators for motion** (`kick_acc`, `vortex_acc`, `stream_base`, all non-decreasing). Speed rides on the music without ever reversing.

## The light logic

**The snare is the master light.** One expression appears in five places (core light, core emission squared, haze glow × `sec_glow`, mirror-edge strength, crack light):

`level = snare_floor + (1 - snare_floor) * max(snare, kick_light * kick_flash * kick_on, drop_flash)`, or 1.0 when `snare_on` is 0.

So the room breathes on the snare, kicks only lift it through `kick_light` (0.35), and the drop flash overrides both. Core *size* is separate: `2.6 * sec_core`, section-level, not per hit. The kick has its own rim light (`KickRim`: `8000 * kick_flash * kick_on`, after frame 827).

## Colour

- Edge, mirror, haze and halo gradients run offblack → `#6F5038` → `#89593F` → `#A6613F` → `#C07950` → `#C7BCA6`. Stops 2–6 are the **`WOBAR — Rust`** preset ([[working/WOBAR_VISUAL_RESET]] §8) within rounding. The darkest stop is a blue-black (`#000019`), not Rust's `#0E0813`.
- World: the camera sees **patina `#5C7470`** (Rust's protected cool element, VISUAL_RESET §8) at strength 0.004, i.e. black. Reflections see `metro_noord_2k.hdr`, so the mirror shards have something to reflect.
- Core and core light are near-white (`1.0, 0.97, 0.92`). The white centre is the one non-Rust value.

## final vs intro — what actually differs

Verified by diffing driver expressions in 5.2 (FOOTGUNS V-4: static light values differ only because the two files were saved on frames 1263 and 900):
- `makyo_intro` adds `* (1 - intact)` to the dust-density driver, and keys `HatDust` hidden on frames 1–823, so **no dust before the drop**.
- Nothing else differs. Same parameters, same other 86 driver expressions.

`renders/makyo_final_intro` and `makyo_final_old_intro` suggest the intro section was re-rendered from `makyo_intro`. That's **inferred** from folder names.

## Known debts (fix before reuse)

- **Hard-coded drop frame.** `MirrorCracks` scale (`frame < 827`) and `KickRim` (`frame >= 827`) use a literal frame 3 after the 824 drop. Move them onto `intact` or a `drop_frame` property.
- **`kick_rim`** is declared on KickRim's driver but unused (the expression hard-codes 8000). **`low`** is baked but read by nothing. **`sec_speed`** is in the curves JSON but never made a property.
- **No vocal channel.** MAKYO's sample is spoken dialogue, and the visual still listens only to drums, low end and arrangement.
- Breaking mechanics are read from names (`Break Chance`, `Break Zone`, `hitglow`, `KickIdx`), not stepped through. **Bake from frame 1** (simulation zone) before trusting any break.

## Rendering

`makyo_render_final.py`: deletes and re-bakes the ShardStream simulation, then renders frames 1..N as **16-bit PNG** with motion blur. It's resumable (`use_overwrite` off + placeholders), which is why the script lives on the drive, so queued headless jobs don't need Desktop access.
