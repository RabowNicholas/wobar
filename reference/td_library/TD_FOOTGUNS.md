---
title: TD Footguns — Failure Patterns and Fixes
version: 1.0
last_updated: 2026-04-16
status: live
scope: Confirmed failure patterns in TouchDesigner with exact fixes. General; Wobar-specific failures live in WOBAR_TD_DEBUG_LOG.md.
dependencies: TD_LIBRARY_INDEX.md, TD_APPLE_SILICON.md, TD_EFFICIENT_NETWORKS.md
---

# TD FOOTGUNS — FAILURE PATTERNS AND FIXES

The failures below are confirmed patterns that recur across TD projects. Each entry names the symptom, the cause, and the fix. Read first when debugging.

Organized by category. Use Grep / search by keyword.

---

## A. Feedback and TOPs

### A1. Feedback TOP goes white / blown out
**Symptom:** feedback trail grows brighter each frame until frame saturates.
**Cause:** Level TOP opacity ≥ 1.0 in the feedback loop, or no attenuation at all.
**Fix:** Level TOP (Post tab) → `opacity` ≤ 0.98. Below 0.95 for faster decay. `brightness` ≤ 1.0 in the loop. Never multiply in a gain > 1 inside the loop.

### A2. Feedback TOP goes black
**Symptom:** feedback trail decays instantly to black.
**Cause:** opacity too low or Composite TOP is not adding source back.
**Fix:** confirm Composite TOP (operand A = source, operand B = feedback) mode is Add / Over / Screen — not Subtract. Raise opacity to 0.95–0.98.

### A3. Feedback runs at the wrong resolution
**Symptom:** feedback looks pixelated or cropped vs source.
**Cause:** Feedback TOP → Common page → Resolution mismatch with upstream.
**Fix:** set Feedback TOP Resolution → "Use Input." If downsampling intentionally, match all branches to the same explicit resolution.

### A4. Feedback has a one-frame lag that looks wrong
**Symptom:** feedback lags source by 1 frame; feels sluggish.
**Cause:** this is the pipeline's design — feedback is last frame's output. Not a bug.
**Fix:** if you don't want lag, you don't want feedback. Use Trails TOP or Blur TOP instead.

### A5. GLSL TOP output is black on Mac
**Symptom:** shader compiles, no output.
**Cause:** geometry shader stage in the shader — not supported on Metal (see `TD_APPLE_SILICON.md` §1).
**Fix:** rewrite without geometry stage. Use compute for per-vertex logic, or split into two shader passes.

### A6. GLSL TOP compiles but shows garbage
**Symptom:** output is noise or wrong colors.
**Cause:** uniforms unset; texture samplers at wrong index; swizzle mismatch.
**Fix:** in GLSL TOP → Vectors 1 tab, declare every uniform and set defaults. Texture inputs are sampled as `sTD2DInputs[0]`, `[1]` etc.; wire inputs in the correct order.

### A7. Blur TOP at high radius kills framerate
**Symptom:** cook time jumps when Blur radius raised.
**Cause:** Blur TOP is O(radius²) for non-separable blur.
**Fix:** use Luma Blur TOP (cheaper, single-channel aware), or stack two small blurs instead of one big one. Downsample before blurring, composite back up.

### A8. Composite TOP "over" mode looks wrong with alpha
**Symptom:** edges have dark fringe or halos.
**Cause:** straight alpha vs premultiplied alpha mismatch.
**Fix:** Composite TOP → Pre-Multiply RGB by A / Post-Divide — match the upstream assumption. ProRes 4444 reads premultiplied; PNGs are usually straight.

---

## B. Audio Pipeline

### B1. No audio reactivity at all
**Symptom:** CHOP chain is flat; visuals don't respond.
**Cause:** Audio Device In CHOP is not the right device, BlackHole not routed, or levels too low.
**Fix:**
1. Audio Device In CHOP → Device param → pick BlackHole or interface explicitly.
2. Viewer on the Audio Device In CHOP — should show moving channels at source levels.
3. If flat: Mac Audio MIDI Setup → BlackHole → confirm aggregate device or Ableton output routing.

