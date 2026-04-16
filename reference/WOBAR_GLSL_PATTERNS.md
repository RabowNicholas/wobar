---
title: WOBAR GLSL Patterns
version: 1.0
last_updated: 2026-04-15
status: live
scope: Act-specific GLSL TOP fragment shader patterns for WOBAR. 2 shaders per act, audio-reactive, paste-ready for TD GLSL TOP. Each shader saved as .frag in touchdesigner/glsl/.
dependencies: [[reference/WOBAR_TD_AGENT_RULES]], [[reference/WOBAR_FRAMEWORK]]
---

# WOBAR GLSL PATTERNS

Paste-ready fragment shaders for TD GLSL TOP. Audio-reactive via uniforms. No external library dependencies.

**TD GLSL TOP conventions (every shader uses these):**
- `vUV.st` — UV coordinate (0→1 range, origin bottom-left)
- `out vec4 fragColor` — output declaration
- `TDOutputSwizzle(vec4(...))` — required TD output wrapper
- No `#version` directive needed — TD injects it
- Uniforms bound via glslTOP color page: `color0name` = uniform name, `color0rgbr` = expression
- Aspect correction: `uv.x *= 720.0 / 1280.0` for portrait 720×1280

**Uniform binding pattern:**
```
color0name  → "uTime"       color0rgbr → absTime.seconds
color1name  → "uSubBass"    color1rgbr → op('audio_ref')['sub_bass'] if op('audio_ref').numChans > 0 else 0
color2name  → "uEnergy"     color2rgbr → op('audio_ref')['energy'] if op('audio_ref').numChans > 0 else 0
color3name  → "uTransient"  color3rgbr → op('audio_ref')['transient'] if op('audio_ref').numChans > 0 else 0
```

---

## Act 1 / INVOCATION — Warmth, breath, circle, 60-80 BPM

**Constraints:** circles, warm purple glow, breath rhythm. No sharp geometry, no aggressive motion, no cool colors.

### act1_breath_circle.frag
File: `touchdesigner/glsl/act1_breath_circle.frag`

Warm purple radial glow. Sub-bass drives inner radius. LFO breath at ~70 BPM. Outer ring tracks energy. Angular ripple prevents mechanical feel.

**Uniforms:**
| Name | Expression | Default |
|------|-----------|---------|
| `uTime` | `absTime.seconds` | — |
| `uSubBass` | `op('audio_ref')['sub_bass']` | 0 |
| `uEnergy` | `op('audio_ref')['energy']` | 0 |
| `uBrightness` | `op('ctrl_scene')['brightness']` | 1.8 |
| `uBreathSpeed` | `op('ctrl_scene')['breath_speed']` | 0.25 |

Key technique: `glow = exp(-max(r - coreRadius, 0.0) * 6.0)` — exponential falloff from dynamic inner radius. `coreRadius` driven by both sub_bass and breath LFO simultaneously.

---

### act1_portal_rings.frag
File: `touchdesigner/glsl/act1_portal_rings.frag`

Concentric portal rings scrolling outward slowly. Energy drives brightness. Sub-bass creates radius compression on kicks. Transient = brief white-purple center flash. Deep center void.

**Uniforms:**
| Name | Expression | Default |
|------|-----------|---------|
| `uTime` | `absTime.seconds` | — |
| `uEnergy` | `op('audio_ref')['energy']` | 0 |
| `uSubBass` | `op('audio_ref')['sub_bass']` | 0 |
| `uTransient` | `op('audio_ref')['transient']` | 0 |
| `uBrightness` | `op('ctrl_scene')['brightness']` | 1.6 |
| `uRingSpeed` | `op('ctrl_scene')['ring_speed']` | 0.08 |

Key technique: `fract(r * freq - scroll)` gives repeating concentric bands. `pow(1.0 - smoothstep(0.0, 0.12, band), 3.0)` sharpens inner edge while leaving outer glow.

---

## Act 2 / DESCENSION — Inward pull, depth, spiral, tightening

**Constraints:** inward motion only, depth, tightening with audio. No outward expansion, no warm colors dominating, no flat motion.

### act2_vortex_pull.frag
File: `touchdesigner/glsl/act2_vortex_pull.frag`

Logarithmic spiral tunnel, 3-arm, sub-pressure drives inward scroll. Double FBM warp for turbulence. Growl modulates warp amplitude. Power curves on sub_pressure and chaos suppress breakdown.

