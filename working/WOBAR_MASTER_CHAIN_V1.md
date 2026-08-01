# WOBAR Master Chain — v1

**Created:** 2026-08-01
**Status:** live template. Starting values, not settled answers.
**Companions:** `RESEARCH_MASTER_CHAIN_TOOLS.md` (tool capabilities) · `RESEARCH_MASTERING_EDM_DUBSTEP.md` (practice research)

---

## Purpose

A simple, repeatable mastering chain Nick can run on every track without per-track deliberation. Target is ~90% of a professional result. A pro mix/master engineer gets hired later; this exists to improve the catalog now.

Every value below is chosen so that **when it's wrong, it's wrong safely.** The Range cap, linked stereo, low GP Amount and modest limiting all bound how bad a wrong guess can get. That's the governing design principle — not optimality, but bounded error under compromised monitoring.

---

## Constraints this was designed under

These justify the settings. If a constraint changes, revisit the chain.

| Constraint | Consequence |
|---|---|
| **Monitoring: KRK Rokit 5 G4 + ATH-M50x, untreated room** | Honest floor ~54 Hz (KRK is −10 dB at 43 Hz). Genre's defining band, 20–50 Hz, is inaudible. Both devices are bass-forward and treble-forward, so cross-checking them cannot catch a shared bias |
| **Two playback contexts, weighted equally: streaming + large system** | Needs harmonic reinforcement for phones *and* mono/phase integrity for systems |
| **System access exists, outside the studio** | Feedback loop is available but high-latency. Desk decisions must be pre-formed; system trips are for validation |
| **Vinyl/dubplate: not applicable** | Digital release only. Cutting constraints ignored |
| **Loudness: de-prioritized** | Work to short-term, let integrated fall out. No loudness chasing |
| **Jason Goz weighted up** | Take his *loop* (render → real system → revise) and his *permission* (distortion is legitimate in this genre). Do not take his meter-hostility — that rests on monitoring Nick doesn't have |
| **Sub dynamics (resolved)** | Flatten note-to-note · protect within-note envelope · constant sub ceiling with section contrast built above the sub band |
| **Mixes are Nick's own** | Anything the chain struggles with is fixable upstream at no cost. Master follows mix |

---

## The chain

```
1. Trim / gain      →  fixed input level. Set once.
2. God Particle     →  character. Amount low.
3. Pro-MB           →  one sub band. Set once, leave it.
4. Ozone            →  Imager → EQ → Exciter → Maximizer
```

Per track, only two things get touched: **Ozone EQ (0–2 broad moves)** and **Maximizer threshold**. Everything else is template.

---

# Stage 1 — Trim

**What it is:** a plain volume control before anything else. Gain/utility plugin or clip gain.

### Setting
**Loudest section reads −16 LUFS Short-Term. Peaks under 0 dBFS.**

**How:** loudness meter on the master → play the biggest 10 seconds → adjust trim until Short-Term reads −16.

### Why
- God Particle was built for mix buses. A normal unmastered mix's loudest section sits around −16 to −14 LUFS-S — the level its designers tuned it at.
- **The number matters less than its constancy.** GP changes behavior with input level: louder in means more compression, a different EQ curve, a different processor. If input level wanders track to track, nothing downstream is repeatable.
- Pinning the level doesn't make GP predictable. It makes it *consistent*, which is enough to build on.

This is the least glamorous step and the one that keeps everything else honest.

---

# Stage 2 — God Particle

**Position: first**, immediately after trim.

Reasons: its input level is controlled by Stage 1 · everything after it is corrective, so you're always fixing a known thing · keeps its hidden limiter away from Ozone's Maximizer.

## Amount: 35%

**What it does:** blends the whole processed chain against dry. 100% on the dial is only ~50% wet internally — restraint is built in by design.

