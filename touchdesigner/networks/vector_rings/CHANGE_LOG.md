# CHANGE LOG — vector_rings

TD comp path: `/project1` (no wrapping baseCOMP), live in `NewProject.1.toe` on Desktop (unsaved).

Vector-void prototype: 40 wireframe circles instanced on the 40 points of a second circle, drawn with a `lineMAT`. Nick's geometry sketch; agent work is the render spine downstream of it.

---

## 2026-07-24 — move_001 — render spine

**Built**
- `cam_main` (cameraCOMP, perspective) — tz/fov/rx/ry bound to `ctrl_master`
- `render_main` (renderTOP) — 720×1280, `rgba16float`, `antialias='aa8'`, `camera='cam_main'`
- `null_render` → `null_out` — the two stable taps; export and any future window read from `null_out`
- `ctrl_master` (baseCOMP) — custom pages **Camera** (Camdist 6, Camfov 40, Camrx 0, Camry 0) and **Form** (Linewidth 2, Linefade 1, Linealpha 1, Nearcolor `#A085AE` dusty lavender, Farcolor `#2D0546` deep purple mid)
- `line1` (existing lineMAT) width + near/far colors bound to `ctrl_master`

**Decisions**
- **No lights.** `lineMAT` is unlit — a lightCOMP would be dead weight and a debug surface. `render_main.par.lights` left at `*` with no lights in scope.
- **8× MSAA is the whole quality lever for wireframe-on-black.** The NC license caps every TOP at 1280×1280, so there is no supersample-and-downsample path; MSAA is internal to the render and unaffected by the cap.
- **`rgba16float` from the renderTOP onward** — headroom for whatever post lands later, and no banding in dark purple (AGENT_RULES §Pixel Format).
- **Render background left transparent** (renderTOP has no `bgalpha`; default is alpha 0). Compositing over black belongs at the end of a post chain, so the void stays true black instead of bloom-lifted charcoal.
- Format locked to **720×1280 vertical** per Nick; NC cap is 1280 per side so this is the operating size, with FFmpeg upscaling to 1080×1920 at delivery.
- Delivery target is **both** realtime/VJ and offline file render. `null_out` is the single tap that serves both — a windowCOMP and a `moviefileoutTOP` can each hang off it without restructuring.

**Cut from scope mid-move**
- A `base_post` COMP (CA → grade → bloom → grain → void comp, 19 ops) was built and then destroyed at Nick's instruction — post-processing is not wanted yet. The `Post` page on `ctrl_master` was removed with it.

---

## 2026-07-24 — move_002 — black background

**Built**
- `void_black` (constantTOP, 720×1280, `rgba16float`, true black, alpha 1)
- `comp_void` (compositeTOP, `operand='over'`, `swaporder=True`) — input 0 = `void_black` (bottom), input 1 = `null_render` (top)
- Chain is now `render_main → null_render → comp_void → null_out`

**Fixed**
- The six `line1` color pars from move_001 were silently stuck in `ParMode.CONSTANT` at 1.0 — assigning `.expr` to an **RGBA-tuplet member** does not auto-flip mode the way it does on a scalar par, and it resets `.val`. Wireframe was rendering pure white. Repaired by setting `.mode = ParMode.EXPRESSION` explicitly. Logged to `TD_CLAUDE_DEBUG_LOG.md`.
- Verified: lines now render at `#A085AE` near / `#2D0546` far on true black.

**Known state / open**
- `geo1.instancetop` points at `null1`, a **nullSOP**. It works — 40 instances render — but the par is nominally the TOP-based slot. Left alone; flagged in case instancing gets restructured.
- Face-on at Camdist 6 the piece reads as a dense mandala disc. Most of the lattice sits in the lineMAT's *far* color band, so the frame is very dark. `distancenear`/`distancefar` on `line1` are still at defaults and are the dial for that, not exposed on `ctrl_master` yet.
- No audio pipeline. Per AGENT_RULES build order, audio comes after the visual is fully parametrized.
