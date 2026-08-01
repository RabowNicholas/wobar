# RESEARCH — Master Chain Tool Capabilities

**Status:** temporary working doc. Capability research only — no chain design, no recommendations.
**Created:** 2026-08-01
**Scope:** The God Particle (Cradle), FabFilter Pro-MB, iZotope Ozone 12 Advanced.
**Purpose:** hold the understanding while the next research step runs. Retire or promote to `reference/` once chain decisions are made.

---

## Part 0 — Tool identities at a glance

| | God Particle | Pro-MB | Ozone 12 Advanced |
|---|---|---|---|
| Class | Opaque macro-processor | Transparent surgical engine | Full suite + analysis + AI assist |
| Philosophy | Taste, pre-decided | Precision, zero taste | Coverage + measurement |
| Controls exposed | ~6 | Everything | Everything, 21 plugins |
| Value | Consistency, removes choices | Exact intervention | Breadth + reference/metering |
| Cost | Can't fix one thing without moving all | Gives zero guidance | CPU, latency, decision overhead |

### Capability overlap

| Job | God Particle | Pro-MB | Ozone 12 |
|---|---|---|---|
| Broad tonal EQ | ±6 dB fixed curve only | none | Equalizer, Match EQ, Stabilizer |
| Dynamic EQ | hidden | yes, full control | Dynamic EQ, Spectral Shaper |
| Multiband comp | hidden, 3 targets | 6 bands, all exposed | Dynamics (4 bands) |
| Upward comp / expansion | no | yes (positive Range) | Impact, Unlimiter |
| Mid/side | no | per band | Equalizer, Imager, Dynamics |
| External sidechain | no | per band, own trigger range | limited |
| Saturation | baked in | none | Exciter, Vintage series |
| Stereo width | no | no | Imager |
| Limiting | yes, adaptive | yes (via ratio) | Maximizer IRC 5 |
| Stem-level intervention | no | no | Stem EQ, Master Rebalance, Stem Focus |
| Reference match / metering | no | no | Track Referencing, TBC, Codec Preview |

---

## Part 1 — The God Particle (Cradle)

Modeled on Jaycen Joshua's mix-bus chain. Clipper/saturation → EQ shaping → multiband compression → limiter, tuned as one unit. Stage order, thresholds, ratios, crossovers, time constants all hidden. Defaults = Joshua's actual settings, not a neutral state. Plugin is "on" the instant it's inserted.

### Controls

| Control | Range | Does |
|---|---|---|
| Amount | 0–200% | Master intensity + parallel blend. 100% ≈ 50% wet internally — parallel-blended under the hood, so "full" is already restrained. 200% = past designer intent. |
| EQ Low / Mid / High | ±6 dB each | Scales the baked-in curve. Fixed centers/shapes, not free EQ. |
| MB Comp targets Low / Mid / High | per-band amount | How hard each band leans into the baked compressor. No threshold/ratio/attack/release exposed. |
| Limiter | on/off + amount | Final catch stage, adaptive/program-dependent release. |
| Output / trim + meters | — | Level match in/out. |

### Boundaries

- **Cannot:** choose crossover frequencies, set attack/release, do mid/side, sidechain, linear phase, target LUFS, A/B against a reference.
- **Can:** impose a finished aesthetic — glue, density, top-end sheen, low control — in one move, identically across every track. Consistency is the actual feature.
- **Level-dependent, no auto gain-staging.** Same knob positions at −18 LUFS input vs −8 LUFS input = different processor. See Part 3 Test C.
- Non-transparent by design. Prints color even at low Amount.

**Mental model:** a decision, not a toolkit.

---

## Part 2 — FabFilter Pro-MB

### Architecture

Up to **6 freely-placed bands**. Bands may overlap, sit anywhere, or snap into a classic crossover system. Crossover steepness **6 → 48 dB/oct**.

### Per-band (Expert panel)

| Param | Notes |
|---|---|
| Threshold | Where band engages |
| **Range** | Signed. Negative = downward compression. Positive = expansion / upward compression. Flips band from compressor → expander → gate → upward comp. Also a hard cap on how far the band can move. |
| Ratio | Full range, incl. limiting |
| Knee | Variable, soft → hard |
| Attack / Release | Frequency-dependent intelligent curves |
| Lookahead | up to 20 ms |
| Output gain | Per band |
| Stereo Link | Variable %, not just on/off |
| Channel mode | Stereo / Left / Right / Mid / Side per band |
| External sidechain | Per band, **with its own trigger frequency range** — listens at one range, acts on another |

