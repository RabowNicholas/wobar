---
title: Network vs GLSL — Decision Framework
version: 1.0
last_updated: 2026-04-16
status: live
scope: When to build with nodes, when to write a shader. Addresses default-to-GLSL tendency.
dependencies: TD_LIBRARY_INDEX.md, TD_EFFICIENT_NETWORKS.md
---

# NETWORK VS GLSL — WHEN TO USE WHICH

TouchDesigner's superpower is composable nodes. GLSL is an escape hatch, not a default. This file frames the decision. Read before any new build.

---

## The Default

**Build with nodes first. Only reach for GLSL when the node graph stops being a better option.**

Reasons the node path is the default:
- Every parameter is exposed and easy to drive with CHOPs, DATs, or UI.
- Every intermediate result is visible in the viewer — you can see what broke.
- Cook optimization (Selective, Always, Off) applies automatically.
- Network edits are undoable step by step; a shader rewrite isn't.
- Nodes survive upgrades; custom shaders sometimes don't.
- Collaboration (including with an AI) works because node names and parameters are shared vocabulary. Shader code lives inside one operator and is opaque until read line by line.
- Reuse happens by copying a chain or exporting a COMP, not by re-extracting logic from a `main()`.

---

## When Networks Win

Use nodes for:

- **Feedback-based visuals.** Feedback TOP + Transform + Level is the native idiom. Recreating this in a single fragment shader means writing your own ping-pong buffers. Don't.
- **Anything with trails.** Same reason — TD's TOP graph is literally ping-pong buffers behind the curtain.
- **Compositing stacks.** Over, Add, Multiply, Screen, luma key, alpha mask — Composite TOP and Layer Mix TOP are equivalent to a shader at this point and infinitely more legible.
- **Audio-reactive control.** CHOP chain → Null → Lag → `op()` reference in parameters is easier to tune than uniform plumbing.
- **Procedural geometry.** POPs + Attribute POPs replace most of what a vertex shader would do, and they live in the render tree.
- **Scene graph.** Camera COMP, Light COMP, Render TOP pipeline — no reason to re-implement.
- **Instancing.** POP instancing has a GUI for everything. GLSL instancing requires more plumbing than it saves.
- **Post FX stacks.** Bloom TOP, Edge TOP, Blur TOP, Chromatic TOP, Threshold — these are one click. A custom post-stack shader is one long function.
- **Experimenting.** If you don't know what you want yet, nodes let you try 10 versions in 10 minutes.

---

## When GLSL Wins

Reach for GLSL (GLSL TOP or GLSL Multi TOP) when:

- **The exact math does not exist as a node.** Example: signed distance field raymarching, domain-warp noise, custom reaction-diffusion kernels, Mandelbox, fluid simulation.
- **The node network would be >15 nodes for something that is 20 lines of shader.** Heuristic: if you find yourself chaining 3 Math TOPs + a Function TOP + a Remap + a Composite just to compute a single scalar per pixel, that's shader territory.
- **Per-pixel branching matters.** Nodes operate on whole textures; shaders let you compute differently per pixel/region based on values.
- **You need multiple output buffers in one pass.** GLSL Multi TOP writes to up to 32 outputs in one shader invocation — impossible with regular TOPs.
- **You're doing genuine SDF / raymarcher work.** This is always a shader.
- **You already have a reference shader** (from Shadertoy, a paper, a friend's patch) and porting to nodes would be a waste.

---

## The Hybrid Pattern (Most Wobar Work)

The mature answer is usually: **networks drive, shaders do the hard local math.**

Common hybrid layouts:

**Pattern A — Shader nucleus, node shell**
```
Audio pipeline (CHOPs)   ──►  GLSL TOP (noise field, 20 lines)  ──►  Transform TOP ──►  Feedback TOP ──►  Bloom ──► Out
Control UI (COMPs) ─────────►        (uniforms)
```
The shader computes the one thing that couldn't be done with nodes. Everything around it — driving values, post, feedback — is node-graph.

**Pattern B — Node stack, shader for a single effect**
```
Scene (SOPs/POPs + Render TOP) ──►  Chromatic Aberration GLSL TOP  ──►  Composite ──► Out
```
Most of the build is nodes. One custom effect (e.g., chromatic aberration with an unusual falloff curve) is a GLSL TOP.

**Pattern C — POP + GLSL compute for heavy instancing**
```
POP generator ──► Attribute POPs (positions, colors) ──► GLSL POP (custom per-point math) ──► Instance in Geometry COMP
```
POPs are already on the GPU via compute. Writing a GLSL POP stage is the right move when you need per-point logic that the stock POPs don't give you.

---

## Red-Flag Checks Before Writing a Shader

Before you open a GLSL TOP, answer these:

1. **Can this be done with 3–5 stock TOPs?** If yes, stop. Use the TOPs.
2. **Is there a pattern in `WOBAR_GLSL_PATTERNS.md` or `TD_PATTERNS_*.md` that already does this?** Copy, don't rewrite.
3. **Is the reason I'm picking GLSL "because that's what I know"?** If yes, try nodes first for 10 minutes.
4. **Does the shader need inputs from CHOPs?** Plan the `chop()` / `chopc()` calls and the uniform plumbing before writing.
5. **Is there geometry shader code in it?** If yes — doesn't work on Metal. Rewrite as compute or split into two passes. See `TD_APPLE_SILICON.md` §1.

---

## When You Do Write a Shader — Good Habits

- **Name it descriptively.** `glsl_noise_domainwarp_a1`, not `glsl_top`.
- **One shader does one thing.** Don't make a mega-shader that does noise + feedback + color + post. Split across GLSL TOPs or use the node graph between them.
- **Expose parameters as uniforms with default values.** Never hardcode a value that might want tuning.
- **Write the node-graph equivalent in a comment** at the top of the shader if the shader was a direct rewrite. Makes future-you's debugging vastly easier.
- **Test at a low resolution first.** Shader errors at 1280² with heavy math can crash TD on Mac. Develop at 256².
- **Read `WOBAR_GLSL_PATTERNS.md`** before writing shaders for Wobar — the act-specific patterns are already there.

---

## When To Go Back To Nodes

If you started in GLSL and find yourself writing:
- Texture sampling loops to implement a blur → use Blur TOP
- If/else on pixel value to pick colors → use Lookup TOP with a ramp
- Copying the same math across three shaders → that math should be earlier in the node graph
- Feedback state management → use Feedback TOP

These are signs the network was the right tool all along.

---

## Pragmatic Rule of Thumb

> Nodes for shape of the pipeline. Shaders for the math inside a single step.

When unsure, build the node version first. If it's over-complicated or slow, surgically replace the gnarly middle with a GLSL TOP. Don't start in GLSL because it "felt more powerful."