**Uniforms:**
| Name | Expression | Default |
|------|-----------|---------|
| `uTime` | `absTime.seconds` | — |
| `uSubPressure` | `op('audio_ref')['sub_pressure']` | 0 |
| `uChaos` | `op('audio_ref')['sub_bass'] * op('audio_ref')['energy']` | 0 |
| `uGrowl` | `op('audio_ref')['growl']` | 0 |
| `uBrightness` | `op('ctrl_scene')['brightness']` | 1.4 |
| `uScrollBase` | `op('ctrl_scene')['scroll_speed']` | 0.45 |
| `uArmCount` | `op('ctrl_scene')['arm_count']` | 3.0 |

Key technique: `float depth = 1.0 / (r + 0.01)` — logarithmic depth. `float chaos = pow(clamp(uChaos, 0.0, 1.0), 3.0)` — suppresses breakdown rumble, passes drop peaks. Clockwise global rotation via `float globalRot = -uTime * (0.20 + chaos * 0.25)`.

Color: muted cyan/teal (`vec3(0.18, 0.35, 0.42)`) — Act 2 approved blue-teal departure from base purple.

---

### act2_spiral_descent.frag
File: `touchdesigner/glsl/act2_spiral_descent.frag`

2-arm Archimedean spiral tightening with sub-bass. Arms fade to bright near center (singularity). Sub-bass tightens the coil spacing. Clean geometric descent.

**Uniforms:**
| Name | Expression | Default |
|------|-----------|---------|
| `uTime` | `absTime.seconds` | — |
| `uSubBass` | `op('audio_ref')['sub_bass']` | 0 |
| `uSubPressure` | `op('audio_ref')['sub_pressure']` | 0 |
| `uEnergy` | `op('audio_ref')['energy']` | 0 |
| `uBrightness` | `op('ctrl_scene')['brightness']` | 1.5 |
| `uTwist` | `op('ctrl_scene')['twist']` | 4.0 |

Key technique: `float theta = r / b` — Archimedean spiral distance field. `b = 0.30 - tighten * 0.18` where `tighten = pow(uSubBass, 2.0)` — sub-bass tightens coil spacing with power curve.

---

## Act 3 / CONFRONTATION — Fracture, imperfect mirror, cold palette, digital

**Constraints:** 85-90% mirror (never 100%), cold palette only, glitch on peaks. NO warm/orange tones. Perfect symmetry is forbidden.

### act3_mirror_fracture.frag
File: `touchdesigner/glsl/act3_mirror_fracture.frag`

Imperfect 6-fold kaleidoscope (88% mirror factor). Double FBM structure. Cold indigo/blue palette. Transient fires digital block-glitch displacement. Counterclockwise rotation for tension.

**Uniforms:**
| Name | Expression | Default |
|------|-----------|---------|
| `uTime` | `absTime.seconds` | — |
| `uTransient` | `op('audio_ref')['transient']` | 0 |
| `uEnergy` | `op('audio_ref')['energy']` | 0 |
| `uSubBass` | `op('audio_ref')['sub_bass']` | 0 |
| `uBrightness` | `op('ctrl_scene')['brightness']` | 1.3 |
| `uFoldCount` | `op('ctrl_scene')['fold_count']` | 6.0 |
| `uMirrorAmt` | `op('ctrl_scene')['mirror_amt']` | 0.88 |

Key technique: `kaleido()` function blends between full-mirror and original angle by `mirrorAmt` — values below 1.0 leave visible seams, which reads as fracture/damage. Glitch: `uv.x += glitchShift * glitchAmt` where `glitchShift` is per-row hash tied to frame time.

**Warning:** `uMirrorAmt` must stay between 0.80–0.92. At 1.0 = perfect symmetry = forbidden by Act 3 constraint.

---

### act3_grid_distort.frag
File: `touchdesigner/glsl/act3_grid_distort.frag`

Wave-distorted grid. Multiple overlapping sine waves driven by energy. Transient fires discrete block-shift fracture. Sub-bass increases grid density. Cold palette only — no warm tones anywhere.

**Uniforms:**
| Name | Expression | Default |
|------|-----------|---------|
| `uTime` | `absTime.seconds` | — |
| `uTransient` | `op('audio_ref')['transient']` | 0 |
| `uEnergy` | `op('audio_ref')['energy']` | 0 |
| `uSubBass` | `op('audio_ref')['sub_bass']` | 0 |
| `uBrightness` | `op('ctrl_scene')['brightness']` | 1.2 |
| `uGridScale` | `op('ctrl_scene')['grid_scale']` | 8.0 |
| `uWaveAmp` | `op('ctrl_scene')['wave_amp']` | 0.15 |

