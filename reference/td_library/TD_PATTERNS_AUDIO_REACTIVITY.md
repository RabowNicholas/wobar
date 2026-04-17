---
title: Audio Reactivity Patterns
version: 1.0
last_updated: 2026-04-16
status: live
scope: Recipes for audio-reactive visuals — band splits, envelopes, onset, spectral analysis, tempo sync.
dependencies: TD_LIBRARY_INDEX.md, TD_OPERATORS_CHOP.md, TD_WORKFLOW_LIVE_AUDIOREACTIVE.md
---

# AUDIO REACTIVITY PATTERNS

Every audio-driven visual in TD reduces to the same spine: **input → filter → analyze → smooth → route to parameters**. This file covers the canonical patterns at each stage and the variations that matter.

---

## The Canonical Spine

```
Audio Device In ──► Audio Filter (BPF) ──► Analyze (RMS) ──► Math (normalize) ──► Lag (smooth) ──► Null ──► [drives parameters]
```

Repeat per band. Three bands (sub / mid / high) is the minimum for musical responsiveness. More bands if the track benefits.

Reason this works: each stage solves one problem.
- Audio Filter: isolates the frequency region (kick, snare, vocals, hat).
- Analyze RMS: turns the waveform into an amplitude envelope.
- Math: normalizes so different tracks respond consistently.
- Lag: removes jitter; sets the feel.
- Null: named endpoint for downstream reference.

---

## Stage 1 — Input

### Live input (gigs)
```
Audio Device In CHOP — Device = BlackHole (or audio interface)
```
- On Mac, BlackHole is the bridge from Ableton to TD. See `TD_APPLE_SILICON.md` §4.
- Pick the explicit device by name, not "Default."

### Pre-rendered / music video work
```
Audio File In CHOP — File = /path/to/track.wav, Play = On
```
- Use WAV or AIFF for offline render. Lossless; no decode artifacts.
- Preload before timeline start to avoid first-frame hitch.

### Verification
Put a viewer on the Audio Device In / Audio File In. You should see channels moving with the source audio. If flat → no signal. See `TD_FOOTGUNS.md` §B1.

---

## Stage 2 — Frequency Split (Audio Filter CHOP)

Isolate the band you want to drive visuals with.

### Standard three-band split
| Band | Filter Type | Cutoff | Use |
|------|-------------|--------|-----|
| Sub | Band Pass | 40–80Hz | Kick impact, bass drop |
| Low Mid | Band Pass | 100–300Hz | Bassline, snare body |
| Mid | Band Pass | 400–2500Hz | Vocals, leads, melody |
| High | Band Pass | 2500–8000Hz | Hats, cymbals, vocal brightness |
| Air | High Pass | 8000Hz | Shimmer, air, high detail |

### Filter tuning
- **Filter Order**: 2 is default, 4 is sharper. Higher orders isolate more cleanly but add latency and CPU cost. 4 is the sweet spot for visuals.
- **Type**: Butterworth — flat passband, good rolloff.
- For truly sharp separation (e.g., isolating a synth lead from the kick), use FFT approach via Audio Spectrum CHOP instead of Audio Filter.

### Less-is-more pattern
```
Audio Device In ──► Audio Filter (BPF 60Hz, order 4) ──► ... ──► Null ("null_audio_sub")
```
Start with one band. Add more as the visual needs them. Don't split into 8 bands speculatively — half the bands will never be referenced.

---

## Stage 3 — Envelope Extraction (Analyze CHOP)

Convert the filtered waveform to a scalar amplitude over time.

### RMS (standard)
```
Audio Filter ──► Analyze CHOP (Method = RMS, Window = 256 samples)
```
- **Window = 256 samples** at 44.1k is ~6ms — fast enough for kick response, smooth enough to avoid jitter.
- **Window = 1024** for slower, musical content (pads, vocals).
- **Window = 64** for very snappy onset-style response.

### Peak (for onsets)
```
Audio Filter ──► Analyze CHOP (Method = Peak)
```
- Peak catches transients better than RMS.
- Pair with Trigger CHOP for onset detection.

### Alternative — Envelope CHOP
Specifically designed for amplitude envelope extraction with attack/release style smoothing.