**Global:** dry/wet 0–200%, real-time analyzer with freeze, band solo/mute/bypass, output metering, 64-bit internal, sample-accurate automation, up to 4× linear-phase oversampling.

### What it can be configured into

Dynamic EQ · classic 3–4 band bus comp · de-esser · multiband upward compression · multiband gate/expansion · frequency-selective ducking off external source · mid/side band work · parallel band processing (100–200% wet).

### Boundaries

No saturation, no clipping, no widening, no loudness targeting, no metering beyond level/spectrum. Purely dynamics × frequency × stereo field.

---

## Part 3 — Ozone 12 Advanced

21 plugins, all loadable standalone in the DAW (Advanced only; Standard is mothership-only).

### Spectral / EQ
- **Equalizer** — 8 bands, digital/analog/baxandall, mid/side, per-band phase behavior
- **Dynamic EQ** — threshold-driven bands, mid/side capable
- **Match EQ** — 8,000+ bands; snapshots reference spectrum, generates matching filter; Amount + Smoothing
- **Stem EQ** *(new, Advanced)* — source separation applied to EQ; EQs vocals/drums/bass/instruments separately inside a finished stereo file
- **Stabilizer** — adaptive real-time EQ toward a target shape; 25 new genre targets in 12
- **Spectral Shaper** *(Advanced)* — fast per-frequency-region taming, faster than static EQ

### Low end
- **Bass Control** *(new, Advanced)* — dedicated LF shaping/balancing across playback systems. First of its kind in Ozone.
- **Low End Focus** *(Advanced)* — punch vs smooth contour on sub/low band

### Dynamics
- **Dynamics** — up to 4-band comp/limit/gate, detection filter, transient/RMS detection
- **Impact** — 4-band microdynamics; expands or contracts dynamic contrast rather than peaks; bidirectional
- **Unlimiter** *(new, Advanced)* — inverse limiting; restores transients on over-squashed source
- **Maximizer** — IRC 5 new in 12, alongside IRC I–IV + Transient/Modern

### Stereo
- **Imager** — up to 4-band width, stereoize, vectorscope + correlation meter
- **Master Rebalance** *(Advanced)* — separation for level; change drum/bass/vocal volume inside a stereo file
- **Stem Focus** *(Advanced, improved nets in 12)* — routes any other module to act on one separated stem only

### Color
- **Exciter** — multiband harmonic generation, several saturation flavors, post-filter
- **Clarity** — polish/loudness-oriented processing
- **Vintage Tape / Compressor / Limiter / EQ** — analog-modeled, coarser and more colored

### Analysis / QC (mostly Advanced)
- **Master Assistant** with Custom flow
- **Tonal Balance Control** — spectrum vs genre/reference targets, links to Ozone/Neutron EQ
- **Track Referencing** — level-matched A/B, per-module target matching
- **Codec Preview** — audition as MP3/AAC at 8 resolutions
- **Dithering** — MBIT+ with noise shaping
- **A/B on every module** *(new in 12)*
- Metering: LUFS-I/S/M, true peak, LRA, dynamics, spectrum, spectrogram
- **Relay** — bonus utility plugin

### Boundaries
Module order free but chain lives in one host. CPU heavy; latency varies by module. Separation modules are neural — artifacts at extreme settings.

---

## Part 4 — Maximizer / IRC decoded

### Limiter fundamentals

Limiter applies **negative gain over time** so peaks never exceed ceiling. Character comes from how it builds the gain envelope:

- **Detection** — where it looks for peaks (broadband / per-band / lookahead window)
- **Release shape** — how gain returns, and whether speed varies by frequency/program
- **Distortion allowance** — how much waveform truncation before it chooses envelope movement instead

Fast release = louder, more distortion + IMD. Slow release = cleaner, pumping, less loud.

### Topology

