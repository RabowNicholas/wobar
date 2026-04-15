---
title: Research — Posting Quality (Compression + TD Export)
version: 1.0
last_updated: 2026-04-15
status: in progress
scope: Research plan for mitigating quality loss on visualizer posts to IG Reels and TikTok. Covers platform re-encode behavior, TD export ceiling, master file spec, and empirical benchmark.
dependencies: [[WOBAR_TD_REFERENCE]], [[WOBAR_ACTIVE]]
---

# RESEARCH — POSTING QUALITY

## Research question
What's the maximum quality visualizer I can get onto IG Reels and TikTok given my current TD export ceiling and platform re-encoding?

## Why this matters
Act 2 underwater gradients, Act 3/4 feedback smears, and grain-heavy analog pipeline are all compression-sensitive. Current TD export path (Free license → MPEG 4 → HandBrake) is a constraint I haven't pressure-tested. Platforms re-encode aggressively and inconsistently across upload paths. Without a locked recipe, quality is unpredictable post-by-post.

---

## Phase 1 — Platform re-encode behavior

Desk research. ~half day.

For both IG Reels and TikTok in 2026:
- Accepted container, codec, max bitrate on ingest
- Re-encode parameters after processing: target bitrate, codec, chroma subsampling (4:2:0 vs 4:2:2), color space, bit depth
- Upload path differences — which preserves the most quality
  - IG: mobile app vs web uploader vs Meta Business Suite vs scheduling tools
  - TikTok: mobile app vs web (already known 10GB vs 287MB) vs TikTok Studio vs scheduling tools
- Known failure modes for motion-heavy / gradient-heavy / dark content
- Safe zones — confirm current values (top ~250px, bottom ~340px) against current UI

**Deliverable:** one-page spec sheet per platform saved to working/.

---

## Phase 2 — TD export ceiling

Desk + hands-on. ~half day.

Evaluate three pipelines:

1. **Current** — Free license → MPEG 4 out of TD → HandBrake H.264
2. **Upgrade** — Commercial/Pro license → h264nvgpu direct from TD
3. **Sidestep** — Image sequence (PNG or EXR) from TD → FFmpeg assembly

For each: quality ceiling, file size, render time, workflow friction, cost.

The image sequence route is the most likely to be overlooked — no compression at render, full control at assembly, works on Free license. Worth real benchmark.

**Deliverable:** decision matrix. Pick one as default export path.

---

## Phase 3 — Master file spec

Synthesis. ~1 hour.

From Phase 1 + 2, lock a single master export recipe that:
- Feeds the platform enough bitrate that their re-encode isn't starved
- Survives chroma subsampling without color shift on Act 2 teals / Act 3 deep purples / Act 4 saturated reds
- Doesn't band on gradients (dither at export if needed)
- Preserves grain as grain, not as noise

**Deliverable:** write locked recipe into `reference/WOBAR_TD_REFERENCE.md` Section 8, replacing or augmenting current export table. Include upload protocol (which path to use).

---

## Phase 4 — Benchmark

Hands-on. ~half day spread over 2 days.

One 30-second torture-test clip, five sections:
1. Smooth gradient (Act 2 underwater register)
2. Fast feedback (Act 3/4 smear)
3. Dark + sub-bass (black level ceiling)
4. Fine grain (analog texture preservation)
5. Saturated color (chroma subsampling stress)

Export via chosen pipeline. Upload via chosen path. Screen-record result from the live feed. Compare to master side-by-side on the five sections. Iterate recipe if needed.

**Deliverable:** pass/fail notes per section. Recipe adjustments if anything breaks.

---

## What we learn along the way
Content-side mitigations (grain protecting gradients, motion budget, black level ceiling) surface during Phase 4. No upfront research — benchmark reveals what breaks.

## Final output
Updated `reference/WOBAR_TD_REFERENCE.md` Section 8 with a locked export recipe and upload protocol. That's the artifact that makes this research permanent.
