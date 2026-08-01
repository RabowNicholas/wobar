# RESEARCH — Mastering Practice: General EDM + Deep Dubstep

**Status:** temporary working doc. Findings only — no chain design, tool-agnostic.
**Created:** 2026-08-01
**Companion:** `RESEARCH_MASTER_CHAIN_TOOLS.md` (tool capabilities)
**Purpose:** gather what credible practice actually says, at two levels, before weighting.

---

## Source credibility tiers

Weight findings by tier. Tier assignment is about *verifiability of the claim's origin*, not whether the advice is good.

**Tier 1 — Named engineers with verifiable credits, speaking in primary interviews; standards bodies.**
- **Jason Goz** — Transition Mastering, Croydon. Bought a Neumann lathe in 1997, Transition full-time since 1998. The dubstep scene's mastering/cutting engineer of record; Mala confirms DMZ dubs were cut there. Most directly relevant single source in this entire document.
- **Beau Thomas** — Ten Eight Seven Mastering, London. Ex-DnB artist (Babylon Timewarp, Intense), trained as vinyl cutter at Heathmans. 1500+ mastering/cutting credits.
- **Stuart Hawkes** — Metropolis. 25+ years; Goldie *Timeless*, extensive DnB and UK bass, plus Disclosure/Avicii/Winehouse.
- **Ian Shepherd** — Mastering Media, founder of Dynamic Range Day, co-developer of Loudness Penalty. Speaking in Sound On Sound.
- **Alex Gordon** — Abbey Road.
- **Katie Tavini** — mastering engineer, Brighton.
- **Joe Lambert** — Joe Lambert Mastering.
- **Bob Katz** — K-System author.
- **Mala (Digital Mystikz)** — not an engineer, but Tier 1 as a *primary source on deep dubstep sound-system practice* (RBMA lecture).
- **ITU-R BS.1770-4 / AES TD1008** — measurement and loudness standards.

**Tier 2 — Trade press and vendor research with actual data or named sourcing.**
- iZotope's LUFS/tonal analyses (real measurements, published numbers; vendor bias toward "use our tools" but the data is data)
- Sound On Sound technique articles
- MusicTech, DJ Mag, Attack Magazine features
- Florian Meindl / Riemann (named techno producer-engineer, club-focused)

**Tier 3 — Practitioner forums. Real experience, no verification, survivorship bias.**
- Gearspace mastering forum, Dogs On Acid, Dubstepforum, KVR.
- Useful for *what practitioners actually do* and for surfacing disagreements. Not useful as authority.

**Tier 4 — SEO content mills and mastering-service blogs.**
- Numerous "LUFS targets 2026" pages, "How to master dubstep" guides, AI-mastering company blogs.
- These recycle each other. When a number appears **only** in Tier 4, treat it as unsourced folklore, not practice. Several widely repeated claims below live only here — flagged.

---

# LEVEL A — General EDM mastering

## A1. Loudness: the measured picture

**iZotope 2024 Hot Dance/Electronic chart analysis** *(Tier 2, real measurements)*:

| Song | Artist | Int. LUFS | LRA | True Peak | Note |
|---|---|---|---|---|---|
| Miles On It | Marshmello & Kane Brown | −6.2 | 4.8 LU | +0.22 dBTP | raw distortion in choruses |
| Forever Young | Guetta / Alphaville / Ava Max | −7.7 | 6.7 LU | +0.92 dBTP | clean loudness via sidechain |
| Beautiful People | Guetta & Sia | −7.7 | 5.8 LU | +1.50 dBTP | higher PLR |
| Dreamin | Dom Dolla | −7.7 | — | — | sibilance flagged |
| Hypnotized | Anyma & Ellie Goulding | −7.0 | 6.6 LU | −0.29 dBTP | "good and loud" achieved cleanly |
| Focus | John Summit | −7.0 | 5.4 LU | −0.28 dBTP | same engineer approach (Cassian) |
| Slow Motion | Marshmello × Jonas Brothers | −8.7 | 10.0 LU | +0.57 dBTP | distortion in bass |
| Move | Adam Port & STRYV | −9.1 | 4.2 LU | −0.23 dBTP | 40+ weeks charting |
| The Days | CHRYSTAL | −10.3 | 3.5 LU | +0.61 dBTP | self-produced, headroom left |
| Neverender | Justice & Tame Impala | −11.3 | 13.8 LU | −0.09 dBTP | clean, punchy, best imaging |

