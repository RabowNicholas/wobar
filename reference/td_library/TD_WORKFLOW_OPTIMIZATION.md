---
title: TD Optimization Workflow
version: 1.0
last_updated: 2026-04-16
status: live
scope: Perf tuning protocol — diagnosing slow projects, Perform Mode, cook flags, caching, offline render for heavy scenes.
dependencies: TD_LIBRARY_INDEX.md, TD_EFFICIENT_NETWORKS.md, TD_FOOTGUNS.md
---

# TD OPTIMIZATION WORKFLOW

Protocol for diagnosing and fixing slow projects. Start at the top; skip to relevant sections if the symptom is already known.

---

## 1. Measure First

### Is it actually slow?
- In-editor: watch the Timeline header → frame drops show there.
- Perform Mode is faster than the editor (editor draws extra overlays). **Always benchmark in Perform Mode** before calling it slow.
- Perf CHOP / Perform CHOP — cook time per frame in ms.
- Target: <16.6ms at 60fps, <8.3ms at 120fps.

### Per-operator cook time
```python
# Textport:
for op in parent().findChildren(tags=['!disabled']):
    if op.cookTime > 0.5:
        print(f"{op.path}: {op.cookTime:.2f}ms")
```
Or: enable **Project → Probe → Performance Monitor** → see which operators cost the most.

### What to look for
- Top 3 most-expensive operators usually account for 70%+ of cook time.
- Any single op > 5ms → candidate for optimization.
- Any COMP > 10ms → investigate internals.

---

## 2. Quick Wins — Try These First

Before deep restructuring:

1. **Enter Perform Mode** — usually 20–30% faster than editor.
2. **Lower resolution** — halve any TOP's resolution via Resolution TOP; halve it on Feedback branches specifically.
3. **Close unused COMPs** — click the "orange dot" to mark Cook Type = Off on dev-only branches.
4. **Disable debug viewers** — all those node viewers cost VRAM.
5. **Set 16-bit TOPs to 8-bit** in the final display chain (keep 16-bit only where HDR matters — feedback, render).
6. **Pre-warm Engine COMPs** at load, not at runtime (see `TD_FOOTGUNS.md` §H4).

These alone often bring a 20ms project to 10ms.

---

## 3. Feedback Optimization

Feedback TOP is the single biggest perf sink for visual-heavy projects.

### Downsample before feedback
```
Source (1280²) ──► Resolution TOP (640²) ──► feedback chain at 640² ──► Resolution TOP (1280²)
```
4× cheaper feedback. Often visually identical.

### Pixel format
Feedback at 16-bit RGBA is ~2× more bandwidth than 8-bit. If HDR isn't needed in the feedback loop, set to 8-bit.

### Reduce loop complexity
Remove every non-essential op inside the feedback cycle. Move post (Bloom, Chromatic) outside the loop.

### See `TD_PATTERNS_FEEDBACK.md` §Performance for more.

---

## 4. Render Optimization

### Reduce light count
Each dynamic light adds a render pass. 1 directional + 1 ambient is often enough.

### Disable shadows on non-hero geometry
Geometry COMP → Render tab → Light Mask → exclude certain lights from certain geometry; disable cast/receive shadows where unnecessary.

### MSAA level
4× is usually enough. 8× doubles cost; reserve for offline renders.

### Instancing instead of many Geometry COMPs
See `TD_PATTERNS_INSTANCING.md`. N Geometry COMPs = N draw calls. 1 Geometry COMP with N instances = 1 draw call.

### Simplify materials on instanced geometry
Constant MAT > Phong MAT > PBR MAT in cost. Point Sprite MAT is cheapest for billboarded particles.

---

## 5. CHOP Chain Audit

### Look for expensive CHOPs
- Analyze CHOP with large window sizes.
- Expression CHOP (per-cook Python).
- Script CHOP.
- Large Filter CHOP with high order.

### Fix
- Replace Expression CHOP with Math + Logic chains.
- Lower Analyze window size where possible.
- Pre-compute once, Export from a Null (see `TD_EFFICIENT_NETWORKS.md` §3).

---

## 6. DAT / Python Audit

Execute DATs firing per frame are the most common hidden cost.