### B2. Reactivity is jittery / strobey
**Symptom:** visuals flicker on every small audio detail.
**Cause:** no Lag CHOP after Analyze; raw RMS is noisy.
**Fix:** add Lag CHOP (attack 0.05s, release 0.2s — or whatever makes the visual feel right).

### B3. Reactivity is delayed behind the audio
**Symptom:** kick lands, visuals respond 100ms later.
**Cause:** Analyze CHOP with large window, or Lag CHOP attack too slow, or BlackHole + Audio Filter adding buffer latency.
**Fix:** reduce Analyze window; reduce Lag attack; reduce Audio Filter filter order. For tight kick-sync, trigger from Audio Spectrum CHOP onset detection, not RMS.

### B4. Band split doesn't isolate bass
**Symptom:** "sub" band responds to mids.
**Cause:** Audio Filter CHOP Butterworth with low order doesn't have sharp enough rolloff.
**Fix:** raise Filter Order to 4+. Cutoff: sub 20–80Hz, low mid 80–400Hz, mid 400–2500Hz, high 2500Hz+. Use Audio Filter with type "Band Pass" explicitly.

### B5. Audio goes silent unexpectedly
**Symptom:** audio was working, now nothing.
**Cause:** Mac switched active audio device (plugged in headphones, Bluetooth connected, etc.) and Audio Device In CHOP is still pointed at the old one.
**Fix:** set Audio Device In CHOP → Device to the explicit name, not "Default." Check at session start.

### B6. Audio File In CHOP doesn't play
**Symptom:** file is loaded, timeline isn't moving.
**Cause:** Play parameter not on; or file path is broken; or Audio File In is CPU-blocking load.
**Fix:** set Play = On. If stuttering on load, pre-load the file (toggle Reload) before Perform Mode.

---

## C. Network Structure and Cooking

### C1. Network cooks too hot at idle
**Symptom:** cook time > 5ms when nothing should be moving.
**Cause:** something set to Cook Type = Always that shouldn't be; or an expression reference is re-triggering.
**Fix:** in Textport: `op('/project1').cookedChildren()` (or walk via Info DAT). Find Always operators. Set to Selective unless needed.

### C2. A downstream change doesn't propagate
**Symptom:** editing a parameter upstream has no effect downstream.
**Cause:** Cook Type = Off somewhere in the chain; or a Null is caching a stale result (rare).
**Fix:** check Cook Type on every operator in the chain; reset to Selective.

### C3. COMP contents don't cook
**Symptom:** a Base COMP's internal operators don't run.
**Cause:** no output is being pulled from the COMP — orphan sub-network.
**Fix:** either wire an Out CHOP/TOP/etc. inside the COMP and reference it externally, or flag the COMP's Cook Type → Always if it must always run.

### C4. Expression reference breaks on COMP clone
**Symptom:** copied a Base COMP, internal references resolve to the original COMP's ops.
**Cause:** absolute paths (`/project1/original/...`) don't re-map on clone.
**Fix:** use relative paths (`../null_audio`) or `me.parent()` patterns. Cloning works when paths are relative.

### C5. Select TOP shows black
**Symptom:** Select TOP → Path is set, output is black.
**Cause:** path typo, or the source TOP has no downstream pull so it's not cooking (and Select only pulls the image — it doesn't force upstream to cook).
**Fix:** add a Null TOP at the source side, set it to Cook Type = Always if nothing else pulls, or add a viewer on the source chain.

---

## D. Rendering (3D)

### D1. Render TOP is completely black
**Symptom:** nothing visible in the render.
**Cause:** no camera attached; no light attached; or scene SOP is empty.
**Fix:** Render TOP parameters → Camera = your Camera COMP path, Lights = your Light COMP path, Geometry = your Geometry COMP path. Confirm the Geometry COMP's SOP input is not empty.

### D2. Render TOP is black except for background color
**Symptom:** background shows, geometry doesn't.
**Cause:** camera pointing away; geometry behind camera's near clip; material alpha = 0.
**Fix:** Camera COMP View tab → look-at your geometry; check Near/Far clipping. Phong MAT → Alpha > 0.

