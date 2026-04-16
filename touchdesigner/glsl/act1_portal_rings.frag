// act1_portal_rings.frag
// Act 1 / INVOCATION — Concentric portal rings slowly expanding, energy drives brightness
// TD GLSL TOP: vUV.st, out vec4 fragColor, TDOutputSwizzle(), no #version directive

uniform float uTime;        // absTime.seconds
uniform float uEnergy;      // op('audio_ref')['energy'] — ring brightness
uniform float uSubBass;     // op('audio_ref')['sub_bass'] — radius nudge on kicks
uniform float uTransient;   // op('audio_ref')['transient'] — flash on note attacks
uniform float uBrightness;  // ctrl_scene.brightness (base 1.6)
uniform float uRingSpeed;   // ctrl_scene.ring_speed (base 0.08)

out vec4 fragColor;

void main() {
    vec2 uv = vUV.st * 2.0 - 1.0;
    float aspect = 720.0 / 1280.0;
    uv.x *= aspect;

    float r = length(uv);

    // Scroll rings outward over time — slow, meditative
    float scroll = uTime * uRingSpeed;

    // Ring pattern: sharp inner edge, soft outer glow
    // fract(r * freq - scroll) gives repeating concentric bands
    float freq = 4.5;
    float band = fract(r * freq - scroll);

    // Thin bright rings with wide dark gaps
    float ring = pow(1.0 - smoothstep(0.0, 0.12, band), 3.0);
    ring += pow(1.0 - smoothstep(0.88, 1.0, band), 3.0) * 0.5;

    // Sub-bass creates subtle radius compression on kicks
    float rmod = r + uSubBass * 0.04 * sin(uTime * 8.0);
    float kickRing = exp(-abs(fract(rmod * freq - scroll) - 0.05) * 30.0) * uSubBass;

    // Transient flash: brief white-purple burst from center
    float flash = exp(-r * 3.0) * uTransient;

    // Deep center void (the portal itself is darkness)
    float voidMask = smoothstep(0.0, 0.15, r);

    // Color: deep purple rings on black, warm highlight on energy peak
    vec3 ringCol  = vec3(0.42, 0.06, 0.65);
    vec3 innerCol = vec3(0.65, 0.18, 1.00);
    vec3 flashCol = vec3(0.80, 0.50, 1.00);

    float totalRing = (ring + kickRing) * voidMask;
    vec3 color = ringCol * totalRing;
    color += innerCol * totalRing * (1.0 - smoothstep(0.0, 0.4, r)) * 1.5;
    color += flashCol * flash;

    // Energy modulates overall brightness
    color *= uBrightness * (1.0 + uEnergy * 0.6);

    // Vignette
    float vig = 1.0 - smoothstep(0.6, 1.1, r);
    color *= vig;

    fragColor = TDOutputSwizzle(vec4(clamp(color, 0.0, 1.0), 1.0));
}