Key technique: Two-axis sine distortion + per-row hash block shift on transient. `gridMask = 1.0 - lineX * lineY` — inverted product gives lines, not cells. Hard vignette (0.25–0.85) for claustrophobic feel.

---

## Act 4 / RELEASE — Outward, full palette, warm accents required, rhythm

**Constraints:** outward radial expansion, full color palette (warm orange accent REQUIRED), rhythm-driven. No inward motion, no cool-only palette.

### act4_radial_burst.frag
File: `touchdesigner/glsl/act4_radial_burst.frag`

Outward expanding rings + radial rays. Warm orange (#B45014) burst on every transient. Energy multiplies ring visibility. Sub-bass core pulse on kicks. Wide vignette = expansive.

**Uniforms:**
| Name | Expression | Default |
|------|-----------|---------|
| `uTime` | `absTime.seconds` | — |
| `uEnergy` | `op('audio_ref')['energy']` | 0 |
| `uTransient` | `op('audio_ref')['transient']` | 0 |
| `uSubBass` | `op('audio_ref')['sub_bass']` | 0 |
| `uBrightness` | `op('ctrl_scene')['brightness']` | 1.8 |
| `uRingSpeed` | `op('ctrl_scene')['ring_speed']` | 0.35 |
| `uRingCount` | `op('ctrl_scene')['ring_count']` | 6.0 |

Key technique: `fract(r * uRingCount - scroll)` with positive scroll = outward expansion. Transient orange: `warmOr * flashFade` where `flashFade = exp(-r * 2.5) * uTransient` — warm orange radiates from center on every note attack.

**Act 4 rule:** `warmOr = vec3(0.706, 0.314, 0.078)` (#B45014). This line must exist in every Act 4 shader.

---

### act4_corona_pulse.frag
File: `touchdesigner/glsl/act4_corona_pulse.frag`

Pulsing corona halo at energy-driven radius + N rotating arms. Arms blend purple→warm orange at tips. Transient fires expanding scatter rings. Growl adds arm texture noise.

**Uniforms:**
| Name | Expression | Default |
|------|-----------|---------|
| `uTime` | `absTime.seconds` | — |
| `uEnergy` | `op('audio_ref')['energy']` | 0 |
| `uTransient` | `op('audio_ref')['transient']` | 0 |
| `uSubBass` | `op('audio_ref')['sub_bass']` | 0 |
| `uGrowl` | `op('audio_ref')['growl']` | 0 |
| `uBrightness` | `op('ctrl_scene')['brightness']` | 1.7 |
| `uArmCount` | `op('ctrl_scene')['arm_count']` | 8.0 |
| `uRotSpeed` | `op('ctrl_scene')['rot_speed']` | 0.40 |

Key technique: `cos(rotA * uArmCount)` for N-arm corona pattern. Counterclockwise rotation = joyful energy (positive `uRotSpeed`). `mix(armPurp, armWarm, pow(arm, 2.0) * 0.7)` — warm orange only at arm tips where arm is brightest.

---

## Act 5 / RETURN — Closing, callback to Act 1, pure purple, breath returns

**Constraints:** circle returns, portal closing, breath rhythm returns. No new visual concepts — only Act 1/2 language.

### act5_portal_close.frag
File: `touchdesigner/glsl/act5_portal_close.frag`

Iris vignette closing from uRadius=1.0 (open) to uRadius=0.0 (black). `uRadius` must be driven externally by a timer/LFO. Act 1 breath pattern preserved inside portal. Pure purple — no departures.

**Uniforms:**
| Name | Expression | Default |
|------|-----------|---------|
| `uTime` | `absTime.seconds` | — |
| `uRadius` | `op('ctrl_scene')['portal_radius']` | 1.0 |
| `uSubBass` | `op('audio_ref')['sub_bass']` | 0 |
| `uEnergy` | `op('audio_ref')['energy']` | 0 |
| `uBrightness` | `op('ctrl_scene')['brightness']` | 1.5 |
| `uBreathSpeed` | `op('ctrl_scene')['breath_speed']` | 0.25 |

Key technique: `inside = 1.0 - smoothstep(portalR - irisSoftness, portalR + irisSoftness * 0.3, r)` — asymmetric softness (sharper leading edge as it closes). `irisSoftness` shrinks as `uRadius` shrinks = crisper closure.

**[VERIFY]** `uRadius` drive: wire a Math CHOP timer (0→1 normalized) → invert → feed to `ctrl_scene.portal_radius`. Use Lag CHOP (down=30s) for smooth closure.

---

### act5_ember_settle.frag
File: `touchdesigner/glsl/act5_ember_settle.frag`

Drifting particle embers settling downward. 16 independent embers with unique seeds, each with position/size/speed variation. Sub-bass creates brief upward lift on kicks. Very slow, meditative close.

**Uniforms:**
| Name | Expression | Default |
|------|-----------|---------|
| `uTime` | `absTime.seconds` | — |
| `uSubBass` | `op('audio_ref')['sub_bass']` | 0 |
| `uEnergy` | `op('audio_ref')['energy']` | 0 |
| `uBrightness` | `op('ctrl_scene')['brightness']` | 1.2 |
| `uDriftSpeed` | `op('ctrl_scene')['drift_speed']` | 0.04 |
| `uEmberCount` | `op('ctrl_scene')['ember_count']` | 12.0 |

Key technique: For loop over 16 embers (GLSL unrollable). Each ember: unique `hash(seed)` for position, speed, size, phase. Downward drift = `py = startY - t * 0.8`. Vertical wrap via `mod()` — embers respawn from top. Lift via `uSubBass * sin(phase + uTime * 2.0)`.

**Performance note:** 16-iteration loop compiles fine on GPU. Do not exceed 24 iterations — diminishing returns and potential compile time.

---

## Reusable Utility Functions

These appear across multiple shaders. Copy directly.

### Hash + Noise (2D)
```glsl
float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float noise(vec2 p) {
    vec2 i = floor(p); vec2 f = fract(p); f = f*f*(3.0-2.0*f);
    return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),
               mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y);
}
```

### FBM (4 octaves)
```glsl
float fbm(vec2 p) {
    float v = 0.0; float a = 0.5;
    for (int i = 0; i < 4; i++) { v += a * noise(p); p *= 2.1; a *= 0.5; }
    return v;
}
```

### Hue Rotate (constrained color cycling)
```glsl
vec3 hueRotate(vec3 c, float angle) {
    float cosA = cos(angle); float sinA = sin(angle);
    vec3 k = vec3(0.57735);
    return c * cosA + cross(k, c) * sinA + k * dot(k, c) * (1.0 - cosA);
}
// Use with ±0.4 rad max to stay within purple family
// 3 independent oscillators: sin(t*0.018)*0.40, sin(t*0.031+2.1)*0.35, sin(t*0.052+4.3)*0.30
```

### Power Curve (audio signal conditioning)
```glsl
// Suppress breakdown rumble, pass drop peaks
float chaos = pow(clamp(uChaos, 0.0, 1.0), 3.0);      // 3.0 = steep
float subP  = pow(clamp(uSubPressure, 0.0, 1.0), 2.5); // 2.5 = moderate
// Use for any audio signal that should be calm at low values and reactive at high
```

### Imperfect Kaleidoscope Fold (Act 3)
```glsl
vec2 kaleido(vec2 uv, float folds, float mirrorAmt) {
    float a = atan(uv.y, uv.x);
    float r = length(uv);
    float sector = 3.14159 / folds;
    a = mod(a, 2.0 * sector);
    float folded = abs(a - sector);
    a = mix(a, folded, mirrorAmt);  // mirrorAmt < 1.0 = seam visible
    return vec2(cos(a), sin(a)) * r;
}
```

---

## Act Color Reference

| Act | Base dark | Mid | Bright | Accent | Forbidden |
|-----|-----------|-----|--------|--------|-----------|
| 1 | `vec3(0.04, 0.00, 0.08)` | `vec3(0.35, 0.04, 0.47)` | `vec3(0.75, 0.20, 1.00)` | None | Cool, green |
| 2 | `vec3(0.02, 0.00, 0.05)` | `vec3(0.18, 0.35, 0.42)` | `vec3(0.40, 0.65, 0.80)` | Muted teal | Warm |
| 3 | `vec3(0.00, 0.00, 0.04)` | `vec3(0.05, 0.08, 0.22)` | `vec3(0.30, 0.40, 0.70)` | Ice blue | **ALL WARM** |
| 4 | `vec3(0.01, 0.00, 0.04)` | `vec3(0.45, 0.08, 0.70)` | `vec3(0.80, 0.50, 1.00)` | `vec3(0.706, 0.314, 0.078)` | Cool-only |
| 5 | `vec3(0.02, 0.00, 0.05)` | `vec3(0.28, 0.03, 0.45)` | `vec3(0.75, 0.20, 1.00)` | None | New visuals |
