---
title: TouchDesigner on Apple Silicon
version: 1.0
last_updated: 2026-04-16
status: live
scope: Mac-specific platform realities for TD 2025.32460 on M1 hardware. Codec limits, GPU translation, known bugs, Non-Commercial license constraints.
dependencies: TD_LIBRARY_INDEX.md
---

# TOUCHDESIGNER ON APPLE SILICON

This file captures everything that is different on Mac / Apple Silicon / TD 2025.x versus the default "generic TD" assumption. Read before export, before buying a sensor, before assuming a tutorial's workflow works on this machine.

Target hardware: M1 MacBook Pro (primary), M1 Mac Studio (secondary).
Target TD build: 2025.32460 — Non-Commercial license.

---

## 1. GPU Stack — Vulkan via MoltenVK

TD 2025 runs on **Vulkan** as its rendering API. On Mac there is no native Vulkan driver — TD uses **MoltenVK** to translate Vulkan calls to **Metal**. This is a transparent translation layer, but it has consequences:

- **Geometry shaders are not supported on Metal.** Operators or GLSL code that rely on the `geometry` shader stage silently fail or degrade. POPs sidestep this because they are compute-based. Render TOP with GLSL geometry stages: avoid.
- **Compute shaders work.** POPs depend on compute. This is why the POP family works on Mac.
- **Validation layers are not Metal-native.** GLSL error messages on Mac sometimes lag the actual error by one compile cycle — always "compile twice" mentally when debugging a shader.
- **Performance ceiling is the Metal translation ceiling, not raw Vulkan.** Benchmarks from Windows/NVIDIA do not transfer. Expect 30–60% lower throughput on heavy fragment/compute loads versus equivalent-tier PC.

**Practical rule:** if a technique explicitly names geometry shaders, find the compute/POP equivalent before attempting.

---

## 2. Non-Commercial License — Hard Limits

The free Non-Commercial license used here imposes:

- **Output resolution cap: 1280×1280.** Any TOP wider or taller than 1280 gets watermarked or clamped. Plan the render graph with 1280 as the ceiling. For vertical 9:16: render at 720×1280. For 16:9 video: render at 1280×720. Upscale outside of TD (FFmpeg, Topaz) for final delivery.
- **H.264 export is unavailable.** Movie File Out TOP locks H.264 behind Commercial. Use ProRes or image sequences instead — see §4.
- **NDI output is limited / sometimes disabled.** Touch In/Out TOP works locally but network streaming is gated.
- **Perform Mode output resolution is also capped.** Fullscreen projection to a 1080p projector still renders internally at ≤1280 on one axis.
- **Watermark appears on Movie File Out in some codec paths.** Verify a 10-second render before committing to a long export.

If a feature silently fails with no error, license-gate is the first hypothesis.

---

## 3. Codecs — What Works, What Doesn't

### Reading (Movie File In TOP)
| Codec | Status on Mac |
|-------|---------------|
| ProRes (all flavors) | Native, hardware accelerated |
| HAP / HAP Q | Requires AV Foundation plugin; CPU-decoded on Mac |
| H.264 / H.265 | Reads fine (hardware decode via VideoToolbox) |
| Notch LC | CPU decode only on Mac, expensive |
| DNxHR / DNxHD | Reads via AV Foundation |
| Image sequences (EXR, PNG, TIFF) | Native; EXR is preferred for HDR/linear |

### Writing (Movie File Out TOP)
| Codec | Status on Non-Commercial Mac |
|-------|-------------------------------|
| ProRes 422 Proxy/LT/HQ/4444/4444XQ | Works — preferred |
| H.264 | **Commercial only** — blocked |
| H.265 | **Commercial only** — blocked |
| HAP | Works if plugin installed |
| Image sequence (PNG / EXR / TIFF) | Works — use for maximum quality |
| DNxHR | Works |

**Default export: ProRes 422 HQ for deliverables. PNG sequence for archival masters.**

### Known codec bugs in 2025.x
- **ProRes 4444 with HDR10 metadata**: writing produces files QuickTime won't read. Use 422 HQ, or write 4444 and strip HDR metadata externally.
- **Movie File Out + audio channel** on Mac occasionally drops the last frame — pad the render by 1 frame.
- **Alpha in ProRes**: only 4444 and 4444XQ support alpha. Do not expect alpha in 422.

---

## 4. Audio Routing on Mac

Mac audio pipeline is fundamentally different from Windows ASIO:

