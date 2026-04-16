// act2_spiral_descent.frag
// Act 2 / DESCENSION — 2-arm Archimedean spiral tightening with sub-bass
// TD GLSL TOP: vUV.st, out vec4 fragColor, TDOutputSwizzle(), no #version directive

uniform float uTime;         // absTime.seconds
uniform float uSubBass;      // op('audio_ref')['sub_bass'] — tighten spiral
uniform float uSubPressure;  // op('audio_ref')['sub_pressure'] — scroll speed
uniform float uEnergy;       // op('audio_ref')['energy'] — arm brightness
uniform float uBrightness;   // ctrl_scene.brightness (base 1.5)
uniform float uTwist;        // ctrl_scene.twist (base 4.0 — arm turns before center)

out vec4 fragColor;

float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}
float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    return mix(
        mix(hash(i), hash(i+vec2(1,0)), f.x),
        mix(hash(i+vec2(0,1)), hash(i+vec2(1,1)), f.x),
        f.y
    );
}

void main() {
    vec2 uv = vUV.st * 2.0 - 1.0;
    float aspect = 720.0 / 1280.0;
    uv.x *= aspect;

    float r = length(uv);
    float a = atan(uv.y, uv.x);

    // Sub-bass tightens spiral (smaller b = tighter coil)
    float tighten = pow(clamp(uSubBass, 0.0, 1.0), 2.0);
    float b = 0.30 - tighten * 0.18;  // Archimedean b parameter

    // Scroll: inward pull over time (sub_pressure = faster)
    float subP = pow(clamp(uSubPressure, 0.0, 1.0), 2.5);
    float scroll = uTime * (0.30 + subP * 1.5);

    // Clockwise rotation
    float rot = -uTime * 0.15;
    float ra = a + rot;

    // Archimedean spiral: r = b * theta → theta = r / b
    // We want "distance from nearest arm"
    float PI2 = 6.28318;
    float armsN = 2.0;
    float theta = r / b;
    float armPhase = fract((theta - scroll) / PI2 * armsN + ra / PI2 * armsN);

    // Thin bright arms
    float armWidth = 0.08 + (1.0 - tighten) * 0.06;
    float arm = smoothstep(armWidth, 0.0, abs(armPhase - 0.5) * 2.0 - (1.0 - armWidth * 2.0));
    arm = clamp(arm, 0.0, 1.0);

    // Subtle noise along the arm edge
    float n = noise(uv * 4.0 + vec2(uTime * 0.3, 0.0)) * 0.15;
    arm *= 1.0 + n;

    // Center singularity glow
    float core = exp(-r * 5.0);

    // Color: near-black background, muted blue-purple arms, bright cyan core
    vec3 bgCol   = vec3(0.02, 0.00, 0.05);
    vec3 armCol  = vec3(0.20, 0.38, 0.50);   // muted cyan/slate Act 2
    vec3 coreCol = vec3(0.40, 0.65, 0.80);   // brighter blue-white at singularity

    vec3 color = bgCol;
    float armFade = 1.0 - smoothstep(0.0, 0.8, r);  // arms bright near center
    color += armCol * arm * (0.5 + armFade * 0.8) * (1.0 + uEnergy * 0.5);
    color += coreCol * core * 1.2;
    color *= uBrightness;

    // Deep vignette — edges are void
    float vig = 1.0 - smoothstep(0.35, 1.0, r);
    color *= vig;

    fragColor = TDOutputSwizzle(vec4(clamp(color, 0.0, 1.0), 1.0));
}