**Why 35%:** GP's default is tuned for commercial pop/R&B mix buses — denser and brighter than deep 140. At 35% you get roughly a third of something already halved. Enough for glue and top-end sheen; not enough to overwrite the mix.

**The bypass test — how to know you're right:**
- Bypass sounds **broken** → too high
- Bypass changes **nothing** → too low
- Bypass sounds **slightly flatter, less finished** → correct

This is the test for the whole chain, not just this stage. Mastering should make bypass sound unfinished, not make engaged sound different.

## EQ Low / Mid / High: 0 (flat)

**What they do:** scale a tone curve baked into the plugin. They don't create EQ, they multiply an existing shape.

**Why flat:** the shape is unmeasured. Scaling an unknown curve produces an unpredictable result, and part of it lands in frequencies that are inaudible on this rig.

**Exception:** if every track wants the same move here, that's a mix issue, not a mastering one. Fix upstream.

## Comp targets — Low: minimum · Mid / High: ~25%

**What they do:** how hard each region hits the built-in compressor.

**Why Low at minimum:** it acts on 20–90 Hz — inaudible on this rig — with unknown time constants. Pro-MB does that job two stages later, properly and with a safety cap. **Two uncontrolled compressors on the same band is the worst configuration in the chain.** Give the job to the one that can be steered.

**Why Mid/High low but present:** this is where GP's glue lives, and it's the region that can actually be judged here.

## Limiter: off if it defeats

Ozone's Maximizer is the final limiter. Two limiters in series each doing a little is less controllable than one doing the job — and GP's is invisible.

If it can't be defeated, 35% Amount keeps it barely engaged.

## Output: match bypass level

**Critical.** Louder always sounds better. If engaged is 1 dB louder than bypassed, GP will seem to improve the track whether or not it does. Bypassed and engaged must read the same Short-Term LUFS before any A/B is meaningful.

---

# Stage 3 — Pro-MB

**What a multiband compressor does:** splits audio into frequency slices and turns down whichever slice gets too loud, independently of the others.

**The one job here:** sub notes are not equally loud — a 40 Hz and a 55 Hz note carry different energy at the same velocity. This evens them.

**Why it matters:** DJs set channel gain by the loudest moment. One hot sub note means the whole track gets gained down, so mids and highs arrive weak next to the previous record.

## One band. No others.

| Setting | Value | What it does | Why this value |
|---|---|---|---|
| **Band range** | 20–90 Hz | Which slice this band controls | 20 low: nothing musical below. 90 high: keeps kick body out — include the kick and the sub ducks on every kick hit, which is not the goal |
| **Phase mode** | **Dynamic Phase** | How the band is split off | Linear Phase splits perfectly but smears a faint ghost *before* the kick attack — the one artifact bass music can't afford. Dynamic Phase avoids it, adds no delay, and is transparent when the band isn't working |
| **Crossover slope** | 24 dB/oct | Sharpness of the band edges | Isolated enough that touching sub doesn't touch kick body; not so steep it's surgical |
| **Ratio** | 2.5:1 | How hard it squeezes past the line | Low ratio = evening out. High ratio = hard ceiling. Evening out is the goal |
| **Range** | **−3 dB** | Hard cap on maximum gain reduction | **The safety belt.** This band is inaudible here. If threshold is wrong, worst case is 3 dB — noticeable, not destructive. Uncapped, a wrong threshold could pull 10 dB out of the sub undetected |
| **Attack** | 30 ms | Reaction speed | A 40 Hz wave takes 25 ms per cycle. Faster than one cycle reshapes the wave itself rather than its volume — that's distortion, not compression. **Arithmetic, not taste** |
| **Release** | 200 ms | Recovery speed | At 140 BPM a 1/8 note is 214 ms. 200 ms recovers with the groove rather than against it |
| **Stereo link** | 100% | Both channels move together | Sub is mono anyway; independent movement would wobble the image |
| **Lookahead** | 0 | Reacting slightly early | Unnecessary for leveling, and it adds latency |
| **Threshold** | **1–2 dB GR** on loudest sub notes | The line signal must cross | Play the biggest section, lower threshold until the meter reads 1–2 dB, stop. 6 dB means a leveler has become a squasher |

