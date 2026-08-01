# WOBAR Master Chain — v1.1

**Created:** 2026-08-01
**Revised:** 2026-08-01 — **built for real, at the desk, in Ableton.** v1 was written from research; every stage below has now been instantiated, and the values that survived contact are marked. Several did not.
**Status:** live. **Built and saved as an Ableton template.**
**Companions:** `WOBAR_MASTER_CHECKLIST.md` (the per-track procedure — use that one to work) · `RESEARCH_MASTER_CHAIN_TOOLS.md` (tool capabilities) · `RESEARCH_MASTERING_EDM_DUBSTEP.md` (practice research)

> **This doc holds the reasoning. The checklist holds the procedure.** If you are mastering a track, open the checklist. Come here when you want to know *why* a value is what it is, or when something needs to change.

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

Per track, only two things get touched: **Ozone EQ (0–2 broad moves)** and **Maximizer Gain**. Everything else is template.

---

# The rig — Ableton

*Added 2026-08-01 from the build session. Getting this wrong makes every measurement downstream meaningless, and none of it is obvious.*

**Master a rendered file in a dedicated set — never the production session.** Stage 1 pins input level; a production set is a moving target, and level-matched A/B requires a source that doesn't change between listens.

**Device order on the Master track:**

```
Utility → Swiss Army Meters → [ God Particle → Pro-MB → Ozone ] → Utility (A/B comp)
                    ↑                                                      ↑
              input meter                                    off by default — see below
```

**Two meter instances, not one.** The first reads Stage 1's input level. Input drift is the single most likely cause of the chain misbehaving track to track, and this makes it visible at a glance instead of a re-measure.

**The A/B compensation rig — keep it in the template permanently.** The most useful check in the chain and it needs its own device:

1. Chain engaged, looped on the drop → note Short-Term on the output meter
2. Chain bypassed → note it again
3. The difference goes into the **end-of-chain Utility**, which stays **off** while the chain is on
4. Group the three processors (`Cmd+G`) so the A/B is two clicks: chain on / comp off ←→ chain off / comp on

Match within ~0.2 dB. The comp value is per-track, since it tracks the Maximizer's Gain.

**Session hygiene, all of it load-bearing:**

| Setting | Why |
|---|---|
| **Warp OFF** on the clip, and Auto-Warp Long Samples off in Preferences | Live warps long samples by default — you would be mastering a time-stretched version of the mix |
| Clip Gain 0, track fader 0, **Master fader 0** | Master-track devices are **pre-fader** in Live. Touching the master fader changes level *after* the limiter, outside the chain |
| Interface sample rate = file rate = export rate | Live has no project sample rate; it runs at the driver's. A mismatch means auditioning through a converter that won't be in the render |

**Sample rate: 44.1 kHz, catalog-wide** (decided 2026-08-01). The existing catalogue, sample library and delivery specs in this lane are all 44.1; modern plugins oversample internally, so the aliasing argument for 48k is largely obsolete; and the one place 48k genuinely wins — video — is a single conversion at the very end, which is the right place for it. **The rule that matters more than the rate: pick one and never convert mid-pipeline.** If the catalogue ever moves to 48, move it at a clean release boundary.

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

### Do the work upstream — the render standard

*Added 2026-08-01. The first mix taken to the mastering desk arrived at **−7.7 LUFS integrated, +1.6 dBTP**, with nothing on the master bus. That is a gain-staging problem, not a mix problem — crest was ~8.8 dB, so nothing was crushed — but it meant Stage 1 was being asked to make up 9 dB.*

**Every render out of a production set should already land at ~−16 LUFS-S on the loudest section, peaks around −6 dBFS.** Achieve it with a **Utility on the production master**, left there permanently. Never by pulling individual faders — that changes the mix.

