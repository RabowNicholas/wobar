---
title: Wobar Active — current context
version: 2.2
last_updated: 2026-08-04
status: live
scope: The current state of every live thread — what it is, where it stands, and what is genuinely unresolved. **Context, not a task tracker.** Nick tracks his own work; this file exists so a session can start already knowing the state of the world. Decisions and their reasoning live in the governing docs; history lives in git and [[working/WOBAR_SESSION_LOG]].
dependencies: [[WOBAR_CONTEXT]]
---

# WOBAR — CURRENT CONTEXT

**What belongs here:** what is live, what is decided, what is blocked, what is genuinely open.
**What does not:** next-action lists, progress narration, session recaps. Those are work tracking — [[working/WOBAR_SESSION_LOG]] holds the history, git holds the changes, and Nick holds the work.

Retired threads move to [[working/WOBAR_CLOSED]], which is worth reading — it records **what was tried and why it was dropped**, so dead ideas don't get re-proposed.

---

## POSITION

22 Spotify monthly listeners · 55 SoundCloud followers (11 tracks) · 400 Instagram followers · **0 label releases · 0 demos ever sent** · not on Beatport.

**A local presence and a skill set, not an audience.** Those numbers are the arithmetic of the inputs, not underperformance — this is a cold start, and it needs the opposite response to a conversion problem. Baselines owned by [[working/WOBAR_GROWTH_PLAN]].

**Assets that are rare at this stage:** Flow State (Nick is on the *buying* side — he books DJs) · a working TouchDesigner AV practice · `wobar.music`, live and the strongest expression of the world anywhere.

---

## THREADS

### Goal Re-Specification — settled 2026-07-30
**State: the doc work is done.** [[working/WOBAR_ROADMAP]] §1 is governing: **"12 months: people who come back."** A listener hears it once, a fan returns — the same test locally (a second night) and online (a repeat listen). Local and online are one goal with two expressions.

Written with it: **§1.1** what a fan is (returns → seeks it out → passes it on; **fan ≠ follower**; ladder **listener → fan → Wanderer**) · **§1.2** duration not reach · **§5** the return measures · **[[working/WOBAR_SURFACES]] §1.5** the duration axis.

**Unexploited and free, none ever used:** Spotify listener segments (closest thing to a return counter that exists — ⚠ exact field names unverified) · asking the room at Flow State who came for Wobar · the Spotify editorial pitch, one per release · Beatport distribution · two verified-open label doors, **Deadbeats** (`bit.ly/Demos4Deadbeats`, four fields) and **Jadū Dala** (`jadudala@gmail.com`, private links).

**Open:** the Mirror hasn't been re-read against a return goal, and depth 2 has no other home.
**Parked (Nick, "not now"):** designing the Flow State set, and capturing sets at all. Live is ceiling-3 and still marked *undesigned*; capture also gates **bucket 1 (Performance)** of [[working/WOBAR_SOCIAL_PLAN]] — which as of 2026-08-03 is the **top** of the peer funnel, so that funnel currently has no entry point.

### Give-Back Content — the niche
**State: subject locked 2026-08-04, no format.** Governing doc is [[working/WOBAR_GIVEBACK_NICHE]]; evidence is [[working/RESEARCH_STORYTELLING]].

**Locked:** audience is **DJ-producers who do both** · vocabulary is **tension and release** · thesis is **the mechanic never changes, only the scale does** · content comes from a six-rung scale ladder, where rungs 2–5 are the territory and the **3↔4 crossing is the lane**.

**Why that audience** — structural, not demographic. A pure producer works rungs 1–3 and 5; a pure DJ works rung 4. Only someone who does both has felt the mechanic at both ends, so the thesis is **checkable against their own memory rather than taken on faith** — the strongest position available to someone with no credential.

**The bucket list changed underneath it.** CUTDWN's list adopted verbatim — **performance / music / give-back** — displacing memes, which are demoted to a format rather than retired (nothing was disproved; it lost a taxonomy argument). Reasoning at the point of decision in [[working/WOBAR_SOCIAL_PLAN]] §3 and §3.5.

