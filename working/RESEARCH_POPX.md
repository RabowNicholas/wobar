# RESEARCH — POPX (Mini UV)

Captured 2026-04-29 from the open Patreon tab plus the public POPX docs site
and supporting web search. Anything I couldn't directly observe is flagged.

---

## TL;DR

**POPX** is a paid TouchDesigner operator pack built by **Mini UV** (Yuval),
distributed exclusively through his Patreon. It extends TouchDesigner's
native POPs (Point Operators) with a **GPU-first geometry pipeline** for
generating, transforming, and simulating instanced geometry in real time.
Think: a more opinionated, packaged, GPU-accelerated successor to manually
hand-rolled instancing / particles networks — with first-class falloffs,
modifiers, and physics simulations (Flow, Soft Body, DLG, Physarum, etc.).

It ships in two flavors — **POPX Lab** and **POPX Pro** — gated behind
Patreon tiers, with the public docs and tutorial intro series on YouTube
acting as the marketing top of funnel.

---

## Source / what I could see

- **On-screen, observed directly** in the open tab `patreon.com/cw/_mini_uv`:
  creator name, hero image, member/post counts, bio (truncated), Latest post,
  three Recent posts.
- **Public POPX docs** at `popsextension.com` — operator names, categories,
  per-operator descriptions.
- **Web search** for Patreon post titles, YouTube series, AllTouchDesigner
  presence, Mini UV bio.
- **Not accessible** — locked Patreon tier descriptions (exact $ pricing
  and benefit lists), full bodies of paid posts, member-only changelogs.
  Patreon refused both direct fetch and Chrome MCP navigation.

---

## The creator — Mini UV

- **Name**: Yuval, online handle **Mini UV** (`@_mini_uv` across IG, YT,
  Patreon).
- **Background**: Electrical engineer; describes himself as an electrical
  and sound engineer turned real-time generative artist. Came to
  TouchDesigner while exploring generative systems.
- **Focus**: Simulation, physics, and GPU-based workflows — particle
  systems, fluid sims, growth systems, instancing.
- **Site**: `miniuv.art`
- **Channels**:
  - YouTube `@_mini_uv` — free intro tutorials (POPX Introduction,
    Installation Guide, Soft Body Part 1, etc.).
  - Instagram `@_mini_uv` — work-in-progress visuals.
  - AllTouchDesigner `alltd.org/uploader/miniuv` — community presence.
  - Discord — dedicated POPX server (linked from a recent Patreon post:
    "POPX | Discord Server").

---

## The Patreon page (observed)

URL: `https://www.patreon.com/cw/_mini_uv` (canonical: `patreon.com/_mini_uv`)

Tagline / page title: **"Creating TouchDesigner Tools and Tutorials"**

Header stats (as of 2026-04-29):
- **5.8k members**
- **59 posts**

Bio (truncated on the public page, transcribed from the screenshot):
> Yuval, also known as Mini UV, is a real-time generative artist and
> TouchDesigner developer focused on simulation, physics, and GPU-based
> workflows. With a background in electrical engineering, he discovered
> TouchDesigner while exploring…

Top-level nav: Home · Posts · Collections · Shop · Membership ·
Recommendations · Gift.

---

## Posts visible on the homepage

**Latest post**
- *New POPX Tutorial by Okamirufu!* — "Hey everyone, Okamirufu just
  released a new tutorial using POP and POPX. It explores animating
  geometry over a mesh, building a full workflo[w]…" — 19 hours ago,
  3 hearts. Thumbnail reads "MOVE ALONG MESH POPX".
  - Read: there is a community of secondary creators (e.g., Okamirufu)
    making POPX content; Mini UV amplifies them.

**Recent posts (carousel, three visible)**
1. **POPX Version 1.3.0 is out!** — March 30 — 14 hearts, 7 comments.
   Snippet: "This release brings new tools and workflow improvements.
   New operators: Planar Patch:…" (cut off).
2. **POPX Version 1.2.1 — Quick Fixes** — March 2 — 5 hearts.
   Snippet: "A small maintenance update focused on stability. Fixes:
   • Fixed POPX integration in the…"
3. **POPX Version 1.2.0 is out!** — February 27 — 11 hearts, 5 comments.
   Snippet: "I'm excited to share with you the new POPX 1.2.0 release!
   This update brings major performance…"

Implied release cadence: roughly every 3–4 weeks, with point-release
quick-fixes in between. Active development.

---

## Other POPX posts surfaced via search (not on visible homepage)

- **POPX Lab | Version 1.0.1 — First Release** — initial release on the
  Lab tier.
- **POPX Pro | Version 1.0.1 — First Release** — initial release on the
  Pro tier (separate post from Lab).
- **POPX Introduction Series** — an ongoing tutorial series.
- **POPX Soft Body Series – Part 1 is Now Live!** — tutorial walkthrough
  of the Soft Body simulation operator.
- **POPX | Discord Server** — links to the community Discord.
- **POPX Collection** (`patreon.com/collection/1866826`) — curated
  collection of 13 POPX posts.
- **New Tier Available** (older post, likely the moment the POPX-gated
  tier was introduced).

---

## What POPX actually is

