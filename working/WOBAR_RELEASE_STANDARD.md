---
title: WOBAR Release Standard
version: 0.1
last_updated: 2026-06-10
status: live — accretes per session; promote to reference/ when stable
scope: Release-readiness gates for WOBAR visualizers. Every build runs these gates before it ships. Every miss caught in a session becomes a new line here.
dependencies: [[reference/WOBAR_EMOTIONAL_REGISTER]], [[reference/WOBAR_TD_AGENT_RULES]], [[reference/WOBAR_TD_REFERENCE]]
---

# WOBAR RELEASE STANDARD

A visualizer is release-ready when it passes all three gates. This doc grows: when a session catches a quality miss not covered below, add the line. Origin: heave stress test, 2026-06-10.

---

## Gate 1 — Technical

- [ ] 60 fps sustained through full song playback (perf check, not eyeball)
- [ ] Zero new errors (`td_get_errors` on network root; pre-existing third-party internals documented, not silently ignored)
- [ ] Master export NC-safe: `mjpa` .mov (or PNG sequence) + `pcm16` audio, `audiochop` → locked-to-timeline 44100 source, `fps = me.time.rate`
- [ ] Full-song render completes start to finish, audio synced (spot-check first 10s / a drop / last 10s)
- [ ] 720×1280 master minimum (NC cap 1280); platform transcode happens outside TD

## Gate 2 — Brand

- [ ] Emotional-register check passes for the target act (`WOBAR_EMOTIONAL_REGISTER.md`) — read the act's "what breaks it" list and check each item explicitly
- [ ] Act's documented failure modes checked by name. Act 4: (1) still water — no dead/static stretches, (2) missing warmth — discharge without color activation, (3) hypnotic-instead-of-driving
- [ ] Palette discipline: no pure white, no neon/glowstick hues, desat-psychedelic range only (`WOBAR_TD_REFERENCE.md §4`)
- [ ] Could NOT ship as a generic bass-artist visual — names at least one mirrors/encounter decision

## Gate 3 — Craft

- [ ] No dead frames: something is always moving (motion floor — camera drift, churn, breath), independent of audio
- [ ] Post chain ON and graded for the piece's register (grade / bloom / grain minimum; CA where it serves)
- [ ] Grain present — banding protection through platform 4:2:0 re-encode
- [ ] Composition deliberate at 3 checkpoints: intro frame, biggest drop, outro frame — screenshot each and look
- [ ] Audio reactivity normalized record-first (p10/p90, p95 sparse bands) — no raw-channel bindings
- [ ] All performance values on ctrl_master custom pars — nothing hand-buried in op fields

---

## Session log — standard additions

| Date | Added | Source miss |
|------|-------|-------------|
| 2026-06-10 | Seed version — all three gates | heave stress test: still-water + cool-monochrome gaps caught at brand check |
