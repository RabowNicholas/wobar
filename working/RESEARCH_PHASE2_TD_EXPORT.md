---
title: Research Phase 2 — TD Export Pipeline Evaluation
version: 1.0
last_updated: 2026-04-15
status: draft
scope: Compare three TD export pipelines for quality, cost, workflow friction. Picks default path. Feeds Phase 3 master recipe.
dependencies: [[RESEARCH_POSTING_QUALITY]], [[RESEARCH_PHASE1_PLATFORM_SPECS]], [[WOBAR_TD_REFERENCE]]
---

# PHASE 2 — TD EXPORT PIPELINE EVALUATION

## The three pipelines

### A. Current — Free license → MPEG 4 → HandBrake H.264
Movie File Out TOP → MPEG 4 Part 2 (.mp4) → HandBrake re-encodes to H.264.

### B. Upgrade — Commercial/Pro license → h264nvgpu direct
Movie File Out TOP → H.264 (.mp4) using NVIDIA hardware encoder, single pass.

### C. Sidestep — Free license → image sequence → FFmpeg
Movie File Out TOP in Image Sequence mode → PNG or 16-bit TIFF / EXR frames → assemble externally with FFmpeg to H.264.

---

## Decision matrix

| Dimension | A. Free + HandBrake | B. Pro h264nvgpu | C. Image sequence |
|-----------|---------------------|------------------|-------------------|
| **Quality ceiling** | Low–moderate | High | **Highest** |
| **Generational loss** | 2 encodes (MPEG 4 → H.264) | 1 encode | 0 until FFmpeg stage |
| **Bit depth preserved** | 8-bit (MPEG 4 Part 2) | 8-bit at encode | **10/16-bit** (PNG 16-bit, EXR 32-bit float) |
| **Chroma at master** | 4:2:0 forced | 4:2:0 (h264nvgpu) | Full 4:4:4 until FFmpeg |
| **Dither control** | None | None | **Full** (x264 tune, AQ, grain retention) |
| **Cost** | $0 | ~$600 Commercial license | $0 |
| **Render speed** | Fast | **Fastest** (GPU encode) | Slow (disk I/O bound) |
| **Disk footprint per 30s @ 1080×1920 @ 30fps** | ~40 MB | ~40 MB | ~900 MB–3 GB (PNG) to ~15 GB (EXR) |
| **Workflow friction** | Two-tool, manual HandBrake | One-tool | Two-tool, needs FFmpeg command |
| **Hardware needed** | Any | NVIDIA GPU | Fast NVMe SSD strongly recommended |
| **Feedback loop during iteration** | Medium (MPEG 4 preview fast) | Fast | Slow (wait for sequence render) |

---

## Key insights

**Pipeline A is a dead end.** MPEG 4 Part 2 is a 25-year-old codec and acts as a lossy intermediate. Every pixel that hits HandBrake has already been compressed once. For a visualizer that's about to go through another aggressive re-encode on IG/TikTok, that's three generations of loss total. Retire this path.

**Pipeline C is the sleeper pick.** TD writes uncompressed frames to disk. Nothing is lost at render. FFmpeg then does a single, fully controllable encode to H.264 with every knob available: CRF target, 2-pass, x264 tunes (`grain` is particularly relevant for the analog grain pipeline), dithering on 16-bit → 8-bit conversion, precise chroma handling. This is how VFX pipelines have always worked — TD's image sequence mode is just the TD-native way to tap that pattern. Quality ceiling is the highest of the three, and it costs nothing.

**Pipeline C's real cost is iteration speed.** Rendering a 30s clip as 900 PNGs takes longer than rendering an MPEG 4, and eats disk. Not great for dial-in sessions where you render 20 variations. Good for final exports, not for iteration.

**Pipeline B is the production answer if budget allows.** $600 once for fast single-encode H.264 direct out of TD. Worth it if posting volume ramps up. Quality is within margin-of-error of C for the delivery format (both hit 4:2:0 8-bit H.264 eventually; C has more control over *how* it gets there). C gives marginally better gradient protection if dither is configured well.

---

## Recommended approach

**Two-tier workflow:**

- **Iteration / dial-in renders:** Pipeline A (Free + HandBrake) or raw MPEG 4 out of TD for quick preview. Never posted.
- **Final / posted exports:** Pipeline C (image sequence → FFmpeg) until a Commercial license is justified. Then Pipeline B.

This splits the iteration speed problem (fast feedback when dialing) from the quality problem (lossless master when publishing). Nothing currently posted would come from Pipeline A.

---

## Pipeline C — concrete setup

**TD side (Movie File Out TOP):**
- Type: Image Sequence
- Image File Type: PNG (start here — good balance; EXR if HDR-style gradient work reveals banding)
- Bit Depth: 16-bit
- Filename pattern: `frame_######.png` in a per-render subfolder
- Match project cook rate to 30 fps before rendering

**Disk prep:**
- Allocate ~1 GB per 30s of 1080×1920 PNG 16-bit
- Use NVMe SSD — HDD will bottleneck the frame writes

**FFmpeg assembly (final encode target: 18 Mbps H.264 CRF 18):**
```
ffmpeg -framerate 30 -i frame_%06d.png -i audio.wav \
  -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p \
  -colorspace bt709 -color_primaries bt709 -color_trc bt709 \
  -tune grain -x264-params "aq-mode=3:aq-strength=0.8" \
  -c:a aac -b:a 320k -ar 48000 \
  -movflags +faststart \
  output.mp4
```

Key flags:
- `-crf 18` — quality-targeted encode, visually lossless against source
- `-preset slow` — more time, better compression
- `-tune grain` — preserves grain / analog texture instead of smoothing it into mush
- `aq-strength=0.8` and `aq-mode=3` — adaptive quantization that protects dark areas and gradients
- `-colorspace/primaries/trc bt709` — explicit Rec.709 tagging so platforms don't second-guess
- `-movflags +faststart` — metadata at front of file for clean upload

**Audio side:** export audio separately from TD (or from original source). FFmpeg muxes with the video in the same command. Avoids TD's audio codec quirks.

---

## Open questions (test in Phase 4)

1. Is 8-bit PNG sufficient, or does 16-bit PNG survive the pipeline noticeably better on Act 2 gradients?
2. Does `-tune grain` actually protect the analog grain pipeline, or does it make banding worse elsewhere?
3. What CRF value holds up best after platform re-encode — 18, 16, or visually lossless 14?
4. How does Pipeline C output compare to hypothetical Pipeline B output on the same torture-test clip?

---

## Sources
- Derivative docs — Movie File Out TOP
- Interactive & Immersive HQ — Export Movies in TouchDesigner / Codecs for TouchDesigner Explained
- Derivative docs — OpenEXR
- VideoHelp Forum — x264 advanced settings (banding reduction)
- scottstuff.net — Benchmarking FFmpeg H.265 / H.264 options
- Blackmagic Forum — Banding when saving gradients to 8-bit H.264
- GitHub Gist (YamashitaRen) — 10-bit H.264 explanation