**Aggregate:** average integrated **−8.3 LUFS (±1)**, range **−6.2 to −11.3**, average LRA **5.5 LU (±1.5)**.

Two things worth noting in that table: several chart-topping masters **exceed 0 dBTP** (up to +1.50), and the two the analyst rated best-sounding (Hypnotized, Focus) are **not** the loudest — they're −7.0 with negative true peak.

**Ian Shepherd's position** *(Tier 1)* is structurally different and worth reading carefully:
> "Integrated LUFS is not a target loudness for mixing or mastering. Integrated is about distribution levels."

He works to **Short-Term LUFS**, recommends the loudest sections sit **no higher than −10 LUFS-S**, and makes the rest balance musically by ear. He notes ~90% of streamed tracks are normalized. Momentary LUFS he considers too fast to be useful for music.

Implication: "master to −8 integrated" and "cap short-term at −10" are not the same instruction, and the second is the one a Tier 1 engineer actually gives. Integrated falls out of the arrangement; short-term is what you control.

**Genre-adjacent club practice** *(Tier 2, Florian Meindl/Riemann)*: −12 LUFS for dynamic house, up to −7 for techno.

**Scene practice for bass genres** *(Tier 3, DnB forums)*: engineers commonly master DnB around −7; artists frequently request −5; extremes at −4. Unverified but consistent across threads.

## A2. True peak and headroom

- **−1.0 dBTP ceiling** is the near-universal recommendation, to survive lossy codec conversion (Tier 2/4 consensus, grounded in ITU-R BS.1770-4).
- Chart masters routinely violate it (see table). It is a robustness guideline, not a rule anyone enforces.
- **PLR** (true peak − integrated LUFS) is the honest squash metric. Higher PLR reads clearer and less fatiguing at equal loudness.

**Mix delivery headroom** *(Tier 1, DJ Mag feature)*:
- **Alex Gordon (Abbey Road):** peaks at −3 to −6 dB are fine, but "hitting −1dB or even 0dB is absolutely fine… it shouldn't be clipping and slamming into 0dB throughout."
- **Jason Goz (Transition):** warns specifically against "too much limiting on the individual channels, and/or the stereo buss," and asks that files peak below 0 dBFS on delivery.
- **Beau Thomas:** values mixes that haven't been "overprocessed or brickwalled."
- Work at **24-bit** minimum (Gordon: at 16-bit, hitting 0 distorts).

Note the divergence from the widely repeated Tier 4 rule "leave −6 dB of headroom." Two Tier 1 engineers say the absolute number barely matters; what matters is that the mix isn't already squashed.

## A3. What actually makes a master loud (Tier 1 consensus)

**Beau Thomas:**
> "A good mix-down that is very controlled and sounds great will nearly always become really loud easily."

And on why the demand exists at all: *"It's clubs, almost definitely."* — loudness pressure in dance music is a club-culture artifact, not a streaming one.

**Practitioner corollary** *(Tier 3, mastering forum, echoed by Joe Lambert Tier 1)*: loudness comes from **spectral space**, not from processing.
- "Big bass doesn't even need to actually be heavy on the bass frequencies, it's more about perception. There's not much low end on some records that sound huge, which means they can be super loud as well."
- Joe Lambert: "Cutting lows to get bigger lows can feel counter-intuitive at first, but be ruthless."

## A4. Low end — the general-EDM rules

**Kick/bass frequency division** *(Joe Lambert, Tier 1)*:
- Sub bass owns **40–80 Hz**; tight punchy kick dominates **90–180 Hz** — or the inverse. Pick one, don't contest.
- "You just can't have it both ways."
- Common untreated-room measurement traps: peaks around 60 Hz and 110 Hz, holes around 80 Hz.