### D3. Geometry is lit flat / no shading variation
**Symptom:** 3D looks 2D.
**Cause:** no Light COMP wired; or material is Constant MAT; or normals are missing on the SOP.
**Fix:** use Phong MAT or PBR MAT; ensure Light COMP is wired; add a Normal SOP on geometry if computed normals are missing.

### D4. Texture on geometry appears upside down
**Symptom:** UV-mapped texture flipped.
**Cause:** convention mismatch — TOP origin is top-left, UV origin is bottom-left.
**Fix:** on the MAT texture map, Flip Y; or Transform TOP → Flip Y before using as texture source.

### D5. Instancing shows one instance only
**Symptom:** set Instance count > 1, see one.
**Cause:** Instance data CHOP or SOP is single-sample; or Geometry COMP → Instancing tab is Off.
**Fix:** Geometry COMP → Instancing tab → On; point Translate OP at a multi-sample CHOP or a POP. Confirm the CHOP has N samples where N = desired instance count.

### D6. Instances appear but all stacked at origin
**Symptom:** N instances, visible count = 1.
**Cause:** Translate CHOP channels are single-sample or identical per sample.
**Fix:** the CHOP feeding Translate must have one sample per instance, each with unique positions. Use Pattern CHOP or POP positions.

---

## E. POPs (New in 2025)

### E1. POP viewer shows nothing
**Symptom:** POP network built, viewer empty.
**Cause:** no geometry operator downstream; or POP output not wired into a render chain.
**Fix:** POP pipeline needs: generator POP → transform/attribute POPs → wire into Geometry COMP's Instance (or convert via a SOP In POP for legacy path).

### E2. POPs run CPU-slow on Mac
**Symptom:** POP network hits cook time > 16ms for small point counts.
**Cause:** rare — but happens if a POP is doing per-point Python via Execute DAT reference, or if compute shader compilation failed silently.
**Fix:** confirm compute path is active (no geometry shader fallback). Remove any per-cook Python DAT references. Simplify per-point math; move to Attribute POP arithmetic instead of scripts.

### E3. Attribute POP value doesn't flow through
**Symptom:** set Attribute POP, downstream POP ignores it.
**Cause:** attribute name mismatch or class (vec3 vs float) mismatch.
**Fix:** match attribute names exactly (case-sensitive). Use a POP Info DAT to inspect attributes on the stream before the consuming POP.

---

## F. MIDI / OSC / Control

### F1. MIDI controller has no effect
**Symptom:** hardware moves; CHOP doesn't.
**Cause:** MIDI In CHOP not pointed at the right device; MIDI In Map CHOP has wrong channel/CC; input not connected in macOS Audio MIDI Setup.
**Fix:**
1. Audio MIDI Setup → MIDI Studio → confirm device is live and input is enabled.
2. MIDI In Map CHOP → Device → pick explicitly (not "All").
3. MIDI In Map CHOP → Channel Prefix — to scope to one channel if needed.
4. Viewer on MIDI In Map CHOP → move a control on hardware — channel should appear and move.

### F2. MIDI control values jitter
**Symptom:** knob is steady but CHOP value flickers.
**Cause:** controller sends 7-bit values (0–127), creating 127 steps; small hand tremor crosses steps.
**Fix:** Filter CHOP with a small lag on the MIDI input. Or map to a smooth range via Math CHOP.

### F3. OSC In CHOP receives nothing
**Symptom:** sender is sending, CHOP shows no channels.
**Cause:** port mismatch; or sending app is on a different local network; or firewall blocking UDP.
**Fix:**
1. Confirm port matches sender (default TouchOSC 9000, Resolume 7000).
2. OSC In CHOP → Network Address → leave blank (any interface) or set to local IP.
3. On Mac: System Settings → Network → Firewall → allow TD.

### F4. OSC address wildcards don't catch messages
**Symptom:** using `/2/fader1` pattern, no channel appears.
**Cause:** wildcards in OSC In CHOP are literal unless Bundle Name Prefix matches.
**Fix:** send messages with the exact address you filter on. Use OSC In DAT to see raw incoming messages if unsure.