| Control | Function |
|---|---|
| Threshold | Drives signal into limiter. Lower = more GR = louder. The loudness knob. |
| Ceiling | Output cap. Delivery spec, not a sound control. |
| Character | Release shaping; behavior differs per mode |
| Stereo Independence | 0% = L/R linked (identical GR). 100% = independent. Advanced splits into separate **transient** and **sustain** values. |
| Transient Emphasis (IRC IV) | How much the limiter respects transient peaks. Higher = punch kept, less loudness. |
| True Peak toggle | Sample-peak → inter-sample peak detection. Costs oversampling/CPU/latency. |
| GR meter | If it never returns toward 0, that's continuous gain reduction, not limiting. |

Threshold and Ceiling are independent with auto gain compensation — easy to over-limit without noticing.

### Modes

- **IRC I** — Adaptive release with frequency awareness. Fast on transients (no pumping), slow on steady bass (no LF distortion). Cleanest, least loud.
- **IRC II** — IRC I optimized for transient preservation; transients sharper under aggressive limiting.
- **IRC III** — Psychoacoustic model sets limiting speed per moment. Four character styles constraining release: *Clipping* (loudest, most distortion), *Pumping* (slow, deliberate breathing), *Crisp* (fast, transient-forward), *Balanced*. First mode where you choose an artifact rather than avoid one.
- **IRC IV** — Dozens of psychoacoustically spaced bands. Limits **only the bands contributing most to each peak** → drum transients limited without ducking vocals. Kills intermodulation. Most transparent at high GR; highest CPU/latency.
- **IRC 5** (Ozone 12) — Newest. Internals unpublished. Treat as the IRC IV lineage pushed further; A/B against IRC IV rather than assuming it's strictly better.
- **Modern** — Fast, clean, contemporary-loud; Character sets release speed directly.
- **Transient** — Punch preservation prioritized over loudness.

### Stereo Independence

- Linked (0%): peak in L pulls both channels. Image solid, less loud. Center content (kick/sub/vocal) unaffected either way.
- Independent (100%): louder, but a hard-panned peak ducks only that channel → **image pulls the other way for that instant**.
- Advanced splits transient vs sustain because independence is usually fine on transients and destructive on sustains.

### True peak

Samples are points; the DAC reconstructs the curve between them, and that curve can exceed the highest sample. A master at −0.1 dBFS can hit **+0.5 to +1.5 dBTP** after reconstruction, worse after lossy encode. ITU-R BS.1770-4 requires ≥4× oversampling to measure. True Peak mode limits the reconstructed peak.

### What to measure
GR depth (avg and peak) · PLR change · mode A/B **at matched loudness** (otherwise louder always wins).

---

## Part 5 — Pro-MB phase modes, physically

A filter delays some frequencies more than others = **group delay**. Group delay varying with frequency = waveform shape changes even when magnitude response is correct. Every band split is a filter, so the crossover itself is a sound.

### Minimum Phase
Analog behavior. Phase rotates around each crossover, group delay varies, **zero latency**.
- Transient energy smeared **forward in time** — natural, matches physical systems, ear tolerates it
- Bands don't sum phase-flat through the crossover → classic multiband glue, and classic low-mid buildup/scoop at crossover points
- Steeper crossover = more phase rotation concentrated there

### Linear Phase
Symmetric FIR. **Constant group delay across all frequencies**, no phase distortion, bands sum perfectly.

Costs:
- **Latency** ≈ half the filter length. LF accuracy needs long filters → a linear-phase crossover at 80 Hz is expensive in ms.
- **Pre-ringing.** Symmetric impulse response puts ringing *before* the transient. Physically impossible in nature; ear has no masking template for it.

Audible where: **low frequency + high transient content.** Kick attack, 808 onset, snare crack. Reads as blur/ghost in front of the hit — attack loses its edge from silence. Bass music is the worst case.

Wins where: overlapping/parallel band processing · M/S that must recombine cleanly · crossover-point coloration unacceptable · dragging crossover frequencies live.

Pro-MB adds up to 4× linear-phase oversampling on top.

### Dynamic Phase (FabFilter proprietary)
- **Zero latency**
- **No static phase change** — band isn't filtering when it isn't gain-reducing; plugin is transparent at rest
- **No pre-ringing** — no symmetric FIR involved
- Phase behavior only appears as gain changes

Read: an idealized analog EQ that only exists while working. Why Pro-MB in Dynamic Phase with one narrow band is the canonical dynamic-EQ tool — the band acoustically vanishes when the problem isn't present.

