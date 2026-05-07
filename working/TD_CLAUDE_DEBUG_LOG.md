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
| 2026-04-26 | Set `geometryCOMP.par.instanceop = chop` for position-based instancing | Single instance only (or no instances) — `instanceop` is the legacy/SOP-based "default instance OP" par. Position channels (instancetx/ty/tz) require their channel source to come from `instancetop`. | Confused `instanceop` (legacy SOP-default) with `instancetop` (channel source for translates). Already documented in Act 2 vortex reference network but not in central debug log. | Use `geo.par.instancetop = chop_or_top` for translate-source. Set `geo.par.instancecountmode = 'oplength'` so count derives from the CHOP. Channel name pars `instancetx/ty/tz = 'tx'/'ty'/'tz'`. | other |
| 2026-04-26 | Created `geometryCOMP` programmatically and assumed it was empty | TD auto-creates a default `torus1 (torusPOP)` child with render=True. Anything you put inside renders **alongside** the torus — and the torus is much larger, so it dominates the frame as a giant white blob. | Hidden default behavior — invisible when building in UI (you see the torus immediately) but easy to miss when building via Python. | Immediately after `parent.create(geometryCOMP)`: `geo.op('torus1').destroy()` (or set its `.render = False`). Verify with `for c in geo.children: print(c.name, c.render)`. | other |
| 2026-04-26 | Used `absTime.seconds` inside a `scriptCHOP` onCook callback and assumed the CHOP would recook every frame | Script CHOP cooks once and caches — the callback's reference to `absTime.seconds` doesn't establish a TD time-dependency. Output stays frozen at the first cook's value; downstream (e.g. instance positions) appears static. | Time references inside Python callbacks are not auto-tracked as TD dependencies the way expression-mode parameters are. | Wire a time-dependent CHOP into the script CHOP's input so it has a reason to recook each frame. Pattern: a `constantCHOP` with `par.value0.expr = 'absTime.seconds'` and `mode = ParMode.EXPRESSION`, connected to script CHOP input[0]. Constant CHOP itself is auto time-dependent because of the absTime expression. | other |
| 2026-04-26 | Inside scriptCHOP onCook, used `me.storage['state'] = ...` and tried to read it externally via `script_chop.storage['state']` | `me.storage` from inside an OP's callback DAT refers to the **DAT's** storage, NOT the operator the callback is attached to. So state went to the callback DAT's storage; the script CHOP's own `.storage` stayed empty. | Confused which `me` is in scope inside a callback DAT — it's the DAT, not the operator wired to use it. | To persist per-OP state from a callback DAT: use `op('relative_or_absolute_path').storage[...]` explicitly to pin to the desired OP. To inspect from outside: read the CALLBACK DAT's `.storage`, not the operator's. Verify with `print(list(me.storage.keys()))` from inside vs `list(target_op.storage.keys())` from outside. | other |
| 2026-04-26 | Assumed `compositeTOP` accepts 3+ input slots when operand=Add | compositeTOP exposes only 2 input connectors (`inputConnectors[0]` and `[1]`); accessing `inputConnectors[2]` raises `IndexError: list index out of range`. The "blends N inputs" idea applies to its operation, not the connector count. | Conflated TD's compositeTOP with classic node-graph multi-input compositors. | For 3+ source layers: chain compositeTOPs (out of comp_a feeds into comp_b alongside the next layer), or use a `MultiCompositeTOP` if available, or layer via Over/Add chains. Sketch: `comp1 = src + layer1; comp2 = comp1 + layer2; comp3 = comp2 + layer3; ...`. | other |
| 2026-05-04 | Set par expression `'1.5 + 0.15 * sin(absTime.seconds * 2 * math.pi * 0.1)'` on a TOP parameter | `NameError: name 'sin' is not defined` — TD parameter expressions don't auto-import `sin`/`cos`/etc. into namespace, only `math` and `tdu` modules are accessible. Bare `sin()` doesn't resolve. | Confused TD parameter expression namespace with general Python scope where `from math import *` would have made `sin` global. | Always use `math.sin()`, `math.cos()`, `math.pi` (and `math.tau` if needed) in parameter expressions. Pattern: `<base> + <amp> * math.sin(absTime.seconds * 2 * math.pi * <freq_hz>)`. | expressions |
| 2026-05-04 | Set `circleTOP.centerx=0.5, centery=0.5` to place a black-pupil mask at frame center (with `centerunit=fraction`) | Circle rendered in upper-right corner of frame instead of centered. `centerx/y` with `centerunit=fraction` (and `justifyh/v=center`, the default) is an OFFSET from the justify anchor, NOT an absolute position. So 0.5, 0.5 nudged the circle by half the resolution in each axis. | Confused fraction-coords with normalized 0-1 absolute coords (e.g. like rampTOP keys). | For a centered shape with center-justify (default), set `centerx=0, centery=0`. Default values are already 0,0 — leave alone unless deliberately offsetting. Only set non-zero if you want an offset from the justify anchor. | other |
| 2026-05-04 | Set `circleTOP.radiusx=radiusy=0.3` with `radiusunit=fraction` expecting a true circle on a 720×1280 frame | Rendered as a tall oval (radius_x = 0.3 × 720 = 216px, radius_y = 0.3 × 1280 = 384px). `fraction` mode is anisotropic — radius is interpreted independently per-axis as fraction of width/height. | Forgot that `fraction` mode treats x and y separately on non-square frames. The default `fractionaspect` would have aspect-corrected. | For a true circle: use `radiusunit='fractionaspect'` (default — fraction of larger/smaller dim depending on TD), OR `radiusunit='pixels'` with explicit pixel count. `'fraction'` is for when you specifically want anisotropic radius scaling. | other |

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
