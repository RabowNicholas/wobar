---
title: Blender Phase 2 Stress Test — Research Plan
version: 1.0
last_updated: 2026-05-23
status: live
scope: Research plan for stress-testing the 23-file reference/blender_library/ brain before it goes load-bearing on real Blender work. Plan-only deliverable. Execution happens in subsequent sessions.
dependencies: [[working/BLENDER_MCP_RESEARCH]], [[reference/blender_library/BLENDER_LIBRARY_INDEX]]
---

# BLENDER PHASE 2 STRESS TEST — RESEARCH PLAN

## Goal

Validate that `reference/blender_library/` (23 files, ~13,500 lines, written 2026-05-22) is correct, complete, agent-usable, and structurally on-par with `reference/td_library/`. End state: when Claude is handed an agentic Blender task and pulls files per the decision tree, the output should be expert-level on stock Blender 4.5 LTS features — no hallucinated APIs, no missed defaults, no gaps in the patterns an agentic technical artist actually needs.

The brain was written in a single 2026-05-22 session from web research without live API access. That's the risk. This stress test is the verification pass before we install the MCP connector and start trusting it.

## Non-goals

- Live MCP connector behavior testing (separate effort, post-install).
- Phase 3 `WOBAR_BLENDER_*.md` brand-layer docs (not built yet — out of scope).
- Actually rendering anything in Blender.
- Rewriting files that pass — only fix what fails.

## The four dimensions

Pulled from Nick's stress-test scope answer. Each dimension gets its own pass with its own pass criteria. Order recommended: D1 → A + B in parallel → C → D2 (cheapest structural problems first; D2 parity needs A+B fixes already landed).

---

### Pass A — Accuracy

**Question being answered.** Is every fact in the 23 files actually true for Blender 4.5 LTS?

**Method.** File-by-file, line-by-line fact-check against authoritative sources. Three categories of claim to verify:

1. **API claims** — class names, method signatures, `bl_idname` strings, property names, default values, enum string literals. Verify against `docs.blender.org/api/current/`.
2. **UI claims** — panel names, editor names, mode names, menu paths, shortcut keys. Verify against `docs.blender.org` user manual.
3. **Behavior claims** — engine behaviors, performance characteristics, version-specific quirks, M1/Metal specifics. Verify against release notes, Blender source on `projects.blender.org`, and `blender.stackexchange.com` for community-confirmed gotchas.

**Per-file workflow.**
- Read file top-to-bottom.
- For each factual claim, mark `CONFIRMED` / `WRONG` / `STALE` / `UNVERIFIED`.
- For `WRONG` and `STALE`: fix in source file, log diff to `working/BLENDER_VERIFICATION_LOG.md`.
- For `UNVERIFIED` claims that can't be web-checked (require live install): mark them in a new `BLENDER_FOOTGUNS.md` section "Pending live verification."

**Files in priority order** (most load-bearing first, so failures cascade least):
1. `BLENDER_PYTHON_API.md` — every other file references this. Single largest accuracy risk.
2. `BLENDER_DATA_MODEL.md` — vocabulary anchor; if this drifts, every pattern file drifts.
3. `BLENDER_GEOMETRY_NODES.md` — encyclopedic, fast-moving area (simulation zones, repeat zones, fields are recent).
4. `BLENDER_SHADER_NODES.md` — encyclopedic, version-sensitive (Khronos PBR Neutral added 4.4).
5. `BLENDER_RENDER_CYCLES.md` — OIDN GPU/Metal claims need verification.
6. `BLENDER_RENDER_EEVEE.md` — engine string (`BLENDER_EEVEE_NEXT`) version-sensitive.
7. `BLENDER_ANIMATION.md` — Action Slot system added 4.4 may not be reflected correctly.
8. `BLENDER_APPLE_SILICON.md` — platform claims age fast; macOS minimums shift per release.
9. `BLENDER_MATERIALS.md`, `BLENDER_MODELING.md`, `BLENDER_SCULPTING.md` — apply same method.
10. `BLENDER_COMPOSITOR.md`, `BLENDER_ASSET_IO.md`, `BLENDER_ADDONS.md`, `BLENDER_UI_VOCABULARY.md` — apply same method.
11. Pattern files (`PATTERNS_PROCEDURAL`, `PATTERNS_LIGHTING`, `PATTERNS_CINEMATIC`) — fact-check the supporting claims, parity-check the recipes (pass D2).
12. Workflow files (`WORKFLOW_RENDER_FOR_TD`, `WORKFLOW_ASSET_FOR_TD`, `WORKFLOW_AGENT_DRIVEN`) — fact-check the API/format claims.