- **Core Audio is the only I/O stack.** No ASIO.
- **BlackHole** (free virtual audio driver) is the standard bridge: Ableton → BlackHole → Audio Device In CHOP. Use BlackHole 2ch for mono/stereo sets, 16ch when you need multiple stems into TD separately.
- **Aggregate Devices**: built in macOS Audio MIDI Setup, used to combine BlackHole + real interface so you can monitor while routing. Configure with BlackHole as master clock.
- **Latency**: BlackHole adds ≤1ms; audio pipeline end-to-end latency with Audio Filter/Analyze CHOPs is usually 10–20ms at 44.1k. Compensate downstream with Lag CHOP if the visuals feel ahead.
- **Audio Device Out CHOP** picks up Core Audio devices — the Mac version lists them by the user-visible name, not ASIO-style handles.

---

## 5. Syphon and NDI — Current State on Mac

**Syphon** is the Mac equivalent of Spout (inter-app texture sharing, zero-copy).
- **Syphon TOPs are shipped with TD** but in 2025.x there are reports of broken Syphon output from TD on macOS — texture appears black in receiver.
- **Workaround:** route through Spout-to-Syphon bridge apps if Syphon Out breaks, or fall back to Screen Capture by the receiving app.
- Always verify Syphon is working at start of a session, not mid-show.

**NDI** on Apple Silicon:
- Has been flaky on M1 through multiple TD builds. Confirm in the current project before relying on it for a gig.
- **Safer choice for Mac AV integration:** Syphon when it works, or render to a virtual display and screen-capture.

---

## 6. Sensors — Mac Compatibility

| Sensor | Mac Apple Silicon support |
|--------|---------------------------|
| Kinect Azure | **Not supported** on macOS. Windows only. |
| Intel RealSense | **Not supported** on Apple Silicon in TD 2025. |
| Orbbec Femto Bolt / Femto Mega | **Supported** via Orbbec SDK; some models require `sudo` to access USB permissions. Use Kinect Azure TOP/CHOP family with Orbbec driver. |
| Webcam (Video Device In TOP) | Works via AVFoundation |
| Leap Motion | Discontinued officially; third-party plugins exist but unstable on ARM |
| MediaPipe (Google) | **Best option for body/hand tracking on Mac.** Use the MediaPipe GPU plugin — runs on the M1 GPU via Metal. Low-latency hand tracking, body pose, face landmarks. |
| ZED (Stereolabs) | Arm64 macOS support limited — verify before buying |

**Default body/hand tracking on this machine: MediaPipe GPU plugin. Default depth: Orbbec.**

---

## 7. Known Bugs in 2025.32460 on Mac

Running list. Update when confirmed.

- **Movie File Out → HDR10 metadata on ProRes 4444** produces unreadable files (see §3).
- **Syphon Out intermittently black on macOS** — verify every session.
- **NDI Out stability on M1** — acceptable for dev, risky for gigs.
- **Text TOP emoji rendering** falls back to outline-only for some color fonts — use Text SOP with a font atlas for color emoji.
- **Geometry shaders in GLSL TOP** silently produce black output on Metal — use compute path or POPs.
- **Engine COMP cold-start latency** on M1 is noticeably higher than Windows; pre-warm Engines before Perform Mode.

---

## 8. Performance Headroom on M1

Rough calibration for budgeting a project:

- **M1 MacBook Pro base (8 GPU cores)**: comfortable at 1280×720 60fps with feedback + 2–3 heavy post TOPs. Chokes around 1280×1280 + feedback + large POP instancing.
- **M1 Max / Pro with 14+ GPU cores**: adds headroom for full-frame feedback + ≥2 GLSL TOPs simultaneously.
- **Mac Studio M1 Max/Ultra**: use as render machine for long exports — thermal budget is higher so sustained renders don't throttle.

**When framerate drops:**
1. Cache early — Null TOP + Cook Type = Selective.
2. Downsample before feedback.
3. Move analysis work (Analyze TOP, large Math CHOPs) outside the cook path to a timer.
4. Move heavy geometry to POPs with GPU instancing.

See `TD_EFFICIENT_NETWORKS.md` and `TD_WORKFLOW_OPTIMIZATION.md` for the recipes.

---

## 9. Practical Session Setup Checklist

Before starting any session on this machine:

1. Confirm TD version in About → should say 2025.32460.
2. Check Preferences → GPU. On M1, TD uses the integrated Apple GPU; there is no discrete GPU choice.
3. Audio MIDI Setup → confirm BlackHole + aggregate device exist if you'll be routing Ableton.
4. Resolution Cap reminder: no TOP over 1280 on either axis.
5. Create a `crashAutoSave` folder the project writes to on an external SSD, not internal (internal fills quickly with heavy feedback captures).
6. Enable Preferences → Auto-Save every 5 minutes for Wobar work.