### F5. Ableton Link shows not connected
**Symptom:** Ableton Link CHOP — Connected = 0.
**Cause:** no other peer on the network advertising Link; or firewall; or wrong network interface.
**Fix:**
1. Another Link-enabled app must be running (Ableton Live, another TD instance with Link on).
2. Link uses multicast — both devices on the same LAN, not segregated guest wifi.
3. Confirm Ableton Link CHOP → Enabled = On.

---

## G. Export / Recording

### G1. Movie File Out TOP — H.264 is greyed out
**Cause:** Non-Commercial license does not support H.264 export.
**Fix:** use ProRes 422 HQ for final, or PNG image sequence. See `TD_APPLE_SILICON.md` §3.

### G2. Movie File Out starts but produces a 0-byte file
**Symptom:** record button clicked, file is empty or unreadable.
**Cause:** file path invalid; or codec/container mismatch; or TD crashed mid-record.
**Fix:** absolute path with valid parent folder. ProRes + .mov extension. Watch Textport for errors during the first few frames.

### G3. Audio isn't in the exported video
**Symptom:** video renders, plays silent.
**Cause:** Movie File Out TOP doesn't record audio by default — audio path must be wired on the Audio tab.
**Fix:** Movie File Out TOP → Audio tab → point at the Audio CHOP that has the track. Enable audio record.

### G4. Export framerate is wrong
**Symptom:** exported video plays too fast or too slow.
**Cause:** TD timeline rate ≠ Movie File Out rate; or source file had a different rate and wasn't retimed.
**Fix:** TD project → set FPS (Timeline settings) to target. Movie File Out → Codec tab → FPS = same. For offline rendering, set "Record Delay" and "Record Time" in frames, not seconds.

### G5. Exported ProRes 4444 file won't play in QuickTime
**Symptom:** export finishes, QuickTime gives an error.
**Cause:** HDR10 metadata bug in TD 2025.x ProRes 4444 on Mac.
**Fix:** use ProRes 422 HQ (no HDR metadata path) or strip HDR metadata externally with `ffmpeg -bsf:v hdr10_meta=strip` or Shutter Encoder.

### G6. Export at 1280×1280 but final canvas needs 1920×1080
**Cause:** Non-Commercial 1280 cap.
**Fix:** render at 1280×720 and upscale externally. Topaz Video AI or FFmpeg lanczos. Or render in landscape-safe frame at 1280×720 without upscale.

---

## H. Perform Mode / Live

### H1. Perform Mode drops frames
**Symptom:** stutters visible in projection or Perform Mode header shows drops.
**Cause:** cook time exceeding frame budget; or a cook spike from initialization.
**Fix:**
1. Reduce resolution.
2. Cache heavy chains with Null + Cook Type = Selective.
3. Pre-warm Engine COMPs before Perform Mode — clone/initialize all scenes at project load.
4. Switch to Replicator-free instancing (POPs).

### H2. Perform Mode window shows on wrong monitor
**Cause:** Perform window monitor setting mismatched with OS display arrangement.
**Fix:** Window COMP → Monitor → pick explicit index (not "Main"). Reboot TD after changing macOS display arrangement.

### H3. Crash recovery file is missing
**Symptom:** TD crashed, crashAutoSave folder is empty.
**Cause:** crashAutoSave not enabled, or external drive not mounted, or permission denied.
**Fix:** Preferences → Auto-Save every 5 minutes. CrashAutoSave directory — set to an always-mounted location with write permission. Confirm the folder exists and has recent files before a gig.

### H4. Engine COMP cold-start hitch when first entering a scene
**Symptom:** switching scenes causes a visible pause.
**Cause:** Engine initialization on first pull.
**Fix:** pre-warm at project load: for every Engine COMP, call its pull once (e.g., via an Execute DAT on Start). Or use `clone` with pre-instantiated state.

---

## I. Ableton / Audio Integration

### I1. TDAbleton shows not connected
**Cause:** Max For Live device not installed; or TD side not listening; or wrong Link / M4L port.
**Fix:**
1. Install Max For Live pack; drop the TDAbleton M4L device onto a track in Ableton.
2. TD side: the TDAbleton COMP — click Connect.
3. If still failing, check M4L console for errors.