**Sound On Sound (Tier 2)** adds three established dance approaches:
1. Separate kick and bass **in time** (classic dance technique)
2. Give the **bass** most of the sub energy while a less sub-heavy kick plays alongside — creates the illusion the kick is bigger than it is
3. Deliberately overdrive the mix bus / mastering chain with the kick, treating the distortion as part of the sound

**Mono bass** — the most contested number in this document. Reported crossovers:
- 90–110 Hz, 120 Hz, 150 Hz, 150–180 Hz (sides only), up to 300–350 Hz — all appear in Tier 2/3 sources
- 120 Hz at ~6 dB/oct described as the common mastering default
- Correlation target: **near +1 below 100 Hz**; content sitting at +0.3 to +0.5 down there is called out as a large-system failure mode
- **Tier 1 dissent (vinyl engineers):** the rule "is one of those things that's been vastly over simplified and taken out of context." Vinyl reproduces plenty of bass, and *some* out-of-phase low end is not a problem for a skilled cutter. Their position: leave the bass-monoing to the cutting engineer, who has an elliptical EQ and knows how much to apply.

**Why it matters at all:** bass wavelengths are long; small L/R timing differences produce large cancellation when summed. Club subs are summed to mono because directional sub below ~100 Hz is physically unachievable. "Sounds great in the studio, disappears in the club" is the standard symptom.

## A5. Dynamics processing (general)

**Multiband compression — genuinely disputed.**
- *For:* it's the fix-it tool for material you didn't mix; lets you control one band's energy without touching the rest. Riemann/Meindl goes further and suggests **using a multiband instead of a limiter** — higher ratios in the bass, lower in mids/highs — to keep dynamics while controlling energy.
- *Against (Tier 3 mastering forum, strongly worded):* "Multiband isn't going to give you a big bass, in fact it most likely will ruin definition in your bass. If you just multiband a dubstep mix you'll squash the bass and bring out the bass in the offbeat moments which likely will not help." Consensus in that thread: fix at the source.

**Protecting the low end during bus compression** *(Tier 2, Sage Audio)*: sidechain-filter the detector so lows don't trigger compression, or use a multiband with the low band's threshold set high enough that it never engages. The lows keep their amplitude while mids/highs get controlled.

**Saturation** *(Tier 2)*: saturation is simultaneously soft-knee compression and harmonic generation. Multiband saturation adds energy *upward* in the spectrum from a band — a fundamentally different move from compression.

## A6. Monitoring and calibration

**Bob Katz K-System** *(Tier 1)*: monitor calibration tied to metering scale, typically **83 dB SPL C-weighted slow** per channel. K-12 is the scale nominated for club/EDM-adjacent material, K-14 for modern pop/rock, K-20 for audiophile/classical.

**Jonathan Wyner** *(Tier 1, via iZotope)*: fixed, calibrated playback level is the point — without it "we lose our anchor and point of reference." Crest-factor references he gives: classic rock 8–12 dB peak-to-average; pop ~2 dB tighter; acoustic jazz around −14 dB RMS; classical −18 to −20.

**Jason Goz** *(Tier 1)*, the counterweight:
> "Don't watch the meter."

He rejects waveform visualization outright, arguing visual information degrades sonic judgement, and says **"95% of what I do is listening to the same thing over and over again."** Ear-training is the gate: "An engineer who can't spot 1k from 2k from 5k — they haven't learned the fundamentals."

---

# LEVEL B — Deep dubstep specific

Where the genre departs from general EDM. Fewer credible sources exist; the ones that do are unusually good.

## B1. The genre is defined by the playback system, not the file

Deep dubstep coalesced around DMZ / FWD>> in South London, built for **large sound systems capable of physically reproducing sub-bass**. The music is sparse, half-time at 140, built on negative space and low-end pressure. Foundational energy sits **20–40 Hz** — below where most EDM even operates — with clean sine subs generally cited at **30–60 Hz**.

**Mala** *(Tier 1, RBMA)* on how tracks were actually validated:
> At Plastic People, "you really are exposed to your production. You'd go in there and you'd listen to it and you could tell instantly what was wrong with it."