**Set once, leave across tracks.** Per-track tuning of an inaudible band is guessing.

**If the GR meter moves on every kick:** the kick has energy inside the band. Narrow to 25–70 Hz or raise the threshold.

---

# Stage 4 — Ozone

## a. Imager

**Setting: band 1 crossover at 120 Hz, width 0 (full mono).**

**What it does:** collapses everything below 120 Hz to dead centre.

**Why 120 Hz:**
- Below ~100–120 Hz direction is not localizable by ear — stereo down there gives nothing
- Club subwoofers sum to mono regardless
- Stereo content down there can **cancel** on summing — the "huge at home, gone on the system" failure
- Not lower (80): leaves 90–110 exposed where cancellation still bites
- Not higher (300): collapses the bass's body and character, losing width worth keeping

**Check:** correlation meter near +1.

## b. Equalizer

**Setting: flat to start. Maximum 2 moves, maximum 2 dB each, wide Q (0.5–1.0).**

**How to decide:** level-matched references in Tonal Balance Control. Move only where clearly outside the reference range.

**Why gentle and wide:** mastering EQ shapes the whole record. Narrow cuts are surgery, and surgery belongs in the mix. Precision judgement isn't available on this rig — wide moves are wrong more gracefully.

**Watch for:** the same move on five tracks running is monitoring bias, not five coincidences. At that point standardize it deliberately and note it in the change log.

## c. Exciter

**Setting: low band only (below ~120 Hz). Warm/tube mode. Low amount.**

**What it does:** generates new harmonics above a frequency already present.

**Why it's needed:** the sub lives at 30–60 Hz. Phones, laptops and earbuds reproduce none of it. Harmonics an octave or two up give the ear something to hear, and the brain reconstructs the missing fundamental — perceived bass the speaker never produced.

**Why warm/tube rather than aggressive:** those modes favour **even** harmonics — octaves of the original note, which reinforce the sense of *that note*. Odd harmonics add grit and edge, a different job.

**How to set it — test, don't guess:**
1. Render two versions, with and without
2. Listen **on a phone**
3. Without it the bass should feel absent; with it, present
4. Check on the KRKs — audible as distortion there means back it off

The one move that serves both contexts at once: on a real rig the harmonics sit under a fundamental that's actually there; on a phone they are the whole story.

## d. Maximizer

| Setting | Value | Why |
|---|---|---|
| **Mode** | IRC IV (A/B against IRC 5) | IRC IV limits only the frequency bands causing each peak. Here the kick and sub cause nearly every peak — other modes pull the whole track down on every kick, so everything pumps. IRC 5 is newer; A/B and keep whichever holds the low end better |
| **True Peak** | **On** | Digital audio is dots; the speaker draws the curve between them and that curve can rise above every dot. Codecs make it worse. This watches the real curve |
| **Ceiling** | **−1.0 dBTP** | Room for overshoot plus codec error |
| **Threshold** | **2–3 dB GR** at loudest section | Past ~3 dB on a bass track the kick loses snap. Under 1 dB it isn't doing anything |
| **Stereo Independence** | 0–20% (linked) | Independent is louder, but a hard-panned peak yanks the image sideways for that instant. Loudness is de-prioritized |
| **Transient Emphasis / Character** | Middle, leaning punch | Preserves attack at a small loudness cost |
| **Result target** | Loudest section **−9 to −10 LUFS-S** | Shepherd's rule: work to short-term, let integrated fall out of the arrangement |

---

# Setup order

Later stages depend on earlier ones being settled. Build in this order:

1. Trim to −16 LUFS-S
2. GP at 35%, output level-matched to bypass
3. Pro-MB threshold for 1–2 dB GR
4. Imager mono below 120 Hz
5. EQ — leave flat on first pass
6. Exciter — phone-tested
7. Maximizer last — threshold for 2–3 dB GR

**Save as a DAW template.** Rebuilding per track is how consistency dies.

---

# Per-track workflow

1. Trim to −16 LUFS-S at the loudest point
2. GP — leave at template unless the track clearly asks otherwise
3. Pro-MB — don't touch
4. Ozone EQ — max two broad moves, decided against references in TBC
5. Maximizer threshold — 2–3 dB GR
6. Run the verification tests below

---

# Verification tests

| Test | Pass condition |
|---|---|
| Whole-chain bypass, level-matched | Bypassed sounds **less finished**, not different |
| Phone test | Bass present on phone speaker |
| Mono button | Low end doesn't vanish or drop noticeably |
| Correlation meter <100 Hz | Near +1 |
| True peak | ≤ −1.0 dBTP |
| Codec Preview as AAC | Nothing new breaks up |
| System trip | It moves air, and the drop lands |

The first five are free and rig-independent. Run them every time.

---

# Troubleshooting

| Symptom | Likely cause | Move |
|---|---|---|
| Everything pumps on the kick | Maximizer mode, or Pro-MB band too wide | Switch to IRC IV; narrow band to 25–70 Hz |
| Sub thin or gone on the system | Mono cancellation, or Imager crossover too high | Check correlation; verify kick/sub phase in the mix |
| Bass invisible on phone | Exciter too low | Raise slowly, re-test on phone |
| Harsh or edgy | GP Amount too high, or wrong Exciter mode | Drop Amount to 25%; switch to a warmer mode |
| Master sounds smaller than references | Loudness chasing rather than balance | Level-match and re-A/B — may already be fine |
| Kick lost its snap | Maximizer taking too much | Reduce to 2 dB GR |
| Chain works on one track, not the next | Input level varying into GP | Re-check Stage 1. This is the most likely cause of inconsistency in the whole chain |

---

# Deliberately excluded

| Excluded | Why |
|---|---|
| Any linear-phase processing | Pre-ringing on kick/808 attack. This genre is the worst case for it |
| Full-spectrum multiband compression | Research consensus: squashes bass definition, surfaces offbeat bass |
| Stabilizer / Master Assistant | Their targets are chart dance/electronic — the −8.3 LUFS Marshmello/Guetta population, not this lane |
| Bus compression | Pro-MB does the one dynamics job that matters. More stages = more unmeasured interaction |
| A dedicated clipper | Not owned. A real gap — transient clipping ahead of a limiter is how bass music gets level without pumping. Doesn't bite while loudness is de-prioritized |

---

# Known open items

Carried forward, not blocking:

1. **God Particle is unmeasured.** Level-dependence, crossovers, time constants, THD and stereo behavior all unknown. Protocol in `RESEARCH_MASTER_CHAIN_TOOLS.md` Part 6. Until run, GP is a bounded but unknown quantity — mitigated by fixed input level and low Amount, not eliminated.
2. **No comp dataset.** Spectral targets are currently judgement, not measurement. Without it, Ozone's genre defaults pull toward chart EDM.
3. **Rig offset unquantified.** Predicted from spec as a low-mid deficit and treble deficit; unconfirmed.
4. **Analyzer not built.** Would close items 1–3. Parked by decision.
5. **IRC 5 vs IRC IV** unresolved — needs an A/B on real material.

Accepted risk: systematic low-end error is invisible on this rig and permanent once released. Mitigated by the Range cap, mono-below-120, correlation checks, and system trips before release. Not eliminated.

---

# Change log

Record what moved, why, and what evidence caused it. Especially after system trips — those are the highest-value data points available.

| Date | Stage | Change | Reason / evidence |
|---|---|---|---|
| 2026-08-01 | — | v1 created | Initial template from tool + practice research |