---

## Stage 4 — Normalize (Math CHOP)

Audio levels vary wildly by track. Normalize so visuals respond the same whether the track is loud or quiet.

### Fixed scale
```
Analyze RMS ──► Math CHOP (Scalar tab: mult = 5.0, post-add = 0.0)
                     (Range tab: From Range 0–0.2 → To Range 0–1)
```
Use when you know the track's typical level.

### Auto-normalize (rolling max)
```
Analyze RMS ──► split:
  ├► Analyze (Max window 500 samples) ──► Lag (slow) ──► "running_max"
  └► direct
      ──► Math (divide direct by running_max) ──► clamp 0–1
```
The visual always hits 1.0 at the loudest recent moment.

### Normalize gotcha
Mastered tracks compressed hard have small dynamic range — normalizing makes everything 0.9+. Raise the reference floor before dividing, or use Peak analysis instead of RMS.

---

## Stage 5 — Smooth (Lag CHOP / Filter CHOP)

Raw envelopes are too twitchy. Smooth them until they feel right.

### Lag CHOP — standard
```
Math (normalized) ──► Lag CHOP
    Lag 1 (attack) = 0.02s (fast rise on hits)
    Lag 2 (release) = 0.15s (smooth decay)
```
- **Attack**: how fast the signal rises. 0.01–0.05 for kick-tight.
- **Release**: how slowly the signal falls. 0.1–0.5 depending on how much "glow" you want.

### Different feels
| Feel | Attack | Release |
|------|--------|---------|
| Snappy kick pump | 0.01 | 0.08 |
| Musical pulse | 0.03 | 0.2 |
| Atmospheric breath | 0.1 | 0.8 |
| Instant (glitch-style) | 0 | 0 (no lag) |

### Filter CHOP alternative
- Filter CHOP with low cutoff Hz smooths via low-pass.
- More predictable frequency-domain behavior; slightly less intuitive to dial in.

---

## Stage 6 — Route (Null + Export / Expression)

### Naming convention
Every audio endpoint is a Null CHOP named `null_audio_<band>`.
- `null_audio_sub`, `null_audio_mid`, `null_audio_high`, `null_audio_vocal`, `null_audio_rms_overall`.

### Export to parameter
Right-click parameter → Export CHOP. Cheapest drive path.

### Expression reference
Use when math is needed:
```python
op('null_audio_sub')['rms'][0] * 2.5 + 0.1
```

### DO NOT do this in 50 parameters
Consolidate the math into a CHOP chain, export a single Null channel. One read, many drives.

---

## Onset Detection

Triggering an event on every kick:

```
Audio Filter (BPF 60Hz) ──► Analyze RMS (window 64, fast) ──► Lag (attack 0.005, release 0.02)
                       ──► Math (derivative: current - 1-frame-delayed)
                       ──► Trigger CHOP (threshold 0.3, pulse length 0.05)
                       ──► Null ("null_kick_trigger")
```

Alternative via **Beat CHOP** — detects tempo + beats automatically:
```
Audio Device In ──► Beat CHOP ──► Null ("null_beat_phase")
```

### Using the trigger
- Export to Strength param of an effect (pulses brighten the visual on every kick).
- Drive Trigger → CHOP Execute DAT → Python callback for scripted events.

---

## Spectral Analysis (Audio Spectrum CHOP)

When you need per-frequency data (not just amplitude of a band):

```
Audio Device In ──► Audio Spectrum CHOP (Bins = 256, Window = 1024)
                 ──► Null ("null_spectrum")
```

Use cases:
- Drive 256 visual elements by their corresponding frequency bin.
- Detect specific pitch regions (e.g., vocal presence in 2kHz range).
- Paint a spectrogram.

Compose with:
- **Math CHOP** — scale the bin magnitudes.
- **Shuffle CHOP** — pick specific bins.

### Spectral waterfall pattern
```
Audio Spectrum ──► CHOP to TOP (each bin → pixel column, time → pixel row) ──► Feedback / scrolling ──► visual spectrogram
```

---

## Tempo Sync