The test was the room, not the meter. Dubs were cut at **Transition** — mastered and cut in the same pass, on a Neumann lathe with a diamond stylus.

On the bassline itself: Mala starts from **a straight sine wave** with "a bit of EQing and filtering, maybe a little bit of reverb," and low-cuts to stop it going "flabby with not much tightness or control." He describes finding the right sub frequency like a car's biting point.

**Consequence for mastering:** in this lineage the master's job is to survive and exploit a system with real sub extension. That is close to the opposite of the phone-speaker optimization that drives general EDM loudness practice.

## B2. Jason Goz — the most relevant single source

Transition is the mastering facility of the genre. His stated positions:

- **On the low end as the point:** he describes a bassline that "will engulf you like a sleeping bag. A very dangerous, 50hz, shake your chest sleeping bag." His target is bass that is *terrifying and engulfing*, not merely present. 50 Hz named explicitly as the chest-impact region.
- **On distortion by genre:** some dance records tolerate distortion — "you wouldn't get away with that for a jazz piece that's been recorded at Abbey Road and is very clean and pure." Distortion is a permitted tool in this genre in a way it is not elsewhere.
- **On method:** test cut → listen → process from experience → test again. Iterative, listening-led, meter-hostile.
- **On mix delivery:** no heavy limiting on individual channels or the stereo bus; peak below 0 dBFS.
- **On vinyl:** "an evil mistress." He checks with **four different types of stylus**, and does deliberate test cuts "to get it to misbehave." Notes that a lot of perceived distortion originates in playback systems rather than in the master.

## B3. Vinyl / dubplate constraints — still live in this genre

Unlike most modern EDM, deep dubstep still cuts to lacquer and dubplate. That imposes real physics:

**Beau Thomas** *(Tier 1)*:
> "You can't cut stereo bass; if music's too wide it can cut the vinyl too deep, or the sides can distort, so you have to pull the stereo width in slightly."

And on groove geometry: "Cutting is like pushing a pyramid into sand; the deeper you go, the wider the groove becomes." Groove spacing ("land") must balance — too little and records jump, too much and side length collapses. He also compensates for the treble loss toward the centre of a side by riding treble up as the track plays.

Other cutting-room facts (Tier 2):
- Excessive/wide low end can make the needle jump the groove
- **Elliptical EQ** exists solely to keep the low end in phase for the lathe
- Bass-monoing is sometimes applied specifically **to allow a hotter cut** when the client wants a loud record
- Dynamic masters translate better to vinyl than squashed ones
- Sibilance and hi-hat transients need taming for the format

## B4. Sub-bass in a club context

**On sub dynamics** *(Tier 2, Meindl, techno context but directly transferable):*
> "Avoid very dynamic sub-bass … because in a club the subwoofers will most likely run on maximum all the time anyway and the PA systems have limiters on the subwoofers."

This is a real constraint that almost no streaming-oriented advice accounts for: **the venue's own limiters are the last stage of your chain**, and they are frequency-split. A master with wildly dynamic sub hands its low-end shape over to a limiter you've never heard.

**Club playback level control** is the DJ's gain knob, not normalization — so relative loudness between your track and the next one is set by a human, and the DJ can only fix level, not squash.

## B5. Translation to small speakers — the counter-pressure

Deep dubstep's fundamentals sit below what phones, laptops, and Bluetooth speakers reproduce at all. Standard technique *(Tier 2/3 consensus)*: **add harmonics above the fundamental** so the ear reconstructs the missing sub (missing-fundamental effect). Methods cited: saturating/distorting a low-passed sine, deliberately generating odd vs even harmonic sets, octave-up harmonic layers, bass-enhancement processors.

This is the central tension of the genre at the mastering stage: the sound is defined by 20–50 Hz content that most listeners' playback cannot render, and the fix (harmonic reinforcement) is also what makes a master sound less pure on the systems that *can* render it.

## B6. Mix-side low-end discipline (what mastering can't fix)

