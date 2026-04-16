// act5_ember_settle.frag
// Act 5 / RETURN — Drifting particle embers settling downward. Pure purple. Very slow.
// No new visual concepts — uses only Act 1/2 visual language (circles, glow).
// TD GLSL TOP: vUV.st, out vec4 fragColor, TDOutputSwizzle(), no #version directive

uniform float uTime;        // absTime.seconds
uniform float uSubBass;     // op('audio_ref')['sub_bass'] — ember lift on sub hits
uniform float uEnergy;      // op('audio_ref')['energy'] — ambient glow
uniform float uBrightness;  // ctrl_scene.brightness (base 1.2 — dimmer than Act 4)
uniform float uDriftSpeed;  // ctrl_scene.drift_speed (base 0.04 — very slow settle)
uniform float uEmberCount;  // ctrl_scene.ember_count (base 12.0)

out vec4 fragColor;

float hash(float n) { return fract(sin(n) * 43758.5453); }
float hash2(vec2 p) { return fract(sin(dot(p, vec2(127.1,311.7)))*43758.5453); }
float noise(vec2 p) {
    vec2 i=floor(p); vec2 f=fract(p); f=f*f*(3.0-2.0*f);
    return mix(mix(hash2(i),hash2(i+vec2(1,0)),f.x),
               mix(hash2(i+vec2(0,1)),hash2(i+vec2(1,1)),f.x),f.y);
}

// Single ember: returns brightness at uv given ember's world position
float ember(vec2 uv, vec2 pos, float size) {
    float d = length(uv - pos);
    return exp(-d * d / (size * size)) * smoothstep(size * 2.0, 0.0, d);
}

void main() {
    vec2 uv = vUV.st * 2.0 - 1.0;
    float aspect = 720.0 / 1280.0;
    uv.x *= aspect;

    float totalGlow = 0.0;
    float n = uEmberCount;

    for (float i = 0.0; i < 16.0; i++) {
        if (i >= n) break;

        // Each ember has unique stable identity
        float seed = i * 13.7 + 1.0;
        float startX  = (hash(seed + 0.1) * 2.0 - 1.0) * 0.7;
        float startY  = (hash(seed + 0.2) * 2.0 - 1.0) * 0.6;
        float speed   = uDriftSpeed * (0.5 + hash(seed + 0.3) * 1.0);
        float drift   = (hash(seed + 0.4) - 0.5) * 0.08; // sideways drift
        float size    = 0.025 + hash(seed + 0.5) * 0.030;
        float phase   = hash(seed + 0.6) * 6.28318; // timing offset

        // Settling downward (y decreases over time = falling)
        // Sub-bass creates brief upward lift
        float lift = uSubBass * 0.12 * sin(phase + uTime * 2.0) * exp(-uTime * 0.1);
        float t = uTime * speed;

        // Ember position: drifts sideways, settles down
        float px = startX + sin(t * 0.7 + phase) * 0.06 + drift * t;
        float py = startY - t * 0.8 + lift;  // downward drift, slow

        // Wrap vertically — embers respawn from top
        py = mod(py + 1.2, 2.4) - 1.2;

        // Fade near bottom (settling = disappearing)
        float settleAlpha = smoothstep(-1.1, -0.3, py);
        // Also fade with age in current cycle
        float cycleAlpha = smoothstep(0.0, 0.3, settleAlpha);

        totalGlow += ember(uv, vec2(px, py), size) * cycleAlpha;
    }

    // Ambient noise field — very faint, like atmospheric haze
    float ambNoise = noise(uv * 2.5 + vec2(uTime * 0.02, 0.0)) * 0.06;
    ambNoise *= (1.0 + uEnergy * 0.4);

    // Pure purple palette — Act 5, no new language
    vec3 bgCol    = vec3(0.02, 0.00, 0.05);
    vec3 emberCol = vec3(0.60, 0.15, 0.90);  // bright purple ember
    vec3 glowCol  = vec3(0.28, 0.03, 0.45);  // softer purple glow halo
    vec3 ambCol   = vec3(0.08, 0.00, 0.14);  // faint ambient fill

    vec3 color = bgCol;
    color += emberCol * pow(clamp(totalGlow, 0.0, 1.0), 1.5);
    color += glowCol  * clamp(totalGlow, 0.0, 1.0) * 0.5;
    color += ambCol   * ambNoise;

    color *= uBrightness * (1.0 + uEnergy * 0.20);

    // Very soft vignette — Act 5 is open, not claustrophobic
    float r = length(uv);
    float vig = 1.0 - smoothstep(0.70, 1.20, r);
    color *= vig;

    fragColor = TDOutputSwizzle(vec4(clamp(color, 0.0, 1.0), 1.0));
}