**Pass criteria.**
- Zero unverified `bl_idname` strings in shipped pattern/workflow files (every one is `CONFIRMED` or moved to a pending-live-verification list).
- Zero contradicted version claims (e.g., "added in 4.4" verified against 4.4 release notes).
- Every fixed error appears in `BLENDER_VERIFICATION_LOG.md` with file/line/before/after.
- `BLENDER_FOOTGUNS.md` updated with any failure patterns surfaced during the fact-check.

**Estimated effort.** Largest pass. Multi-session in execution. PYTHON_API alone is 1177 lines.

---

### Pass B — Completeness

**Question being answered.** What does an agentic Blender artist need that the brain doesn't cover?

**Method.** Three sub-passes.

**B1 — Burn down the empirical-verification flags.** The index explicitly lists 6 verification flags at the bottom. Each one is a known gap. Plan to convert each from "flagged" to "confirmed" or "documented as live-verify-only":

| Flag | Where it lives | How to verify pre-install |
|------|---------------|---------------------------|
| Exact Blender version installed | `BLENDER_APPLE_SILICON.md`, `BLENDER_RENDER_EEVEE.md`, `BLENDER_ANIMATION.md` | Confirm target = 4.5 LTS. Build a small "version diff matrix" 4.2 → 4.5 documenting Action Slot system (4.4+), Khronos PBR Neutral (4.4+), `grease_pencils_v3` collection rename. |
| Exact MCP connector tool surface | `BLENDER_WORKFLOW_AGENT_DRIVEN.md` | Read addon source on the Blender Lab repo. Document tool names + parameters before install. |
| 60+ `bl_idname` strings | `PYTHON_API`, `GEOMETRY_NODES`, `SHADER_NODES`, `COMPOSITOR` | Cross-reference each against Blender's `nodeitems_builtins.py` and shader/geom-node registration source. |
| OIDN GPU (Metal) device availability | `RENDER_CYCLES.md`, `APPLE_SILICON.md` | Check Blender source for Metal-OIDN registration. Note: may be moot on M1 — verify Apple Silicon GPU denoiser actually appears in dropdown post-install. |
| macOS minimum version | `APPLE_SILICON.md` | Check release notes for 4.2 → 4.5. Lock the minimum claim. |
| Library override / asset library / Extensions install paths | `ADDONS.md`, `ASSET_IO.md` | Confirm via current Blender docs. Legacy add-on directory pathway may be deprecated in favor of Extensions. |

**B2 — Gap analysis against the four Anthropic-blessed workflows.** The official launch demos four agentic technical artist workflows: scene-graph cleanup, Geometry Nodes annotation, material dependency audit, render-cost triage. For each:
- Walk through the workflow conceptually as if Claude were doing it via MCP.
- Identify every API call, every concept, every UI reference needed.
- Check the brain covers each. Log any miss.

**B3 — Gap analysis against industry-standard pattern density.** For the three pattern files (`PATTERNS_PROCEDURAL`, `PATTERNS_LIGHTING`, `PATTERNS_CINEMATIC`):
- Pull pattern inventories from authoritative community sources: Erindale (geometry nodes), Default Cube (geometry nodes), CG Cookie (general), Blender Guru (lighting/cinematic), Polygon Runway (stylized 3D).
- Count canonical patterns covered vs. canonical patterns missing.
- Flag missing patterns by priority (would-WOBAR-use-it vs. industry-standard-but-tangential).

**Pass criteria.**
- Every B1 verification flag is `CONFIRMED` or `LIVE-VERIFY-PENDING` with a specific verification step queued.
- Each of the four Anthropic-blessed workflows has a documented "Claude could execute this end-to-end from the brain" walk-through, or a list of specific gaps.
- Each pattern file shows ≥80% coverage relative to its community benchmark, or has gaps listed with priority labels.

**Estimated effort.** Medium. B1 and B2 are bounded. B3 has the highest risk of expanding scope — cap the community survey at 3 sources per pattern file.

---

### Pass C — Agent-usability

**Question being answered.** Can Claude actually drive Blender successfully using these docs as context — or do the docs explain everything except how to use them?

**Method.** Synthesize agent behavior without live API. Two sub-passes.

**C1 — Decision-tree walk.** For each branch of the `BLENDER_LIBRARY_INDEX.md` decision tree:
- Simulate the prompt: "Nick says X."
- Walk the decision tree to the recommended file pulls.
- Read only those files.
- Compose the MCP prompt Claude would issue.
- Audit: is the prompt complete? Does Claude know which `bpy.ops` call to make, with which parameters, in which mode (object vs edit vs sculpt)?

