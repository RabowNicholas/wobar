---
title: Wobar Mastering Checklist
version: 1.0
last_updated: 2026-08-01
status: live
scope: The per-track procedure. Follow this to master a track. Reasoning lives in [[working/WOBAR_MASTER_CHAIN_V1]] — come here to work, go there to understand or change something.
dependencies: [[working/WOBAR_MASTER_CHAIN_V1]]
---

# MASTERING CHECKLIST

**Only two things get decided per track: the EQ (0–2 moves) and the Maximizer Gain.** Everything else is template. If you find yourself adjusting a third thing, stop and ask why — that's either a mix problem or a template problem, and neither gets solved by tweaking here.

---

## A. In the production set — before you render

- [ ] **Utility on the master**, permanently. Loudest section renders at **~−16 LUFS-S**, peaks around **−6 dBFS**
- [ ] Nothing else on the master bus
- [ ] Selection extends **past the last tail** — Live cuts hard at the boundary
- [ ] Export: **WAV · 44100 · 24-bit · No Dither · Normalize OFF · Convert to Mono OFF · MP3 OFF**
- [ ] Name it so you can't master the wrong file later

> **Normalize OFF is the one that silently destroys everything above it.**

---

## B. Open the mastering template

- [ ] Open `WOBAR_MASTER_v1.als` — do **not** rebuild the chain
- [ ] Drag the mix onto the audio track
- [ ] **Warp OFF** on the clip
- [ ] Clip Gain **0** · track fader **0** · **Master fader 0**
- [ ] Interface sample rate = **44.1 kHz**
- [ ] Loop ~10 seconds of the **biggest section**. This loop is used for every measurement today

---

## C. Stage 1 — Trim

- [ ] Bypass everything below the first meter
- [ ] Adjust **Utility Gain** until the input meter reads **−16 LUFS Short-Term** on the loop
- [ ] Let it settle across the whole loop — don't read the first second

> **Expected: near 0.00 dB.** If a track needs +5 or −4, that's information about the mix, not the master. Note it and look at the mix before continuing.

---

## D. Template stages — verify, don't adjust

- [ ] **God Particle** — Amount 100%, eq flat, limiter off, input untouched, output at template value
- [ ] **Pro-MB** — don't touch. One band, 20–90 Hz, Dynamic Phase, threshold set as insurance
- [ ] **Imager** — mono below 120 Hz
- [ ] **Exciter** — Amount 7.5, Warm, band 1 only, Oversampling ON, Gain Match ON

> **Pro-MB will usually show little or no gain reduction. That is correct** — it's there to catch an outlier sub note, not to work on every track. Never lower its threshold to make something happen.

---

## E. Stage 4b — EQ *(one of two per-track decisions)*

- [ ] Start **flat**
- [ ] Open **Tonal Balance Control**, level-matched
- [ ] **Maximum 2 moves · maximum 2 dB each · wide Q (0.5–1.0)**
- [ ] Move only where clearly outside the reference range
- [ ] Most tracks: leave it flat

> **If you make the same move on five tracks running, that is monitoring bias, not five coincidences.** Standardize it into the template deliberately and log it.

---

## F. Stage 4d — Maximizer *(the other per-track decision)*

**Order matters — the first two change how much gain you need.**

- [ ] **Output Level: −1.00**
- [ ] **True Peak: ON**
- [ ] Mode: **IRC 5**
- [ ] Raise **Gain** until **GR peak-hold reads 2–3 dB** on the drop
- [ ] Check **LUFS-S lands −9 to −10**

> **GR is the ceiling. LUFS is the target.** Never push past 3 dB GR to reach a loudness number. Landing on target at 1.5 dB of GR is a good outcome.
>
> **GR should peak, not sit.** Moving = limiting. Pinned = compressing the whole program, and that's where the life goes.
>
> Read the **peak-hold**, not the resting number.

---

## G. Verification — run every time

The first five are free and don't depend on the room being good.

- [ ] **Bypass A/B, level-matched.** Set the end-of-chain comp Utility to the difference, group the processors, toggle. **Pass: bypassed sounds *less finished*, not different**
- [ ] **Mono.** Low end doesn't vanish or drop. If it thins → phase issue between kick and sub, fix in the mix
- [ ] **Correlation.** No sustained negative
- [ ] **True peak ≤ −1.0 dBTP** across the **whole track**, not just the drop
- [ ] **Codec Preview as AAC** — nothing new breaks up. **Turn it off before rendering**
- [ ] **Phone.** First 30 seconds on the phone's own speaker. Can you identify the pitch of the bassline?
- [ ] **System trip** before release, when possible

**Fail conditions and what they mean:**

| Symptom | Move |
|---|---|
| Bypass sounds **broken** | Chain doing too much — GP Amount down, re-match output |
| Bypass sounds **identical** | Chain doing nothing — check it's actually engaged |
| Everything pumps on the kick | Maximizer mode, or Pro-MB band too wide |
| Low end vanishes in mono | Kick/sub phase — upstream fix |
| Kick lost its snap | GR over 3 dB — back off Gain |
| Chain behaves differently to last track | **Check Stage 1 first.** Input drift is the most likely cause of every inconsistency |

---

## H. Render

- [ ] **Codec Preview OFF**
- [ ] Selection past the tail
- [ ] **WAV · 44100 · 24-bit · No Dither · Normalize OFF**
- [ ] Version the filename

---

## I. Log it

Record for every track: **date · trim value · Maximizer Gain · GR peak · LUFS-S · integrated · any EQ moves · anything that surprised you.**

This is the only way the template ever improves. A trim value drifting away from zero, the same EQ move recurring, Pro-MB suddenly working hard — none of those are visible in a single session, and all of them are visible across ten.

**A correction appearing twice becomes a change to [[working/WOBAR_MASTER_CHAIN_V1]].**

---

## Standing rules

- **Master follows the mix.** Anything this chain struggles with is fixable upstream at no cost, and upstream is where it belongs
- **Level-match before every comparison.** Any "is this better?" answered at unequal loudness is answered wrong
- **Loudness is de-prioritized.** Platforms normalize toward −14 LUFS — extra loudness doesn't reach the listener, but the transient cost does
- **When a setting is wrong, it should be wrong safely.** That principle chose most of the values in this chain, not optimality
- **Never delay a release on a mastering question**
