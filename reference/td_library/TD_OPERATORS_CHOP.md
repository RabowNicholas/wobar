---
title: CHOPs — Channel Operator Catalog
version: 1.0
last_updated: 2026-04-16
status: live
scope: Every CHOP in TD 2025.32460. The time / control / audio pipeline.
dependencies: TD_LIBRARY_INDEX.md, TD_PATTERNS_AUDIO_REACTIVITY.md, TD_WORKFLOW_MIDI_OSC.md
---

# CHOPs — CHANNEL OPERATORS CATALOG

CHOPs are **channels of samples over time**. They carry audio, control signals, animation curves, timing, keyboard/mouse/MIDI/OSC input, and any numeric data the rest of TD needs.

**Core facts:**
- A CHOP has one or more **channels**, each a stream of samples.
- Sample rate is either the project cook rate (60 or 120 usually) or audio rate (44.1k/48k).
- CHOP chains are cheap individually; an Analyze CHOP or expression CHOP can be the expensive step.
- Null CHOPs are the endpoint convention — name every endpoint, reference from there.

---

## Audio I/O

### Audio Device In CHOP
Core Audio input on Mac.
- Params: Device (explicit, not Default), Sample Rate, Channels, Buffer Length.
- Use: BlackHole → Audio Device In → band split → visuals.
- On Mac: use explicit device name — "Default" changes when peripherals connect.

### Audio Device Out CHOP
Core Audio output.
- Params: Device, Sample Rate.
- Use: TD sends audio out (monitoring, generative audio).

### Audio File In CHOP
Plays an audio file as a CHOP stream.
- Params: File, Play, Cue, Speed, Loop, Volume.
- Use: pre-recorded tracks for offline rendering / music video export.

### Audio File Out CHOP
Records audio to disk.

### Audio Stream In CHOP / Audio Stream Out CHOP
Network audio I/O.

### Audio Play CHOP
Triggers audio playback on event — one-shot sound FX.

### Audio NDI In CHOP
Receives NDI audio.

---

## Audio Analysis

### Audio Filter CHOP
Frequency filter — LPF / HPF / BPF / Notch / Shelf / Peak.
- Params: Filter Type, Cutoff, Q / Filter Order, Gain.
- Use: isolate sub / mid / high before Analyze. Butterworth filter; increase order for sharper rolloff.

### Audio Spectrum CHOP
FFT — time-domain audio to frequency bands.
- Params: Window Length, Bins, Window Type.
- Use: frequency-domain analysis (which note is playing, spectral center, band energies).

### Audio Band EQ CHOP
Multi-band equalizer.

### Analyze CHOP
Reduces a CHOP to a summary statistic.
- Modes: RMS, Average, Max, Min, Peak, Median, Sum, Standard Deviation.
- Params: Input, Window (samples), Method.
- Use: Audio Filter → Analyze RMS → Lag = canonical envelope follower.

### Envelope CHOP
Extracts amplitude envelope — attack/release style smoothing.

### Beat CHOP
Detects beats / tempo from incoming audio.
- Params: Sensitivity, Min Tempo, Max Tempo.
- Use: auto-tempo sync when you don't have Link.

### Metronome CHOP (no dedicated op; use Beat + Ableton Link)
Canonical timing comes from Ableton Link CHOP.

### Audio Movie CHOP
Extracts audio from a Movie File In TOP / loaded movie.

---

## Timing / Animation

### Timer CHOP
Precise, scriptable timer.
- Params: Length, Cycle, Cue, Cycle Count, Goto, callbacks (onStart, onCycle, onDone).
- Use: timed segments, scripted countdowns, Perform-Mode state machines.

### Beat CHOP (timing use)
Provides beat pulses and tempo-based timing.

### Ableton Link CHOP
Ableton Link sync.
- Params: Enabled, Tempo, Quantum, Beat Phase.
- Use: visuals locked to Ableton / Serato / Link-aware apps.

### Clock CHOP
Outputs project clock values.

### LFO CHOP
Oscillating waveforms.
- Params: Type (sin, saw, tri, pulse), Frequency, Amplitude, Phase, Offset.

### Pattern CHOP
Generates parametric patterns (ramps, steps, sine, pulse, random, noise).
- Params: Type, Length, Frequency.
- Use: source for animation curves, instance position distributions.

### Keyframe CHOP / Animation CHOP
Author animation curves in TD.

### Wave CHOP
Generates specific waveforms with fine control.

### Countdown / Delay / Stopwatch — composed from Timer

---

## Channel Math

### Math CHOP
Per-channel or inter-channel math.
- Combines OP1–OP4 on Combine tab (Add/Mul/Max/Min/Avg/Diff/Subtract).
- Scalar math on Scalar tab (mult, add, gain, offset).
- Range remap via From Range / To Range tabs.
- **Use everywhere.** Most common CHOP after Null.

