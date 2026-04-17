---
title: TD Export Workflow
version: 1.0
last_updated: 2026-04-16
status: live
scope: Rendering music videos and visual loops to disk — Movie File Out, image sequence, ProRes pipeline on Mac, offline rendering.
dependencies: TD_LIBRARY_INDEX.md, TD_APPLE_SILICON.md
---

# TD EXPORT WORKFLOW

Exporting finished visuals — music videos, loops, reference renders — on the Mac / Non-Commercial setup.

---

## Hard Constraints on This Machine

- **1280 cap on any TOP** — resolution ceiling.
- **No H.264/H.265 export** — Commercial only.
- **ProRes is the primary codec**.
- **PNG / EXR image sequences are the archival choice**.

See `TD_APPLE_SILICON.md` §3 for full codec reality.

---

## Decision — Real-time vs Offline Render

### Real-time record
Movie File Out TOP while the project runs at full framerate.
- **Use when:** project cooks comfortably at 60fps.
- **Pros:** fast, one pass, audio baked in.
- **Cons:** any frame drop corrupts the record.

### Offline render
TD can render non-real-time — frames are computed as long as they take and written sequentially. Timeline advances one frame per computation.
- **Use when:** project cooks > 16.6ms/frame OR quality settings need to be pushed beyond real-time budget.
- **Pros:** no frame drops, can use 8× MSAA, high-res effects, long feedback stabilization times.
- **Cons:** takes longer wall-clock time.

Offline render is the right choice for music videos on the Non-Commercial budget.

---

## Setting Up an Offline Render

### 1. Project settings
- **Timeline FPS**: 30 or 60 for music video output. 24 for cinematic feel.
- **Timeline length**: match song duration. End frame = FPS × duration seconds.

### 2. Movie File Out TOP configuration
- **File** — absolute path, .mov extension.
- **Codec** — ProRes 422 HQ (default).
- **FPS** — match Timeline FPS.
- **Record Mode** — set based on needs:
  - **Manual** — click Record Now to start, Stop to end.
  - **Record** — records while Record parameter is pulsed.
  - **Record Delay / Record Time** — automated start/stop at specified frames.

### 3. Audio track
Movie File Out TOP → Audio tab:
- **Audio Input** — point at the Audio CHOP with your track.
- **Audio Record** = On.
- **Audio Sample Rate** — match source (44.1k or 48k).

### 4. Launch offline render
- **Play Mode** → Sequential (no real-time advance; each frame waits for cook to finish).
- Hit Record on Movie File Out.
- Let it run. TD will advance frames at whatever speed cooking allows.

### 5. Verify first frames
Render 10 seconds first. Open in QuickTime. Confirm:
- Colors match expectation (no colorspace mismatch).
- No dropped frames or corruption.
- Audio is present and synced.

### 6. Full render
Once verified, run the full duration.

---

## Codec Choices on Mac

| Codec | Quality | File Size | Use |
|-------|---------|-----------|-----|
| ProRes 422 Proxy | Low | Smallest | Preview / editing |
| ProRes 422 LT | Medium | Small | Broadcast, web |
| ProRes 422 HQ | High | Medium | **Default for masters** |
| ProRes 4444 | Very High (alpha) | Large | When alpha matters |
| ProRes 4444 XQ | Highest | Very Large | Broadcast finishing |
| PNG sequence | Lossless | Huge | Archival, VFX pipeline |
| EXR sequence | Lossless HDR | Very Huge | HDR archival |

**Default recipe: ProRes 422 HQ, 1280×720, 60fps.**

---

## Image Sequence Export

### Setup
- Movie File Out TOP → Codec = PNG / TIFF / EXR.
- File path should include a pattern: `render/frame_%06d.png` → frame_000000.png, frame_000001.png, etc.
- Directory should exist; pre-create it.

### Advantages
- No codec lossy step.
- Resumable: if TD crashes mid-render, restart at the last written frame.
- Cleanup / retouch per frame possible.

### Downstream
Assemble with FFmpeg or Resolve:
```
ffmpeg -framerate 60 -i frame_%06d.png -i track.wav -c:v prores_ks -profile:v 3 -c:a aac output.mov
```
Profile 3 = ProRes 422 HQ.

---

## Upscaling Beyond 1280

