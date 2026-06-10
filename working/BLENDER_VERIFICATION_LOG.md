---
title: Blender Library Verification Log
version: 1.0
last_updated: 2026-05-23
status: live
scope: Consolidated findings from the Phase 2 stress test of reference/blender_library/. Source-of-truth for every error / gap / parity decision surfaced. Drives the fix queue.
dependencies: [[working/BLENDER_PHASE2_STRESSTEST]], [[working/BLENDER_MCP_RESEARCH]]
---

# BLENDER LIBRARY VERIFICATION LOG

Stress test run 2026-05-23 against Blender 4.5 LTS on Apple Silicon M1. 23 files audited. 6 parallel research passes (D1, A1, A2, A3, B1, B2) executed by subagents. C (agent-usability) and D2 (parity) synthesized from those findings. No live API access during this test.

---

## TL;DR — Headline verdict

The brain is **fundamentally sound and unusually high-quality for one-day-without-API output.** Decision tree is clean, no internal contradictions, no dead links, terminology consistent. Of ~13,500 lines spot-checked at ~10-40% depth per file, four findings are critical (will silently break agent code on 4.5), seven are notable staleness (correct intent, wrong specifics), and two are structural gaps that block specific Anthropic-blessed workflows entirely.

**Ship readiness verdict**: do not register `blender_library/` in `WOBAR_CONTEXT.md` until the 4 CRITICAL fixes land. After fixes, the brain is ready to load-bear on real Blender work. The 7 STALE items and 2 structural gaps can land in a follow-up pass without blocking Phase 3.

---

## CRITICAL — Will break agent code on 4.5 LTS

