// act3_mirror_fracture.frag
// Act 3 / CONFRONTATION — Imperfect 6-fold kaleidoscope (88% mirror), cold palette only,
// transient-triggered glitch on peaks. NO warm colors.
// TD GLSL TOP: vUV.st, out vec4 fragColor, TDOutputSwizzle(), no #version directive

uniform float uTime;        // absTime.seconds
uniform float uTransient;   // op('audio_ref')['transient'] — glitch trigger (peaks only)
uniform float uEnergy;      // op('audio_ref')['energy'] — brightness modulation
uniform float uSubBass;     // op('audio_ref')['sub_bass'] — structure scale pulse
uniform float uBrightness;  // ctrl_scene.brightness (base 1.3)
uniform float uFoldCount;   // ctrl_scene.fold_count (base 6.0)
uniform float uMirrorAmt;   // ctrl_scene.mirror_amt (base 0.88 — NOT 1.0, imperfect)

out vec4 fragColor;

float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1,311.7))) * 43758.5453); }
float noise(vec2 p) {
    vec2 i = floor(p); vec2 f = fract(p);
    f = f*f*(3.0-2.0*f);
    return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),
               mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y);
}
float fbm(vec2 p) {
    float v = 0.0; float a = 0.5;
    for (int i = 0; i < 4; i++) { v += a * noise(p); p *= 2.1; a *= 0.5; }
    return v;
}

// Imperfect kaleidoscope fold — mirror_amt < 1.0 = seam visible
vec2 kaleido(vec2 uv, float folds, float mirrorAmt) {
    float a = atan(uv.y, uv.x);
    float r = length(uv);
    float sector = 3.14159 / folds;
    a = mod(a, 2.0 * sector);
    // Blend between full mirror and original angle at seam
    float folded = abs(a - sector);
    a = mix(a, folded, mirrorAmt);
    return vec2(cos(a), sin(a)) * r;
}

void main() {
    vec2 uv = vUV.st * 2.0 - 1.0;
    float aspect = 720.0 / 1280.0;
    uv.x *= aspect;

    // Glitch: transient adds pixel-block offset (cold, digital, violent)
    float glitchAmt = uTransient * 0.08;
    float glitchRow = floor(vUV.t * 24.0) / 24.0;
    float glitchShift = (hash(vec2(glitchRow, floor(uTime * 30.0))) - 0.5) * 2.0;
    uv.x += glitchShift * glitchAmt;

    // Slow global rotation — tunnel-like (counterclockwise for Act 3 tension)
    float rot = uTime * 0.12;
    float cr = cos(rot); float sr = sin(rot);
    uv = vec2(cr*uv.x - sr*uv.y, sr*uv.x + cr*uv.y);

    // Imperfect kaleidoscope fold
    vec2 kuv = kaleido(uv, uFoldCount, uMirrorAmt);

    // FBM structure — double warp for depth
    float slowT = uTime * 0.20;
    float wx = fbm(kuv * 1.4 + vec2(slowT, 0.0)) - 0.5;
    float wy = fbm(kuv * 1.4 + vec2(0.0, slowT + 3.1)) - 0.5;
    vec2 wuv = kuv + vec2(wx, wy) * 0.12;

    float f = fbm(wuv * 2.2 + vec2(uTime * 0.08, 0.0));

    // Sub-bass scales the pattern (barely — structural, not dramatic)
    float scale = 1.0 + uSubBass * 0.06;
    f = fbm(wuv * 2.2 * scale);

    // COLD PALETTE ONLY — blues, cold greys, near-white on peaks
    // Absolutely no warm tones. Act 3 rule: zero warm.
    vec3 darkCol  = vec3(0.00, 0.00, 0.04);   // near black with blue cast
    vec3 midCol   = vec3(0.05, 0.08, 0.22);   // cold indigo
    vec3 peakCol  = vec3(0.30, 0.40, 0.70);   // cold blue-white
    vec3 glitchCol= vec3(0.60, 0.75, 1.00);   // icy blue flash on transient

    vec3 color = mix(darkCol, mix(midCol, peakCol, f * f), f);
    color += glitchCol * uTransient * 0.6 * (1.0 - smoothstep(0.3, 0.7, length(uv)));

    color *= uBrightness * (1.0 + uEnergy * 0.35);

    // Sharp vignette — Act 3 is claustrophobic
    float r = length(uv);
    float vig = 1.0 - smoothstep(0.3, 0.9, r);
    color *= vig;

    fragColor = TDOutputSwizzle(vec4(clamp(color, 0.0, 1.0), 1.0));
}
