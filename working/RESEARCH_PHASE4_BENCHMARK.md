---
title: Research Phase 4 — Torture-Test Benchmark Protocol
version: 1.0
last_updated: 2026-04-15
status: ready to execute
scope: Controlled test to validate the export recipe from Phase 3 against real platform re-encodes. Answers open questions flagged in Phases 1–3.
dependencies: [[RESEARCH_POSTING_QUALITY]], [[RESEARCH_PHASE1_PLATFORM_SPECS]], [[RESEARCH_PHASE2_TD_EXPORT]], [[WOBAR_TD_REFERENCE]]
---

# PHASE 4 — BENCHMARK PROTOCOL

## Goal
Validate the Pipeline C recipe (image sequence → FFmpeg → upload) against IG Reels and TikTok re-encodes. Prove or disprove the grain-as-banding-protection hypothesis. Find the breaking points.

## The torture-test clip

One 30-second clip. Five 6-second sections, one failure mode each. Built in TD using existing WOBAR networks so it's representative of real content, not synthetic test patterns.

| Section | Duration | Source | Tests |
|---------|----------|--------|-------|
| **1. Smooth gradient** | 0:00–0:06 | base_act2 underwater spiral, no grain layer | Banding on smooth teal gradient. The worst-case for 4:2:0. |
| **2. Fast feedback / smear** | 0:06–0:12 | base_act3 feedback TOP chain at high scale/opacity | Macroblocking on fast motion, smear artifacts |
| **3. Dark + sub-bass pulse** | 0:12–0:18 | base_act1 or base_act5 near-black with sub-bass reactive pulse | Black crush, shadow banding, low-light macroblocking |
| **4. Fine analog grain** | 0:18–0:24 | Act 4 visual WITH full grain pipeline (Section 5 of TD_REFERENCE) | Grain preservation vs grain-eaten-to-noise |
| **5. Saturated color** | 0:24–0:30 | Act 3/4 at peak saturation — deep purple or cathartic red | Chroma subsampling color shift, saturation clipping |

Keep composition inside the cross-platform safe zone (center 980 × 1230). Audio: use a track with clean sub-bass for Section 3 trigger.

## Render & assembly

Exact recipe from WOBAR_TD_REFERENCE.md Section 8 (Pipeline C):

1. TD Movie File Out → Image Sequence → PNG 16-bit, 30 fps, 1080 × 1920
2. FFmpeg assembly with the documented command, CRF 18, `-tune grain`, Rec.709 tagged

Also render a **control** using the old Pipeline A (MPEG 4 → HandBrake) for direct comparison. This answers "how much does Pipeline C actually win by."

Two files:
- `wobar_torture_pipelineC.mp4` (new recipe)
- `wobar_torture_pipelineA.mp4` (old path, control)

## Upload matrix

Four upload events total. Same day, same WiFi:

| # | File | Platform | Path |
|---|------|----------|------|
| 1 | Pipeline C | Instagram Reels | Desktop web (instagram.com) |
| 2 | Pipeline C | TikTok | Desktop web (tiktok.com/upload) |
| 3 | Pipeline A | Instagram Reels | Desktop web |
| 4 | Pipeline A | TikTok | Desktop web |

Post each as an unlisted / draft or immediately archive after upload + screen-record. Do not leave up — this is a test, not content.

**Optional 5th and 6th uploads** if time allows: Pipeline C via mobile app on both platforms, to verify desktop-web-beats-mobile empirically.

## Capture & scoring

For each of the 4 uploaded files:
1. Let the platform finish processing (wait 2–5 min after upload)
2. Open the post on the platform's native app on phone
3. Screen-record playback at full quality
4. Pull the screen recording off the phone to desktop

Score each of the 5 torture-test sections per upload on these dimensions (0–3 scale):
- **Banding** (0 = none, 3 = severe)
- **Macroblocking** (0 = none, 3 = severe)
- **Color shift vs master** (0 = matches, 3 = obviously wrong)
- **Grain preservation** (0 = preserved cleanly, 3 = eaten to noise or smoothed away)
- **Overall perceived quality** (0 = indistinguishable from master, 3 = visibly broken)

Score in a small table saved to `working/RESEARCH_PHASE4_RESULTS.md`.

## Decisions this benchmark makes

1. **Pipeline A vs Pipeline C delta** — how much quality is Pipeline A actually losing? If small, Pipeline A might stay as a quick-iteration tool.
2. **Grain hypothesis** — does adding grain (Section 4) band *less* than the no-grain gradient (Section 1)? If yes, grain is a mitigation. If no, it's a texture choice only.
3. **CRF sweet spot** — if CRF 18 is overkill (file survives at CRF 20), can save render time and disk on posted finals.
4. **IG vs TikTok aggressiveness** — which one degrades harder on which failure mode. Informs per-platform recipe tweaks.
5. **Do we need 16-bit PNG** — if 8-bit PNG holds up on the gradient section, we halve disk footprint.

## Time budget
- TD render: 30s clip × 5 sections × image sequence ≈ 15–30 min render + assembly
- Uploads: 4 × ~5 min processing + capture ≈ 40 min
- Scoring: 30 min
- Write-up: 30 min

**Total: ~2.5 hours, single sitting.**

## Prerequisites before executing
- [ ] Confirm FFmpeg installed (`ffmpeg -version`)
- [ ] Torture-test clip sections defined as TD timeline moves or separate Base COMP sequence
- [ ] Fresh IG and TikTok accounts or willingness to archive posts immediately
- [ ] Phone for screen-recording with enough storage
- [ ] Quiet block of 2.5 hours

## After Phase 4
Results feed back into `reference/WOBAR_TD_REFERENCE.md` Section 8 — adjust CRF, confirm or kill the grain hypothesis, add any platform-specific tweaks discovered. Close the research loop.