Branches to walk:
1. Build geometry from scratch (modeling)
2. Build a procedural environment (geometry nodes + procedural patterns)
3. Sculpt an organic form
4. Create or modify a material
5. Set up an EEVEE render
6. Set up a Cycles render
7. Animate something audio-driven (the bake-audio-to-driver pattern)
8. Import an asset
9. Export render for TD ingest

**C2 — Archetypal task simulation.** Pick 5 archetypal Blender tasks that would actually happen in WOBAR work:
1. Build a procedural chamber interior (geometry nodes scatter + lighting + cinematic camera)
2. Author a black PBR material with subtle iridescence
3. Bake audio to driver, drive a single object's scale by sub-bass envelope
4. Render a 720×1280 portrait Mirror clip with alpha for TD ingest (Cycles, with denoiser)
5. Author a glass shader for an Act 1 orb-style render

For each task: compose the full prompt sequence Claude would issue to the MCP. Self-rate completeness (1-5) and correctness (1-5) per prompt. Log every uncertainty as a brain gap.

**Pass criteria.**
- All 9 decision-tree branches produce executable prompt sequences using only the brain.
- 5 archetypal tasks average ≥4/5 on both completeness and correctness.
- Every uncertainty surfaced becomes either a brain fix or a footgun-log entry.

**Estimated effort.** Medium. Bounded by 9 + 5 = 14 simulation runs. Each run is 20-30 min if done thoroughly.

---

### Pass D — Consistency + parity

**Question being answered.** Does the brain hold together internally, and does it match the shape that already works (`td_library`)?

**Method.** Two sub-passes.

**D1 — Internal consistency.** Cheap structural sweep, run first.
- Decision tree in `BLENDER_LIBRARY_INDEX.md` → every referenced file exists, every section it implies actually exists in the target file.
- Cross-file naming — does `BLENDER_DATA_MODEL` use the same terms as `BLENDER_PYTHON_API`? Spot-check key concepts: Scene, Collection, Object, Mesh, Material, NodeTree.
- Cross-file recommendations — any place where File A says "use X" and File B says "don't use X"? Most likely site: PYTHON_API recommending `bpy.ops` vs. low-level `bpy.data` manipulation; pattern files may default differently.
- Dead links and broken cross-references — every `[[wiki-link]]` resolves to an actual file in the vault.
- Frontmatter consistency — every file has matching version, status, target Blender version, target platform fields.

**D2 — Parity with `td_library`.** Structural comparison after A + B fixes have landed.

| Slot | td_library | blender_library | Parity |
|------|-----------|-----------------|--------|
| Index file | TD_LIBRARY_INDEX | BLENDER_LIBRARY_INDEX | ? |
| Platform constraints | TD_APPLE_SILICON | BLENDER_APPLE_SILICON | ? |
| Build philosophy / mental model | TD_NETWORK_VS_GLSL, TD_EFFICIENT_NETWORKS | (nothing direct?) | likely gap |
| Footgun log | TD_FOOTGUNS | BLENDER_FOOTGUNS (seeded only) | partial |
| Operator catalogs (encyclopedic) | TD_OPERATORS_POP/TOP/CHOP/SOP/MAT/DAT/COMP (7) | PYTHON_API + DATA_MODEL + GEOMETRY_NODES + SHADER_NODES (≈4) | shape differs |
| Third-party library guides | TD_POPX_GUIDE | (none — would be add-on guides) | gap |
| Pattern library | 8 PATTERN files | 3 PATTERN files | depth differs |
| Workflow playbooks | 8 WORKFLOW files | 3 WORKFLOW files | depth differs |
| Debug log integration | TD_CLAUDE_DEBUG_LOG referenced | (no equivalent yet) | gap |

For each parity gap: decide if it should close (Blender brain grows to match) or stay open (Blender domain genuinely smaller / differently shaped). Document the call.

**Pass criteria.**
- Zero unresolved internal contradictions.
- Zero dead links.
- Parity table fully filled with explicit "matches" / "intentional gap" / "should close" judgments per row.
- Recipe density per pattern file documented and benchmarked against the TD equivalent.

**Estimated effort.** D1 is fast (1-2 hours). D2 needs A + B fixes already in to be meaningful.

---

## Sources to consult — locked, ordered by authority

