---
title: Live VJ Workflow
version: 1.0
last_updated: 2026-04-16
status: live
scope: Performance setup — scene switching, hardware controllers (APC40, Launchpad, Launch Control XL), Engine COMP isolation, pre-gig checklist.
dependencies: TD_LIBRARY_INDEX.md, TD_WORKFLOW_LIVE_AUDIOREACTIVE.md, TD_WORKFLOW_MIDI_OSC.md, TD_OPERATORS_COMP.md
---

# LIVE VJ WORKFLOW

Performing with TD. Covers scene architecture, hardware controllers, Perform Mode, and gig-day reliability.

---

## Architecture — Scene Isolation

### The problem
A live TD project has 10–30 scenes. If they all cook simultaneously, framerate dies. If they cook on-demand only, scene switches hit a cold-start.

### The solution — Engine COMP per scene
```
Project root
  ├─ Base "controls"           → UI, MIDI, OSC, timeline
  ├─ Base "audio_core"         → audio pipeline → null_audio_*
  ├─ Engine "scene_1" (tox)    → cooking isolated in separate process
  ├─ Engine "scene_2" (tox)
  ├─ Engine "scene_3" (tox)
  ├─ ...
  ├─ Switch TOP (active_scene_index) → selects Engine output
  └─ Post / Output
```

### Why
- Engines cook in parallel (separate processes).
- Non-active Engines can be paused.
- Engine crash doesn't crash the main project.
- Pre-warm at load: all Engines initialize before the show starts.

### Non-Commercial limit
Engine COMP clone count is limited on Non-Commercial. Check per-build. If limited, use Base COMPs with Cook Type = Off for non-active scenes instead.

---

## Scene Switching

### Crossfade between scenes
```
Switch TOP or Cross TOP:
  - Input 0: Engine output of current scene
  - Input 1: Engine output of next scene
  - Crossfade value driven by controller knob or keypress
```

### Hard cut
Switch TOP with instant index change.

### Beat-locked switch
```
Trigger on Ableton Link beat phase == 0 (bar start) → change Switch index
```

### UI surface for scene selection
Grid of Button COMPs on a Panel Container COMP. Each button toggles Switch index and animates its own visual state.

---

## Hardware Controllers

### APC40 MK2
- 40 clip launch pads + 8 knobs per track + 8 tracks + master.
- **Wiring via MIDI In Map CHOP** with device = "Akai APC40 mkII."
- Clip launch pads → 40 discrete triggers → use for scene pads.
- Top knobs (8×8 = 64 via channel layers) → continuous controls.
- **Limitation**: lacks some buttons for transport — combine with Launch Control XL.

### Launchpad X (Novation)
- 64 pads (8×8), RGB LEDs, velocity-sensitive.
- **Wiring via MIDI In Map CHOP.**
- Excellent for clip launching, drum triggers, scene selection.
- RGB feedback via MIDI Out CHOP — send SysEx / note-on to set pad colors.
- **Setup tip**: Programmer Mode gives direct access to all 81 pads including top row (otherwise reserved for track selection).

### Launch Control XL
- 24 knobs (3 rows × 8 cols), 8 faders, 16 pads.
- **Wiring via MIDI In Map CHOP** — most reliable controller for per-param tuning.
- Fader row is tactile and predictable — assign to key runtime parameters.

### Generic MIDI controllers
Any class-compliant MIDI controller works. MIDI In Map CHOP with "Device = <name>" is the universal approach.

---

## Controller Mapping Pattern

### Global control COMP
```
Base "controls"
  ├─ MIDI In Map CHOP (APC40) → Null "apc40"
  ├─ MIDI In Map CHOP (LCXL)  → Null "lcxl"
  ├─ OSC In CHOP (phone)      → Null "osc"
  ├─ Keyboard In CHOP         → Null "keyboard"
  │
  ├─ Math / Filter / Lag CHOPs → smoothing per control
  ├─ Switch CHOP selecting active controller source → Null "active_control"
  │
  └─ Named Null CHOPs: "master_intensity", "scene_index", "crossfade_a_b", etc.
```

### Scene consumers
Every Engine COMP pulls from the global control Nulls via Select CHOP:
```
Select CHOP (Path = /project1/controls/master_intensity) → Null → drives scene param
```

### One source of truth
If the controls COMP is the only place MIDI is consumed, swapping controllers = swap one COMP. No per-scene re-mapping.

---

## Perform Mode