Done this way, Stage 1's trim lands at or near **0.00 dB** on every track, and a track that suddenly needs +5 or −4 is telling you something about that mix before you have heard a note. Confirmed on the first track: **trim = 0.00 dB, −16.5 LUFS-S, −4.0 dBTP, 12.3 dB crest.**

**Ableton render settings that matter:** Normalize **Off** (it rescales to 0 dBFS and destroys the gain staging) · Dither **None** at 24-bit · sample rate matched to the interface and the file · selection extended past the last tail, because Live cuts hard at the boundary.

---

# Stage 2 — God Particle

**Position: first**, immediately after trim.

Reasons: its input level is controlled by Stage 1 · everything after it is corrective, so you're always fixing a known thing · keeps its hidden limiter away from Ozone's Maximizer.

## Amount: 100%

> **Revised 2026-08-01 from 35%, at the desk, by level-matched A/B on Nick's own material.** The 35% figure was an *inference* from GP's pop/R&B tuning — it was never tested. Tested, it lost. Both settings were output-matched before comparison.

**What it does:** blends the whole processed chain against dry. 100% on the dial is only ~50% wet internally — restraint is built in by design.

**Why 100%:** at 35% the effect was audible but only barely — a slight fullness in the mids and nothing else anywhere. That is inside the doc's own "too low" band. Level-matched against 100%, 100% won on real material. Because the dial tops out around 50% wet internally, 100% here is not the overprocessing the number suggests.

**Measured on this rig, 2026-08-01** (first real track through the chain): internal GR at both settings — **mid −2.4 dB · low −1.0 dB** · high not recorded. Output trim to match bypass was **−0.7 dB at 35%**.

**The bypass test — how to know you're right:**
- Bypass sounds **broken** → too high
- Bypass changes **nothing** → too low
- Bypass sounds **slightly flatter, less finished** → correct

This is the test for the whole chain, not just this stage. Mastering should make bypass sound unfinished, not make engaged sound different.

## EQ Low / Mid / High: 0 (flat)

**What they do:** scale a tone curve baked into the plugin. They don't create EQ, they multiply an existing shape.

**Why flat:** the shape is unmeasured. Scaling an unknown curve produces an unpredictable result, and part of it lands in frequencies that are inaudible on this rig.

**Exception:** if every track wants the same move here, that's a mix issue, not a mastering one. Fix upstream.

## Comp targets — ⚠ these controls do not exist

**Corrected 2026-08-01 at the plugin.** v1 specified "Comp Low: minimum · Comp Mid/High: ~25%." **There are no such controls.** The full control set is:

`input · eq (low/mid/high) · amount · limiter · output`, plus power toggles for eq, amount and limiter, and a Sidechain INT/EXT switch.

The `low / mid / high` readouts on the right of the interface sit under a **gain reduction** label. They are **meters, not controls** — read-only.

### The GR meters are pre-blend — do not read them as a safety gauge

**They do not change with Amount.** At 35% and at 100% they read identically, because Amount is a dry/wet blend and the meters show what the internal engine is doing *before* that blend.

Consequences:

- **The meter is not what lands on your track.** At 35% Amount, a −1.0 dB low-band reading was delivering roughly a third of a dB to the output. At 100% the same reading delivers close to all of it.
- **Do not subtract GP's low-band GR from Pro-MB's target.** An earlier version of this correction did exactly that and was wrong. Pro-MB's target stays **1–2 dB** as originally specified.
- **GP's crossover frequencies remain unknown.** Its "low" may be everything under ~300 Hz, not 20–90. Do not assume the band overlaps Pro-MB's cleanly.

The v1 worry — two uncontrolled compressors fighting over the sub band, GP's being invisible — is **partly** answered: it is observable now. But observable-in-the-engine is not the same as knowing what reaches the master, and at 100% Amount more of it reaches the master than at 35%. Bound this stage with the mono, correlation and phone checks, not with the meter.