1. **docs.blender.org** — current 4.5 LTS user manual. Canonical for UI, behavior, defaults.
2. **docs.blender.org/api/current/** — Python API reference. Canonical for `bpy.*`, `bmesh`, `mathutils`.
3. **projects.blender.org** — Blender source + commit history + release notes. Canonical when docs disagree with behavior, or for version-introduction dates.
4. **claude.com/resources/tutorials/using-the-blender-connector-in-claude** — Anthropic's official MCP tutorial. Canonical for the four blessed-workflow patterns.
5. **blender.org/lab/mcp-server/** — official MCP distribution page. Client-rendered — use Chrome tools (`mcp__Claude_in_Chrome__navigate` + `mcp__Claude_in_Chrome__get_page_text`) if WebFetch returns shell HTML.
6. **blender.stackexchange.com** — community-confirmed behaviors and gotchas. Use when docs are silent or wrong.
7. **devtalk.blender.org** — developer forum. For undocumented API behavior and roadmap context.
8. **BlenderArtists.org** — community forum. For practical workflow patterns.
9. **YouTube — Erindale Wenninger, Default Cube, CG Cookie, Blender Guru, Polygon Runway** — for pattern-density benchmarking only (B3). Not authoritative for API claims.
10. **GitHub — `ahujasid/blender-mcp`** — community MCP source. Useful reference for connector patterns even though we're using the official.

**Source ranking rule.** If two sources disagree, higher-ranked wins. If docs.blender.org disagrees with source, source wins and the disagreement gets logged.

---

## Working files this stress test will produce

| File | Purpose | Created by |
|------|---------|-----------|
| `working/BLENDER_VERIFICATION_LOG.md` | Per-file diff log: claim, source, verdict, fix | Pass A |
| `working/BLENDER_MCP_TOOL_SURFACE.md` | Documented MCP tool surface inferred from addon source | Pass B1 |
| `working/BLENDER_WORKFLOW_WALKTHROUGHS.md` | Walk-throughs of the 4 blessed workflows + 5 archetypal tasks with completeness/correctness scores | Pass C |
| `working/BLENDER_PARITY_TABLE.md` | Filled parity table vs. td_library with judgments per row | Pass D2 |
| `reference/blender_library/BLENDER_FOOTGUNS.md` | Grown with any failure patterns surfaced | All passes |

The four working files are deliverables of execution. They are not deliverables of this conversation — this conversation produces only the plan you are reading.

---

## Execution order (suggested)

1. **D1** first. Fast, cheap, finds structural problems that change Pass A scope.
2. **A** and **B** in parallel, file-by-file. A is the longest pole.
3. **C** uses the brain after A+B fixes have landed.
4. **D2** last. Parity only matters once content is correct.

Each pass closes with a session entry in `working/WOBAR_ACTIVE.md` and a verification-log diff.

---

## Pass criteria — when is the stress test done

| Pass | Done when |
|------|-----------|
| A | Every shipped `bl_idname` is `CONFIRMED`. Every version claim verified against release notes. Verification log fully populated. |
| B | Every empirical-verification flag in the index is `CONFIRMED` or queued as `LIVE-VERIFY-PENDING` with a specific check. All 4 blessed workflows walked through with gaps logged. Pattern files benchmarked against community sources. |
| C | All 9 decision-tree branches produce executable prompt sequences. 5 archetypal tasks average ≥4/5 completeness + correctness. |
| D | D1: zero dead links, zero unresolved contradictions. D2: parity table fully judged. |

When all four pass: register `reference/blender_library/` and `working/BLENDER_MCP_RESEARCH.md` in `WOBAR_CONTEXT.md`. Install the MCP connector. Begin Phase 3 (`WOBAR_BLENDER_*.md`).

---

## Risks and known unknowns

- **Anthropic MCP tool surface is documented from press coverage, not from the addon source.** Pre-install verification depends on the addon being readable on GitHub or the Blender Lab repo. If it's not, B1's MCP-surface verification has to wait for install.
- **Blender 4.6 may release during execution.** Version target may shift mid-stress-test. Lock 4.5 LTS as the verification target up front; treat 4.6 as a follow-up delta.
- **Some `bl_idname` strings are stable across releases; others change.** Spot-check methodology means some misses will slip through pre-install. Accept and log; live verification post-install catches the rest.
- **Pattern-density benchmarking against YouTube creators is subjective.** Cap to 3 sources per pattern file. Judge with "would WOBAR use this?" as the priority lens, not "is it possible in Blender?"
- **Execution effort estimate is one-session-per-pass at minimum.** Tight horizon for plan-writing today does not imply tight horizon for execution. Treat this plan as multi-session work.

---

## Out of scope for this stress test

- Any live Blender API calls.
- Any MCP connector behavior testing (queue for post-install).
- Any WOBAR-specific brand layer (`WOBAR_BLENDER_*.md`) — Phase 3.
- Rewriting files that pass — fix only what fails.
- Building new pattern files — only audit existing ones. New patterns earn their place after live work surfaces the need.
