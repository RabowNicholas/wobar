---
title: Efficient TouchDesigner Networks
version: 1.0
last_updated: 2026-04-16
status: live
scope: How to structure networks so they cook cheaply and stay legible. Cook control, bridging CHOP→TOP, Null/Select discipline, caching, instancing.
dependencies: TD_LIBRARY_INDEX.md, TD_WORKFLOW_OPTIMIZATION.md
---

# EFFICIENT TOUCHDESIGNER NETWORKS

A network is not just a graph of operators — it is a graph of **cooks**. Every frame, TD decides which operators need to recompute. Efficient networks are ones where the expensive operators cook only when they must.

This file covers the structural habits that make networks fast. Runtime tuning and debugging perf problems is in `TD_WORKFLOW_OPTIMIZATION.md`.

---

## 1. Cooking — The Core Mental Model

Every operator has a **Cook State** per frame:
- **Cook** — recompute this frame.
- **Don't cook** — reuse last frame's output.

The rules that determine "cook" on a given frame:
- An input changed.
- A parameter changed.
- An expression referencing time / another operator resolved to a new value.
- The operator's Cook Type is "Always."
- A downstream operator requested its output (pull-cook).

TD is pull-cook: the bottom of the graph pulls from the top. An orphan network (no Out/viewer/render pulling it) doesn't cook.

**Implications:**
- Disconnecting an operator from the downstream chain stops it cooking.
- Wiring a Null TOP to the viewer makes that chain cook every frame.
- A single `op('...').par.x` in a parameter of a cooking operator will re-cook the referenced operator every frame.

---

## 2. Cook Type Parameter

Every operator has a Common page → **Cook Type**:

| Cook Type | When it cooks | When to use |
|-----------|---------------|-------------|
| Selective | Only when its inputs or parameters change | **Default for everything.** |
| Always | Every frame regardless | Feedback TOP source side, operators reading time-varying external state |
| Off | Never — outputs stay static | Capture a result once and freeze it |

**Rule: leave Selective unless you have a specific reason otherwise.** The most common perf regression is an operator silently set to Always by accident — check this first when cook time spikes.

---

## 3. Null Discipline — Cache Breakpoints

Null TOP / Null CHOP / Null SOP serve two jobs:

1. **Named endpoint** — referenceable, stable point in the graph.
2. **Cache breakpoint** — downstream operators read the Null, not the expensive upstream chain.

**Pattern:**
```
[heavy chain] ──► Null ──► [many downstream consumers]
```
If 5 operators reference the same expensive chain, put a Null between them so the chain cooks once, not 5 times. Without the Null, some graph configurations will cause the chain to cook per-consumer.

**Naming convention** (also in `WOBAR_TD_AGENT_RULES.md`): name every Null — `null_audio_rms`, `null_feedback_frame`, `null_controller_x`. Naming forces clarity about what's in the signal.

---

## 4. Select Operator Discipline

**Select TOP / Select CHOP / Select DAT / Select SOP / Select POP** pull a channel/texture/row from somewhere else by name.

Use Select when:
- You want a chain in network A to reference output of network B without a wire across the project.
- A COMP internal needs to grab an external signal.

Do **not** use Select when:
- The source is one operator away — just wire it.
- Using Select to rename — use a Rename CHOP or just name the Null.

**Performance note:** Select operators are cheap themselves, but they don't eliminate the upstream cook — the source still cooks if it's being pulled. Use Null on the source side as the cache point.

---

## 5. CHOP → TOP Bridging

Driving TOP parameters from CHOP values is one of the most common things you do. There are two ways:

### 5a. Export (CHOP → parameter)
- Right-click a TOP parameter → **Export CHOP**.
- The CHOP channel value is pushed into the parameter every cook.
- Fast, no expression evaluation.
- **Preferred when a parameter reads from a single channel.**

### 5b. Expression reference
```python
op('null_audio_rms')['rms'][0]
```
- Evaluates the expression every cook.
- Slower than Export (by a small amount, but it adds up).
- **Use when you need math**: e.g. `op('null_audio')['rms'][0] * 3 + 0.1`.

### 5c. The bridge pitfall
Do not expression-reference the same CHOP in 20 parameters across the network. Instead, do the math once in a CHOP chain and Export from a Null CHOP. You trade expression cost for a single named channel.

---

## 6. Cooking Scope — Common Sinks

Operators that are expensive per cook:

| Operator | Why it's expensive | Mitigation |
|----------|-------------------|------------|
| Feedback TOP | Reads+writes large texture per frame | Downsample before feedback, see `TD_PATTERNS_FEEDBACK.md` |
| GLSL TOP / GLSL Multi TOP | Full-resolution fragment shader | Lower resolution during dev; simplify math |
| Blur TOP with large radius | O(radius²) cost for non-separable | Use Luma Blur for smaller cost, or separable two-pass |
| Analyze TOP / CHOP at high rate | Reads back GPU→CPU | Reduce sample rate; only cook on onset |
| Render TOP with many lights | Each light adds cost | Bake lighting; use fewer lights |
| Movie File In TOP at 4K+ | Disk/decode cost | Pre-transcode to ProRes Proxy |
| Large Replicator COMP | N clones each cook | Switch to POP instancing |
| Execute DAT firing per frame | Python in the cook path | Move to onTick with lower rate |
| Noise TOP with high frequency + high resolution | Per-pixel noise math | Precompute into a texture, Lookup from that |