## Limiter: off — confirmed defeatable

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
| **Attack** | **50%** | Reaction speed | See below — **Pro-MB has no ms values** |
| **Release** | **50%** | Recovery speed | See below |
| **Stereo link** | 100% | Both channels move together | Sub is mono anyway; independent movement would wobble the image |
| **Lookahead** | 0 | Reacting slightly early | Unnecessary for leveling, and it adds latency |
| **Threshold** | **1–2 dB GR** on loudest sub notes | The line signal must cross | Play the biggest section, lower threshold until the meter reads 1–2 dB, stop. 6 dB means a leveler has become a squasher |

### Attack and release — corrected 2026-08-01

**v1 specified 30 ms and 200 ms. Pro-MB does not have millisecond controls.** Both are **percentages, 0–100%**, and per FabFilter's own documentation the plugin *"uses intelligent algorithms to determine the actual attack time in milliseconds, heavily depending on program material, band width and frequency range."*

This is better than what v1 wanted, not worse. **The band is 20–90 Hz, so Pro-MB is already doing the arithmetic v1 was doing by hand** — a low band automatically gets slow timing. The "faster than one cycle of a 40 Hz wave is distortion, not compression" reasoning still holds; it's just being enforced by the plugin rather than by a number you type.

**50% on both.** FabFilter states that **20% and above** gives transparent, program-dependent behaviour and is the recommended mastering range; **0–20%** deliberately becomes more linear and pumpy, which is a creative effect and the opposite of this stage's job.

50% attack is also right for the *actual* goal rather than merely safe: you are flattening note-to-note **level** while protecting the **within-note envelope**. A slow attack lets each sub note's transient through untouched and acts only on its sustained body.

**Verify by watching the GR meter, not by trusting the number** — this is the only calibration available on a band you cannot hear:

| What you see | What it means |
|---|---|
| GR drifting gently with the sub line | Correct |
| GR snapping hard on every kick | Attack too fast — raise it |
| GR never returning to zero between phrases | Release too slow — lower it |
| GR visibly pumping in and out | Release too fast — raise it |

**Set once, leave across tracks.** Per-track tuning of an inaudible band is guessing.

**If the GR meter moves on every kick:** the kick has energy inside the band. Narrow to 25–70 Hz or raise the threshold.

---

## ⚠ Stage 3 is insurance, not an active stage — established 2026-08-01

**Nick's basslines rarely move.** The first track through the chain has a bassline spanning **±1 semitone** — roughly a 12% frequency spread, so its sub notes carry nearly identical energy. **The unevenness this stage exists to fix is not in the material.** It was solved in the writing, upstream, for free — which is the doc's own governing principle working as intended.

**Do not chase gain reduction.** Dropping the threshold until something moves would be compressing a problem that isn't there.

**Set it as a fixed level and leave it forever:**

1. Play the **whole track**, not the drop loop — watch for the single hottest low-end moment anywhere
2. Set threshold so that moment just **kisses 1 dB** and nothing else triggers
3. Never touch it again

Because Stage 1 pins every track's input, that threshold means the same thing on every track. It sits idle on narrow basslines and engages on a track that walks an octave, with no decision from you.

**Why keep it at all, given it will mostly idle:** the failure it prevents is invisible to you and permanent once released. One hot sub note forces a DJ to gain the whole record down, and you would never hear that happen in this room. Idle costs nothing — Dynamic Phase is transparent when the band isn't working, which is exactly why it was chosen over Linear Phase.

**Do not leave the threshold at its default.** Threshold is an *absolute* level; a default may sit below your sub and compress continuously on the one band you cannot hear, bounded only by the Range cap. Set it or remove the plugin — a default is the worst of the three options.

**Open caveat:** the template threshold was calibrated on a track whose bassline doesn't move — the easiest possible case. **The first track with a wide bassline is the real test.** If it sits idle there too, the number is too high and it should be recalibrated on that track.

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

### ⚠ "Width 0" is wrong — corrected 2026-08-01

