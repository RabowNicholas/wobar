// act4_radial_burst.frag
// Act 4 / RELEASE — Outward expanding rings with warm orange transient flash
// Full palette: purple base + warm orange accents (#B45014). Outward only.
// TD GLSL TOP: vUV.st, out vec4 fragColor, TDOutputSwizzle(), no #version directive

uniform float uTime;        // absTime.seconds
uniform float uEnergy;      // op('audio_ref')['energy'] — ring brightness/count
uniform float uTransient;   // op('audio_ref')['transient'] — warm flash on beats
uniform float uSubBass;     // op('audio_ref')['sub_bass'] — core pulse
uniform float uBrightness;  // ctrl_scene.brightness (base 1.8)
uniform float uRingSpeed;   // ctrl_scene.ring_speed (base 0.35 — outward, Act 4)
uniform float uRingCount;   // ctrl_scene.ring_count (base 6.0)

out vec4 fragColor;

float hash(vec2 p) { return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453); }
float noise(vec2 p) {
    vec2 i=floor(p); vec2 f=fract(p); f=f*f*(3.0-2.0*f);
    return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),
               mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y);
}

void main() {
    vec2 uv = vUV.st * 2.0 - 1.0;
    float aspect = 720.0 / 1280.0;
    uv.x *= aspect;

    float r = length(uv);
    float a = atan(uv.y, uv.x);

    // Outward scroll (positive = expanding away from center)
    float scroll = uTime * uRingSpeed;

    // Ring bands — outward, so freq shrinks to give wide bands far from center
    float band = fract(r * uRingCount - scroll);

    // Sharp inner edge, soft glow trailing outer edge (direction of travel = outward)
    float ring = smoothstep(0.0, 0.06, band) * (1.0 - smoothstep(0.5, 1.0, band));
    ring = pow(ring, 1.5);

    // Radial rays — rotate slowly, add visual rhythm
    float rayFreq = 12.0;
    float ray = 0.5 + 0.5 * sin(a * rayFreq + uTime * 0.8);
    ray = pow(ray, 6.0) * 0.4;

    // Energy = more rings visible (multiplies brightness)
    float energyMod = 0.5 + uEnergy * 0.8;

    // Sub-bass core pulse: bright center on kicks
    float core = exp(-r * (3.0 - uSubBass * 1.5)) * (0.5 + uSubBass * 0.8);

    // Transient: warm orange burst from center outward
    // #B45014 = vec3(0.706, 0.314, 0.078)
    float flashFade = exp(-r * 2.5) * uTransient;
    float flashRing = exp(-abs(r - uTime * 2.0 * uTransient) * 8.0) * uTransient * 0.5;

    // COLOR — full palette: purple base + warm orange accent
    vec3 bgCol    = vec3(0.02, 0.00, 0.06);
    vec3 ringPurp = vec3(0.45, 0.08, 0.70);   // base purple ring
    vec3 ringMid  = vec3(0.65, 0.20, 0.95);   // bright purple peak
    vec3 warmOr   = vec3(0.706, 0.314, 0.078); // #B45014 warm orange accent
    vec3 coreCol  = vec3(0.80, 0.50, 1.00);   // white-purple core

    vec3 color = bgCol;
    color += mix(ringPurp, ringMid, ring) * ring * energyMod;
    color += ringPurp * ray * (1.0 - smoothstep(0.0, 0.6, r));
    color += coreCol * core;

    // Warm orange on transient — Act 4 MUST have warm accent
    color += warmOr * flashFade * 1.5;
    color += warmOr * flashRing;

    color *= uBrightness;

    // Wide vignette — Act 4 is expansive, soft edges
    float vig = 1.0 - smoothstep(0.55, 1.1, r);
    color *= vig;

    fragColor = TDOutputSwizzle(vec4(clamp(color, 0.0, 1.0), 1.0));
}
