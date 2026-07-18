---
title: Corridor Research Plan — Lit Procedural 3D
version: 1.0
last_updated: 2026-07-17
status: live — APPROVED 2026-07-17
scope: A depth-learning plan to master the two sides of a professional-looking procedural TD corridor — (A) procedural geometry, (B) camera + lighting + atmosphere. Front-loaded on M1 Metal platform risk and on the true documentation gaps. Each phase = learn in depth → build a probe in TD → capture into the brain. Derivative documentation is the priority source.
dependencies: [[WOBAR_VISUAL_RESET]], [[WOBAR_WORLD]], [[TD_LIBRARY_INDEX]], [[TD_APPLE_SILICON]], [[TD_PATTERNS_3D_SCENES]], [[TD_OPERATORS_POP]], [[TD_OPERATORS_MAT]]
---

# CORRIDOR RESEARCH PLAN — LIT PROCEDURAL 3D

**Why this exists.** Five prior WOBAR pieces read competent but *flat* — nearly all 2D
shaders / TOP composites, the lane with the lowest professional ceiling in TD. The
professional bar is **light + depth + atmosphere** on real procedural 3D geometry.
This plan learns the two sides that clear that bar and plays entirely to TD's native,
Mac-safe strengths (POPs = GPU compute, full-speed on M1).

**Approved 2026-07-17:** Phase 0 blocking-first; full depth (no lean shortcut);
**prioritize Derivative documentation** (docs.derivative.ca) as the primary source,
TD forum for Metal-specific behavior, in-TD probes for anything the docs can't judge.