In current Ozone the band Width control runs roughly **−100 to +100, where 0 means *unchanged*.** Setting it to 0 does nothing while looking like the job is done. **Drag band 1's width to its minimum.**

Reduce the Imager to **two bands** if the extra crossovers will delete — one crossover at 120 Hz is all this needs. Bands at 0 are designed to be transparent, so four bands is untidy rather than wrong.

Leave **Stereoize off**, **Recover Sides off**, **Amount 100%**, and don't press **Learn**.

### Verifying it — the correlation check as written in v1 does not work

**Ozone's correlation meter is full-band.** Your mids and highs are still stereo, so it will never read +1 and shouldn't. v1's "check: correlation near +1" would fail on a correctly-configured chain.

**Correct method: solo band 1, then read it.** Soloed, the meter shows sub content only and **should read +1**, with the vectorscope collapsed to a vertical line. Unsolo afterwards.

### Why not Live's Utility "Bass Mono"

Ableton's Utility has a Bass Mono control at the same frequency and it is tempting. **Use the Imager anyway** — the Utility sits at the *front* of the chain, ahead of God Particle, which does unmeasured stereo processing. Mono-ing at the front does not guarantee a mono output; doing it last guarantees what actually leaves the chain. Utility's Bass Mono can be left on as well if you want the compressors to see an already-mono sub, but it is not sufficient alone.

## b. Equalizer

**Use the plain `Equalizer` module.** Ozone 12 offers five and only one belongs here — recorded 2026-08-01 because the choice will come up again:

| Module | Verdict |
|---|---|
| **Equalizer** | ✅ **Use this.** Static, digital, fully predictable — which is the basis for choosing anything in this chain |
| Stem EQ | ❌ Source-separates the master into stems. **Nick owns the multitrack** — if the bass needs EQ, EQ the bass in the mix, free and lossless. Reaching for separation artifacts to fix what's fixable at source is the exact inversion this doc warns about |
| Match EQ | ❌ Requires a validated reference target, which is **open item #2**. Without it you inherit another record's mix decisions wholesale, including whatever its engineer did to compensate for *their* room — and this rig can't hear it going wrong |
| Dynamic EQ | ❌ Solves undiagnosed problems. If a frequency is only sometimes a problem, that's a mix issue |
| Vintage EQ | ❌ A modeled curve plus saturation. Flavour, not correction, and unmeasured. GP at 100% is already supplying character |

**Setting: flat to start. Maximum 2 moves, maximum 2 dB each, wide Q (0.5–1.0).**

**How to decide:** level-matched references in Tonal Balance Control. Move only where clearly outside the reference range.

**Why gentle and wide:** mastering EQ shapes the whole record. Narrow cuts are surgery, and surgery belongs in the mix. Precision judgement isn't available on this rig — wide moves are wrong more gracefully.

**Watch for:** the same move on five tracks running is monitoring bias, not five coincidences. At that point standardize it deliberately and note it in the change log.

## c. Exciter