Consistent across Tier 1 and Tier 3 bass-music sources:
- Kick low-passed roughly **100–140 Hz**, or kicked up an octave to sit near **120 Hz**, so it doesn't contest the sub
- Keep drums dry and tight with little sub so the bass owns the bottom
- Sidechain sub to kick where they overlap
- Cut lows from the **sides** at ~150–180 Hz to clear space for a mono sub
- Sparse mid-range, mono sub, and real headroom is described as the mixdown practice that made large-system translation work
- Even out multiple bass elements with a single stage of multiband before trying to master

---

# Contradictions to resolve (the actual decision points)

| # | Question | Position A | Position B |
|---|---|---|---|
| 1 | What is the loudness target? | Chart EDM averages −8.3 LUFS-I; bass scenes push −7 to −5 | Shepherd (Tier 1): integrated is not a target at all — cap short-term at −10 LUFS-S and let integrated fall out |
| 2 | How low do you mono the bass? | 100–120 Hz is the mastering default; correlation ~+1 below 100 Hz | Vinyl engineers (Tier 1): over-simplified internet rule; leave it to the cutting engineer, who has an elliptical EQ |
| 3 | Multiband compression on a bass master? | The core fix-it tool; Meindl even proposes it *instead of* a limiter | Ruins bass definition, surfaces offbeat bass; fix at source |
| 4 | Meters or ears? | Calibrated monitoring + LUFS/PLR/correlation instrumentation (Katz, Wyner, Shepherd) | Goz (Tier 1, most genre-relevant): "Don't watch the meter" — 95% listening, test cuts |
| 5 | Should the sub be dynamic? | Musical dynamics are the point of deep dubstep | Club PA sub limiters will flatten it anyway; dynamic sub cedes control to a limiter you can't hear |
| 6 | Is distortion acceptable? | Goz: dance records tolerate it, unlike acoustic material. SOS: producers deliberately overdrive the bus with the kick | Chart analysis flags audible distortion as a *defect* in −6.2 LUFS masters |
| 7 | Headroom into mastering? | Tier 4 orthodoxy: leave −6 dB | Gordon (Abbey Road): −1 or even 0 is fine, just don't slam continuously. Goz: peak below 0, no bus limiting. The *shape* matters, not the number |
| 8 | Who is the master for? | Streaming/normalized playback → dynamics survive, loudness buys nothing | Sound system / dubplate / DJ set → different physics, different priorities, no normalization |

---

# What no source could answer

Gaps that public research cannot close — these need first-party measurement.

1. **No published loudness dataset exists for deep dubstep.** The iZotope data is Billboard dance/electronic — Marshmello, Guetta, John Summit. Nothing measured for Deep Medi / Sentry / Artikal / Wheel & Deal-class releases. The genre's actual numbers are unmeasured in public.
2. **No LRA/PLR figures for the genre.** Half-time sparse arrangements should behave very differently from four-to-the-floor, and nobody has published it.
3. **SoundCloud's real normalization behavior** for underground uploads is asserted at −14 by aggregator sources, none Tier 1.
4. **Club PA sub-limiter behavior** — crossover points, thresholds, release — is venue-specific and undocumented.
5. **How much harmonic reinforcement is optimal** for phone translation without compromising the sound-system version. No source quantifies the trade.

**Closing the gap is straightforward:** build a reference set of 15–25 deep dubstep releases you consider correctly finished, measure integrated LUFS, short-term max, LRA, true peak, PLR, and low-band correlation on every one, and produce the dataset that doesn't exist. That measurement is worth more than every Tier 3/4 source in this document combined — it's the same move that beat the external comp sweeps before.

---

# Weighting questions for discussion

1. **Which playback context is primary** — SoundCloud/streaming, DJ/sound system, or both equally? Answer determines whether loudness practice or dynamic practice dominates.
2. **Does Goz's meter-hostile, listening-led method get weighted above instrumented practice** on the grounds that he's the genre's actual engineer? Or is that a judgement built on 25 years of calibrated ears that doesn't transfer?
3. **How much do vinyl/dubplate constraints count** if nothing is being cut? They shaped the genre's sonic conventions — do those conventions still bind when the format doesn't?
4. **Is chart-EDM loudness data (−8.3 avg) relevant at all**, or is it a different music with different goals that happens to share a parent genre?
5. **Where does the phone-vs-system trade sit** given that the 12-month goal is people listening online?
6. **Sub dynamics:** protect them as musical content, or flatten them as club-survival insurance?

