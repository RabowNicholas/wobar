---
title: TD Claude Debug Log
version: 1.0
last_updated: 2026-04-15
status: live
scope: Log of every instance where Claude gave wrong TouchDesigner technical advice in a WOBAR session. Future Claude sessions must read this before any TD build or advice to avoid repeating confirmed failures.
---

# TD CLAUDE DEBUG LOG

This file logs every confirmed case where Claude gave incorrect TouchDesigner advice — wrong parameter names, wrong operator types, wrong architecture, wrong assumptions. It is not a general knowledge base. Every entry is a real failure from a real session. Read it before any TD build. If your planned action matches a past failure, use the corrected pattern instead and cite the entry.

---

## Failure Log

| Date | Wrong advice Claude gave | Actual TD behavior | Root cause | Corrected pattern | Tag |
|------|--------------------------|-------------------|------------|-------------------|-----|
| 2026-04-14 | Used `filterCHOP` for frequency band extraction | `filterCHOP` is a smoothing/interpolation filter — has nothing to do with audio frequencies | Confused name similarity: "filter" sounded right for audio filtering | Use `audiofilterCHOP` with `par.filter='bandpass'`, `par.units='frequency'`, `par.cutofffrequency` | audio |
| 2026-04-14 | Set `analyzeCHOP` `function='average'` on highpass filter output | HP filter output is bipolar (positive and negative samples) — averaging cancels out to ~0, giving a useless flat signal | Assumed `average` was the general RMS equivalent; didn't account for signal polarity | Use `function='rmspower'` for any chain coming out of a highpass filter. Bandpass output works with `average` because it produces a unipolar envelope | audio |
| 2026-04-15 | Pointed `moviefileoutTOP` `audiochop` at `null_audio` (the analysis CHOP) | `null_audio` runs at project cook rate (30 fps), not 44100 Hz — TD error: "Audio CHOP sample rate must be 44100" | Assumed `null_audio` was the audio output because it's named "audio"; it's actually the analysis channel bundle | Point `audiochop` at the raw `audiofileinCHOP` (e.g. `audio_in`) which runs at 44100 Hz. Analysis CHOPs are not audio streams | export |

---

## Recurring Themes

### audio
Failures related to audio pipeline construction, operator selection, and signal analysis.
- `filterCHOP` ≠ frequency filter — always use `audiofilterCHOP`
- HP filter output is bipolar — always use `rmspower` in `analyzeCHOP`, never `average`
- Analysis CHOPs (null_audio, band outputs) are not audio streams — they run at cook rate, not 44100 Hz

### export
Failures related to recording and render output setup.
- `null_audio` is an analysis CHOP at rate 30, not an audio waveform — use the source `audiofileinCHOP` for `moviefileoutTOP` audiochop

### feedback
*(No entries yet — append as confirmed)*

### GLSL
*(No entries yet — append as confirmed)*

### twozero
*(No entries yet — append as confirmed)*

### expressions
*(No entries yet — append as confirmed)*

### other
*(No entries yet — append as confirmed)*