### Beat CHOP — auto-detect tempo
```
Audio Device In ──► Beat CHOP
     Outputs: bpm, beat_phase (0–1 over one beat), bar_phase, pulse.
```
- Fast but can mis-detect at low volume or in busy tracks.

### Ableton Link CHOP — preferred when Ableton or Link-aware app is running
```
Ableton Link CHOP
     Outputs: beats, phase, bpm, enabled.
```
- Accurate, network-synced, adjustable quantum (bar length).
- Requires another Link peer on the LAN.

### Using tempo
- Drive an LFO CHOP's frequency from BPM: `bpm / 60` = beats per second.
- Trigger scene changes on bar_phase crossing.
- Quantize animation to musical divisions (quarter, eighth, triplet).

---

## Per-Song Calibration

Different tracks need different filter cutoffs and smoothing. Build a control COMP for per-song tuning:

```
Base COMP "audio_tuning"
  Custom Params:
    - Sub Cutoff (Hz)
    - Mid Cutoff (Hz)
    - Sub Lag Attack / Release
    - Sub Gain
  
  Audio Filter's cutoff param = me.parent().par.Subcutoff
  Lag CHOP's Lag1 param = me.parent().par.Sublagattack
  ...
```
Per track, adjust params in one place.

---

## Common Audio-Reactive Visual Mappings

### Brightness / glow intensity
`null_audio_sub` drives Level TOP gamma or Bloom intensity.

### Scale / size
`null_audio_rms_overall` drives Transform TOP scale — whole visual breathes.

### Color shift
`null_audio_high` drives HSV Adjust hue — treble shifts hue.

### Particle count / density
`null_audio_mid` drives POP Point Generator count or Sprinkle POP count.

### Camera shake
`null_audio_sub` drives Camera COMP translate offsets with small multiplier.

### Feedback decay
`null_audio_sub` inverse-drives Level TOP opacity in feedback loop — louder = longer trails.

### Noise amplitude
`null_audio_high` drives Noise TOP amplitude — treble adds detail/grain.

### Tunnel speed
`null_audio_sub` drives Transform TOP tz on feedback loop — bass pushes camera forward.

### Geometry displacement
`null_audio_mid` drives Noise SOP / Noise POP amplitude on a mesh — mid shakes geometry.

---

## Mac-Specific Gotchas

1. **Latency:** Core Audio + filters + analysis = 10–20ms end-to-end. If visuals feel behind, run a Lag on the visual side with negative offset (trick: drive animation from a time-shifted CHOP). See `TD_APPLE_SILICON.md` §4.
2. **Audio device switches:** plugging in headphones mid-session changes the default device. Pin the device explicitly.
3. **BlackHole bleed:** if monitoring through BlackHole without an aggregate device, you won't hear Ableton. Always run through an aggregate device for monitoring.
4. **Sample rate mismatches:** Ableton at 48k + TD Audio Device In at 44.1k → click / stutter. Match sample rates project-wide.

---

## Performance

- Audio Filter + Analyze + Lag chain is cheap.
- Audio Spectrum with large bin counts (>2048) gets expensive.
- One chain per band — don't duplicate Audio Device In per band; feed one input into multiple filters.
- Analyze CHOP with window > 4096 begins to impact cook time.

---

## Canonical Project Template

```
[Base COMP: audio_core]
  ├─ Audio Device In → Null ("null_audio_raw")
  ├─ Audio Filter (sub) → Analyze RMS → Math → Lag → Null ("null_audio_sub")
  ├─ Audio Filter (mid) → Analyze RMS → Math → Lag → Null ("null_audio_mid")
  ├─ Audio Filter (high) → Analyze RMS → Math → Lag → Null ("null_audio_high")
  ├─ Audio Filter (sub) → Analyze Peak → Trigger → Null ("null_kick_trigger")
  ├─ Ableton Link CHOP → Null ("null_link")
  └─ Audio Spectrum → Null ("null_spectrum")
```

Every scene COMP pulls from these `null_audio_*` names via Select CHOP or `op()` expression. One source of truth; consistent feel across scenes.

---

## Reading This File

Read Stage 1 through 6 once — that's the spine. Grep for specific operator patterns (onset, spectrum, tempo). For platform issues, see the Mac gotchas section.
