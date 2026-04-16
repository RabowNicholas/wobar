// act2_vortex_pull.frag
// Act 2 / DESCENSION — Logarithmic spiral tunnel, 3-arm, sub-pressure drives inward scroll
// TD GLSL TOP: vUV.st, out vec4 fragColor, TDOutputSwizzle(), no #version directive

uniform float uTime;         // absTime.seconds
uniform float uSubPressure;  // op('audio_ref')['sub_pressure'] — sustained pull strength
uniform float uChaos;        // op('audio_ref')['sub_bass'] * energy — combined chaos
uniform float uGrowl;        // op('audio_ref')['growl'] — turbulence amplitude
uniform float uBrightness;   // ctrl_scene.brightness (base 1.4)
uniform float uScrollBase;   // ctrl_scene.scroll_speed (base 0.45)
uniform float uArmCount;     // ctrl_scene.arm_count (base 3.0)

out vec4 fragColor;

// Simple 2D noise for turbulence
float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}
float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    float a = hash(i);
    float b = hash(i + vec2(1,0));
    float c = hash(i + vec2(0,1));
    float d = hash(i + vec2(1,1));
    return mix(mix(a,b,f.x), mix(c,d,f.x), f.y);
}

void main() {
    vec2 uv = vUV.st * 2.0 - 1.0;
    float aspect = 720.0 / 1280.0;
    uv.x *= aspect;

    // Power curve — breakdown calm, drop intensity
    float chaos = pow(clamp(uChaos, 0.0, 1.0), 3.0);
    float subP  = pow(clamp(uSubPressure, 0.0, 1.0), 2.5);

    // Turbulence domain warp (growl = bass wobble)
    float warpAmp = 0.04 + uGrowl * 0.18;
    float slowT = uTime * 0.25;
    float wx = noise(uv * 1.8 + vec2(slowT, 0.0)) * 2.0 - 1.0;
    float wy = noise(uv * 1.8 + vec2(0.0, slowT + 2.7)) * 2.0 - 1.0;
    vec2 wuv = uv + vec2(wx, wy) * warpAmp;

    float r = length(wuv);
    float a = atan(wuv.y, wuv.x);

    // Logarithmic spiral: depth = 1/r (approaches infinity at center)
    float depth = 1.0 / (r + 0.01);

    // Scroll inward: increase depth over time
    float scrollSpeed = uScrollBase * (0.45 + chaos * 5.0) * (1.0 + subP * 3.0);
    float scroll = depth - uTime * scrollSpeed;

    // Global clockwise rotation
    float globalRot = -uTime * (0.20 + chaos * 0.25);
    float armA = a + globalRot;

    // N-arm spiral bands
    float spiralFreq = 1.8;
    float spiral = fract(armA / (6.2832 / uArmCount) + scroll * spiralFreq);
    float band = smoothstep(0.0, 0.3, spiral) * (1.0 - smoothstep(0.7, 1.0, spiral));

    // Center void fade
    float voidMask = smoothstep(0.0, 0.08, r);
    float band_final = band * voidMask;

    // Color: deep purple → muted cyan Act 2 palette
    vec3 darkCol  = vec3(0.04, 0.00, 0.08);
    vec3 bandCol  = vec3(0.18, 0.35, 0.42);   // muted cyan/teal Act 2
    vec3 coreCol  = vec3(0.35, 0.55, 0.65);   // brighter cyan toward center

    float centerBlend = 1.0 - smoothstep(0.0, 0.5, r);
    vec3 color = mix(darkCol, bandCol, band_final);
    color = mix(color, coreCol, band_final * centerBlend);
    color *= uBrightness * (1.0 + subP * 0.5);

    // Vignette: dark edges pull you in
    float vig = 1.0 - smoothstep(0.4, 1.0, r);
    color *= vig;

    fragColor = TDOutputSwizzle(vec4(clamp(color, 0.0, 1.0), 1.0));
}