---

## Sources

**Tier 1 — named engineers / primary**
- [Jason Goz (Transition Mastering) — Spitfire Audio interview](https://composer.spitfireaudio.com/en/articles/frequencies-sonic-concentration-and-chasing-ghosts-with-mastering-engineer-jason-goz)
- [Beau Thomas (Ten Eight Seven) — MusicTech interview](https://musictech.com/features/beau-thomas-ten-eight-seven-mastering/)
- [Ian Shepherd on Loudness & Dynamics — Sound On Sound](https://www.soundonsound.com/techniques/ian-shepherd-loudness-dynamics)
- [Mala (Digital Mystikz) — Red Bull Music Academy lecture](https://www.redbullmusicacademy.com/lectures/mala-5-db-to-perfection/)
- [Beginner's Guide: Preparing for Mastering — DJ Mag (Gordon, Tavini, Goz, Thomas)](https://djmag.com/longreads/beginner-s-guide-preparing-mastering)
- [Joe Lambert Mastering — Know Your Lows](https://joelambertmastering.com/mixing-advice-from-your-mastering-engineer-tip-1-know-your-lows/)
- [Stuart Hawkes — Metropolis Studios](https://www.thisismetropolis.com/engineers/stuart-hawkes/)
- [Jonathan Wyner via iZotope — How loud should my master be](https://www.izotope.com/en/learn/how-loud-should-my-master-be.html)
- [K-System — Wikipedia](https://en.wikipedia.org/wiki/K-system)

**Tier 2 — trade press / vendor data**
- [LUFS and tonal analysis of 10 top-charting dance and electronic songs — iZotope](https://www.izotope.com/en/learn/dance-electronic-analysis)
- [Mixing Bass — Sound On Sound](https://www.soundonsound.com/techniques/mixing-bass)
- [After the Loudness War: Techno Mastering — Riemann / Florian Meindl](https://riemannkollektion.com/blogs/techno-producer-knowledge-hub/after-the-loudness-war-techno-mastering-2020)
- [Wax Off Wax On: Curve Pusher Turns 20 — Attack Magazine](https://www.attackmagazine.com/features/interview/wax-off-wax-on-curve-pusher-turns-20/)
- [Mastering For Vinyl: A Practical Guide — Raretone](https://www.raretonemastering.com/post/mastering-for-vinyl-a-practical-guide-for-audio-engineers)
- [Mono bass when mastering for vinyl — Masterdisk](https://www.masterdisk.com/post/mastering-for-vinyl)
- [What is Saturation for Mixing and Mastering — Sage Audio](https://www.sageaudio.com/articles/what-is-saturation-for-mixing-and-mastering)
- [Make subs that cut through on small speakers — MusicTech](https://musictech.com/tutorials/subs-for-small-speakers/)
- [Meditate On Bass Weight: Mala — TRENCH](https://trenchtrenchtrench.com/features/meditate-on-bass-weight-how-mala-become-dubsteps-countercultural-north-star)
- [A Brief History of Early Dubstep — Museum of Youth Culture](https://www.museumofyouthculture.com/a-brief-history-of-early-dubstep/)

**Tier 3 — practitioner forums**
- [Utilizing multiband compression in mastering dubstep and heavy bass music — Gearspace](https://gearspace.com/board/mastering-forum/641506-utilizing-multiband-compression-mastering-dubstep-heavy-bass-music.html)
- [Summing low frequencies to mono for vinyl — Gearspace](https://gearspace.com/board/mastering-forum/1275202-summing-low-frequencies-mono-vinyl.html)
- [How many LUFS are you mastering to — Dogs On Acid](https://www.dogsonacid.com/threads/how-many-lufs-are-you-dogs-mastering-your-tracks-to.811971/)

**Standards**
- ITU-R BS.1770-4 (true-peak measurement) · AES TD1008 (streaming loudness recommendation)
