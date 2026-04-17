---
title: MIDI & OSC Workflow
version: 1.0
last_updated: 2026-04-16
status: live
scope: MIDI In/Out and OSC In/Out — controller wiring, phone apps, external software integration, mapping patterns.
dependencies: TD_LIBRARY_INDEX.md, TD_OPERATORS_CHOP.md, TD_OPERATORS_DAT.md, TD_WORKFLOW_LIVE_VJ.md
---

# MIDI AND OSC WORKFLOW

Getting control signals into and out of TD. MIDI for hardware controllers; OSC for phones, iPads, and cross-app communication.

---

## MIDI — Core Operators

### MIDI In Map CHOP (recommended)
- Automatically detects all incoming MIDI notes/CCs on a device and exposes as channels.
- Channel names are human-readable: `n1`, `n2`, `c1`, `c7`, etc.
- **The primary way to get MIDI in.**

Setup:
```
MIDI In Map CHOP:
  - Device: "Akai APC40 mkII" (or other device name)
  - Map Type: Note On, CC, or All
  - Source: Note / CC / Program
```

### MIDI In CHOP (more manual)
- Specify exact channel numbers.
- Useful when MIDI In Map is adding unwanted channels.

### MIDI Out CHOP
- Send MIDI notes/CCs to a device.
- Useful for RGB feedback on Launchpad / APC.
- Set device, specify channel/note/value/velocity.

### MIDI Event DAT
- Every MIDI event as a log row.
- Useful for debugging or driving script triggers.

---

## Recognizing MIDI Devices on Mac

### Audio MIDI Setup (Mac)
Application → Utilities → Audio MIDI Setup → Window → Show MIDI Studio.
- Lists all connected MIDI devices.
- If TD doesn't see a device, it usually isn't here either.

### TD MIDI device panel
Dialogs → MIDI Device Mapper. Confirms what TD sees.

### Common device names
- "Akai APC40 mkII"
- "Akai APC40"
- "Launchpad X"
- "Launch Control XL"
- "Ableton Push 2"

Copy exactly what Mac reports — device name is case/space-sensitive in TD.

### USB issues on M1
- Some MIDI controllers require a powered USB hub (Launchpad X draws power).
- USB-C dongles sometimes fail — use Apple-branded or known-good.
- If a controller disappears mid-session, unplug/replug usually works.

---

## Reactive vs Event MIDI

### Continuous (CCs)
Knobs and faders send CCs constantly as they move. Wire as a CHOP channel.
```
MIDI In Map → c1 channel (0–127)
  → Math CHOP (scale to 0.0–1.0) → Lag CHOP (smooth) → Named Null
```

### Discrete (Notes)
Buttons and pads send note-on / note-off. Wire as a trigger:
```
MIDI In Map → n60 channel
  → On press = 127, release = 0
  → Logic CHOP (threshold 1) → Trigger CHOP (edge) → pulse
```

Or for toggle: Count CHOP with Reset on second press.

### Velocity-sensitive pads (Launchpad X)
```
Note pressure is on the note's value (1–127). Use directly:
  → amplitude of a burst effect = velocity / 127
```

---

## MIDI Output — RGB Feedback

### Launchpad X color feedback
```
MIDI Out CHOP:
  - Device: Launchpad X
  - Send note-on with velocity = color index
  - Each note value (pad position) × velocity (color) sets pad color
```

Launchpad X uses specific SysEx for full RGB. For basic colors, velocity 1–127 maps to the built-in palette.

### APC40 MK2 feedback
Similar — CC values drive track strip colors; note values light pad LEDs. Exact mapping is in Akai's docs.

### Reason for feedback
- Visual indication that a scene is active on the controller.
- Scrubbing feedback when a fader moves.
- State sync when software changes state externally.

---

## OSC — Core Operators

### OSC In CHOP
Receives numeric OSC messages.
- Port: usually 9000 or 7000.
- Protocol: UDP.
- Exposes OSC paths as channel names (e.g., `/accxyz/x` → `accxyz_x`).

### OSC In DAT
Receives OSC messages as rows in a DAT.
- Path, type tags, arguments per row.
- Useful for string-based or mixed-type OSC.

### OSC Out CHOP
Sends numeric channels as OSC messages.
- Target: IP address + port.
- Channel name becomes OSC path.

### OSC Out DAT
Send arbitrary OSC messages from a table.

---

## OSC from Phone — TouchOSC / OSC/PILOT / Lemur

### TouchOSC (most common)
- iOS/Android app.
- Design custom control layouts (buttons, faders, XY pads).
- Send to Mac IP + port (e.g., 9000).

Setup:
```
Phone TouchOSC: connect to same WiFi, send to MacIP:9000
TD: OSC In CHOP, port 9000
  → channels = TouchOSC control paths (e.g., /1/fader1)
```

### OSC/PILOT
- Desktop OSC controller (free for basic).
- Handy for testing before a phone setup.

### Phone accelerometer / gyro
- TouchOSC can send device orientation as OSC.
- Shake your phone → OSC channel → drives a visual parameter.

---

## OSC for Cross-App Communication

### TD ↔ Resolume
```
TD OSC Out → Resolume port (e.g., 7000)
TD sends /composition/layers/1/clips/1/connect 1 → triggers a clip in Resolume
```

### TD ↔ Max
```
TD OSC In on port A
TD OSC Out on port B → Max listens on port B
```

Bidirectional.

### TD ↔ Processing / openFrameworks
Same OSC pattern. Standard protocol across creative coding tools.