A **GPU-accelerated framework on top of TouchDesigner's native POPs**, for
generating, transforming, and simulating instanced geometry in real time.
The headline idea is the **POPX Geometry packed-data structure**: each
piece of geometry is represented by a single point that carries its full
transform (position, rotation, scale, pivot) plus user attributes. That
compact format lets every transformation run directly on the GPU, without
hand-rolled matrix math or attribute construction.

Compatibility note from the docs: POPX operators interoperate with
**standard TouchDesigner POP geometry**, not just POPX-format geometry —
so you can drop them into existing POP / instancing networks without
converting everything.

### Operator categories

POPX operators are organized into **5 main types**:

1. **Generators** — create geometry (entry point of a POPX network).
2. **Falloffs** — define spatial / attribute-based influence regions used
   to drive Modifiers.
   - Examples: **Noise Falloff** (procedural noise-driven), **Attribute
     Falloff** (turn any numeric point attribute into a falloff source).
3. **Modifiers** — transform instances. Stack-able layers that adjust
   position, rotation, scale, pivot, color, custom attrs. Driven directly
   or via falloffs.
   - Examples: **Transform**, **Randomize**, **Move Along Mesh**,
     **Pivot**.
4. **Tools** — utility ops.
   - Examples: **Geometry** (renders POPX Geometry with per-instance
     material assignment by index), **Voxelize** (converts mesh / point
     cloud geometry into a 3D texture / voxel volume).
5. **Simulations** — time-based physics.
   - **Flow** — GPU 3D fluid solver, Navier-Stokes for incompressible
     flow; smoke / fire / atmospheric.
   - **Soft Body** — soft body dynamics.
   - **DLG (Differential Line Growth)** — iterative edge-subdivision
     growth, brain-coral / organic branching.
   - **Physarum** — slime-mold sensor-driven network/vein patterns.
   - The docs also reference **DLA** and **SPH** in the simulation family.

### Workflow shape

Standard POPX network reads as: **Generator → (Falloffs) → Modifiers →
Tools/Render**. Simulations are a parallel branch — time-based physical
systems that feed back into the geometry stream.

### Per-operator UX details (from the docs)

- Each operator carries **per-parameter help text**.
- Each operator's **About page has a Help toggle** that opens its
  documentation page on `popsextension.com` directly from inside TD.
  → Strong DX signal; the docs are designed as part of the in-tool
  experience, not just marketing.

---

## Distribution / licensing

- **Where**: Patreon-only. Subscribe to the gated tier and download the
  `POPX.tox` package from the release post.
- **Tier**: Public docs and search results call it the **"Advanced" tier**.
  The Patreon ships in **two flavors — POPX Lab and POPX Pro** (separate
  release posts, separate example folders). I could not see the locked
  tier descriptions, so I can't confirm exact $/month pricing or the
  Lab-vs-Pro feature split from the on-page state alone.
- **Platforms**: Windows and macOS, per the public Installation Guide.
- **License terms (from public docs)**: usable in commercial and
  non-commercial projects; modifiable internally for personal workflow;
  usable inside TouchDesigner on any machine you own.

---

## Open questions / what I couldn't pull

These would require either being logged in to the Patreon membership page
or for you to scroll the open tab so I can screenshot more:

- Exact **$/month** price for each tier and the Lab-vs-Pro split.
- Full **changelog text** for v1.3.0 / v1.2.1 / v1.2.0 (snippets are
  truncated on the homepage).
- Full bio (cuts off after "exploring…").
- Total POPX post count over time (the Collection says 13, but new
  releases since then haven't been re-collected).
- Whether the Discord is gated by tier or open to all members.

If you scroll the page or open Membership / a release post, I can take
another screenshot and fill those in.

---

## Why this is interesting for WOBAR

POPX maps directly onto WOBAR's TD work — Act 2 underwater/tunnel/fractal
networks, Act 3 collapse, instancing-heavy systems. Specific overlaps
worth flagging for the TD coach context:

- **Soft Body / Flow / Physarum** are exactly the "organic, audio-reactive
  growth" textures the framework keeps reaching for.
- **Move Along Mesh** is a clean primitive for mesh-bound particle motion
  (Act 2 surface / underwater).
- **Voxelize** turns mesh into a 3D volume — useful for Act 3 dissolution
  / collapse-into-particulate moves.
- **Falloff + Modifier stacking** is structurally similar to the
  noise-driven instancing patterns in `TD_PATTERNS_INSTANCING.md` and
  `TD_PATTERNS_AUDIO_REACTIVITY.md`, but pre-built and GPU-native.

If WOBAR ends up subscribing, POPX likely replaces a chunk of hand-rolled
GLSL/instancing scaffolding rather than augmenting it.

---

## Reference URLs

- Patreon home: https://www.patreon.com/_mini_uv
- Patreon about: https://www.patreon.com/_mini_uv/about
- POPX Collection: https://www.patreon.com/collection/1866826
- Docs home: https://www.popsextension.com/
- Docs — Getting Started: https://www.popsextension.com/docs/guides/getting-started/
- Docs — Installation: https://www.popsextension.com/docs/guides/installation/
- Personal site: https://www.miniuv.art/
- YouTube: https://www.youtube.com/@_mini_uv
- Instagram: https://www.instagram.com/_mini_uv/
- AllTouchDesigner uploader page: https://alltd.org/uploader/miniuv/