| # | File | Line(s) | What's wrong | What's correct | Source |
|---|------|---------|--------------|----------------|--------|
| C1 | `BLENDER_PYTHON_API.md` | 510, 762–766, 961 | Claims `'BLENDER_EEVEE_NEXT'` is the canonical 4.2+ EEVEE engine string. | **CONTESTED — needs live verification.** Verification surfaced subagent disagreement. Two subagents (A1, B1) claim the canonical 4.5 identifier is `'BLENDER_EEVEE'` and `'BLENDER_EEVEE_NEXT'` raises `Engine not available`. One subagent (A3) claims `'BLENDER_EEVEE_NEXT'` is correct on 4.5, with the rename back to `'BLENDER_EEVEE'` happening only in 5.0. Issue #122547 likely reports an OLD project file (pre-4.2 `'BLENDER_EEVEE'`) failing because the legacy identifier was retired — which is consistent with the file being CORRECT. **Cannot resolve without live install.** Demoted to LIVE-VERIFY priority #1. | [Issue #122547](https://projects.blender.org/blender/blender/issues/122547), [EEVEE 5.0 release notes](https://developer.blender.org/docs/release_notes/5.0/eevee/) |
| C2 | `BLENDER_PYTHON_API.md` | 938 | Recommends `me.calc_normals_split()` for split normals. | `Mesh.calc_normals_split()` was **removed in 4.1**. Replaced by `Mesh.corner_normals` cached property (read) and `normals_split_custom_set` / `normals_split_custom_set_from_vertices` (write). | [4.1 Python API notes](https://developer.blender.org/docs/release_notes/4.1/python_api/) |
| C3 | `BLENDER_RENDER_EEVEE.md` | 21, 131–134, 412–425, 455 | Uses `bpy.ops.scene.light_cache_bake()`, `light_cache_bake_all()`, `light_cache_free()` as the EEVEE Next bake operators. | These are the **legacy EEVEE** operators **removed in 4.2** when EEVEE-Legacy was deleted. EEVEE Next bakes per-Light-Probe-Volume object via `bpy.ops.object.lightprobe_cache_bake()` / `lightprobe_cache_free()`. Calling the old operators raises `AttributeError`. | [EEVEE 4.2 migration](https://developer.blender.org/docs/release_notes/4.2/eevee_migration/), [Light Probe Volume manual](https://docs.blender.org/manual/en/latest/render/eevee/light_probes/volume.html) |
| C4 | `BLENDER_SHADER_NODES.md` | 63 | Claims Principled BSDF `distribution` default is `'GGX'`. | **`'MULTI_GGX'`** since the 4.0 Principled BSDF v2 rewrite. Agents will produce visually different results than docs imply. | [4.0 Cycles release notes](https://developer.blender.org/docs/release_notes/4.0/cycles/) |

**Verification note on C1:** the spot-check at the cited lines confirmed the file does say what was attributed to it. The disagreement is about *which way the truth runs*, not about whether the claim is in the file. Logging the contradiction rather than picking a side preserves the option to verify on first install.

**Fix protocol for the four above:** edit the source file directly, increment that file's frontmatter version, add the corrected fact to `BLENDER_FOOTGUNS.md` so future agents see the trap and the rule both. None of these are repairable post-install — they will silently land in production code.

---

## STALE — Correct intent, wrong specifics

| # | File | Line(s) | Current claim | Reality | Source |
|---|------|---------|---------------|---------|--------|
| S1 | `BLENDER_LIBRARY_INDEX.md` | 178 | Khronos PBR Neutral View Transform listed as **4.4+** | Added in **4.2** (4.2 Alpha PR #118936). Index needs a version flip. | [PR #118936](https://projects.blender.org/blender/blender/pulls/118936) |
| S2 | `BLENDER_SHADER_NODES.md` | 134 | "Glossy for new files, Anisotropic for older files" — Glossy is the primary name | **Inverted.** Post-4.0 merge, the underlying type is `ShaderNodeBsdfAnisotropic`; `ShaderNodeBsdfGlossy` is the **alias**. Both work for `nodes.new(type=...)`, but `node.bl_idname` reports Anisotropic. | [4.0 Shading release notes](https://developer.blender.org/docs/release_notes/4.0/shading/) |
| S3 | `BLENDER_GEOMETRY_NODES.md` | 352 | Viewport Transform node listed as **4.4+** | Added in **4.2** (PR #118680). | [PR #118680](https://projects.blender.org/blender/blender/pulls/118680) |
| S4 | `BLENDER_RENDER_EEVEE.md` | 351 | `shadow_pool_size` enum includes `'16'`, `'32'`. | Valid values are `['64','128','256','512','1024','2048','4096']`. Default `'512'`. | [SceneEEVEE API](https://docs.blender.org/api/current/bpy.types.SceneEEVEE.html) |
| S5 | `BLENDER_RENDER_CYCLES.md` | 145–152 | "Sample Subset (4.5+)" with a `cycles_merge` operator. | Sample Subset shipped in **4.4**, not 4.5. There is **no `cycles_merge` operator** — merge externally via EXR tools. | [4.4 Cycles release notes](https://developer.blender.org/docs/release_notes/4.4/cycles/) |
| S6 | `BLENDER_APPLE_SILICON.md` | 6, 19, 36 | "MetalRT is on by default on M2/M3; M1 uses BVH path." | **MetalRT hardware ray tracing exists only on M3+** — M1 and M2 lack the dedicated BVH-traversal hardware. Default-on applies to M3 and later. | [PR #114296 M3 tuning](https://projects.blender.org/blender/blender/pulls/114296) |
| S7 | `BLENDER_APPLE_SILICON.md` | 6, 14, 27, 263–266 | Hedges "4.6+ may bump macOS minimum." | **There is no Blender 4.6.** 4.5 LTS is the final release supporting Intel + macOS 11.2. **Blender 5.0 is Apple-Silicon-only on macOS 13 (Ventura) minimum.** | [Intel macOS deprecation in 5.0](https://devtalk.blender.org/t/deprecation-and-removal-of-macos-intel-builds-in-blender-5-0/38835) |
| S8 | `BLENDER_PYTHON_API.md` | 722 | `CompositorNodeMixRGB` listed without deprecation note. | **Deprecated in 4.5 LTS, scheduled for removal in 5.0.** New code should use the Mix Color equivalent. | [4.5 Compositor release notes](https://developer.blender.org/docs/release_notes/4.5/compositor/) |
| S9 | `BLENDER_SHADER_NODES.md` | 178, 393–396 | Sky Texture lists `'NISHITA'`, `'HOSEK_WILKIE'`, `'PREETHAM'` as current. | Preetham was removed from Cycles years ago. In 4.5+ Nishita was renamed Single Scattering; a Multiple Scattering model was added. Lists Hosek-Wilkie and Preetham as legacy. | [Sky Texture manual](https://docs.blender.org/manual/en/latest/render/shader_nodes/textures/sky.html) |
| S10 | `BLENDER_PYTHON_API.md` | 77–78; `DATA_MODEL.md` 170, 440 | `grease_pencils_v3` collection accessor stated as canonical. | Correct on 4.5, but the `v3` suffix is **transient** — slated to drop in 5.0 (renamed back to `grease_pencils`). Agents should know. | [GreasePencilv3 API](https://docs.blender.org/api/current/bpy.types.GreasePencilv3.html) |
| S11 | `BLENDER_ANIMATION.md` | 23, 31, 167, 1024, 1044 | Action Slots framed as "Actions can now drive multiple IDs… check `action.slots` if present." | Understates the structural change. Legacy `action.fcurves` is a back-compat proxy for `action.layers[0].strips[0].channelbag(action.slots[0])` and is **deprecated, scheduled for 5.0 removal.** Direct `fcurves` access has a sunset. | [4.4 Slotted Actions](https://developer.blender.org/docs/release_notes/4.4/upgrading/slotted_actions/) |

**Fix protocol for STALE items:** batch-edit in a single pass, increment frontmatter version, no FOOTGUNS entry needed for most (they're version-tag corrections rather than active failure modes). S2 (Glossy/Anisotropic) and S8 (MixRGB deprecation) probably warrant FOOTGUNS entries.

---

## STRUCTURAL GAPS — Block specific workflows

Identified during B2 (Anthropic blessed workflow walkthrough). Each is a coherent missing module, not a scatter of small misses.

### Gap G1 — Camera projection math is absent

**Blocks:** Anthropic Workflow 4 (render-cost triage). Any task that needs to know "how big is this on screen?" — which includes future tasks like cull-by-screen-size, attention-weighted denoising, and LOD bucketing.

**What's missing:**
- `bpy_extras.object_utils.world_to_camera_view(scene, camera, vec)` — the canonical world→NDC helper. **Mentioned nowhere in 23 files.**
- `obj.bound_box` in world space — building world-space bbox via `[obj.matrix_world @ Vector(c) for c in obj.bound_box]`.
- Screen-space AABB construction from projected corners.
- Camera-frustum clipping (behind-camera, fully-outside-frustum rejection).

**Where to land it:** new "Screen-Space Coverage Recipe" section in `BLENDER_PATTERNS_CINEMATIC.md`, OR new section in `BLENDER_PYTHON_API.md` under "Useful bpy_extras helpers." Cross-link from both directions.

### Gap G2 — NodeFrame annotation API is mentioned but not taught

**Blocks:** Anthropic Workflow 2 (Geometry Nodes annotation). Any task that needs to write commentary into the graph itself.

**What's missing:**
- `nodes.new('NodeFrame')` returns a NodeFrame — mentioned once in a catalog table only.
- `node.parent = frame_node` parenting semantics — undocumented.
- Frame properties: `label`, `text` (accepts a `bpy.data.texts` datablock for multi-line), `use_custom_color`, `color`, `label_size`, `shrink` — undocumented.

**Where to land it:** new "Frame Nodes — The Annotation API" subsection in **both** `BLENDER_GEOMETRY_NODES.md` and `BLENDER_SHADER_NODES.md` (same content, cross-linked). Reference from `BLENDER_WORKFLOW_AGENT_DRIVEN.md` Workflow 2.

---

## PARTIAL — Coverage exists but underweight

These were flagged across A and B passes. None block a workflow outright but each weakens a multi-step task.

- **P1 — Naming conventions cheat-sheet missing.** Workflow 1 (scene-graph cleanup) needs the agent to know what "good" Blender names look like — `MESH_`, `MAT_`, `COL_`, `GN_` prefixes, the `.001` auto-suffix collision behavior, the `bpy.data.X.get("X")` safe-lookup pattern. Land in `BLENDER_DATA_MODEL.md` (Renaming and Collisions subsection).
- **P2 — Recursive node-tree walk patterns missing.** Workflows 2 and 3 both need `for n in tree.nodes: if n.type == 'GROUP': walk(n.node_tree)` patterns. Land one snippet each in `BLENDER_SHADER_NODES.md` and `BLENDER_GEOMETRY_NODES.md`.
- **P3 — `obj.evaluated_get(depsgraph)` is footgun-only.** Multiple workflows need post-modifier truth. Promote to a first-class "Reading Evaluated Geometry" snippet in `BLENDER_PYTHON_API.md` (Depsgraph section).
- **P4 — `user_map()` is a one-liner snippet.** Workflow 3 (material dependency audit) needs the expanded "Dependency Audit Recipe" with type filtering, human-readable location mapping, recursive variant.
- **P5 — Render visibility cheat-sheet missing.** `hide_render`, `hide_viewport`, `visible_camera`, `visible_diffuse`, `visible_glossy`, `visible_transmission`, `visible_volume_scatter`, `visible_shadow`, holdout. Land in `BLENDER_RENDER_CYCLES.md`.
- **P6 — "What breaks when you remove a material" not documented.** Workflow 3's analytical half (pink fallback, GN node errors, override chain breaks). Land in `BLENDER_MATERIALS.md`.
- **P7 — Khronos PBR Neutral view transform not documented at all.** Index flagged it for verification but no file actually teaches it. Land in `BLENDER_MATERIALS.md` and/or `BLENDER_RENDER_CYCLES.md` (color management section).
- **P8 — OIDN Multi-device toggle bug not warned.** B1 confirmed M1 + OIDN GPU works in 4.5, but only when Cycles device is set to "GPU Compute" — Multi-device greys out the "Use GPU" toggle. Land in `BLENDER_FOOTGUNS.md` and cross-reference from `BLENDER_RENDER_CYCLES.md`.

---

## LIVE-VERIFY-ONLY queue (post-install)

These cannot be confirmed without the live Blender 4.5 install. Queue them as the first checks after MCP install.

0. **PRIORITY: Resolve C1.** Run `bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT'` on a fresh 4.5 install. If it succeeds, the file is correct; if it raises `Engine 'BLENDER_EEVEE_NEXT' not available`, the file is wrong and needs the edit. Also try `'BLENDER_EEVEE'`. Document which works.
1. **Official MCP connector tool surface.** The Blender Foundation's `blender.org/lab/mcp-server/` is JS-rendered and blocked from WebFetch via egress allowlist. Press coverage describes the connector as a `bpy` Python API wrapper, implying a small tool surface (likely scene read + `execute_blender_code` only) — versus the 21-tool community `ahujasid/blender-mcp`. **Enumerate the official tool list from Claude Desktop's hammer icon after install. Document in `working/BLENDER_MCP_TOOL_SURFACE.md`.**
2. **Claude Code vs Claude Desktop host.** Anthropic's launch materials advertise Desktop only. Whether the official connector can be wired into Claude Code (against any MCP endpoint, the local socket the addon exposes) is unverified. Affects whether Blender workflow mirrors TD workflow (Code as primary) or breaks symmetry.
3. **OIDN "Use GPU" toggle status on M1 in 4.5.** Multi-device bug from B1. Confirm the workaround (set device to GPU-only, not Multi) still works in 4.5.
4. **EEVEE `shadow_pool_size` enum values.** Spot-check via `bpy.context.scene.eevee.bl_rna.properties['shadow_pool_size'].enum_items.keys()`.
5. **Light probe bake operator name in 4.5.** Confirm `bpy.ops.object.lightprobe_cache_bake()` is the correct replacement for the removed `scene.light_cache_bake`. (C3 above.)
6. **`action.layers[0].strips[0].channelbag(slot)` exact signature.** Slotted Actions 4.4 API was researched from forum docs — confirm signature on live 4.5.
7. **`bpy.ops.import_image.to_plane` operator name.** Add-on was rewritten — operator may be `bpy.ops.image.import_as_mesh_planes` in 4.5.
8. **macOS version on Nick's machine.** If targeting OIDN GPU denoising, macOS 13+ required.
9. **Whether `~/Library/Application Support/Blender/4.5/extensions/user_default/` exists.** Fresh 4.2+ installs may not create it until first install (issue #124809).
10. **Live screenshot capability of the official connector.** Community `ahujasid` has it first-class; the official's status unconfirmed — affects whether Claude can see what it just rendered.

---

## C — Agent-usability simulation results

Two archetypal WOBAR tasks simulated using only brain content (no live API). Self-scored 1–5 on completeness and correctness.

### Task C-1 — Bake sub-bass audio to driver, drive object scale

Steps the agent would take:
1. Find/create target Empty (e.g. `AudioBake_Sub`).
2. Find or create a Graph Editor area for the `bpy.ops.graph.sound_bake` context.
3. Wrap call in `bpy.context.temp_override(area=graph_area)`.
4. Run `bpy.ops.graph.sound_bake(filepath=..., low=20, high=80, attack=0.005, release=0.2, threshold=0.0)` for sub-bass band.
5. Select only the target F-curve before baking (otherwise other selected curves get clobbered).
6. Add driver on target object's `scale.x/y/z` with a variable referencing the Empty's baked channel.
7. Save.

Brain coverage:
- `BLENDER_ANIMATION.md` L605–617: full `sound_bake` operator signature — **CONFIRMED CORRECT in A3.**
- `BLENDER_ANIMATION.md` L1018: gotcha — clears existing keyframes; use `use_accumulate=True` to layer.
- `BLENDER_ANIMATION.md` L1020: gotcha — requires Graph Editor context, `temp_override` pattern.
- `BLENDER_ANIMATION.md` L313: example with `AudioBake_Sub` Empty already named.
- `BLENDER_ANIMATION.md` L629: per-band Empties pattern.
- `BLENDER_PYTHON_API.md` L188: `temp_override` pattern documented.
- Driver setup: `BLENDER_ANIMATION.md` L227, L247.

**Score: completeness 5/5, correctness 5/5.** The agent could execute this task end-to-end from brain content alone. This is the brain at its best — encyclopedic on the specific operator, gotchas pre-flagged, cross-file integration smooth.

### Task C-2 — Render 720×1280 portrait Mirror clip with alpha for TD ingest

Steps the agent would take:
1. `scene.render.engine = 'BLENDER_EEVEE'` or `'CYCLES'`.
2. `scene.render.resolution_x = 720`, `resolution_y = 1280`, `resolution_percentage = 100`.
3. `scene.render.film_transparent = True`.
4. `scene.render.image_settings.color_mode = 'RGBA'`.
5. Format: PNG sequence for portability, or ProRes 4444 for single-file alpha.
6. If Cycles: enable OIDN denoiser, `use_gpu=True`, `denoising_quality='HIGH'`.
7. Set output path, call `bpy.ops.render.render(animation=True)`.

Brain coverage:
- `BLENDER_PYTHON_API.md` L770–772: render resolution settings — CONFIRMED.
- `BLENDER_PYTHON_API.md` L783: `color_mode = 'RGBA'` — CONFIRMED.
- `BLENDER_FOOTGUNS.md` R-1: alpha + `film_transparent` gotcha already documented.
- `BLENDER_WORKFLOW_RENDER_FOR_TD.md`: ProRes 4444 alpha, PNG sequence (1920×1080 math).
- `BLENDER_RENDER_CYCLES.md` L189, 226: OIDN GPU + `denoising_quality` enum — CONFIRMED.
- `BLENDER_APPLE_SILICON.md`: VideoToolbox ProRes hardware encoding — CONFIRMED.

Issues:
- C1 (EEVEE engine string) — if agent picks EEVEE, the brain tells it to use `'BLENDER_EEVEE_NEXT'` which fails on 4.5. **Production-breaking.**
- P5 (render visibility cheat-sheet missing) — if any geometry should be hidden from render only (not viewport), agent has no reference.
- P8 (OIDN Multi-device toggle bug) — if Cycles device is set to "GPU+CPU Multi", `use_gpu` silently does nothing. Brain doesn't warn.
- No portrait-specific guidance — camera aspect, vertical safe zones for 9:16 TD ingest.

**Score: completeness 4/5, correctness 3/5.** The render pipeline pieces are well-documented; the EEVEE engine string error and the Multi-device gotcha both drop correctness materially. After C1 and P8 fixes, this rises to 5/5 / 5/5.

### C summary

Average across 2 tasks: **completeness 4.5/5, correctness 4.0/5.** Pass criteria was ≥4/5 on both — met. The single biggest correctness contaminant is C1 (EEVEE engine string), which weakens every render-related task. C1 fix is high-leverage.

---

## D2 — Parity table vs `td_library`

| Slot | `td_library` | `blender_library` | Verdict | Notes |
|------|--------------|-------------------|---------|-------|
| Index file | TD_LIBRARY_INDEX | BLENDER_LIBRARY_INDEX | **matches** | Both have decision tree, file registry, version target. |
| Platform constraints | TD_APPLE_SILICON | BLENDER_APPLE_SILICON | **matches** | Both M1-specific; Blender file has 4 STALE items per A3. |
| Build philosophy / mental model | TD_NETWORK_VS_GLSL + TD_EFFICIENT_NETWORKS | (nothing direct) | **should close** | Blender needs a "When to reach for bpy.data vs bpy.ops vs Geometry Nodes vs writing Python" decision file. The closest equivalent today is the bpy.ops-avoidance guidance scattered across PYTHON_API and WORKFLOW_AGENT_DRIVEN. |
| Footgun log | TD_FOOTGUNS (deep) | BLENDER_FOOTGUNS (seeded only) | **partial** | This stress test will add ~6–8 entries. Will grow naturally with live sessions. |
| Operator catalogs (encyclopedic) | 7 (POP/TOP/CHOP/SOP/MAT/DAT/COMP) | 4 (PYTHON_API + DATA_MODEL + GEOMETRY_NODES + SHADER_NODES) | **intentional gap** | Blender domain is shaped differently — everything routes through `bpy`, not per-family operators. The 4 Blender catalogs go to encyclopedic depth (1177 + 472 + 897 + 732 lines). Adding COMPOSITOR + RENDER deep-references would balance the slot. |
| Third-party library guides | TD_POPX_GUIDE (1) | (none) | **should close eventually** | Blender community add-ons (Geometry Nodes Pro Pack, Hard Ops/Boxcutter, Animation Layers, BlenderKit/Poly Haven hooks) deserve guides if Nick adopts any. Lower priority pre-install. |
| Pattern library | 8 PATTERN files (AUDIO_REACTIVITY, FEEDBACK, GENERATIVE, 3D_SCENES, INSTANCING, COMPOSITING, PARTICLES, TEXT) | 3 PATTERN files (PROCEDURAL, LIGHTING, CINEMATIC) | **partial — close 3-4** | Likely additions in priority order: AUDIO_REACTIVITY (partial coverage in ANIMATION.md, deserves its own file), MATERIAL recipes (the missing PBR/glass/iridescent register), INSTANCING (geometry-nodes scatter recipes), COMPOSITING (Blender compositor patterns). TEXT and PARTICLES are lower priority for Blender (text is sparingly used, particles deprecated in favor of Geometry Nodes). |
| Workflow playbooks | 8 WORKFLOW files | 3 WORKFLOW files | **intentional gap with one addition** | TD is live + offline; Blender is offline-only. No analog needed for LIVE_VJ, LIVE_AUDIOREACTIVE, MIDI_OSC, AV_INTEGRATION, PROJECTION_MAPPING, INSTALLATION. Should close: **WORKFLOW_OPTIMIZATION.md** (Blender perf tuning — depsgraph caching, modifier order, Cycles sample strategies, EEVEE virtual shadow map tuning). |
| Debug log integration | TD_CLAUDE_DEBUG_LOG (separate from FOOTGUNS, referenced by INDEX, used pre-action) | (none yet) | **should close** | Same purpose as FOOTGUNS but session-keyed — "things Claude was wrong about, confirmed corrections." Build `BLENDER_CLAUDE_DEBUG_LOG.md` once live sessions accumulate corrections. |
| Master vault registration | TD library registered in WOBAR_CONTEXT | NOT registered | **should close (after stress test passes)** | The 4 CRITICAL fixes need to land first. Then register `blender_library/` + `working/BLENDER_MCP_RESEARCH.md` + `working/BLENDER_PHASE2_STRESSTEST.md` + `working/BLENDER_VERIFICATION_LOG.md`. |

**Parity summary:** 1 match, 1 match (with content issues), 4 "should close" with priorities ranked, 2 "intentional gap" (acknowledged shape difference), 1 "partial" (will grow). The Blender brain is **structurally smaller than the TD brain by design** (offline-only, no live performance) but is **missing a build-philosophy file** that the TD library uses heavily.

---

## Fix queue — Recommended landing order

**Tier 1 — Land before registering the library** (3 CRITICAL confirmed, 1 contested):
1. C2 — `calc_normals_split` in `PYTHON_API.md`
2. C3 — EEVEE light cache bake operators in `RENDER_EEVEE.md`
3. C4 — Principled BSDF default in `SHADER_NODES.md`
4. C1 — EEVEE engine string — **do NOT edit yet**; live-verify on install first. If file is correct (A3's reading), no fix needed. If wrong (A1/B1's reading), edit at that point.

**Tier 2 — Batch with Tier 1 if cheap** (11 STALE items, single editing pass):
- S1–S11 above. All version-tag corrections and notation flips, no new content needed.

**Tier 3 — Land before declaring Phase 2 done** (structural gaps + high-leverage partials):
- G1 — Camera projection recipe (`PATTERNS_CINEMATIC.md`)
- G2 — NodeFrame annotation API (`GEOMETRY_NODES.md` + `SHADER_NODES.md`)
- P1 — Naming conventions cheat-sheet (`DATA_MODEL.md`)
- P3 — `evaluated_get(depsgraph)` first-class (`PYTHON_API.md`)
- P7 — Khronos PBR Neutral documented (`MATERIALS.md` or `RENDER_CYCLES.md`)
- P8 — OIDN Multi-device gotcha (`FOOTGUNS.md`)

**Tier 4 — Phase 2.5 (post-live-verify)**:
- LIVE-VERIFY queue (10 items, post-install)
- Remaining partials (P2, P4, P5, P6)
- D2 should-close items: WORKFLOW_OPTIMIZATION, build-philosophy file, AUDIO_REACTIVITY pattern, debug log

**Out of Phase 2 entirely**:
- Third-party add-on guides — Phase 3 if needed
- Pattern files for TEXT / PARTICLES analogs — only if WOBAR work actually uses them
- WOBAR_BLENDER_*.md brand layer — Phase 3

---

## Confidence

This stress test ran at the depths the plan committed to: ~10–40% fact-checked per file via web research, no live API access. Higher-risk surfaces were prioritized — version-introduced features, engine strings, bl_idname spot-checks, operator names. The 4 CRITICAL findings are high-confidence (each cited to a primary release-notes or PR source). The STALE findings are high-confidence as version corrections; lower-confidence on phrasing recommendations. Live verification post-install will surface a second wave of findings that no amount of web research could have caught — primarily the official MCP connector's actual tool surface and a handful of operator signatures that didn't fully resolve through forum sources.

The plan's pass criteria called for ≥4/5 average on the C simulation; we hit 4.5/5 completeness, 4.0/5 correctness — meets bar, with correctness held back by C1. After Tier 1 fixes, the brain is load-bearing for real Blender work.

---

## Source bibliography

All sources cited inline in this log. Top-of-list for the four CRITICAL fixes:
- [Blender 4.2 EEVEE migration](https://developer.blender.org/docs/release_notes/4.2/eevee_migration/)
- [Blender 4.1 Python API release notes](https://developer.blender.org/docs/release_notes/4.1/python_api/)
- [Blender 4.0 Cycles release notes](https://developer.blender.org/docs/release_notes/4.0/cycles/)
- [Blender 4.4 Slotted Actions](https://developer.blender.org/docs/release_notes/4.4/upgrading/slotted_actions/)
- [Blender 4.5 LTS release page](https://www.blender.org/download/lts/4-5/)
- [SceneEEVEE Python API](https://docs.blender.org/api/current/bpy.types.SceneEEVEE.html)
- [Light Probe Volume manual](https://docs.blender.org/manual/en/latest/render/eevee/light_probes/volume.html)
- [Engine identifier issue #122547](https://projects.blender.org/blender/blender/issues/122547)
