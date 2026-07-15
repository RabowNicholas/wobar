---
title: TWOZERO MCP Guide
version: 1.1
last_updated: 2026-04-15
status: live
scope: Empirical reference for the TWOZERO MCP server. Capabilities, confirmed behaviors, operator type strings, and known limitations discovered through use.
dependencies: [[reference/WOBAR_TD_AGENT_RULES]], [[reference/WOBAR_TWOZERO_MCP_CATALOG]]
---

# TWOZERO MCP GUIDE

Living doc. Not speculative — only add entries confirmed in a real session.

**Full tool catalog (parameter shapes, decision tree):** `reference/WOBAR_TWOZERO_MCP_CATALOG.md`

---

## Confirmed Operator Type Strings

| Operator | Type string |
|----------|------------|
| Base COMP | `baseCOMP` |
| Constant CHOP | `constantCHOP` |
| Select CHOP | `selectCHOP` |
| Lag CHOP | `lagCHOP` |
| Math CHOP | `mathCHOP` |
| Merge CHOP | `mergeCHOP` |
| Rename CHOP | `renameCHOP` |
| Analyze CHOP | `analyzeCHOP` |
| Audio File In CHOP | `audiofileinCHOP` |
| Audio Filter CHOP | `audiofilterCHOP` |
| Audio Device Out CHOP | `audiodeviceoutCHOP` |
| Record CHOP | `recordCHOP` |
| Filter CHOP | `filterCHOP` |
| Null CHOP | `nullCHOP` |
| GLSL TOP | `glslTOP` |
| Null TOP | `nullTOP` |
| Level TOP | `levelTOP` |
| Blur TOP | `blurTOP` |
| Composite TOP | `compositeTOP` |
| HSV Adjust TOP | `hsvadjustTOP` |
| Movie File Out TOP | `moviefileoutTOP` |
| Text DAT | `textDAT` |
| Annotate COMP | `annotateCOMP` |

---

## Confirmed Parameter Behaviors

| Operator | Parameter | Notes |
|----------|-----------|-------|
| `levelTOP` | `contrast` | Correct name — NOT `contrast1` |
| `levelTOP` | `brightness1` | Correct name — NOT `brightness` |
| `levelTOP` | `gamma1` | Correct name — NOT `gamma` |
| `glslTOP` | `vec0name` / `vec0valuex` | **Scalar float uniforms live on the VECTORS page** — `vec0name` = uniform name, `vec0valuex` = value (`.expr` + `ParMode.EXPRESSION` to bind). Confirmed 2026-07-14 (tunnel_oxidized). |
| `glslTOP` | `vec` | **NOT a uniform count — reads `0` and setting it is a no-op.** The `vecN*` sequence blocks are addressable via `getattr(g.par, 'vec7name')` without growing anything first. Just set `vecNname`/`vecNvaluex` directly. |
| `glslTOP` | *(uniform warnings)* | "Uniform 'X' is not assigned" can persist as a **stale warning** after you assign it — force-cook the shader DAT and the glslTOP to clear. Verify with `.warnings()`, not the badge. |
| `glslTOP` | `color0name` / `color0rgbr` | Color page is for **vec4 color** uniforms only. **Corrected 2026-07-14** — the old entry here claimed "float uniforms live on the color page", which is wrong and sends scalar-float bindings to the wrong page. |
| `glslTOP` | *(uniform declarations)* | TD does **not** auto-declare uniforms. Every uniform must be declared in the shader (`uniform float uTime;`) or it's a compile error, regardless of the page binding. |
| `glslTOP` | `pixeldat` | Path to the textDAT containing the GLSL shader |
| `glslTOP` | `outputresolution` | Set to `0` for custom resolution |
| `glslTOP` | `format` | `rgba16float` for 16-bit float output |
| `constantCHOP` | `const0name` / `const0value` | NOT `value0name` / `value0` |
| `mathCHOP` (range) | `fromrange1` / `fromrange2` / `torange1` / `torange2` | NOT `from1/2`, `to1/2` |
| `lagCHOP` | `lag1` / `lag2` | NOT `lagup` / `lagdown` |
| `audiofilterCHOP` | `filter` / `units` / `cutofffrequency` / `resonance` | For frequency filtering — NOT `filterCHOP` |
| `analyzeCHOP` | `function` | Use `rmspower` for highpass filter output — NOT `average` (HP is bipolar, average ≈ 0) |
| `moviefileoutTOP` | `audiochop` | Must point to raw audio stream (e.g. `audiofileinCHOP`) at 44100 Hz — NOT analysis CHOPs like `null_audio` which run at rate 30 |

---

## Confirmed Limitations

| Limitation | Workaround |
|-----------|-----------|
| `td_set_operator_pars` cannot set expressions | Use `td_execute_python` with `par.expr = "..."` and `par.mode = ParMode.EXPRESSION` |
| `td_create_operator` does not wire connections | Wire via `td_execute_python` with `inputConnectors[n].connect(op)` |
| `td_read_chop` on large recordings exceeds token limits | Analyze inside TD via `td_execute_python` — use `list(ch.vals)` + `sorted()` |
| `audiodeviceoutCHOP` with `cookalways=True` freezes TD | Remove `cookalways` flag. **Re-confirmed 2026-07-14 (tunnel_oxidized), cost a whole session of bogus fps readings:** measured 68.6 ms/cook and 1223 ms/s CPU = **7352% of budget**, holding the project at **fps 0**; `cookalways=False` → fps 60 instantly. **It does NOT show up in `td_get_operator_info` `nonDefaultPars`** (Common-page par) — check it explicitly with `op.par.cookalways.eval()`. Symptom to recognise: fps 0 with a near-idle GPU and one CHOP dominating `td_get_perf` cpu/s. |
| `playmode='locked'` on `audiofileinCHOP` only plays to timeline end | Use `sequential` for continuous playback |

---

## DAT / GLSL Text Workflow

- Write GLSL shader code into a `textDAT` (e.g. `glsl_mandelbulb`)
- Point the `glslTOP`'s `par.pixeldat` at that DAT
- Edit shader via `td_write_dat` — use `old_text`/`new_text` for targeted patches, `text` for full rewrites
- TD recompiles automatically on DAT change; FPS dip after write is normal (recompile, not performance issue)
- `old_text` must be unique in the file — provide more surrounding context if match fails

---

## Known Behaviors

| Behavior | Notes |
|----------|-------|
| FPS shows 0 after shader write | Normal — TD is recompiling the GLSL. Recovers within 1–2 seconds. |
| GPU cook time shows 0.0 in `td_get_perf` | Operator is GPU-cached, not a real zero. |
| `par.val` returns stale value | Use `par.eval()` to verify expression results. |
| `td_create_operator` returns `📋 PAR` block | Read it — contains exact parameter names for the new op type. |
| `td_input_execute` returns immediately | Poll `td_input_status` until `status="idle"` before continuing. |
| `annotateCOMP` nodeY = bottom edge | Top edge = `nodeY + nodeHeight`. Account for this when positioning. |
| HSV desaturation kills warm low-luminance colors | Muted orange/warm palettes with low RGB values go black through `hsvadjustTOP`. Warm palettes need higher base RGB values to survive. |
| Power curves on audio inputs in GLSL | `pow(x, 2.5–3.0)` suppresses breakdown rumble while passing drop peaks. Better than Lag CHOP alone for smooth breakdown behavior. |