### I2. BlackHole appears in Ableton but not in TD
**Cause:** TD started before BlackHole was installed or system restart needed after install.
**Fix:** restart TD. If still absent, check Audio MIDI Setup → BlackHole is visible there.

### I3. Audio Device In CHOP latency >> what Ableton shows
**Cause:** Core Audio buffer differs between apps; TD has its own audio buffer.
**Fix:** Preferences → Audio → Buffer Length. Lower to 128 or 256 samples — but higher CPU cost. If latency is inherent and visual timing matters more than real-time, apply a negative Lag on the visual side (run visuals ahead).

---

## J. Scripting / Python / DATs

### J1. Execute DAT doesn't fire
**Symptom:** callback defined, never runs.
**Cause:** Execute DAT has the wrong Executor selected; or the callback function name is misspelled; or the target DAT is Off.
**Fix:** Execute DAT → toggle the callback on (e.g. "Start" must be on for onStart). Confirm function name matches exactly. Check Textport for errors.

### J2. `op('path')` returns None
**Cause:** path is wrong, or the referenced op is inside an un-initialized COMP.
**Fix:** use `op('../foo')` relative paths. Use `root.findChildren(name='foo')` if you need to search. Avoid hardcoded absolute paths that break on clone.

### J3. Script SOP crashes on large point counts
**Cause:** per-point Python is slow; at >10k points it can hang or crash.
**Fix:** do not use Script SOP for large point counts. Use POPs for per-point logic — they run on GPU. Script SOP is appropriate for <1k points.

### J4. Table DAT references in parameter expressions are slow
**Symptom:** project cooks slower after wiring many ops to a Table DAT.
**Cause:** every parameter that reads a cell re-executes `op('table')[r,c]` every cook.
**Fix:** read once into a CHOP via Eval DAT or a DAT To CHOP; Export CHOP to all parameters. One read, many writes.

---

## K. Platform / System

### K1. TD doesn't launch
**Cause:** GPU drivers, corrupted prefs, permissions.
**Fix on Mac:**
1. Delete `~/Library/Preferences/com.derivative.TouchDesigner2025.plist`.
2. Reboot.
3. Reinstall if still broken.

### K2. TD launches but viewer is black
**Cause:** GPU translation layer issue; or first-launch shader cache building.
**Fix:** wait 1–2 minutes for shader cache on first launch. Force-quit and relaunch. If persists, reinstall MoltenVK with the TD installer.

### K3. Project won't open — "saved in newer version"
**Cause:** the .toe was saved in a build higher than the current install.
**Fix:** update TD; or open .toe as plain text in a hex editor and reset version header (risky — prefer updating).

### K4. Project is huge (>500MB) for little content
**Cause:** referenced media, captured feedback frames, or embedded movies have bloated the save file.
**Fix:** use File → External → External Project to break out heavy resources. Store media on external SSD. Use Movie File In TOP with file paths, never embed large assets.

### K5. Network crashes when you edit a specific operator
**Cause:** this is the signature of a corrupt operator.
**Fix:** copy adjacent operators, delete the bad one, paste them back. Or save, quit, reopen — sometimes an op-level corruption clears.

---

## L. Non-Obvious Things That Are Not Bugs

- **One-frame delay on Feedback** — by design, see A4.
- **TOP opacity parameter being gamma-applied** — Level TOP opacity is linear; if it "looks" wrong after compositing, check Gamma / Colorspace.
- **Project running slower in the editor than in Perform Mode** — editor draws overlays; Perform Mode is faster. Always bench in Perform Mode.
- **CHOP samples looking "stale"** — per-frame CHOP samples are last frame's values relative to the cooking order. This matters in chain topology; fix with re-ordering or explicit Cook Type.

---

## How To Use This File

1. Keyword search first — `/` for the symptom you're seeing.
2. Read the entry's cause and fix.
3. If the fix doesn't resolve it, check `TD_APPLE_SILICON.md` for platform angle, then `WOBAR_TD_DEBUG_LOG.md` for Wobar-specific incidents.
4. If it's a new failure, add an entry here. Format: symptom / cause / fix.

Living document. Every debugging session is a chance to add one entry.
