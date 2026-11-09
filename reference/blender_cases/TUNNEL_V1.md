---
title: Case File — tunnel_v1
version: 0.1
last_updated: 2026-11-07
status: live — reverse-engineered from the files; Nick's reasoning is in WOBAR_VISUAL_IDENTITY
scope: How tunnel_v1 works and what it established, so a new piece can start from it. Parameters live in the kit card; this file holds structure, what each part is for, and what is known vs inferred.
dependencies: [[reference/blender_kit/README]] (KIT_Tunnel), [[reference/blender_library/BLENDER_FOOTGUNS]]
---

# CASE FILE — tunnel_v1

**Source:** `/Volumes/music/blender/tunnel_v1.blend` (saved 2026-10-29; render-identical to its 2026-10-26 save). Render: `/Volumes/music/blender/renders/tunnel_v1_final/` (206 × 16-bit PNG, 2026-10-26) and `tunnel_v1_preview.mp4`. Kit part: `KIT_Tunnel`, which reproduces frame 100 at 0.000/255.

## What it is

A **seamless 206-frame vertical loop** (1080×1920, 30 fps, EEVEE, Standard view transform). The camera sits still at the origin looking down +Y into three nested rectangular tunnels of repeated glass shapes. Rings flow toward the camera, fade in from 70 units away, shrink from a per-layer distance, and are gone before they reach the lens. A warm point light and an emissive bone-coloured orb at the vanishing point make the white centre. The compositor blooms it, then mirrors it four ways.

**No audio, no keyframes, no drivers.** All motion comes from scene time inside `TunnelWalls`, with every cycle tied to `Loop Frames`. Frame 207 diffs 2.2/255 against frame 1, against 62.7 for frame 104. That's the loop proof.

## How the look is built (and which layer does what)

| Effect on screen | Where it comes from |
|---|---|
| Depth and density | Three tunnels at different sizes (6×10.6, 3.6×6.36, 2.1×3.7) and ring counts (120 / 60 / 60) |
| Layers never lining up | Each tunnel's `Color Offset` is a third of the gradient apart (0 / 0.33 / 0.66), and the inner one has 5 spiral arms vs 2 |
| Muted iridescent colour | `ColorGlass`: one gradient (`Color Map - Muted Psychedelic`: plum → oxblood → copper → olive → **one white stop** → teal → navy → plum), indexed by `color_pos` + a gradient across each shape + a **rim shift**, so the edge shows a different hue from the body. Fresnel mixes transparent and anisotropic glossy, plus an edge-falloff glow |
| The rainbow gradient | **Not used.** Two gradients are in the material, and only the muted one is linked |
| White centre | `VanishingOrb` (emission bone `#C7BCA6` at 30) + `VanishingLight` (warm, 71k W) at the far end, blown out by the bloom |
| Kaleidoscope symmetry | **Compositor, not geometry:** bloom → flip X + split at 0.5 → flip Y + split at 0.5. The 3D scene itself is not symmetric |
| Shallow focus | Camera 34 mm, f/1.2, focus 16 |

## Variants on the drive (Oct 26–29)

`tunnel_v1_glass_light`, `tunnel_v1_moire`, `tunnel_v1_pills_kaleido` (Oct 26 look-dev), and `tunnel_v1_rounded_squares` (Oct 29). The last is the same file with the `Shape Source` swapped to `Shape_RoundedSquareWire` (`WireTubes`, emission `WireBone`), half the ring counts, and three new `TunnelWalls` switches (Round Rings / Face Centre / Ring Spin). **The kit uses the rounded-squares node group with those switches off**, which is proven identical to tunnel_v1.

## What it established

Nick's read on this piece lives in [[reference/WOBAR_VISUAL_IDENTITY]] (merged 2026-11-09): *color is what lands: muted, against black, mauve/copper/teal, iridescent shift; white center light for portal pieces; density anytime; symmetry = order; form open.* Color is what he liked most, and he named all four parts. Symmetry reads as **order** (it makes chaos look designed), not as a face or mandala. The white light belongs in portal pieces, not every visual. That file also logs two pulls against WOBAR_BRAND (gloss, pure white). VISUAL_RESET §6.3 has since denied the no-pure-white and imperfect-mirror rules (D1, D2) on this reading.

## Using it as a base

- It is a **loop system**, not a song system. Making it audio-reactive means adding control-empty drivers (see the kit's Control Channels) onto `TunnelWalls` inputs such as Pulse Amount, Spin Speed and Color Offset. None exist yet.
- `Loop Frames` is the master clock. Change scene length and `Loop Frames` together, or the seam shows.
- Swapping the shape is one node value for all three tunnels.
- The kaleidoscope belongs to `TunnelComp`. Drop it to see the real geometry. Any piece that wants symmetry can reuse the compositor alone.