### Crossover steepness
- **6–12 dB/oct** — heavy overlap, natural, gain change leaks broadly. Tonal shaping.
- **24–48 dB/oct** — near-surgical isolation, more phase rotation (min phase) or longer filters (linear phase). Problem removal, worse glue.

### Self-test for pre-ring
Solo one kick. Process with linear phase, heavy band, low crossover. Zoom the waveform to sample level, inspect the 20 ms **before** the transient. Ripple = pre-ring. A/B vs Dynamic Phase at matched loudness.

---

## Part 6 — Reverse-engineering The God Particle

Turns opinion into a spec sheet. Highest-value item on the list: no chain decisions about an unmeasured black box.

### Kit
- **Plugin Doctor** (Ddmf) — automated magnitude/phase, THD spectrum, IMD, dynamic response, transfer curve. ~80% of this list in one pass.
- Ozone analyzers — **Match EQ as a curve-capture device** (computes the input→output difference curve directly)
- Pro-MB analyzer with freeze
- Free: SPAN, Voxengo Curve EQ, null-test utility, oscilloscope plugin

### Protocol

**A — Latency + true bypass.** Duplicate track, one clean / one GP at Amount 0. Time-align, invert, null. Nulls → Amount 0 is true bypass. Doesn't null → the residual is what it does at zero. Record the sample delay.

**B — Static EQ curve vs Amount.** Pink noise at −20 dBFS RMS (low enough that dynamics barely engage). Capture output spectrum at Amount 0/25/50/100/150/200, EQ flat, comp targets minimum. Diff vs input → **the baked curve and how it scales**. Repeat with each EQ knob at +6 / −6 to isolate that band's center, Q, shape.

**C — Level dependence / transfer curve.** *(Run this first.)* Same pink noise at −30/−24/−18/−12/−6 dBFS RMS. Plot input RMS vs output RMS — the bend gives **effective threshold and ratio of the whole chain**. Plot output spectrum at each level; if the curve changes with level, the "EQ" is partly dynamic. GP has no auto gain-staging, so it is a different processor at every input level.

**D — Crossover frequencies.** Narrowband/sine bursts at 40 / 80 / 160 / 320 / 640 / 1.25k / 2.5k / 5k / 10k Hz, high level. Move **one** comp target knob at a time, diff output. Responding frequencies map the band edges.

**E — Time constants.** 1 kHz tone burst (100 ms on / 400 ms off) well over threshold. Output envelope: rise to steady GR = attack; recovery slope = release. Repeat at 60 Hz and 8 kHz — differences reveal frequency-dependent band time constants.

**F — Harmonic + intermodulation distortion.** 1 kHz sine at −18/−12/−6 dBFS; read the harmonic series. Even-order (2nd, 4th) = tube-flavored; odd-order (3rd, 5th) = console-flavored. Log THD% vs Amount. Twin-tone 19 kHz + 20 kHz → energy at 1 kHz = IMD. Repeat 41 Hz + 8 kHz to see how sub content muddies the top.

**G — Stereo behavior.** Correlation + M/S analysis pre/post. Process a mono file — non-mono output means it's doing stereo work. Sum output to mono, compare against processed-then-summed for mono compatibility (club playback).

**H — Amount law.** Build a manual 50/50 blend of dry + GP-at-200%. Null against GP-at-100%. Nulls → blend law confirmed exactly at every position.

### Output
One-page spec: EQ curve per Amount · threshold/ratio · crossovers · attack/release per band · THD/IMD profile · latency · mono behavior.

---

## Part 7 — The three target-curve systems

### Match EQ — static snapshot
Captures long-term average spectrum of a reference and yours, generates the difference as an 8,000+ band filter. Controls: Amount, Smoothing.
- Static. Set once, never adapts.
- **Failure mode:** matches the reference's *arrangement*, not its tone. A busier-midrange reference makes it carve your midrange even when yours is correct. Low smoothing + high amount = you inherit the reference's resonances.
- Best used as a diagnostic that draws a curve you then simplify by hand.

### Stabilizer — adaptive, real-time
Continuously analyzes and applies a **moving** EQ toward a target shape. Tames resonances that come and go. Speed/smoothing set tracking aggression. 25 new genre targets in 12.
- Dynamic process, not a curve. Correction at bar 8 ≠ bar 40.
- **Failure mode:** can't tell your character from your problem. Deliberate resonant sub or signature harsh top gets flattened toward the mean. Aggressive = spectrally average, anonymous master.

