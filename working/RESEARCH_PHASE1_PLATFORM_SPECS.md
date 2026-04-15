---
title: Research Phase 1 — Platform Re-encode Specs (IG + TikTok)
version: 1.0
last_updated: 2026-04-15
status: draft
scope: What IG Reels and TikTok actually do to an uploaded file in 2026. Feeds master export recipe in Phase 3.
dependencies: [[RESEARCH_POSTING_QUALITY]], [[WOBAR_TD_REFERENCE]]
---

# PHASE 1 — PLATFORM RE-ENCODE SPECS

## Shared reality (both platforms)

| Spec | Value |
|------|-------|
| Container | MP4 |
| Video codec | H.264 (H.265/HEVC accepted but inconsistent — stick with H.264) |
| Audio codec | AAC, 48 kHz |
| Resolution | 1080 × 1920 (9:16) |
| Frame rate | 30 fps (24 fps also clean for slower sections) |
| Chroma subsampling | **4:2:0 enforced** — cannot be avoided |
| Color space | Rec.709 SDR — build pipeline around this |
| Bit depth delivered | 8-bit to viewer, but 10-bit source helps protect gradients through re-encode |

The chroma subsampling line is the load-bearing one. 4:2:0 throws away 75% of the color resolution. Smooth gradients (Act 2 teals, Act 3 deep purples) are the first to show banding. Cannot be defeated — only mitigated.

---

## Instagram Reels

**Ingest ceiling (what they accept):**
- File size: 4 GB max
- Bitrate: accepts up to 20–25 Mbps without rejection
- Duration: up to 90 sec for standard Reels, 3 min for newer Reels tier

**Re-encode target (what viewers actually see):**
- Final bitrate: ~3–5 Mbps for 1080p (varies by network / playback device)
- Aggressive — every pixel of headroom at upload is eaten

**Recommended upload bitrate:** 15–25 Mbps H.264 VBR (2-pass if your encoder does it). Lower than 10 Mbps is starvation — the re-encoder has nothing to work with and bands hard.

**Upload path — quality ranking (2026):**
1. Desktop web uploader (instagram.com) — current best, platform-side optimizations
2. Meta Business Suite — comparable to web
3. Mobile app with "Upload at Highest Quality" toggle ON (Settings → Account → Data Usage)
4. Mobile app without toggle — avoid

*Note: the historical "mobile on strong WiFi beats desktop" advice has flipped. Desktop web is now equal or better.*

**Safe zones (1080 × 1920):**
- Top: 210–250 px (username, audio attribution, follow button)
- Bottom: 310–440 px (caption, action buttons, audio track display)
- Right: 84 px (like / comment / share / save column)
- Effective safe area: roughly center ~910 × 1386 px

**Failure modes on visualizer content:**
- Smooth gradients → banding (worst at low bitrate)
- Fast feedback / motion smear → macroblocking
- Dark scenes → black crush + banding in shadows
- Fine grain → either eaten (grain dies) or amplified (noise)

---

## TikTok

**Ingest ceiling:**
- Web uploader: 10 GB, 60 min — preserves higher bitrate, avoids mobile retranscode
- Mobile app: 287 MB — constrained
- "Upload HD" / "Allow High Quality Uploads" toggle available on mobile posting screen (More options) — only appears for qualifying files

**Re-encode target:**
- Final bitrate: ~5–8 Mbps typical, varies by playback device and connection

**Recommended upload bitrate:** 8–12 Mbps H.264 at 30 fps (higher bloats without improving post-encode result). Some sources recommend up to 13–20 Mbps if you have the headroom.

**Upload path — quality ranking:**
1. **Web uploader (tiktok.com/upload) on stable WiFi > 20 Mbps** — best. Already in WOBAR_TD_REFERENCE.md.
2. TikTok Studio (desktop app) — equivalent to web
3. Mobile app with "Upload HD" toggled ON, on strong WiFi
4. Mobile on cellular — avoid (TikTok throttles compression to complete upload)

**Safe zones (1080 × 1920):**
- Top: ~150 px (username, "Following / For You" tabs)
- Bottom: ~340 px (caption, username overlay, action buttons)
- Right: ~100 px (like / comment / share / profile icons)
- Effective safe area: center ~880 × 1430 px

TikTok UI is more aggressive than IG on the bottom third. Plan composition for bottom-third occlusion on both platforms.

**Failure modes:**
- Same as IG, plus:
- TikTok is the first platform to show banding on soft gradients, fog, vignettes
- Compression on cellular uploads is brutal — can lose 30%+ perceived quality

---

## Consolidated safe zone for cross-posting

To avoid re-composing per platform, use the **union** of safe zones:
- Top: **250 px**
- Bottom: **440 px**
- Right: **100 px**
- Left: **0 px** (no engagement column on left side of either platform)
- Effective center for key content: ~980 × 1230 px

This is tighter than either platform alone but ensures content reads clean on both. Matches the existing WOBAR_TD_REFERENCE.md guidance ("center 60% of frame") — formalize with these numbers.

---

## Core mitigations (carry into Phase 3)

1. **Upload bitrate ≥ 15 Mbps for IG, ≥ 10 Mbps for TikTok.** Bitrate headroom is the single biggest lever — the platforms re-encode aggressively, and a starved source bands hard.
2. **10-bit source through the pipeline if possible** — even though delivered 8-bit, 10-bit source survives re-encode with less banding.
3. **Grain protects gradients.** The analog grain pipeline (WOBAR_TD_REFERENCE.md Section 5) may double as banding protection — give the encoder something to latch onto instead of smooth gradient planes. Confirm in Phase 4 benchmark.
4. **Rec.709 SDR end-to-end.** No sRGB conversions, no HDR flags.
5. **Upload via desktop web on both platforms.** Mobile is now worse on IG and has always been worse on TikTok.
6. **Compose to the cross-platform safe zone** (center ~980 × 1230 within 1080 × 1920).
7. **Never re-upload a downloaded / screen-recorded clip** — compound compression is the fastest way to trash a visualizer.

---

## Open questions (resolve in later phases)

- Does 10-bit ProRes master → H.264 for upload actually beat 10-bit H.264 direct? (Phase 2)
- Does grain protect gradients on WOBAR content specifically, or does it get eaten? (Phase 4)
- How aggressive is IG's re-encode on short vs longer Reels — does a 15s clip survive better than 60s at same bitrate? (Phase 4)

---

## Sources
- Stay Abundant — Best Bitrate & Export Settings for Instagram Reels (2026)
- Social Rails — Instagram Video Size & Format Specs 2026
- Capcut Resource — Best Bitrate for Instagram Reels
- Visnalize — Instagram-Ready Media: Reels Video Specs and Compression Guide
- Tokportal / ShortSync — TikTok Upload Video Quality Guide 2026
- RenderCut — High Quality Upload on TikTok
- Pixflow — Best Color Space for YouTube, Instagram, and TikTok Exports
- Tobia Montanari — Chroma Subsampling in Color Grading
- Kreatli / Zeely / SellerPic — Instagram Reels Safe Zone Guide 2026