---

## 7. Resolution Budgeting

Almost all perf on Mac Apple Silicon is resolution-bound. Budget aggressively.

- **Render at the minimum resolution that still looks right.** 1280×720 is usually fine for final delivery given the 1280 cap. 720×720 looks the same if the output isn't full-frame wide.
- **Downsample before feedback.** A Resolution TOP (Input To → 1/2 or 1/4 resolution) in front of Feedback cuts feedback cost 4–16×.
- **Upsample only at the end.** Late in the post stack, a Blur TOP at half res then a Composite TOP at full res often looks identical to full-res blur.
- **Match working resolution to delivery.** Don't render at 1280² if output will be 1280×720.

---

## 8. CHOP Cost Hygiene

CHOPs are cheap individually but add up:

- **Filter CHOP / Lag CHOP / Filter before Math** is fine — these are tiny.
- **Analyze CHOP with Median over 1024 samples** is not — it's a full sort per cook.
- **Math CHOP on 10,000-sample CHOP** is expensive in the "combine all channels" mode — consider downsampling first.
- **Expression CHOP** runs Python per cook — avoid in per-frame chains, prefer Math/Logic CHOPs.

Audio Spectrum CHOP + Audio Filter CHOP + Analyze CHOP is the canonical cheap analysis chain. Don't replace it with a 50-line Expression CHOP just to save nodes.

---

## 9. GPU Instancing (Use POPs)

Rendering many copies of a thing:

| Method | Cost at 10,000 copies | Use |
|--------|----------------------|-----|
| Geometry COMP with Instance SOP input | High — CPU iterates | Legacy; avoid for large N |
| Replicator COMP creating 10k Geometry COMPs | Very high — thousands of COMPs | Use only for small N (<50) with per-instance logic |
| **POP with Instance output to Geometry COMP** | Low — single GPU pass | **Default for large N.** |

POPs run on GPU compute, pack per-point attributes, and feed directly to instance data on a Geometry COMP. For particles, dust, a sea of cubes, or data visualizations — POPs are the answer.

See `TD_OPERATORS_POP.md` and `TD_PATTERNS_INSTANCING.md`.

---

## 10. Common Network Shapes — Efficient Templates

### 10a. Audio analysis spine
```
Audio Device In ──► Audio Filter (band 0) ──► Analyze RMS ──► Math (normalize) ──► Lag ──► Null ("null_audio_sub")
                 ├► Audio Filter (band 1) ──► Analyze RMS ──► Math ──► Lag ──► Null ("null_audio_mid")
                 └► Audio Filter (band 2) ──► Analyze RMS ──► Math ──► Lag ──► Null ("null_audio_high")
```
Cooks only the minimum chain; Nulls are where every other operator references audio.

### 10b. Feedback visual core
```
Source TOP ──► Resolution (downsample) ──► Feedback ──► Transform ──► Level ──► Composite (with Source)
                                              │
                                              └───── Null ("null_feedback_frame") ─► post chain
```
The Feedback → post split at a Null lets you read the feedback frame elsewhere without causing it to cook twice.

### 10c. Render path
```
SOPs/POPs ──► Geometry COMP (with instance POP) ──► Camera + Light ──► Render TOP ──► Null ("null_scene") ──► post stack
```

### 10d. Control COMP + scene split
```
[Base COMP: control_panel]   ──► exports CHOPs ──► referenced by scenes
[Base COMP: scene_act_3]     ──► references control_panel via op() paths
```
Controls live in one place. Scene COMPs read from them. Change a control, every scene updates.

---

## 11. Legibility = Maintainability

Performance and legibility are the same thing at scale. Checklist for any network you will revisit:

- Every Null is named.
- Every COMP's purpose is one sentence; put it in the COMP's Comment.
- Colour operators by role (audio = cyan, control = green, render = purple, post = orange — or whatever, but consistent).
- Cluster related ops visually; leave white space between clusters.
- Hide plumbing inside COMPs so top-level networks fit on one screen.
- No orphaned chains — delete experiments when done or move them to an `experimental` Base COMP disconnected from the main path.

**Rule: if you cannot explain what a sub-network does in one sentence, it is too tangled.**

---

## 12. Before Shipping Perf Check

Before calling a network "done":
1. Perform Mode at target framerate — watch for dropped frames in the header.
2. Cook time: `op.cookTime` in the Textport — should be well under 16.6ms at 60fps.
3. Disable each major sub-network in turn. If disabling it doesn't change the cook time, it's wasting budget.
4. Downsample Feedback branch by 2× — does the look change meaningfully? If no, keep it downsampled.
5. Walk the graph one last time for Cook Type = Always that shouldn't be.

See `TD_WORKFLOW_OPTIMIZATION.md` for the deep optimization protocol.