**Method law (from the vault's own lesson — `WOBAR_VISUAL_RESET` §method).** Text
research cannot judge frames. Every phase builds a small probe in TD (via TWOZERO)
and **Nick looks** — docs inform, the eye rules. No phase is "done" on reading alone.

---

## COVERAGE BASELINE (audit 2026-07-17 — what the brain already holds)

**Geometry side — strong.** POPs catalog, instancing, particles, POPX guide all deep
(POPX even names an "Act 3 tunnel, Reverse=True, distant→close scale"). Gaps: no
consolidated Z-corridor recipe; no rings-down-+Z-with-phase example; **3D
superposition (compositing N corridor render passes) uncovered.**

**Lighting/atmosphere side — split.** Deep on lights, shadow *parameters*, PBR, and 2D
grade/grain post. Weak-to-absent exactly where professional depth comes from:
- **Fog / atmosphere / volumetrics — #1 gap** (one sentence in the whole vault).
- **Depth of field — #2 gap** (concept-only).
- **Shadow / IBL on M1 Metal — UNVERIFIED** (`TD_APPLE_SILICON.md` silent on shadows).
- Camera cinematography thin; **bloom has no canonical build**.

The irony driving this plan: documented deepest where the flat lane lives (2D post),
thinnest where expensive depth is made (in-scene atmosphere, DOF, real light on Metal).

---

## PHASE 0 — PLATFORM REALITY CHECK  *(BLOCKING — do first)*
**Learn:** what actually renders under MoltenVK → Metal on M1 before investing in any
feature. Resolve the unverified holes: `soft2d` / shadow maps, Environment Light / IBL,
PBR correctness, real-DOF cost at 720×1280.
**Derivative docs:** Metal / Vulkan article; Release Notes for the installed build;
Light COMP (shadow params); Environment Light COMP; Render TOP. TD forum for the
Metal caveats the main docs omit.
**Probe:** minimal TD scenes — one lit sphere + soft shadow; one IBL/env-light sphere;
a DOF test. Look: renders correct, black, or degraded? Note fps cost.
**Deliverable:** an **M1 render-feature matrix** appended to `TD_APPLE_SILICON.md`
(feature → works / black / degraded / cost). De-risks every downstream phase.
**Status:** ✅ LIVE-VERIFIED 2026-07-17 — the high-risk set is all GREEN. Promote the
verified rows to `TD_APPLE_SILICON.md` at close-out. Env: `NewProject.1.toe`, build
**2025.32820** (not the vault's assumed 32460), on M1 Metal. Probe scene lives at
`/project1/probe_shadow` (throwaway — keep as reference or discard).

### Phase 0 — LIVE-VERIFIED results (probe scene `/project1/probe_shadow`, 2026-07-17)
Built a lit 3D scene (torus caster + grid floor + cone light + camera + material) and
screenshotted / numerically sampled each feature. All at 1280×1280.
- **Soft2d soft shadows — ✅ WORKS.** The #1 uncertainty. Real soft penumbra renders,
  not black, not hard-only. Requires: light `lookat` the caster + tightened light FOV
  (renderTOP card + confirmed). This was the load-bearing risk — cleared.
- **Direct lighting (cone, diffuse+specular) — ✅ WORKS.**
- **phongMAT — ✅ WORKS** (has native `shadowstrength`/`shadowcolor`; diffuse pars are
  `diffr/diffg/diffb`, NOT `diffuser`).
- **pbrMAT — ✅ WORKS**, both dielectric (metallic 0) lit by direct light AND metallic
  (metallic 0.9) reflecting the environment. NO black-silhouette (the 2021 bug was
  Intel/pre-Vulkan). Pars: `basecolorr/g/b`, `metallic`, `roughness`, `emitr/g/b`.
- **Depth TOP — ✅ WORKS (linchpin).** Sampled numerically: opaque geo returns valid
  varying depth (torus 0.973 / floor 0.968 / background 1.0). Gotcha: perspective depth
  is non-linear — near=0.1/far=200 crushes everything to ~0.99; **tighten the far plane
  (far≈28) for usable precision**, then rerange. `depthTOP.par.op` = the renderTOP,
  `depthspace='cameraspace'` or `'reranged'`. ⚠️ Debug log still holds: transparent /
  instanced geo does NOT write reliable depth — keep DOF/fog geometry opaque.
- **Environment Light / IBL — ✅ WORKS.** Metallic surface reflects the env map. Type is
  `environmentlightCOMP`. Keep `envlightmapprefilter='off'` (debug log: `automatic` ≈
  142ms/frame on M1). Add to renderTOP `lights` alongside the key light.
- **Bloom TOP — ✅ NATIVE (confirmed).** `output='inputplusbloom'`, `bloomthreshold`,
  `bloomintensity`, `min/maxbloomradius`. Don't hand-build bloom.
- **1280×1280 render + aa8 antialias — ✅ WORKS** (edges clean).

**Still to verify (lower risk — quick follow-ups, not blockers):**
- Render Pass / Render Select TOP multipass on Metal (standard MRT — untested live).
- MSAA 8× actually applying vs silently dropping to 4× (aa8 looked clean; not confirmed exact).
- Volumetric fog: no native node — depth-driven fog rides the (working) Depth TOP;
  true volumetric shafts = raymarched GLSL (Phase 3).
- DOF: no native path on any platform — build from the (working) Depth TOP + blur (Phase 3).

**Net:** every feature the lit-atmospheric corridor structurally depends on — real light,
soft shadow, PBR, IBL reflection, valid depth (→ fog + DOF), bloom — is confirmed on M1
Metal at build 2025.32820. Phase 1 (corridor geometry) is unblocked.

### Phase 0 — Doc-draft matrix (Derivative docs + forum; 2026-07-17) — LIVE-VERIFY PENDING
> Not yet promoted to `TD_APPLE_SILICON.md` — reference layer takes only live-verified
> rows. Green = doc says safe; ⚠ = must test in TD before building on it.

- **Compute shaders on Mac: WORK** (Vulkan→MoltenVK→Metal; old "compute = Windows only"
  note is STALE per Derivative staff). GLSL auto-transpiles to MSL.
- **Native Bloom TOP: EXISTS** — do NOT hand-build bloom. 2D/compute → runs on Metal. ✅
- **PBR MAT: likely fine** — the 2021 "black silhouette" bugs were Intel + pre-Vulkan,
  not the current M1 path. ⚠ quick confirm.
- **Environment Light / IBL: FIXED** — the old M1 dummy-light bug was patched 2021.
  Keep HDRI **static** (animated env maps are heavy on M1). ⚠ confirm reflects on PBR.
- **Soft shadows (`soft2d`): UNKNOWN — highest risk.** Fully documented, actively
  maintained in 2025, NOT geometry-shader-dependent (likely OK), but **zero Metal
  confirmation either way.** ⚠⚠ verify FIRST. Fallbacks: `hard2d`, then fake
  (blurred projected shadow / contact shadow).
- **Depth of Field: NO native path on ANY platform.** Render TOP has no DOF param.
  Build from Depth TOP + Blur/Luma Blur, or GLSL bokeh (Swaggy Bokeh). ⚠ GLSL route
  must transpile to MSL. **Depth TOP correctness is the linchpin — DOF *and* depth-fog
  both break if Metal depth readback is wrong. Validate Depth TOP early.**
- **Render Pass / Render Select / Depth TOP (multi-pass, AOVs): UNKNOWN on Metal** —
  standard MRT/framebuffer, no breakage found, no M1 confirmation. ⚠ verify.
- **Instancing: likely OK** (the one forum error was instancing + geometry shader = the
  GS breakage, not instancing). ⚠ verify high counts.
- **MSAA: capped at 8x on Apple GPUs.** Render TOP's 16x/32x cannot run — **cap at 8x**,
  confirm 8x isn't silently dropping to 4x. Edge-quality ceiling at 1280.
- **Geometry-shader nodes: DEAD/black on Metal** (established). No line-expansion / GS
  particle MATs in the corridor.
- **Hardware ray tracing: UNSUPPORTED on macOS.**
- **⚠⚠ POPs: DEGRADED / UNSTABLE on M1.** Release notes: some POPs examples fail on
  macOS (Mac GPU + MoltenVK bugs); **a POPs crash can hang the macOS graphics driver
  and force a REBOOT.** Atomic Float, double-precision attrs, HW ray tracing all
  unsupported for POPs on macOS. **Derivative recommends preferring SOPs.** This
  directly bears on the "focus on POPs" geometry direction — see Phase 1 decision.

**Live-probe queue (run in TD, then promote verified rows):** (1) lit sphere +
`soft2d` shadow — renders soft penumbra, not black/hard-only, at 1280×1280;
(2) PBR sphere (metal/rough/normal/emission) under a real light — no black silhouette;
(3) static-HDRI Environment Light — reflects on PBR; (4) Depth TOP from a Render TOP —
valid depth (gates DOF + fog); (5) 2-pass Render Pass composite; (6) Bloom TOP sanity;
(7) MSAA 8x actually applies. If any POPs geometry is used: save-often, verify the
specific nodes don't crash.

## PHASE 1 — CORRIDOR GEOMETRY SPINE  *(consolidate what you own)*
**Learn:** wire the scattered ingredients into ONE Z-receding corridor recipe —
spine curve → cross-section → recession → camera-facing. Fill the two geometry gaps:
the consolidated recipe + rings-down-+Z-with-per-element-phase. Geometry only, no light.
**Derivative docs:** POP operator pages (Tube, Grid, Line, Sweep/Skin equivalents,
Point Generator, Noise POP, Copy POP); Geometry COMP + Instancing; Alembic/curve
sources. Cross-ref POPX guide (Sweep, Instancer curve-mode, MoveAlongCurve).
**Probe:** a bare procedural tube/instanced corridor receding in Z, noise-animated.
**Deliverable:** new `reference/td_library/TD_PATTERNS_CORRIDOR.md` — the single spine
walkthrough the brain currently lacks.
**Status:** ☐ not started

## PHASE 2 — LIGHT & MATERIAL ON THE CORRIDOR  *(leverage strength)*
**Learn:** apply the already-deep light rigs + PBR to the corridor geometry.
Single-source vs three-point *for a receding tunnel*; rim light for edge read;
**emissive-as-leak** (material = "what leaked through the forcing," lit for real
instead of faked in 2D — crease_veil's instinct, done right).
**Derivative docs:** PBR MAT; Light COMP; Geometry COMP material assignment;
texture-map slots (normal / emit / roughness).
**Probe:** the Phase-1 corridor, now lit + PBR'd. Judge: does light + material read
professional yet?
**Deliverable:** verified lit-corridor look-dev notes + canonical values (into
`TD_PATTERNS_CORRIDOR.md` or a build brief).
**Status:** ☐ not started

## PHASE 3 — THE PROFESSIONAL LEVERS: ATMOSPHERE → DOF → CAMERA → BLOOM  *(the real gaps)*
**Learn (the heart of the plan — where flat becomes expensive):**
- **Atmosphere/fog:** depth-driven fog, in-scene fog, whether volumetric shafts are
  Metal-achievable. This *is* non-arrival — fog eats the far end, a reveal becomes
  un-renderable by construction.
- **DOF:** real vs poor-man's depth-lumablur; focus for the push-in.
- **Camera:** push-in with FOV compression; eased / weighted moves.
- **Bloom:** build the missing canonical bloom (pairs with Phase-2 emissive PBR).
**Derivative docs:** Render TOP (depth, DOF if native); Depth TOP; Render Pass /
Render Select TOP; Camera COMP; fog approaches; Luma Blur / Bloom TOP building blocks.
**Probe:** add fog + DOF + camera push + bloom to the lit corridor. This is the
"does it finally look professional to my eye" gate.
**Deliverable:** new `reference/td_library/TD_ATMOSPHERE_DEPTH.md` — fog, DOF, bloom,
camera-move, corridor-oriented and Metal-verified. **The highest-value artifact here.**
**Status:** ☐ not started

## PHASE 4 — MULTI-PASS RENDER + 3D SUPERPOSITION
**Learn:** depth AOV / render passes / compositing **N corridor render layers by
weight** — the collapse mechanic (weights equalizing, `WOBAR_VISUAL_RESET` §3) rebuilt
in real lit 3D, not a fragment shader. NOT Merge POP (that unions = combining, banned);
keep N parallel render layers, composite additive/by-weight.
**Derivative docs:** Render Pass TOP; Render Select TOP; Depth TOP; Composite TOP
blend modes; multi-camera / multi-render setups.
**Probe:** 2–4 corridor render layers, weights on a slider (later the audio drop).
**Deliverable:** `reference/td_library/TD_PATTERNS_MULTIPASS.md` (or extend
`TD_PATTERNS_COMPOSITING.md`).
**Status:** ☐ not started

## PHASE 5 — INTEGRATE + PROMOTE
**Learn:** fold verified findings into the corridor build brief; make the new files
discoverable.
**Deliverable:** update `TD_LIBRARY_INDEX.md` (+ `WOBAR_TD_INDEX.md`) with the new
files; a corridor build brief that supersedes the v0.1-spec'd `tunnel_oxidized`.
**Status:** ☐ not started

---

## SEQUENCING
0 blocking → 1 → 2 → 3 → 4 → 5. Phases 1–2 may run in one working session (geometry
then light on the same probe). Phase 3 is the gate: if the corridor doesn't read
professional after atmosphere + DOF + camera + bloom, the diagnosis was wrong and we
re-open before Phase 4.

## SOURCE PRIORITY
1. **Derivative documentation** (docs.derivative.ca) — operator pages, articles,
   release notes for the installed build. Primary.
2. **TD forum** — Metal-specific behavior the main docs omit.
3. **In-TD probes via TWOZERO** — the only judge of "does it render" and "does it look
   professional." Overrides docs on both.