**Three constraints the research imposes, and they bind hard:** show, never explain — abstract posts about narrative score 0 while a writeup of a set actually played scored 648 · say **`tell a story`**, never **`storytelling`** (measured: the noun is thin in every craft sub and saturated in r/musicmarketing — it is a marketer's word) · think in public, never claim results.

**A second branch exists and is a sibling, not a child:** brand psychology, taught as analysis rather than testimony. Round designed and unrun — [[working/RESEARCH_PLAN_BRAND]], blocked on WebSearch budget.

**Open:** **neither branch has a format.** Both have a subject and no object, and the show-don't-explain constraint means the object needs a specific set Nick actually played. Also open: whether the flagship claim carries numbers at all (§4 argues it must not — the proportions are free and fixing them is both false and the guru posture) · whether the two branches share a name or a channel · the listener-facing branch, deferred not dropped.

### Master Chain — built 2026-08-01
**State: built, verified, and saved as an Ableton template.** First track taken all the way through. Wobar now masters in-house, from a fixed template, with only two decisions per track — EQ (0–2 moves) and Maximizer Gain.

**Two docs, two jobs:** [[working/WOBAR_MASTER_CHECKLIST]] is the procedure — open it to work. [[working/WOBAR_MASTER_CHAIN_V1]] holds the reasoning and the change log. The form-level posture is in [[reference/WOBAR_SONIC]].

**The upstream half matters as much as the chain:** production sets now carry a permanent Utility so mixes render at ~−16 LUFS-S / −6 dBFS. The first mix to the desk arrived at −7.7 LUFS-I and +1.6 dBTP off an empty master bus — gain, not damage, but it meant the master was being asked to absorb 9 dB. Done right, the mastering trim lands at 0.00 and **becomes a mix diagnostic**: a track needing +5 is telling you something before you've heard a note.

**Decided:** God Particle **100%**, not the researched 35% — level-matched A/B on real material, and 35% sat inside the doc's own "too low" band · **IRC 5** on the limiter · sub mono below 120 Hz · **44.1 kHz catalog-wide**, never converted mid-pipeline · Pro-MB reframed as **insurance, not an active stage**, because Nick's basslines rarely move and the sub-evening problem is already solved in the writing.

**Deliberate deviation:** landed at **−8 LUFS-S** against the doc's −9 to −10, on Delta evidence that only the leading edge of the transient was being removed. Logged as a decision. The counter-argument is unchanged — platforms normalize toward −14, so the loudness doesn't reach the listener while the transient cost does.

**Genuinely open:** **Soft Clip is owned and untested** — it's inside the Maximizer, the vault had recorded it as a gap, and transient clipping ahead of a limiter is how bass music gets level without pumping. It is the highest-value unexplored move here. Also: God Particle remains largely unmeasured and the low-Amount half of that mitigation is now gone by choice · Pro-MB's threshold was calibrated on a ±1 semitone bassline, the easiest possible case · integrated loudness has still only been measured over a looped drop, never a whole arrangement · no comp dataset, so spectral targets are judgement rather than measurement.

### Mirror Threshold — the SMS door into the Ether
**State: spec complete, build not started, blocked on 10DLC** — days-to-weeks of carrier approval, and no door copy works without a number.

**Decided and locked** (`MIRROR_THRESHOLD_SPEC`): **Twilio SMS**, plain — RCS and iMessage-blue ruled out (no A2P blue-bubble API; RCS renders green and reads corporate; Sendblue/LoopMessage carry Apple-ToS ban risk). Local **10DLC long code**. Intentions **stored and sacred** — pinned per thread, never marketing. Automate **only** the two door replies plus STOP/HELP; everything past the door is human. Cost <$50/mo. Stack: Next.js / Neon / Vercel.

**The backbone already exists** in `wobar-landing-page` — `subscribers` + `messages` tables, `api/sms/inbound`, `api/subscribe`, `api/admin/broadcast`, `/admin` inbox, `jose` auth. The real delta is the intention state machine (`state`, `intention`, `crossed_at`) plus ritual copy, not the from-scratch spec code.

**Design note worth keeping:** a `source` field (`invited` | `found`) is one column and the only way to ever tell whether passive placement works. Per spec §0 the two must not be confused. **Acquisition is ~40 right people, invited personally — not volume.**

The Mirror is the `mirror` path inside the Terminal, discovered by wandering.

### Terminal Rebuild — wobar.music
**State: LIVE and public.** Verified in-browser 2026-07-27 — the mark in glowing broken circles, true black, CRT scanlines, the daemon typing in register. Three vault docs had said parked/not-started; they were wrong. **Vector-void is shipped, not merely locked.**

**Form** (`WEB_HOME_SPEC`): the site *is* the Ether made visible, built as an early-RPG terminal you type into — wandering as the literal interaction. Renders the void without depicting the sacred center (§8). Paths: `passages` / `listen` / `wander`+`lore` / `mirror` / `offer`. Guide is **the daemon** — Unix daemon + Socratic *daimonion*, guides by deflection, wayfinder not guru.

**Hard rail:** the daemon's AI **routes and selects from an authored bank, never free-generates.** Free generation breaks Law 0 and the anti-guru rail. Bank lives in `WOBAR_COPY` §daemon.

**Open:** how much of it is actually built past the shell (paths, Sanity load) is unknown · the 30-fragment wander pool isn't loaded into Sanity · **the first Passage is owed and must be Nick-authored** — Passage mode is his verse, never generated · offering length/format limits · naming the terminal/world as a whole.

### World Doc — `WOBAR_WORLD.md` v0.6
**State: teardown live, doc still draft.**

**Lexicon locked:** **Mirror** (one thing, mirrors-all-the-way-in) · **seeing** (the act of entering) · **Wanderer** (member) · **the Ether** (the *interior* — web home + SMS are two ways in, not the SMS list) · **glimpses** (list content). **The mark = two broken circles**, the faceless face. **The Passage** = the written body per Portal EP.

**Cosmology:** the entity is a two-axis vertical — timeless self × all-possibility self. Facelessness is over-determined. Void poems are a translation layer, POV Wobar→down→all of us, under figurative-licence and empower-never-instruct guardrails. §8 is the anti-guru rail.

**Open:** §1 ground-truth placement (in-file vs Nick-eyes-only, now the cosmology is deeper) · the first **void poem** and first **Passage**, both untested voice · **eras** flagged as a mechanic and not formalised (Obscura is a different era, parked) · when the doc leaves draft.

### down_bad_3stack v002 — Act 4 Phase 1 visualizer
**State: full pipeline wired and brand-reviewed. Not saved as a canonical checkpoint, not final-rendered.** 720×1280 (NC licence caps 1280×1280).

**Video timing:** `movie_in` in `specify` playmode, index `max(0, min((me.time.seconds - Videodelay + (Videoskipdur if me.time.seconds >= Videoskipat else 0)) * 23.978347, numImages-1))`, plus a second jump for the final chorus. Set: `Videodelay=-4 · Videoskipat=82 · Videoskipdur=45 · Videojump2at=137 · Videojump2to=40`. Song 193.72s vs source video 183.62s. **Cook rate 60→30** — the comp pipeline couldn't sustain 60 and `me.time.seconds` went slow-mo; `time.end` 11650→5825 preserves 194.17s.

**Audio reactivity:** `base_audio_react` baseCOMP publishes 8 normalized channels (`sub_bass_n, bass_n, mid_n, high_n, energy_n, sub_pressure_n, growl_n, transient_n`), p10→0 / p90→1, p95 for sparse transients. Binding pattern: `Base + React * pow(clamp(audio_n, 0, 2), Curve)`.

**What failed, and why** — worth not repeating: beat pulse as edge-brightness flash didn't read on binary line art · bass→Edgethicken inverted because blur sits before edge · mid wasn't punchy enough (vocals) · transient works analytically but is too sparse to see. **Landed on beat pulse driving global CA.**

**Export gotcha:** `movie_out` must take audio from `base_audio/audio_in`, **not** the sequential clip — that was the bug causing audio-from-zero in export while preview stayed synced.

**Deferred by Nick as "not a big deal":** no forward propulsion, CA possibly too aggressive at 8px, palette unverified, no discharge moment.

### POPX v1.4.0
**State: installed at `/POPX_1_4_0` in the live project; docs updated; never used on a real build.** TD build 2025.32460 stays put — the mismatch warning against POPX's 2025.32820 target is accepted.

**What changed in 1.4.0:** new **Filter** modifier (6 algorithms incl. One Euro adaptive smoothing) · **breaking:** per-curve toggles removed from Sweep / Move Along Curve / Orient Curve, mapping is now auto from TOP rows · **ramp UI renamed across ~10 modules** (`Ramp TOP → Custom * TOP`, `Open … Ramp → Open … Ramp Editor`) · Path Tracer gains DLSS (Windows/NVIDIA only — M1 stays on SVGF/OptiX) · `Emssion*` typo fixed to `Emission*`.

⚠ **Opening any older network that uses Color Modifier ramps, Texture Falloff remap params, or Sweep/Move-Along-Curve TOP modulation may hit silently renamed params.**

### crease_veil — Act 3 ENCOUNTER visualizer
**State: mid-build at `/project1/crease_veil` in a live unsaved `NewProject.1.toe` on the Desktop.** Checkpoint `crease_veil_v001.tox` saved. **Latex read LOCKED.**

**The root insight, and it cost two failed mechanics to find:** **SEEN** (luminous = window, watching) and **FELT** (pressure imprinted in a front-lit surface = skin, trapped) read by *opposite* cues. **Glow always wins and turns the veil into a window.** Locked the FELT pole. Front raking light → sliding specular is the surface-toward-you cue. Nick: *"feels trapped now."*

**Then the glove model** (Nick's ref — a latex glove stretched till you see through it): opacity drops where stretched, colored forms bloom through the thinned spot, plus tension-whitening and wet glints.

**Build:** 2D, glslTOP `membrane` — blobs → comp_height → displace (noise warp) → blur (dome 42 / presence 90); ambient back-field; `latex_grain` micro-normal; motion via `noise_drift` + `noise_breath` CHOPs.

**Direction (Nick):** pivot the height source to POPX **DLA** branching tendrils rendered top-down — worms burrowing under skin, growth as escalation. Keep the membrane shader, swap the source only. **POPX is not loaded in that project** (fresh NewProject); crib `example_projects/DLA.toe`. Nick also called the cadence **too slow**.

### Master Chain v1 — the audio side of the practice
**State: template written and governing, never run on a real track.** [[working/WOBAR_MASTER_CHAIN_V1]] holds the chain, every value, and the reasoning per value.

**Shape:** trim → God Particle (35%) → Pro-MB (one sub band, 20–90 Hz, Dynamic Phase, Range capped −3 dB) → Ozone (Imager mono <120 Hz → EQ → Exciter low-band → Maximizer IRC IV, −1 dBTP). Per track only two things move: two broad EQ decisions and the Maximizer threshold.

**Designed for bounded error, not optimality** — the monitoring cannot verify anything below 55 Hz, so every value is chosen so that being wrong is survivable. The Range cap, linked stereo, low GP Amount and modest limiting all exist for that reason.

**Research behind it:** [[working/RESEARCH_MASTER_CHAIN_TOOLS]] (tool capability + the shared theory) · [[working/RESEARCH_MASTERING_EDM_DUBSTEP]] (practice, sources tiered by verifiability, eight live contradictions between credible engineers).

**Decided:** streaming and large-system weighted equally · vinyl constraints dropped, digital only · loudness de-prioritised, work to short-term and let integrated fall out · Goz's *loop* and his *permission on distortion* adopted, his meter-hostility explicitly not (it rests on monitoring Nick doesn't have) · sub dynamics resolved as flatten note-to-note / protect within-note envelope / constant ceiling with contrast built above.

**Open:** God Particle is unmeasured and level-dependent, so it's a bounded but unknown quantity in the middle of the chain (protocol exists, parked) · no comp dataset, so every spectral target is judgement not measurement · rig offset predicted (low-mid and treble deficit) but unconfirmed · IRC 5 vs IRC IV untested on real material · the analyzer that would close the first three is designed and parked by decision.

**Accepted risk, stated once so it isn't re-litigated:** systematic low-end error is invisible on this rig and permanent once released. Mitigated by the Range cap, mono-below-120, correlation checks and system trips before release. Not eliminated. Nick's call, made knowingly — he wants 90% now and a professional engineer later.

### Ear Training
**State: not started.** The only skill investment on the audio side that doesn't depend on fixing anything else first.

**Why it's live:** Goz's bar — *"an engineer who can't spot 1k from 2k from 5k, they haven't learned the fundamentals."* Nick's own framing is that he doesn't fully understand what the chain is doing. Relative frequency recognition is free, compounds, transfers to mixing and sound design, and **works despite bad monitoring** — interval recognition doesn't need a flat room, which makes it the one thing the KRK/M50x problem cannot block.

**Open:** method and tool unchosen · cadence unchosen · whether it earns a log at all, or is simply practised.

### Mixing Research — the mix standard that doesn't exist
**State: not started.** The asymmetry that exposed it: a master chain is now documented to the value level, and there is no equivalent for the mix, when the mix is where most of the leverage actually sits.

**The evidence it rests on:** every Tier 1 engineer in the research says the same thing, Beau Thomas most directly — *"a good mix-down that is very controlled and sounds great will nearly always become really loud easily."* Nick mixes his own tracks, so everything the master chain currently **bounds** is something the mix could **eliminate**: sub note consistency at source · sub written mono from the start · kick/sub phase alignment · deliberate frequency division (sub 40–80, kick 90–180) · sparse mid-range and negative space as the genre's actual technique.

**Open:** scope — mix standard, or research first then standard · whether it gets the same treatment as the chain (constraints → defaults → verification tests → change log) · whether an audio build log should exist at all, given [[working/TD_BUILD_LOG]] is a working feedback mechanism pointed at the visuals while the music, which is the product, has none.

### Headphone Correction
**State: not applied.** Cheapest fix available anywhere in the practice — free, minutes, and it converts the most detailed monitoring device from actively misleading into the best reference in the room for 80 Hz–10 kHz.

**The problem it addresses:** the ATH-M50x measures V-shaped — elevated 80–200 Hz ("woolly"), a dip at 300–400 Hz, boosted treble, sub-bass roll-off that gets over-corrected for. The KRK Rokit 5 is also bass-forward. **Both devices lie in the same direction**, so cross-checking one against the other cannot catch the shared bias. Predicted consequence: masters that come out thin in the low-mids and dull up top.

**Trap:** correction EQ belongs on the **monitor path only** — never in the render or export chain. A correction curve that reaches the bounce inverts itself into the master.

**Open:** which profile source · where in the signal path it sits given the DAW · whether the KRKs are worth correcting too, or whether a measurement mic should come first so the room and the speaker are separated rather than conflated.

---

## STANDING TRAPS

- **Repost outreach and label doors conflict.** A repost *publishes*. Labels require unreleased **and unpublished**. Released tracks and flips only for repost outreach; unreleased originals stay on private links.
- **Uncleared flips cannot reach DSPs** and are permanently non-monetisable — marketing, never a listener source.
- **Never delay a release on a TouchDesigner build.**
- **Borrowed numbers read as first-party results** — this has now happened repeatedly. Check provenance before a number becomes load-bearing, especially the best one.
- **A scraped zero is not evidence until a control query passes in the same pass.** Same error class as the above, and it cost a confident false finding on 2026-08-03 — *"track endings are severely under-discussed"* was built entirely on rate-limit responses recorded as zero results. **The number 0 looks like data, which is why it survives review.** Harness and the full rule: `scripts/reddit_research.py`, [[working/RESEARCH_STORYTELLING]] §9.