### Logic CHOP
Boolean logic on channels — AND / OR / XOR / NOT with thresholds.
- Use: trigger logic, gating.

### Function CHOP
Apply math functions (sin, cos, pow, exp, sqrt, abs, floor, ceil, fract, etc.).

### Expression CHOP
Python expression per channel.
- Use: **Avoid in per-frame paths**. Use Math/Logic first.

### Filter CHOP
Low-pass filter — smooths jitter.
- Params: Filter Type, Cutoff Frequency.
- Use: cheap smoother.

### Lag CHOP
Attack / release smoother.
- Params: Lag 1 (attack seconds), Lag 2 (release seconds).
- Use: the canonical "feels right" smoother for audio envelopes.

### Limit CHOP
Clamp values to a range.

### Trigger CHOP
Generates a pulse on rising edge.
- Params: Threshold, Pulse Length, Delay.
- Use: onset detection output into downstream event chains.

### Speed CHOP
Integrate velocity into position.

### Delay CHOP
Delay a signal by N samples/seconds.

### Threshold CHOP
Binarize signal at a threshold.

### Clip CHOP
Clip to range.

### Hold CHOP
Holds a value until re-triggered.

### Interpolate CHOP
Interpolates between values.

---

## Merging / Routing

### Merge CHOP
Combines multiple CHOPs — channels become concatenated.
- Params: How (Join Channels, Join Samples, Join Both).

### Shuffle CHOP
Rearranges channels — stacks, alternates, decimates.

### Rename CHOP
Renames channels by pattern.

### Select CHOP
Selects a subset of channels / references a CHOP by path.

### Delete CHOP
Removes channels matching a pattern.

### Reorder CHOP
Changes channel order.

### Pack CHOP
Combines multiple CHOPs into one, sample-by-sample.

### Switch CHOP
Switches between N inputs by index.

### Cross CHOP
Crossfades between two CHOPs.

### Blend CHOP
Weighted blend of multiple CHOPs.

### Null CHOP
Named passthrough — endpoint convention.

### In CHOP / Out CHOP
COMP I/O.

---

## Hardware Input

### Keyboard In CHOP
Keyboard key states as channels.

### Mouse In CHOP
Mouse position, buttons, wheel as channels.

### Joystick CHOP
Game controller input.

### MIDI In CHOP
Raw MIDI events (notes, CCs, pitchbend).
- Output: one channel per message type.
- Use when you need the raw stream.

### MIDI In Map CHOP
**Preferred MIDI input.** Maps incoming MIDI messages to named channels.
- Params: Device, Channel Prefix, Map Table.
- Learn mode: toggle "Active" and move a control — it auto-maps.
- Use: standard for controller integration.

### MIDI Event CHOP
Fires TD events on MIDI input.

### MIDI Out CHOP
Sends MIDI.

### OSC In CHOP
Receives OSC messages over UDP.
- Params: Network Port, Message Prefix, Target Address.
- Use: TouchOSC, Resolume OSC out, custom OSC apps.

### OSC Out CHOP
Sends OSC.

### TUIO In CHOP
Multi-touch protocol (usually via TouchOSC).

### Pipe In CHOP / Pipe Out CHOP
Low-latency inter-process CHOP transport.

### Serial CHOP
Serial port (Arduino, microcontrollers).

### DMX In CHOP / DMX Out CHOP
Lighting control.
- Use: Art-Net → Grand MA / other lighting controllers.

### Art-Net DMX CHOP
Art-Net protocol explicitly.

---

## Tracking / Sensing

### Kinect CHOP / Kinect Azure CHOP
Skeleton tracking. On Mac: use with Orbbec SDK.
- Outputs: joint positions, orientations, confidence per tracked body.

### Leap Motion CHOP
Hand tracking. Deprecated on Apple Silicon.

### Mediapipe CHOP (via plugin)
Hand / body / face landmarks on Mac GPU. **Preferred Mac body/hand tracking.**

### Camera Track CHOP
Tracks features in a video input.

### Face Track CHOP / Pose Track CHOP
Specific tracking use cases.

### ZED / RealSense CHOPs
Check Apple Silicon support before using.

---

## Network

### TCP In / Out CHOP, UDP In / Out CHOP
Raw network protocols.

### Web Server DAT bridge (via DAT to CHOP)
HTTP endpoint that updates CHOPs.

### Multi Touch In CHOP
TUIO / multitouch input.

### WebSocket In/Out (via DAT)
CHOPs bridge through DAT pipeline.

---

## Analysis / Data

### Info CHOP
Operator metadata as channels — cook time, frame, index, pixel count, etc.
- Use: drive logic from project state (frame number modulo, cook time threshold).

### Perform CHOP
Performance metrics — FPS, drops, GPU time.