### Tonal Balance Control — measurement only
No processing. Shows your spectrum against genre target **ranges** (bands, not lines) or a custom reference. Can remote-control linked Ozone/Neutron EQ nodes.
- Zero risk. **Failure mode:** genre targets are wide averages — inside the band proves nothing, outside isn't automatically wrong.

### Master Assistant
Analyzes source, picks target, **builds a chain** (EQ moves, dynamics, exciter, maximizer mode + threshold). Advanced's Custom flow takes intent (reference track, vintage/modern, loudness target). Read *which* modules it enabled and *how hard* — that's a diagnosis of your source.

---

## Part 8 — Dynamics vocabulary (shared layer)

Makes Pro-MB legible; makes GP's hidden values guessable.

### Detection
- **Peak** — instantaneous, catches transients, twitchy
- **RMS** — averaged energy, follows perceived loudness, ignores spikes
- **Detection/sidechain filter** — what the detector hears ≠ what gets processed. High-passing the detector stops kick/sub driving GR on everything. Pro-MB extends this: per-band external sidechain with its own trigger frequency range.

### Core five

| Param | Meaning | Watch |
|---|---|---|
| Threshold | Where processing begins | Meaningless without gain staging |
| Ratio | dB in : dB out above threshold | 2:1 shaping · 4:1 control · 10:1+ limiting · ∞ brickwall |
| Knee | dB-wide transition into the ratio | Soft = ratio ramps in across the knee. Soft knee + low ratio ≈ inaudible leveling |
| Attack | Time to ~63% of target GR | Fast kills transient punch; slow passes transient, compresses body |
| Release | Return time | The character control; sets pumping rate |

### Release vs tempo
**140 BPM:** 1 beat = 428 ms · 1/8 = 214 ms · 1/16 = 107 ms.
Release near a subdivision breathes *with* the groove; between subdivisions it fights the groove. Same release value is musical at one tempo, wrong at another.

### Range (Pro-MB)
Signed cap on band movement. Negative = downward comp, positive = expansion/upward. Unusual property: set an aggressive ratio and still guarantee the band never moves more than N dB.

### Four quadrants

| | Loud material | Quiet material |
|---|---|---|
| **Turn down** | Downward compression (standard) | Downward expansion / gating (noise, tails) |
| **Turn up** | Upward expansion (punch back — Ozone Impact) | Upward compression (density up, noise floor up) |

Pro-MB reaches all four via Range sign + ratio.

### Lookahead
Delays audio while the detector runs ahead → attack can be effectively negative, GR already in place when the transient arrives. Pro-MB up to 20 ms. Costs latency equal to lookahead.

### Stereo link %
100% = one GR value both channels, image never moves. 0% = independent, louder, image shifts on hard-panned events. Pro-MB gives the full range per band.

### Frequency-dependent time constants
FabFilter scales attack/release by band center — 10 ms on a 60 Hz band and a 10 kHz band give musically equivalent, not numerically identical, results.

**Most important low-end rule:** a 60 Hz wave is 16.7 ms long. An attack faster than one cycle rewrites the waveform, not its envelope — that's distortion, not compression. Sub-bass cannot be compressed faster than its own period without generating harmonics.

