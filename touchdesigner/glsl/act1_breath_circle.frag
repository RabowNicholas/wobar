// act1_breath_circle.frag
// Act 1 / INVOCATION — Warm purple radial glow, sub-bass drives radius, LFO breath
// TD GLSL TOP: vUV.st, out vec4 fragColor, TDOutputSwizzle(), no #version directive

// Uniforms — bind via glslTOP color page (color0name / color0rgbr)
uniform float uTime;         // absTime.seconds
uniform float uSubBass;      // op('audio_ref')['sub_bass'] — radius pulse
uniform float uEnergy;       // op('audio_ref')['energy'] — glow intensity
uniform float uBrightness;   // ctrl_scene.brightness (base 1.8)
uniform float uBreathSpeed;  // ctrl_scene.breath_speed (base 0.25, ~70 BPM)

out vec4 fragColor;

void main() {
    vec2 uv = vUV.st * 2.0 - 1.0;
    float aspect = 720.0 / 1280.0;
    uv.x *= aspect;

    float r = length(uv);
    float a = atan(uv.y, uv.x);

    // LFO breath — gentle sine at BPM-anchored rate
    float breath = 0.5 + 0.5 * sin(uTime * uBreathSpeed * 6.2832);

    // Sub-bass expands the inner core radius
    float coreRadius = 0.18 + uSubBass * 0.12 + breath * 0.04;

    // Warm purple radial glow: bright center, soft falloff
    float glow = exp(-max(r - coreRadius, 0.0) * 6.0);

    // Outer ambient ring — slow energy response
    float ring = exp(-abs(r - 0.45 - uEnergy * 0.15) * 14.0);
    ring *= 0.35;

    // Faint angular ripple for non-uniformity (Act 1 feels alive, not mechanical)
    float ripple = 0.5 + 0.5 * sin(a * 6.0 + uTime * 0.8);
    ripple = pow(ripple, 4.0) * 0.12;

    // Color: warm purple core (#5A0F78 → #C060FF highlights)
    vec3 coreCol   = vec3(0.35, 0.04, 0.47);
    vec3 glowCol   = vec3(0.75, 0.20, 1.00);
    vec3 ringCol   = vec3(0.18, 0.00, 0.28);

    vec3 color = coreCol * glow + glowCol * glow * glow + ringCol * ring;
    color += glowCol * ripple * glow * 0.5;

    // Vignette
    float vig = 1.0 - smoothstep(0.5, 1.0, r);
    color *= vig;

    color *= uBrightness * (1.0 + uEnergy * 0.4);

    fragColor = TDOutputSwizzle(vec4(clamp(color, 0.0, 1.0), 1.0));
}