### Local loopback
OSC within the same machine: use `127.0.0.1` as target IP. Low latency.

---

## Mapping Patterns

### Global Control COMP (repeated from `TD_WORKFLOW_LIVE_VJ.md`)
```
Base "controls"
  ├─ MIDI In Map CHOP (APC40)     → Null "apc40"
  ├─ MIDI In Map CHOP (LCXL)      → Null "lcxl"
  ├─ MIDI In Map CHOP (Launchpad) → Null "launchpad"
  ├─ OSC In CHOP (phone)          → Null "osc"
  ├─ Keyboard In CHOP             → Null "keyboard"
  │
  ├─ Math / Filter / Lag CHOPs    → smoothing and scaling per input
  ├─ Switch / Merge CHOPs         → combine or pick active source
  │
  └─ Named Nulls: master_intensity, scene_index, crossfade, etc.
```

Every scene reads from Named Nulls only. No MIDI or OSC ops inside scene COMPs.

### Absolute vs Relative controllers

**Absolute**: knob position = value. Every controller jump is a real value jump.
- Problem: switching scenes with different values, the physical knob position doesn't match stored value → first touch causes a sudden jump.

**Relative**: knob sends +1 or -1 per click, TD integrates.
- Avoids the jump problem.
- Launch Control XL, APC40 both support relative mode for some controls.

**Pickup mode in TD**: a control's incoming value is ignored until the knob passes the stored value. Then it "picks up" and follows.
- Implement with Logic CHOP: output the MIDI value only when `abs(midi - stored) < threshold`, then use it directly thereafter.

### Scene-aware mapping (same knob, different meaning per scene)

```
Global CC knob → Switch CHOP indexed by active_scene_index
  → Each output goes to a scene-specific Null
```

Same physical knob = different param per scene.

### Banks / pages
Bank buttons toggle which logical mapping is active.
```
Bank button pressed → Switch index (0/1/2) → different Null routings per bank
```

Gives you 3× the control surface on the same hardware.

---

## Keyboard Input

### Keyboard In CHOP
- Per-key CHOP channel (1 when pressed, 0 released).
- Use for lock-and-hold buttons.

### Panel COMP with keyboard shortcut
- Panel COMP can trigger Python callback on specific key.
- Script can change scene, reset timeline, trigger effects.

### Keyboard DAT
- Logs every key event with timestamp, useful for debug.

---

## Common MIDI/OSC Patterns

### Pattern — Fader smoothing
```
Fader → MIDI In Map → Math (÷127) → Lag CHOP (attack 0.02, release 0.05) → Named Null
```
- Tactile response without jitter.

### Pattern — Button toggle
```
Button → MIDI In Map → Trigger CHOP (edge detect) → Count CHOP (modulo 2) → Null
```
- Each press flips state 0/1.

### Pattern — 4-step cue stack
```
4 buttons → MIDI In Map → 4 Trigger CHOPs → Index → Named Null "cue_index"
```
- Each button is a cue position.

### Pattern — XY pad
```
OSC In CHOP from /xy → x, y channels → drive two params independently
```
- Phone XY pad controls X/Y parameter pair.

### Pattern — Pattern modulation with MIDI
```
Knob → sensitivity factor
Pattern CHOP at knob-controlled rate → drives an animation
```

### Pattern — MIDI-to-trigger-sequence
```
MIDI note-on → Trigger CHOP → Timer CHOP fires with delays →  parametric fade/sweep
```

---

## OSC Servers and Clients

### OSC In as a server
TD is a server on port 9000 — phones/apps connect to TD.

### OSC Out as a client
TD sends messages to another OSC server (Ableton, Resolume).

### OSC reflect/echo server
Run a tiny OSC server in a DAT Script DAT that logs every incoming message. Debug tool.

---

## Debugging MIDI/OSC

### MIDI In not working
1. Check Audio MIDI Setup shows the device.
2. Check MIDI In Map CHOP's Device name matches exactly.
3. Check no other app has grabbed exclusive access (Ableton can).
4. Check the MIDI Event DAT — are events arriving?

### OSC In not working
1. Check phone and Mac are on same WiFi/subnet.
2. Check Mac firewall allows the port.
3. Use OSC In DAT first to see if messages arrive at all.
4. Check OSC Out on phone side — target IP and port match.

### Latency on OSC
- WiFi adds 5–50ms of jitter.
- Over Ethernet: <1ms.
- For real-time performance control: use MIDI or Ethernet, not WiFi.

### MIDI feedback loop
If MIDI Out loops back to MIDI In (same device), you get feedback → device stays lit, or values oscillate. Be careful when sending pad colors not to trigger the pad's own input.

---

## Device Priority for Nick

For an AV set with Ableton + TD + phone:
- **Launch Control XL**: 24 knobs + 8 faders = global visuals params (intensity, color, effect depth).
- **Launchpad X**: 64 pads = scene launching + effect triggers.
- **APC40 MK2**: transport + macro (or skip if LCXL + Launchpad cover it).
- **Phone (TouchOSC)**: backup + floating control for off-stage tweaks.

Plus Ableton's own hardware (Push 2 or similar) dedicated to the music, not touched for visuals.

---

## Reading This File

For hardware wiring: §MIDI Core Operators + §Recognizing MIDI Devices. For OSC: §OSC Core Operators + §OSC from Phone. §Mapping Patterns is the architecture — one source of truth is critical. §Common MIDI/OSC Patterns is recipe form. §Debugging is the checklist when things aren't responding.
