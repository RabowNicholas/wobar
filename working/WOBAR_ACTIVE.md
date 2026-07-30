---
title: Wobar Active — current context
version: 2.0
last_updated: 2026-07-30
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
**Parked (Nick, "not now"):** designing the Flow State set, and capturing sets at all. Live is ceiling-3 and still marked *undesigned*; capture also gates bucket 1 of [[working/WOBAR_SOCIAL_PLAN]].

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

### Release Schedule
**State: system live; last verified 2026-06-10 and stale since.** 16 releases, biweekly Fridays 5/29 → 12/25. 7 assets per release, each visualizer twice (TK + IG) = 10 posts per 14-day window. T-counter dates auto-calc from B6 in `RELEASE_PACKET.xlsx`.

MUR #01 shipped 2026-05-29 on time with the full packet. #02 was on track for 6/12. **#03's T-21 (6/5) was already past at last check.**

**BTS is trigger-based** — a Mirror clip clearing 1.5× baseline fires one BTS clip 24–48h later, cap 3/release. **No trigger has ever fired.** ⚠ This system predates the peer-layer decision and is scored on IG performance, which [[working/WOBAR_SOCIAL_PLAN]] no longer tracks — it needs reconciling or retiring.

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

---

## STANDING TRAPS

- **Repost outreach and label doors conflict.** A repost *publishes*. Labels require unreleased **and unpublished**. Released tracks and flips only for repost outreach; unreleased originals stay on private links.
- **Uncleared flips cannot reach DSPs** and are permanently non-monetisable — marketing, never a listener source.
- **Never delay a release on a TouchDesigner build.**
- **Borrowed numbers read as first-party results** — this has now happened repeatedly. Check provenance before a number becomes load-bearing, especially the best one.
