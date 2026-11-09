---
title: Blender Cheat Sheet
status: live — growing
scope: Personal keybinding/workflow notes for learning Blender, built for the world-building pipeline in [[WOBAR_VISUAL_RESET]]. Add to as you learn. Keep entries short — this is a lookup sheet, not a tutorial.
---

# BLENDER CHEAT SHEET

## Navigation (mouse only)

| Action | Input |
|---|---|
| Orbit | Middle Mouse Button (MMB) + drag |
| Pan | Shift + MMB + drag |
| Zoom | Scroll wheel, or Ctrl + MMB + drag |
| Zoom to selection | `.` (period, numpad) |
| Frame everything | Home |

## Modifier keys (transform workflow)

The core loop: press a transform key, optionally constrain to an axis, optionally type an exact number, confirm.

| Key | Action |
|---|---|
| G | Grab / Move |
| R | Rotate |
| S | Scale |
| X / Y / Z (after G, R, or S) | Constrain to that axis |
| Shift + X / Y / Z (after G, R, or S) | Constrain to the *other two* axes (exclude that one) |
| Type a number (after G/R/S) | Move/rotate/scale by exact amount |
| Enter or Left Click | Confirm the transform |
| Esc or Right Click | Cancel the transform |

**Example:** `G` → `Z` → `2` → Enter = move the object exactly 2 units up the Z axis.

## Mode switching

| Key | Action |
|---|---|
| Tab | Toggle Object Mode / Edit Mode |
| 1 / 2 / 3 (in Edit Mode) | Vertex / Edge / Face select |

## Open questions / to fill in as I learn
- Selection basics (click, box select, select all)
- Snapping
- Duplicate workflow
- Numpad view shortcuts (front/side/top/camera view)