### Find them
```python
for op in parent().findChildren(tags=['!disabled']):
    if op.type == 'executeDAT' or op.type == 'chopExecuteDAT':
        print(op.path)
```
Review each. If it's doing per-frame work, can that work move to CHOPs?

### Rule
Python in the cook path is the last resort, not the first.

---

## 7. POP / SOP Audit

### SOPs
- Script SOP at large point counts → migrate to POP.
- Subdivide SOP at high levels → cache once.

### POPs
- Simulate POP with huge particle counts → reduce count or split into multiple systems.
- Trail POP with long trails → shorten trail length.

### File-based cache
For static geometry computed via expensive SOP chain: compute once, File Out SOP to `.tog`, then File In SOP to reload.

---

## 8. GPU Memory Budget

M1 GPU shares system RAM — OS needs it too. Heavy VRAM use evicts textures and slows everything.

### Check usage
Perf CHOP → GPU memory used.

### Reduce
- Fewer 16-bit TOPs (convert to 8-bit in display chain).
- Smaller Feedback TOPs (downsample).
- Delete unused TOP viewers (each one keeps the texture in memory).
- Movie File In TOP with large movies preloaded: use Cue mode, not preload mode.

---

## 9. Async / Parallel Strategies

### Engine COMP
Moves a sub-network to another process. Independent cook; doesn't block main.
- Use for: heavy generative scenes, independent post stacks.
- Overhead: process spawn cost. Pre-warm at load.

### Animation Comp / Offline Caching
Render time-consuming scenes offline to an image sequence or movie, then play back at runtime with Movie File In.

---

## 10. Export-Only Optimization

If the project is for music video export (not live), different rules apply:

- Resolution is capped at 1280 on Non-Commercial, but you can render at 30fps or lower and it doesn't matter.
- Temporal AA + motion blur becomes feasible.
- Can render non-real-time: TD can take >16.6ms per frame and the output is still correct.
- See `TD_WORKFLOW_EXPORT.md`.

---

## 11. Live-Only Optimization

If the project is for live performance:

- Target 60fps in Perform Mode.
- Budget 13ms/frame (leave 3.6ms headroom for scheduling jitter).
- Pre-load everything at project open. No cold-start anywhere.
- Engine COMPs for scene isolation.
- crashAutoSave every 5 minutes.
- See `TD_WORKFLOW_LIVE_VJ.md`.

---

## 12. Debug Protocol — When You Can't Find the Bottleneck

1. **Disable every major sub-network.** Project should cook in 1–2ms.
2. **Enable sub-networks one at a time.** Note cook time delta per section.
3. **The sub-network with the biggest delta is the hotspot.**
4. **Inside the hotspot**, disable branches and enable one at a time to find the specific expensive op.
5. **Apply section-specific fixes** from above (Feedback / Render / CHOP / DAT / POP).

---

## 13. Maintenance Habits

Run these every month or before shipping a project:

- Walk the network, check Cook Type settings — any unintended Always?
- Look for orphan chains (disconnected from output) — delete.
- Check resolution of every TOP — any at 1280² that could be smaller?
- Review Execute DATs — any running per frame that could be event-driven?
- Look for Replicator COMPs with N > 50 — migrate to POP instancing.
- Verify that Null TOPs exist at expensive-chain endpoints for caching.

---

## 14. Common Optimization Wins by Magnitude

| Win | Typical impact |
|-----|----------------|
| Half feedback resolution | 3–5ms |
| Remove unused Execute DATs per frame | 1–10ms |
| Convert 16-bit TOPs to 8-bit in display chain | 1–3ms |
| Replace Replicator 100 clones with POP instancing | 10–50ms |
| Move heavy POP sim to Engine COMP | varies |
| Disable shadows on instanced geometry | 2–8ms |
| Lower MSAA from 8× to 4× | 3–5ms |
| Downsample Bloom to half-res before upscaling | 2–4ms |

---

## 15. When To Stop

Optimization has diminishing returns. Stop when:
- Project hits target framerate in Perform Mode consistently.
- You have 20%+ cook-time headroom for jitter.
- Further changes compromise the visual.

Don't micro-optimize the last millisecond if the project already runs well. Spend the time on the visual instead.

---

## Reading This File

Sequential read for first-time optimization. Skip to section 3 or 4 for targeted fixes. Section 12 is the protocol when you don't know where the problem is.
