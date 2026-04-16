// act5_portal_close.frag
// Act 5 / RETURN — Circle vignette closing inward. uRadius driven externally by timer.
// Calls back to Act 1 circle. Pure purple. Breath rhythm returns.
// TD GLSL TOP: vUV.st, out vec4 fragColor, TDOutputSwizzle(), no #version directive
//
// [VERIFY] uRadius should be driven by a Lag CHOP → timer that goes 1.0 → 0.0 over ~60s
// Example expression: op('ctrl_scene')['portal_radius']

uniform float uTime;        // absTime.seconds
uniform float uRadius;      // ctrl_scene.portal_radius (1.0 = open, 0.0 = closed)
uniform float uSubBass;     // op('audio_ref')['sub_bass'] — edge breath
uniform float uEnergy;      // op('audio_ref')['energy'] — interior brightness
uniform float uBrightness;  // ctrl_scene.brightness (base 1.5)
uniform float uBreathSpeed; // ctrl_scene.breath_speed (base 0.25, ~70 BPM — same as Act 1)

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

    // Breath LFO — same frequency as Act 1 (intentional callback)
    float breath = 0.5 + 0.5 * sin(uTime * uBreathSpeed * 6.2832);

    // Portal radius: externally controlled, with breath micro-oscillation
    float portalR = uRadius + breath * 0.015 + uSubBass * 0.008;
    portalR = clamp(portalR, 0.0, 1.1);

    // Soft iris: inside portal = visible, outside = black
    float irisSoftness = 0.03 + (1.0 - uRadius) * 0.02; // sharper as it closes
    float inside = 1.0 - smoothstep(portalR - irisSoftness, portalR + irisSoftness * 0.3, r);

    // Portal edge glow — warm purple ring at the closing boundary
    float edge = exp(-abs(r - portalR) * 20.0);
    edge += exp(-abs(r - portalR) * 6.0) * 0.3;  // wider soft glow

    // Interior: Act 1-like breath circle (callback geometry)
    float innerBreath = exp(-max(r - (0.18 + breath * 0.04 + uSubBass * 0.08), 0.0) * 5.0);
    float innerRing = exp(-abs(r - (0.40 + uEnergy * 0.08)) * 12.0) * 0.25;

    // Subtle noise in the interior (slightly less organized than Act 1 = returning, worn)
    float n = noise(uv * 3.0 + vec2(uTime * 0.15, 0.0)) * 0.08;

    // COLOR: pure purple callback palette (no warm, same family as Act 1)
    vec3 bgCol      = vec3(0.0);  // absolute black outside
    vec3 interiorBg = vec3(0.04, 0.00, 0.08);
    vec3 glowCol    = vec3(0.35, 0.04, 0.47);
    vec3 edgeCol    = vec3(0.65, 0.20, 1.00);  // bright at closing edge
    vec3 innerCol   = vec3(0.75, 0.20, 1.00);
    vec3 ringCol    = vec3(0.28, 0.00, 0.42);

    vec3 color = bgCol;
    // Fill interior
    color += interiorBg * inside;
    color += glowCol * innerBreath * inside;
    color += innerCol * innerBreath * innerBreath * inside;
    color += ringCol * innerRing * inside;
    // Edge
    color += edgeCol * edge * (0.8 + uSubBass * 0.3);
    // Noise texture inside portal
    color += vec3(0.10, 0.00, 0.18) * n * inside;

    color *= uBrightness * (1.0 + uEnergy * 0.25);

    fragColor = TDOutputSwizzle(vec4(clamp(color, 0.0, 1.0), 1.0));
}