**SETTLED 2026-08-01 by phone test: Amount 7.5 (= 50% of the control's range) · Warm · band 1 only, crossover 120 Hz · Mix 100% · Oversampling ON · Gain Match ON.**

**Turn Oversampling ON here** — the opposite of the call on Pro-MB, and worth understanding why. A compressor generates no new frequencies, so there is nothing to alias and oversampling buys nothing. **The Exciter's entire job is generating new harmonics**, and harmonics generated near the top of the spectrum fold back down as aliasing. At 44.1k that ceiling is low. It is doing real work.

**Turn Gain Match ON** — it compensates the module's output so engaging the Exciter doesn't simply make things louder. Same principle as level-matching GP, but automatic. Without it, the louder version wins every A/B, and on a phone speaker that bias is very strong.

**Setting: low band only (below ~120 Hz). Warm/tube mode. Low amount.**

**What it does:** generates new harmonics above a frequency already present.

**Why it's needed:** the sub lives at 30–60 Hz. Phones, laptops and earbuds reproduce none of it. Harmonics an octave or two up give the ear something to hear, and the brain reconstructs the missing fundamental — perceived bass the speaker never produced.

**Why warm/tube rather than aggressive:** those modes favour **even** harmonics — octaves of the original note, which reinforce the sense of *that note*. Odd harmonics add grit and edge, a different job.

**How to set it — test, don't guess.** Render **three** versions, not two — this is a once-ever decision, so get a range rather than a yes/no: **bypassed · a low amount · a high amount**, same 30 seconds of the drop.

1. Phone flat on a table, not in your hand. Moderate volume — phone speakers distort mechanically at the top and it will confuse you
2. **Extremes first**, bypassed vs high, several times. If you can't tell them apart, the band or crossover is wrong — debug before picking a number
3. Then bring the middle value in
4. Back on the KRKs — audible as **distortion** there means back it off

**The cue that actually works: can you identify the *pitch* of the bassline?** Not weight — pitch. With no harmonics the sub is simply gone and you hear only the mid growl. With it working, the note has an identifiable pitch and a floor under it.

**Too much sounds like:** buzzy or nasal, the bass reading as a fuzzy tone sitting *on top* of the track rather than underneath it; honky in the low mids; bass competing with the lead rather than supporting it. Harsher, not lower.

**Two kinds of ugly, don't confuse them:** harmonic grit from the Exciter is constant and tonal. Mechanical speaker distortion is a crackle at peaks that worsens with volume and disappears when you turn down — that one is the phone, not your file.

The one move that serves both contexts at once: on a real rig the harmonics sit under a fundamental that's actually there; on a phone they are the whole story.

**Set once, leave across tracks.** A fixed harmonic generator on a fixed band, fed a fixed input level, does the same thing to every track. Revisit only for a track whose sub sits in a very different register, or a master that sounds gritty on a phone.

## d. Maximizer

**⚠ Ozone 12 renamed the controls.** v1's vocabulary does not match the plugin:

| v1 says | Ozone 12 calls it |
|---|---|
| Threshold | **Gain** — you *raise* it to drive into a fixed ceiling |
| Ceiling | **Output Level** |

| Setting | Value | Why |
|---|---|---|
| **Mode** | **IRC 5** — settled 2026-08-01 | See below. IRC 4 also has three undocumented sub-modes — Classic / Modern / Transient |
| **True Peak** | **On** | Digital audio is dots; the speaker draws the curve between them and that curve can rise above every dot. Codecs make it worse. This watches the real curve. **Turning it on increases GR at the same Gain** — set it before dialing gain, not after |
| **Output Level** | **−1.0** | Room for overshoot plus codec error |
| **Gain** | raise until **2–3 dB GR peak-hold** at the loudest section | Past ~3 dB on a bass track the kick loses snap. Under 1 dB it isn't doing anything |
| **Stereo Independence** | Transient 0% / Sustain 0% | Independent is louder, but a hard-panned peak yanks the image sideways for that instant. Loudness is de-prioritized |
| **Character** | left at default (**2.00, "Fast and Loud"**) | Untested. No research covers it — see open items |
| **Transient Emphasis** | **0%** | Left off. Revisit only if the kick softens |
| **Upward Compress** | **0.0 dB** | Not part of this chain |
| **Soft Clip** | **0%** | Owned but untested — see below |
| **Dither** | **Off** | Rendering 24-bit |
| **Result target** | Loudest section **−9 to −10 LUFS-S** | Shepherd's rule: work to short-term, let integrated fall out of the arrangement |

### GR is the ceiling; LUFS is the target

The rule for every track: **never push past 3 dB GR to reach a loudness number.** Landing on the loudness target with only 1.5 dB of GR is a good outcome, not an incomplete one.

**Read the peak-hold, not the instantaneous number** — the resting readout will show a fraction of the real figure.

**GR should peak, not sit.** 2–3 dB on the transients, falling back toward zero between them. Pinned at a constant value means the limiter has stopped being a limiter and become a compressor on the whole program — that's where the life goes. A floor of half a dB to one dB in a dense drop is normal. **Moving versus pinned is the distinction, not the resting value.**

### IRC 5 — open item #5 closed, 2026-08-01

A/B'd at fixed Gain against IRC 4 Classic, Modern and Transient. **IRC 5 won on preserved snare reverb** — direct evidence it isn't clamping sustained material, which is the pumping failure mode.

**The method, for re-running it:** three passes over the same 2 bars, one thing each pass — (1) the *front* of the kick, does it still click; (2) sustained elements between hits, do they duck and swell; (3) the sub under the kick. **Weight 1 and 2 over 3** — this rig is honest to ~54 Hz, so the kick transient and the pumping are the judgments actually available. Watch short-term while switching: half a dB of loudness difference will pick the winner for you.

### Why the Maximizer looks underworked

The first track settled at **1.6 dB GR peak** — below the 2–3 dB target — while still reaching the loudness target. **This is a consequence of Amount going to 100%.** God Particle is now doing real peak control upstream, so crest is already reduced before the limiter sees it. Not a problem. Logged so a future session doesn't read a low GR figure as a mistake.

### ⚠ Soft Clip exists — the "Deliberately excluded" entry is wrong

The Maximizer contains a **Soft Clip** control with H/M/L character options. The excluded-items table below says a dedicated clipper is *"Not owned. A real gap — transient clipping ahead of a limiter is how bass music gets level without pumping."*

**It is owned.** Left at 0% on the first build — one new variable at a time — and it genuinely doesn't bite while loudness is de-prioritized. But it is the single most relevant untested tool in this chain for this genre.

---

# Setup order

Later stages depend on earlier ones being settled. Build in this order:

1. Trim to −16 LUFS-S
2. GP at 100%, output level-matched to bypass
3. Pro-MB threshold — set as insurance, whole track, just kissing 1 dB
4. Imager mono below 120 Hz, verified **soloed**
5. EQ — leave flat on first pass
6. Exciter — phone-tested, three renders
7. Maximizer last — True Peak on and Output Level set **before** dialing Gain

**Save as a DAW template.** Rebuilding per track is how consistency dies. ✅ Done 2026-08-01.

---

# Per-track workflow

**Use [[working/WOBAR_MASTER_CHECKLIST]] to actually work.** This is the summary.

1. Trim to −16 LUFS-S at the loudest point
2. GP — leave at template unless the track clearly asks otherwise
3. Pro-MB — don't touch
4. Ozone EQ — max two broad moves, decided against references in TBC
5. Maximizer **Gain** — 2–3 dB GR peak-hold
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

**All passed on the first track, 2026-08-01.** Bypass A/B verdict, in Nick's words: *"more full and present, more glued together, sounds like a finished song."* That is the pass condition stated almost exactly as this doc frames it — mastering should make bypass sound **unfinished**, not make engaged sound **different**.

---

# Troubleshooting

| Symptom | Likely cause | Move |
|---|---|---|
| Everything pumps on the kick | Maximizer mode, or Pro-MB band too wide | Switch to IRC IV; narrow band to 25–70 Hz |
| Sub thin or gone on the system | Mono cancellation, or Imager crossover too high | Check correlation; verify kick/sub phase in the mix |
| Bass invisible on phone | Exciter too low | Raise slowly, re-test on phone |
| Harsh or edgy | GP Amount too high, or wrong Exciter mode | Drop Amount (100% is the baseline — try 50%, re-matching output at each value); switch to a warmer mode |
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
| ~~A dedicated clipper~~ | 🔴 **This entry is void — corrected 2026-08-01.** Ozone 12's Maximizer has **Soft Clip** built in, with H/M/L character. It is owned, it is untested, and it is the most relevant unexplored tool here for bass music. Kept at 0% for now |
| Upward Compress (Ozone Maximizer) | Owned, unused. Adds an unmeasured dynamics stage the chain doesn't need |

---

# Known open items

Carried forward, not blocking:

1. **God Particle is still largely unmeasured, and the bound is now looser.** Crossovers, time constants, THD and stereo behavior remain unknown. Protocol in `RESEARCH_MASTER_CHAIN_TOOLS.md` Part 6. What v1 said was "mitigated by fixed input level *and low Amount*" — **Amount is no longer low.** The fixed input level still holds; the low-Amount half of that mitigation is gone by decision, traded for a preference confirmed under level-matched A/B. This raises the value of the analyzer work in item 4 and of system trips.
2. **No comp dataset.** Spectral targets are currently judgement, not measurement. Without it, Ozone's genre defaults pull toward chart EDM.
3. **Rig offset unquantified.** Predicted from spec as a low-mid deficit and treble deficit; unconfirmed.
4. **Analyzer not built.** Would close items 1–3. Parked by decision.
5. ~~**IRC 5 vs IRC IV**~~ — ✅ **CLOSED 2026-08-01.** IRC 5, on preserved snare reverb, A/B'd at fixed gain against IRC 4 Classic/Modern/Transient.

**Opened 2026-08-01 by the build:**

6. **Soft Clip untested.** Owned, sitting at 0%. Transient clipping ahead of the limiter is the standard way bass music gets level without pumping. The highest-value experiment available in this chain.
7. **Maximizer Character untested.** Left at its 2.00 default. No research covers what it does or where the middle of its range is.
8. **GP's output-match value at 100% was not recorded.** −0.7 dB was the figure at 35% and is stale. It lives in the saved template but not in this doc — recover it from the template and write it in.
9. **Pro-MB's threshold was calibrated on the easiest possible case** — a ±1 semitone bassline. The first wide-bassline track is the real test.
10. **Integrated loudness has never been measured over a whole track**, only over a looped drop. Shepherd's rule needs the full arrangement to mean anything.

Accepted risk: systematic low-end error is invisible on this rig and permanent once released. Mitigated by the Range cap, mono-below-120, correlation checks, and system trips before release. Not eliminated.

---

# Change log

Record what moved, why, and what evidence caused it. Especially after system trips — those are the highest-value data points available.

| Date | Stage | Change | Reason / evidence |
|---|---|---|---|
| 2026-08-01 | — | v1 created | Initial template from tool + practice research |
| 2026-08-01 | 1 | Added the **render standard** — production sets carry a permanent Utility so mixes arrive at ~−16 LUFS-S / −6 dBFS | First mix to the desk arrived at −7.7 LUFS-I, +1.6 dBTP with an empty master bus. Crest ~8.8 dB, so gain not damage. Fixing it upstream makes Stage 1 trim ≈ 0.00 on every track and turns trim into a mix diagnostic |
| 2026-08-01 | 2 | **Amount 35% → 100%** | Level-matched A/B on Nick's own material, output re-matched at both settings. 35% sat inside the doc's own "too low" band — audible only as slight mid fullness. 35% was an inference from GP's pop/R&B tuning and had never been tested |
| 2026-08-01 | 2 | **Removed the "Comp targets" spec — those controls do not exist** | Read off the actual plugin. GP has input / eq / amount / limiter / output only. The low-mid-high readouts are gain-reduction *meters* |
| 2026-08-01 | 2 | Recorded that **GP's GR meters are pre-blend** and do not track Amount | Identical readings at 35% and 100%. Means the meter shows engine behavior, not what reaches the master — so it cannot be used as a safety gauge, and GP's low-band GR must **not** be subtracted from Pro-MB's target. An intermediate call to drop Pro-MB to ~1 dB was made on that bad reading and is reverted |
| 2026-08-01 | 2 | Limiter confirmed **defeatable** via its power toggle | Observed on the plugin — v1 hedged with "if it defeats" |
| 2026-08-01 | — | Added **The rig — Ableton** section | Warp, pre-fader master, dual meters, the A/B compensation rig and the sample-rate rule are all invisible failure modes that would corrupt every measurement |
| 2026-08-01 | — | **Sample rate fixed at 44.1 kHz catalog-wide** | Existing catalogue and sample library are 44.1; lane delivery specs skew 44.1; plugin-side oversampling defeats the aliasing argument for 48k; video conversion belongs at the end anyway |
| 2026-08-01 | 3 | **Attack/release rewritten — Pro-MB has no ms values.** Both are 0–100%, set to **50%** | Read off FabFilter's own tooltip: the plugin derives actual times from program material, band width and frequency range, and states 20%+ as the transparent mastering range. v1's "30 ms / 200 ms, arithmetic not taste" was not dialable — but the arithmetic is being done by the plugin |
| 2026-08-01 | 3 | **Reframed as insurance, not an active stage** | Nick's basslines rarely move — the first track spans ±1 semitone, so its sub notes carry near-identical energy. The problem this stage exists to solve is already solved in the writing. Threshold set as a fixed level to catch outliers; never chase GR here |
| 2026-08-01 | 4a | **"Width 0" corrected** — 0 means *unchanged*; mono is the control's **minimum** | Would have silently done nothing while looking correct |
| 2026-08-01 | 4a | **Correlation check corrected** — Ozone's meter is full-band, so **solo band 1** to verify | v1's "correlation near +1" fails on a correctly-configured chain, because mids and highs are still stereo |
| 2026-08-01 | 4a | Rejected Ableton Utility's Bass Mono as a substitute | It sits ahead of GP, whose stereo behaviour is unmeasured. Only the last stage can guarantee the output |
| 2026-08-01 | 4b | Recorded **why the plain Equalizer** and not Stem / Match / Dynamic / Vintage EQ | Ozone 12 offers five. Stem EQ is the notable reject: Nick owns the multitrack, so separation artifacts are never the right way to fix something fixable at source |
| 2026-08-01 | 4c | **Exciter settled: Amount 7.5 (50% of range) · Warm · 120 Hz · Oversampling ON · Gain Match ON** | Phone test, three renders (bypassed / low / high) on the phone's own speaker. Lower than the 12 placeholder. Oversampling ON here is the *opposite* of the Pro-MB call and the reason is recorded in the stage |
| 2026-08-01 | 4d | **Ozone 12 renamed the controls** — Threshold → **Gain**, Ceiling → **Output Level** | v1's vocabulary doesn't match the plugin |
| 2026-08-01 | 4d | **IRC 5 selected — open item #5 closed** | A/B at fixed gain against IRC 4 Classic/Modern/Transient. Won on preserved snare reverb — evidence it isn't clamping sustained material |
| 2026-08-01 | 4d | Recorded that **True Peak ON increases GR at the same Gain** | Set ceiling and True Peak *before* dialing gain, or you dial it twice |
| 2026-08-01 | 4d | ⚠ **"No dedicated clipper" entry voided — Soft Clip is built into the Maximizer** | Owned, untested, left at 0%. The most relevant unexplored tool in this chain for this genre |
| 2026-08-01 | 4d | **Deviation accepted: landed at −8 LUFS-S, not −9 to −10** | Nick's call, on evidence — the Maximizer's Delta showed only the leading edge of the transient being removed, and GR peaked at 1.6 dB. Logged as a decision, not drift. The counter-argument stands and is unchanged: platforms normalize toward −14, so the extra loudness doesn't reach the listener while the transient cost does |
| 2026-08-01 | — | **Verification tests all passed** on the first track | Bypass A/B, mono, correlation, true peak, phone. Nick on the bypass test: *"more full and present… sounds like a finished song"* |