### Setup
Window COMP with:
- Monitor — explicit index (not "Main").
- Size — native resolution of the projector / display.
- Vsync — On (prevents tearing).
- Borders — Off.
- Fullscreen — On.

Press F1 (or specific shortcut) to enter Perform Mode.

### Hotkeys during Perform
- Escape — exit Perform Mode.
- F — toggle fullscreen (if configured).
- 1–9 — scene selection (if you map them).

### Disable editor overlays
Editor draws viewer overlays; Perform Mode doesn't. 20%+ speedup.

---

## Pre-Gig Checklist

24–48 hours before:

- [ ] Save a frozen copy of the project for the gig. Don't develop on the gig project.
- [ ] Enable Preferences → Auto-Save + crashAutoSave on external SSD.
- [ ] Confirm all media files are on the gig machine, not network mounts.
- [ ] Pre-warm all Engine COMPs at project load.
- [ ] Test every scene at least once in Perform Mode.
- [ ] Confirm MIDI controllers are recognized (Audio MIDI Setup on Mac).
- [ ] Test audio input routing: BlackHole or interface → Audio Device In.
- [ ] Full set run at target resolution in Perform Mode. Watch Perf header for drops.

Day of gig:

- [ ] Arrive early. Rebuild the rig from scratch on venue power.
- [ ] Test output to venue projector / LED wall. Resolution, aspect, color space.
- [ ] Close every other app. Chrome and video apps steal GPU.
- [ ] Silence Mac notifications: Do Not Disturb mode.
- [ ] Disable macOS sleep during performance.
- [ ] Have a backup of the .toe project on a separate USB stick.

---

## Live Reliability Tips

### Avoid per-cook Python
Anything running Python every frame is a crash risk. Use CHOP chains.

### Pre-load media
Movie File In TOP → set Cue = On but Play = Off initially. Movies load, don't play, no surprise load at scene enter.

### Don't edit during the show
Any parameter change mid-show is a cook spike. Editing a SOP can lock TD for seconds. Only change exposed controller values during the show.

### Save before every scene
Perform Mode doesn't save — if TD crashes, you lose your working state. Save (Cmd-S) frequently during soundcheck.

### Have a panic button
Keyboard shortcut → Python script → Level TOP opacity = 0 on master output. Gives you a dark screen if something goes wrong.

---

## Scene Patterns for Live

### Pattern — Cue stack
10 buttons on Launchpad, each a hard scene cut.
- Single Switch TOP indexed by MIDI button group.

### Pattern — Fader crossfade
Two Engine COMP scenes, Cross TOP between them driven by a fader.
- Gradual transitions.

### Pattern — Audio-locked auto-sequence
Timer CHOP advances through scenes on bar / phrase boundaries from Ableton Link.
- Set and forget — TD plays itself.

### Pattern — Manual effect overlay
Base scene + overlay layer.
- Overlay is driven by separate MIDI knobs — intensity, style, color.
- Fader = overlay opacity.

---

## Common Live Failures

- **Crash on scene change**: Engine COMP not pre-warmed. Pre-warm at load.
- **MIDI stops responding**: another app grabbed the device (Ableton can lock MIDI). Set exclusive mode in Audio MIDI Setup.
- **Audio cuts out**: Mac switched audio device. Pin device explicitly.
- **Framerate drops specific scene**: that scene wasn't optimized. Run `TD_WORKFLOW_OPTIMIZATION.md` on it.
- **Output is black at Perform Mode**: Window COMP → Monitor index wrong. Check display arrangement.
- **Projector shows wrong color**: colorspace mismatch. Ensure Window COMP + Render TOP colorspace is consistent with the projector's expectation (usually sRGB or Rec.709).

---

## Recording the Performance

### NDI / Syphon Out to a capture app
Send TD's output to a local capture app (OBS, Syphon Recorder) alongside Perform Mode.
- On Mac M1: Syphon Out path can be broken — verify.
- Backup: screen-capture the Perform Mode window.

### Movie File Out while performing
Record to disk simultaneously. Burns extra cook budget — only if the project has headroom.

---

## Multi-Display

### Mirror primary to all
All monitors see the same output. Mac System Settings → Displays → Mirror.

### Extended display
Each monitor gets a different Window COMP with a different TOP. Useful for multi-screen installations.

### Edge-blending / warping for projection
See `TD_WORKFLOW_PROJECTION_MAPPING.md`.

---

## Reading This File

Sequential read before first gig. Pre-Gig Checklist is the most important section — follow it. Controller section for picking/mapping hardware. Patterns for architecting scenes.