### Reading a GR meter
- Returns to 0 between events → limiting / peak control
- Constant value → static gain reduction (you're just turning it down)
- Never reaches 0, moves ±1 dB → leveling
- Slams deep and crawls back → pumping (may be intentional)

---

## Part 9 — Clipping vs limiting, distortion budget

### Mechanical difference
- **Limiter** = envelope processor. Multiplies signal by time-varying gain. Waveform intact, level moves. Artifacts: pumping, ducking, IMD from gain modulation.
- **Clipper** = waveshaper. Truncates the waveform at a ceiling. **No envelope movement** — nothing pumps or ducks. Artifacts: harmonic distortion proportional to waveform removed.

Consequence: a clipper taking 3 dB off a kick transient costs a few percent THD **for 2 ms**, nothing else moves. A limiter taking the same 3 dB pulls the whole mix down for its release duration.

### Hard vs soft
- **Hard clip** — instantaneous ceiling, sharp corner, rich odd-order harmonics, aliasing unless oversampled. Audible as edge.
- **Soft clip** — gradual curve into ceiling, lower-order harmonics, less loudness gained per dB.

Clipping generates harmonics above Nyquist that fold back as **aliasing** — inharmonic and ugly. 4×+ oversampling on any clipper is standard.

### Audibility rule
Clipping only short, sparse, high-crest transient peaks is near-inaudible even at several dB. Clipping **sustained** content — especially sustained low frequency — is immediately audible as grit, because a sub wave is a long smooth curve and flattening it is a large structural change.

### Intersample peaks
Clipped waveforms are full of sharp corners → HF content → reconstruction overshoots between samples. A file at −0.1 dBFS sample peak can be **+1 to +3 dBTP**. Lossy encoders add their own reconstruction error on top. Hence −1.0 dBTP standard delivery ceiling, −1.5 to −2.0 for heavily clipped masters.

### Where loudness comes from in bass music
Sub content carries most of the energy — a 40 Hz sine at −6 dBFS dwarfs a hi-hat at −6 dBFS. So:
- Limiter GR is almost entirely driven by the low end
- Mono, tightly controlled sub with no kick/808 phase cancellation raises loudness before any limiter
- Transient clipping ahead of the limiter unloads it — limiter then handles only sustained material and stops ducking on every kick

### What these tools have

| Tool | Clipping capability |
|---|---|
| God Particle | Baked-in, hidden, non-adjustable. Test F measures amount + order. |
| Pro-MB | None. Zero waveshaping. Purely envelope. |
| Ozone 12 | No dedicated clipper module. Closest: Maximizer IRC III "Clipping" style, Vintage Limiter, Exciter, Vintage Tape. |

### Distortion budget
Every colored stage adds harmonics and they accumulate. Order changes result: saturating *before* limiting means the limiter reacts to the harmonics; clipping *after* limiting means the clipper sees a dense signal with no crest left to remove cheaply.
**Measure it:** 1 kHz sine through the full chain, read total THD, then remove one stage at a time. One stage usually contributes most of it.

---

## Part 10 — Metering and delivery

### LUFS variants

| Meter | Window | Reads |
|---|---|---|
| LUFS-M | 400 ms | Instantaneous, jumpy |
| LUFS-S | 3 s | Section-level. Most useful while working. |
| LUFS-I | whole program | The delivery number. Gated. |

**Gating:** integrated LUFS uses an absolute gate at −70 LUFS plus a relative gate 10 LU below the ungated mean. Silence and quiet intros excluded, so loud sections dominate — exactly what streaming normalization keys on.

### LRA
Statistical spread of short-term loudness (~10th–95th percentile). Classical 15+ LU; modern electronic often 3–5 LU. Low LRA isn't a fault. Most useful as a **change** metric: master LRA 2 LU below mix LRA tells you what the chain cost.

### Crest metrics — the real squash readout
- **PLR** = True Peak − LUFS-I, whole track. 14+ = dynamic, 6–8 = heavily limited.
- **PSR** = short-term peak − LUFS-S, moment by moment. Best single-number read on *where* dynamics died.

### True peak
≥4× oversampled per ITU-R BS.1770-4. Sample peak ≠ true peak. Always meter true peak for delivery.

### Platform normalization, 2026

| Platform | Target LUFS-I | Boosts quiet tracks? |
|---|---|---|
| Spotify | −14 | Yes |
| Apple Music | −16 | Yes |
| YouTube | −14 | No — turns down only |
| Tidal | −14 | No |
| Amazon Music | −14 | No |
| **SoundCloud** | −14 | — |
| Deezer | −15 | — |

Convergence follows the AES TD1008 recommendation.

### The implication
**Playback loudness is no longer under your control.** A −6 LUFS master and a −14 LUFS master play at the same perceived volume on Spotify — the −6 just arrives with transients gone, PLR collapsed, and 8 dB of limiter artifacts baked in, for zero loudness advantage.

Loudness still buys something: on turn-down-only platforms (YouTube/Tidal/Amazon) a quiet master stays quiet; in non-normalized contexts (DJ playback, club, local files, some embeds); and as perceived density/impact — which is **not** LUFS and can be built with saturation and microdynamics instead of limiter depth.

### Codec survival
Lossy encoders discard and reconstruct — output waveform ≠ input, peaks higher. **Codec Preview** auditions MP3/AAC at 8 resolutions pre-export. First to break: cymbals/hats (pre-echo), and anything already clipping (encoder overshoot). Ceiling −1.0 dBTP standard; −1.5 to −2.0 for loud/clipped.

### DJ / club regime
Separate axis from streaming. No normalization. CDJs and mixers have their own limiters and headroom. Club systems expose sub phase problems and mono-compatibility issues headphones hide. Both regimes matter for WOBAR delivery.

---

## Part 11 — Latency, PDC, CPU, print order

### Latency sources

| Source | Typical |
|---|---|
| Linear-phase filtering | Large; grows as target frequency drops |
| Lookahead (Pro-MB) | Exactly the lookahead value, ≤20 ms |
| Oversampling (2×/4×) | Filter latency per stage |
| True-peak limiting | Oversampled detection latency |
| Neural separation (Stem EQ, Master Rebalance, Stem Focus) | Highest in the suite |

### PDC doesn't fix
Live monitoring (40 ms chain = unplayable) · some cross-bus sidechain timing · latency changes mid-session (switching phase mode changes latency and can glitch some hosts).

### CPU, heaviest first
1. Neural separation modules
2. Linear phase at high quality
3. 4× oversampling on anything
4. IRC IV / IRC 5 Maximizer
5. Multiple Pro-MB instances in linear phase
6. Everything else

### Offline vs realtime
Should be sample-identical for deterministic plugins. Watch analysis-dependent modules, plugins with randomization/modeled noise, and hosts that change buffer size offline. Null-test a realtime capture against an offline bounce **once per template**, then trust it.

### Sample rate
Filter behavior, oversampling headroom, and limiter temporal resolution all change with SR. A limiter at 96 kHz has finer time resolution than at 44.1; masters can measure differently after SRC. Pick a project rate and stop moving it.

### Committing / printing
Locks in what you heard (plugin updates can't change a finished master) · enables null-testing each stage · removes latency and CPU from the session.

### Float gain staging caveat
32/64-bit float means intermediate stages can't clip — headroom is unbounded until the final fixed-point file or converter. **But** any level-dependent plugin (God Particle, Vintage modules, any saturation) responds to absolute level. "0 dBFS doesn't clip" and "the plugin sounds different at every level" are both true at once. Part 6 Test C is the one to run first.

---

## Measurement kit — install before deciding anything

- Plugin Doctor (Ddmf) — black-box analysis
- SPAN or any free FFT analyzer — always-on spectrum
- True-peak + LUFS + PSR meter (Ozone's own, or Youlean-class)
- Null-test utility
- Reference tracks, level-matched
- Test signals: pink noise at several RMS levels · sine sweep · tone bursts · twin tones · one isolated kick

---

## Sources

- [Ozone Maximizer / IRC modes — iZotope docs](https://docs.izotope.com/ozone10/en/maximizer/index.html)
- [Mastering with Ozone: Limiting — Splice](https://splice.com/blog/mastering-with-ozone-8-limiting/)
- [Ozone 12 Advanced — iZotope](https://www.izotope.com/products/ozone-advanced)
- [Ozone 12 release — Synthtopia](https://www.synthtopia.com/content/2025/09/06/izotope-ozone-12-now-available/)
- [Ozone 12 three new modules — Magnetic Magazine](https://magneticmag.com/2025/09/izotope-releases-ozone-12-advanced-with-three-new-modules/)
- [FabFilter Pro-MB](https://www.fabfilter.com/products/pro-mb-multiband-compressor-plug-in)
- [LUFS targets per platform 2026 — Forasoft](https://www.forasoft.com/learn/audio-for-video/articles-audio/lufs-targets-per-platform-2026)
- [Streaming LUFS targets 2026 — Mat Leffler-Schulman](https://matlefflerschulman.com/mastering-articles/loudness-targets-and-mastering-for-streaming-platforms)
- [Cradle The God Particle review — MusicTech](https://musictech.com/reviews/plug-ins/cradle-the-god-particle-review-a-grammy-winning-mix-bus-chain-in-a-simple-package/)
- [The God Particle review & tutorial — bchillmusic](https://bchillmusic.com/the-god-particle-plugin-review-mixing-tutorial/)

---

**Open / unverified**
- IRC 5 internals unpublished — treat as IRC IV lineage until A/B'd
- God Particle internal values all unmeasured — Part 6 protocol not yet run