### System CHOP
System-level data — time of day, date, uptime.

### Monitors CHOP
Connected displays — position, resolution.

### Window CHOP
Window-related metrics.

### CHOP to DAT
Converts a CHOP to a table.

### CHOP Execute DAT (bridge)
Calls Python when CHOP values change.

### Constant CHOP
Static channel values — the "literal" CHOP.
- Use: defaults, named thresholds.

### Limit CHOP, Clamp — see Channel Math.

---

## Sample-Rate / Time-Base Conversions

### Resample CHOP
Change sample rate.

### Retime CHOP
Time-stretch / compress.

### Stretch CHOP
Change duration without changing sample rate.

### Trim CHOP
Cut to a range.

### Extend CHOP
Define behavior beyond defined range — hold, loop, cycle.

### Fan CHOP
Reorder CHOP channels into sample slots.

### Sample CHOP
Resample at specified points.

### Copy CHOP
Replicate a channel.

---

## Pattern Generation

### Pattern CHOP — see Timing/Animation.
### Wave CHOP — see Timing/Animation.
### Noise CHOP
Generative noise channels (Sparse, Perlin, Random, Hermite).
- Use: organic driving signals.

### Constant CHOP — see Analysis/Data.

---

## Expression / Export

### Export CHOP (action, not operator)
Right-click parameter → Export CHOP sets a CHOP channel to drive that parameter.
- Fastest parameter-drive path.

### Replace CHOP
Replaces channels matching a pattern with values from another CHOP.

### Reorder / Rename / Shuffle — see Merging.

### Join CHOP
Concatenates samples end-to-end.

### Limit CHOP / Function CHOP / Math CHOP — see Channel Math.

---

## System / Meta CHOPs

### Perform CHOP — see Analysis.

### FIFO CHOP
Streaming first-in first-out buffer.

### Record CHOP
Captures CHOP input to memory / disk.

### Replace CHOP — see above.

### Lookup CHOP
Reads values from an input by indexing.

---

## TDAbleton CHOPs (via TDAbleton COMP)

Exposed inside the TDAbleton COMP, not as standalone CHOPs:
- AbletonTempo, AbletonTransport, AbletonClip, AbletonDevice, AbletonTrack.
- Use: read track state, clip launch, tempo, transport from Live.

---

## Canonical CHOP Chains

### Audio reactivity — band split + envelope
```
Audio Device In ──► Audio Filter (BPF 40Hz) ──► Analyze RMS (window 256) ──► Math (normalize) ──► Lag (0.02 / 0.15) ──► Null ("null_audio_sub")
              ├─► Audio Filter (BPF 800Hz) ──► Analyze RMS ──► Math ──► Lag ──► Null ("null_audio_mid")
              └─► Audio Filter (BPF 5kHz) ──► Analyze RMS ──► Math ──► Lag ──► Null ("null_audio_high")
```

### Onset detection
```
Audio Filter ──► Analyze RMS ──► Lag (fast) ──► Math (derivative) ──► Trigger (threshold) ──► pulses
```

### Tempo-synced animation
```
Ableton Link CHOP ──► Math (extract beat phase) ──► Function (sin) ──► Null ("null_beat_phase")
```

### MIDI controller into params
```
MIDI In Map CHOP ──► Math (scale) ──► Filter (smooth) ──► Null ("null_midi_X") ──► Export to param
```

### OSC from phone
```
OSC In CHOP (port 9000) ──► Rename (remap /1/fader1 → fader_1) ──► Null ──► drives params
```

### Keyboard shortcut
```
Keyboard In CHOP ──► Math (check specific key) ──► Trigger (pulse on press) ──► Execute DAT callback
```

---

## CHOP Sample Rate Considerations

- Audio CHOPs run at 44.1k / 48k — keep audio analysis at audio rate, then resample to project rate only at the end.
- Resample CHOP at the end of an audio analysis chain — produces one sample per cook, ready for export.
- Multi-sample CHOPs driving 10k instances: keep at project rate, 10k samples wide.
- Don't mix audio-rate and project-rate CHOPs before Resample — sample count mismatches cause weird behavior.

---

## CHOP Performance Notes

- Cheap: Math, Logic, Limit, Rename, Select, Null, Merge.
- Medium: Filter, Lag, Analyze (RMS/Mean).
- Expensive: Analyze with sort-based stats (Median), Expression CHOP, CHOP to DAT on large channels, Script CHOP.
- Audio File In at high polyphony with time-stretch enabled is costly — preload and avoid time-stretch where possible.

---

## Reading This File

Grep by CHOP name. Or jump to the section by role: Audio I/O, Audio Analysis, Timing, Channel Math, Routing, Hardware Input, Tracking, Network, Analysis, Patterns. For the pipeline shapes, see "Canonical CHOP Chains."
