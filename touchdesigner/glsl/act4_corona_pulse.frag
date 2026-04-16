// act4_corona_pulse.frag
// Act 4 / RELEASE — Pulsing center corona with rotating arms, full warm palette
// Outward radial expansion, warm orange + purple, rhythm-driven.
// TD GLSL TOP: vUV.st, out vec4 fragColor, TDOutputSwizzle(), no #version directive

uniform float uTime;        // absTime.seconds
uniform float uEnergy;      // op('audio_ref')['energy'] — corona size
uniform float uTransient;   // op('audio_ref')['transient'] — arm flash
uniform float uSubBass;     // op('audio_ref')['sub_bass'] — core brightness
uniform float uGrowl;       // op('audio_ref')['growl'] — arm texture
uniform float uBrightness;  // ctrl_scene.brightness (base 1.7)
uniform float uArmCount;    // ctrl_scene.arm_count (base 8.0)
uniform float uRotSpeed;    // ctrl_scene.rot_speed (base 0.40, counterclockwise)

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

    // Rotating corona arms — counterclockwise = joyful, outward energy
    float rotA = a + uTime * uRotSpeed;

    // N-arm corona: each arm is a cosine lobe
    float arm = cos(rotA * uArmCount) * 0.5 + 0.5;
    arm = pow(arm, 4.0);  // sharpen to defined beams

    // Arm texture from growl noise
    float nAmp = 0.06 + uGrowl * 0.20;
    float armNoise = noise(uv * 3.0 + vec2(uTime * 0.5, 0.0));
    arm *= 1.0 + armNoise * nAmp * 4.0;

    // Arms fade out radially (strong near center, gone at edge)
    float armFade = exp(-r * 1.8);
    arm *= armFade;

    // Corona: pulsing halo at energy-driven radius
    float coronaR = 0.30 + uEnergy * 0.18;
    float corona = exp(-abs(r - coronaR) * 9.0);
    // Sub-bass inner core burst
    float innerCore = exp(-r * (4.0 - uSubBass * 2.5));

    // Outward scatter rings on transient
    float tRing1 = exp(-abs(r - 0.2 - uTransient * 0.3) * 12.0) * uTransient;
    float tRing2 = exp(-abs(r - 0.4 - uTransient * 0.5) * 8.0) * uTransient * 0.6;

    // FULL PALETTE — warm orange + purple (Act 4 MUST include warm accents)
    // #B45014 = vec3(0.706, 0.314, 0.078)
    vec3 bgCol     = vec3(0.01, 0.00, 0.04);
    vec3 armPurp   = vec3(0.50, 0.10, 0.75);   // purple arm base
    vec3 armWarm   = vec3(0.706, 0.314, 0.078); // #B45014 warm orange arm tips
    vec3 coronaCol = vec3(0.80, 0.55, 1.00);   // bright purple halo
    vec3 coreCol   = vec3(1.00, 0.80, 0.90);   // near-white hot center
    vec3 transCol  = vec3(0.75, 0.35, 0.10);   // warm orange on transient

    // Arm color: purple base, warm orange where arm is brightest
    vec3 armColor = mix(armPurp, armWarm, pow(arm, 2.0) * 0.7);

    vec3 color = bgCol;
    color += armColor * arm * 1.2;
    color += coronaCol * corona * (0.6 + uEnergy * 0.5);
    color += coreCol * innerCore * (0.8 + uSubBass * 0.6);
    color += transCol * (tRing1 + tRing2);

    color *= uBrightness;

    // Act 4: wide, expansive vignette
    float vig = 1.0 - smoothstep(0.6, 1.15, r);
    color *= vig;

    fragColor = TDOutputSwizzle(vec4(clamp(color, 0.0, 1.0), 1.0));
}
