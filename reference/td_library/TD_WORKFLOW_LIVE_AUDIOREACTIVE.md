---
title: Live Audio-Reactive Workflow
version: 1.0
last_updated: 2026-04-16
status: live
scope: Live performance with a real Ableton session — Link tempo sync, TDAbleton, BlackHole routing, latency compensation, per-song calibration.
dependencies: TD_LIBRARY_INDEX.md, TD_PATTERNS_AUDIO_REACTIVITY.md, TD_APPLE_SILICON.md, TD_WORKFLOW_LIVE_VJ.md
---

# LIVE AUDIO-REACTIVE WORKFLOW

Performing with a live Ableton session feeding TD. The audio-reactive spine from `TD_PATTERNS_AUDIO_REACTIVITY.md` is reused — this file handles the live-session specifics: tempo sync, routing, latency, and per-song prep.

---

## The Live Challenge

Pre-rendered audio is predictable. A live Ableton session is not:
- Tempo changes mid-set (Nick's set may span 120→140 BPM).
- Arrangement is fluid — a build might run 8 or 32 bars.
- DJ fades, filters, and live FX change the audio content.
- Latency is real — 5–50ms between Ableton → visuals.

**Strategy: use Link for tempo, audio analysis for amplitude/onsets, and accept that "reactive" is 90% amplitude-mapped, 10% beat-locked.**

---

## Audio Routing — Ableton → TD (Mac)

### BlackHole 2ch / 16ch (the standard)
BlackHole is a virtual audio device that lets one app output audio and another app capture it on Mac. Free, M1-native.

```
Ableton master → Audio Output = BlackHole 16ch
TD Audio Device In CHOP → Input Device = BlackHole 16ch → analysis chain
```

### Multi-Output Device for monitoring
You want TD to receive the audio AND hear it through speakers. Create a Multi-Output Device in Audio MIDI Setup:
- Include BlackHole 16ch + the speaker/interface.
- Set Ableton's master output to the Multi-Output Device.
- TD captures from BlackHole while the speakers hear the speaker output.

### Latency consideration
- BlackHole latency is negligible (~1ms).
- Audio Device In CHOP processing latency adds 5–20ms depending on buffer.
- Visual rendering adds 16ms at 60fps.
- Total audio-to-visual latency: 20–50ms, usually perceptible on beats.

See §Latency Compensation below.

### Alternative — interface loopback
Some audio interfaces (RME, UA, Motu) have hardware loopback. Routes audio out of DAW back into an input channel at hardware level.
- Lower latency than BlackHole.
- Reliable, no software layer.

---

## Tempo Sync — Ableton Link

### What Link does
Ableton Link CHOP gives TD exact tempo + beat phase + bar phase from any Link-enabled app on the network.

### Setup
```
Ableton: Preferences → Link/Tempo/MIDI → Link = On
TD: Add Link CHOP to project
  - Channels: tempo, beat, phase, numPeers
```

Within 1–2 seconds, TD shows `numPeers = 1` and tempo matches Ableton. If not, check firewall (Link uses UDP multicast).

### Using Link channels
- **tempo**: current BPM. Scale animations to it: `speed = op('link')['tempo'][0] / 120`
- **beat**: beat number since Link session started (monotonic float).
- **phase**: 0.0–1.0 position within current beat.
- **barphase**: 0.0–1.0 position within current bar (requires quantum).

### Per-beat triggers
```
Trigger CHOP (input = Link phase):
  - Trigger at phase wraparound (phase resets 1.0 → 0.0 each beat)
  → pulse on every beat
```

Or a Logic CHOP: `phase < 0.1` → on for first 10% of each beat.

### Per-bar triggers
```
Logic CHOP: barphase < 0.1 → on at bar start
```

Set Link CHOP's Quantum to 4 for 4/4 bar tracking.

---

## TDAbleton

### What it is
Deeper integration than Link — exposes Ableton session data (tracks, clips, parameters, MIDI notes) to TD via Max For Live devices that ship with TD install.

### Install
1. Locate TDAbleton MaxForLive devices in TD install: `TouchDesigner.app/Contents/Resources/tdAbleton/`.
2. Drop TDA Master.amxd on Ableton's master track.
3. Drop TDA Send.amxd on any track to send that track's info to TD.
4. In TD: drop tdAblMaster COMP → it connects to the Master device via a known port.

### What you get
- Per-track volume, pan, send levels as CHOP channels.
- Clip slot triggers.
- Scene triggers.
- MIDI note events per track.
- Tempo, transport state (play/stop).

### Use cases
- Track volumes as visual intensities. When the "drums" track is hot, drums are visible.
- Clip launches as scene triggers. Launching clip 3 on master triggers scene 3 in TD.
- Device parameter tie-ins: a filter cutoff in Ableton drives a TD noise parameter.

### Performance cost
TDAbleton Master COMP pulls all this data — adds ~1–3ms cook time. Usually fine.

### On M1
TDAbleton works; verify for your specific TD build. If issues, fall back to Link + audio analysis — covers 80% of the use cases.

---

## Audio Analysis in Live Context

### Reuse the spine from TD_PATTERNS_AUDIO_REACTIVITY.md
6-stage chain: input → band split → analyze → normalize → smooth → route.

### Additional for live
- **Auto-normalization matters more**: a set's average loudness varies. Auto-gain keeps the reactivity alive for quiet breakdowns and loud drops.
- **Wide dynamic range smoothing**: use Lag CHOP with different attack/release for drops vs build-ups.
- **Per-band sensitivity**: some songs are bassy, some are airy. Either auto-calibrate or have per-song scenes with tuned sensitivity.

### Fallback for broken audio
If audio cuts out during set (Mac glitch, Ableton freeze), the entire analysis chain goes to zero and visuals go dead. Mitigation:
- Trigger CHOP with `held` = True on the audio stream → holds last known good value for N seconds.
- Automation fallback: if audio is silent > 2 seconds, drive from a sine/noise generator until audio returns.

---

## Latency Compensation

### The problem
By the time TD receives an audio onset and renders a visual, the drop has already hit. Audience sees visual 40–50ms late.

### Approaches

**A. Ignore it (usually fine)**
- 30–40ms is within human tolerance for audio-visual sync, especially for ambient / atmospheric reactive visuals.
- Most FSC audience won't consciously notice.

**B. Predict via Link**
- For tempo-locked visuals, Link phase is always-on — no analysis latency. Use Link phase to drive beat-locked effects. Only use audio analysis for the "above tempo" layer (drums, FX, color).

**C. Compensate via time offset**
- Add a Delay CHOP to your audio signal for the reactivity.
- Wait, no — that delays more. You can't un-delay.
- Instead: pre-analyze a looped audio file for tempo sections and play along. Not live.

**D. Early-trigger with buffer**
- Some live systems use a small audio buffer on the analysis side. TD Audio Device In has a Delay parameter.
- Set to negative in effect — analyze ahead by reducing total pipeline latency.

**E. Visual lag-forward**
- Design visuals to lead the audio: a flash that "anticipates" the kick. Not truly leading — but stylistically fine on repeated patterns.

**In practice: accept the latency, tune Lag CHOP to not exaggerate it, use Link for tight-sync moments.**

---

## Per-Song Calibration

### The problem
Every song has different dynamics. A single reactivity setting doesn't work for a 90-minute set.

### Solutions

**Solution 1 — Scene per song**
- Each song = dedicated TD scene with its own params.
- Cue via MIDI button or scene trigger on song change.
- Most reliable, most work.

**Solution 2 — Adaptive normalization**
- Analyze CHOP with auto-range over long window (30s).
- Normalize: `audio_level - rolling_min` / `rolling_max - rolling_min`.
- Adapts to the current song's dynamic range.

**Solution 3 — Global sensitivity knob**
- One controller knob = master reactivity gain.
- Tweak per song on the fly.
- Less tight, but zero prep.

**Recommendation for FSC sets: Solution 2 baseline + Solution 3 override.**

---

## Live Scene + Audio Pipeline

### Architecture
```
Global Controls COMP
  ├─ Link CHOP → Null "link"
  ├─ Audio Device In CHOP → full audio analysis chain → Named Nulls (null_sub, null_mid, null_high)
  ├─ MIDI In Map CHOP → Null "controller"
  └─ Table DAT "scene_params" → per-scene overrides

Each Engine/Scene COMP pulls:
  - Link for tempo
  - null_audio_* for reactivity
  - Controller knobs for manual
  - Scene-specific params from Table DAT
```

### Why centralize
One analysis chain, N scenes. Swap audio source (BlackHole → live mic → pre-recorded track) by changing one device.

---

## Latency Measurement

Before committing to a latency value, measure it:
1. Play a known transient (claps or drums) in Ableton.
2. TD runs a Record CHOP capturing audio + a visual "latest analyzed level" signal.
3. Compare transient timestamps.

Or simpler: put your hand on a kick in front of the visual output. If the kick flash hits obviously late, latency is >60ms and intolerable.

---

## Live Performance Tips

### Don't do per-frame Python
See `TD_WORKFLOW_LIVE_VJ.md` — Python in cook path is a crash risk. Audio analysis should be CHOP chains.

### Pre-warm the analysis chain
At project load, play 5 seconds of pink noise into Ableton → analysis chain runs → ranges are initialized. Otherwise first 5 seconds of performance have cold-start artifacts.

### Ableton export record as backup
In Ableton, record your master output to disk simultaneously. If TD crashes mid-set, you have a clean audio record and can re-run the set with recorded audio later for video export.

### Test the full chain
- Ableton playing
- TD receiving
- Visuals animating
- Output to projector
- Over the PA

A day before gig. Not at doors.

---

## Common Live Audio Failures

### Audio cuts out in TD, still plays on PA
Multi-Output Device failed on Mac. Cycle through: System Settings → Sound → cycle device → re-select Multi-Output.

### TD cooks audio chain but visuals don't move
Gain too low — check analysis CHOP `rms` actual value in Null. If <0.001, bump Audio Device In Gain or add a Math CHOP with multiply = 10.

### Link says numPeers = 0
Firewall blocking UDP multicast. Mac System Settings → Privacy & Security → Firewall → allow TD + Ableton. Or disable firewall for the gig.

### Tempo drifts
Link handles drift; but if both TD and Ableton are "leading," you get a tug-of-war. Let one lead. In Link settings, pick one app as the "tempo host."

### Ableton hiccup = visual freeze
Audio stops flowing, analysis → 0, visuals die. Fallback to silent-mode trigger as in §Fallback for broken audio.

### Reactivity feels laggy/weak
- Lag CHOP's release is too slow. Drop attack to 0.02, release to 0.15.
- Sensitivity too low. Bump Math multiplier or auto-normalize.
- Pipeline latency too high. Lower Audio Device In buffer size.

---

## Per-Track Audio Signal Paths (TDAbleton)

If using TDAbleton with per-track sends:

```
Ableton "drums" track → TDA Send device → TD receives drums channel as CHOP
Ableton "synth" track → TDA Send device → TD receives synth channel
```

Now TD can animate "drum visuals" from the drums channel alone, even if everything is mixed into the master.

Advantage: visual separation per element, not possible from a single master signal.

---

## Reading This File

If you're using BlackHole + audio analysis only: read §Audio Routing and §Audio Analysis in Live Context. If you're adding Link: add §Tempo Sync. If you want track-level data: read §TDAbleton. §Latency Compensation is for any live setup. §Common Live Audio Failures is a cheat sheet for debugging during soundcheck.