The 1280 cap is painful for 1920×1080 delivery. Two approaches:

### Approach A — Render at 1280×720, upscale externally
- Render at 1280×720 (standard 16:9 for the cap).
- External upscale: Topaz Video AI, FFmpeg with lanczos, or Resolve.
- `ffmpeg -i in.mov -vf scale=1920:1080:flags=lanczos out.mov`.
- Usually looks fine since TD renders are clean (no source noise amplified by upscaling).

### Approach B — Render at 1280×1280 square, crop/pad in post
- Useful if composition benefits from full square canvas then cropped to deliverable.

### Approach C — Upgrade to Commercial license
Removes 1280 cap. Enables H.264/H.265 export. See `TD_APPLE_SILICON.md` §10.

---

## Vertical (TikTok / IG) Export

- Resolution: 720×1280 (vertical, under 1280 cap).
- 30fps or 60fps.
- ProRes 422 HQ.
- Audio at 48k for platform compatibility.
- Optional post: FFmpeg to H.264 for direct upload (external step).

---

## Audio Embedding

### Working audio into the file
Movie File Out TOP → Audio tab → Audio Input CHOP wired. Audio records alongside video.

### Alternative — separate audio file
- Render silent video.
- Add audio externally in Final Cut, Resolve, or FFmpeg.
- Gives you more control over audio levels and editing.

### Sync considerations
- Core Audio on Mac adds variable latency — if offline rendering with audio and sync feels off, export silent + add audio externally.
- Confirm first 10 seconds before full render.

---

## Export Troubleshooting

### H.264 option greyed out
Non-Commercial license — see `TD_FOOTGUNS.md` §G1.

### 0-byte output
Path invalid or codec mismatch. See §G2.

### Silent video
Audio CHOP not wired on Movie File Out's Audio tab. See §G3.

### Wrong framerate
Timeline FPS vs Movie File Out FPS mismatch. See §G4.

### HDR10 ProRes 4444 unreadable
Known 2025 bug — use 422 HQ. See §G5.

---

## Pre-Export Checklist

Before committing to a full render:

- [ ] Timeline length set correctly (end frame = duration × fps).
- [ ] Timeline FPS matches target.
- [ ] Movie File Out TOP path is to an external SSD with enough space.
- [ ] Codec = ProRes 422 HQ (unless you need alpha or smaller).
- [ ] Audio wired and recording on.
- [ ] Resolution ≤ 1280 on any axis.
- [ ] Per-project post/color looks correct in the viewer.
- [ ] 10-second test render completes and opens correctly.
- [ ] Close other GPU-heavy apps (Chrome, etc.).
- [ ] Disable Mac sleep / screensaver during render.

---

## File Organization

Suggested folder structure:
```
/Renders/<track_name>/
  /renders_720p/
    <track>_v1.mov
    <track>_v1_1080upscale.mp4
  /image_sequences/ (if used)
    <track>_frames/
  /masters/
    <track>_master.mov (ProRes 422 HQ)
  /deliverables/
    <track>_tiktok.mp4 (external H.264)
    <track>_ig_feed.mp4
    <track>_yt.mov
```

Keep ProRes masters forever. H.264 deliverables can be regenerated.

---

## Long Render Strategy

Music videos at 3+ minutes can take hours. Tips:

- Render to external SSD, not internal (internal drives thermally throttle; external is less likely).
- Use image sequence if you're worried about crashes — resumable.
- Run overnight.
- Disable Mac Time Machine during render (it pauses I/O randomly).
- Check progress every 30 minutes.
- If render crashes partway, check Cook time spikes in the last second — usually a hit to an uncached op.

---

## Quality vs Speed

| Setting | Quality | Time cost |
|---------|---------|-----------|
| MSAA 2× | Good | +10% |
| MSAA 4× | Better | +25% |
| MSAA 8× | Best | +80% |
| Feedback at full res | Smooth | 4× cost vs half-res |
| HDR EXR sequence | Perfect | 2× vs PNG |

For a music video master: MSAA 4×, feedback at full or half depending on visual, ProRes 422 HQ. For a loop you'll see once: MSAA 2× and call it done.

---

## Reading This File

Sequential read for first export. Jump to Decision section if unsure about real-time vs offline. Upscaling / Vertical sections for platform-specific needs.