---

## 10. Upgrade Considerations

If Nick ever moves off Non-Commercial:
- **Pro ($600) removes the 1280 cap and unlocks H.264/H.265 export.** Also removes Engine COMP instance limits.
- **Commercial ($2200+)** adds Engine COMP licenses at scale and full NDI.
- **Educational** if enrolled — identical to Pro for output.

No upgrade removes the Mac-specific platform constraints (Metal translation, sensor support, geometry shader gap). Those are platform, not license.

---

## 11. Verified M1 Render-Feature Matrix (live-tested 2026-07-17, build **2025.32820**)

Empirically confirmed by building a lit 3D scene in TD on M1 Metal and inspecting output
(screenshot + numeric depth sampling). Source: WOBAR corridor Phase 0. **Note the build:
2025.32820**, newer than this file's §-frontmatter 2025.32460 — Nick's TD updated. These
rows are the "does it actually render on Metal" answers the doc-research could not give.

| Feature | M1 Metal status | Notes / gotchas |
|---------|-----------------|-----------------|
| **Soft shadows** (`lightCOMP.shadowtype='soft2d'`) | ✅ **WORKS** | Real soft penumbra, not black, not hard-only. Requires light `lookat` the caster + tightened light FOV (shadow map renders from light POV). `hard2d` is the fallback. |
| Direct lighting (cone/point/distant) | ✅ WORKS | `lightCOMP` `cr/cg/cb` (not colorr/g/b), `dimmer`, `lighttype`. |
| **phongMAT** | ✅ WORKS | Diffuse pars `diffr/diffg/diffb` (NOT `diffuser`). Native `shadowstrength` + `shadowcolorr/g/b`. |
| **pbrMAT** | ✅ WORKS | Both dielectric (metallic 0) lit by direct light AND metallic (0.9) reflecting env. **No black silhouette** — the 2021 bug was Intel/pre-Vulkan. Pars: `basecolorr/g/b`, `metallic`, `roughness`, `emitr/g/b`. |
| **Depth TOP** | ✅ WORKS | Opaque geo → valid varying depth (sampled: geo <1.0, empty bg =1.0). ⚠️ Perspective depth is non-linear — near=0.1/far=200 crushes all to ~0.99. **Tighten far plane (≈28)** for usable precision. `depthTOP.par.op`=renderTOP, `depthspace='cameraspace'`/`'reranged'`. Transparent/instanced geo still gives flat depth (see §7 / debug log) — keep DOF/fog geo opaque. |
| **Environment Light / IBL** | ✅ WORKS | Metallic surface reflects env map. Type = `environmentlightCOMP`. Keep `envlightmapprefilter='off'` (`automatic` ≈ 142 ms/frame on M1). Add to `renderTOP.par.lights` beside the key light. |
| **Bloom TOP** | ✅ NATIVE | Don't hand-build. `output='inputplusbloom'`, `bloomthreshold`, `bloomintensity`, `min/maxbloomradius`. |
| 1280×1280 render + `aa8` antialias | ✅ WORKS | Clean edges. NC cap is 1280/axis (§2). |
| MSAA `aa16`/`aa32` | ⚠️ Apple GPUs cap at 8× | `renderTOP.par.antialias` exposes aa16/aa32 that Metal can't do — cap at `aa8`. (aa8-vs-4x exact drop not yet confirmed.) |
| Geometry-shader nodes | ❌ dead/black | Established (§1, §7). No line-expansion / GS particle MATs. |
| POPs on macOS | ⚠️ works but unstable | A POPs crash can hang the Mac graphics driver → reboot. Atomic Float, double-precision attrs, HW ray-tracing unsupported for POPs on macOS. Save often. |
| Hardware ray tracing | ❌ unsupported on macOS | — |

**Not native on any platform (build, don't expect a node):**
- **Depth of field** — no native Render TOP DOF param. Build from Depth TOP (✅ above) + Blur/Luma Blur, or GLSL bokeh. Depth TOP is the linchpin: DOF *and* depth-fog both ride it.
- **Volumetric fog / god rays** — no native volume node. Depth-driven fog rides the Depth TOP; true shafts = raymarched GLSL.

**Net:** every feature a lit, atmospheric procedural corridor structurally needs — real
light, soft shadow, PBR, IBL reflection, valid depth (→ fog + DOF), bloom — is confirmed
working on M1 Metal at 2025.32820.
