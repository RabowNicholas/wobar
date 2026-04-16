// act3_grid_distort.frag
// Act 3 / CONFRONTATION — Wave-distorted grid, confrontational, cold palette only
// Transient fractures the grid. NO warm colors.
// TD GLSL TOP: vUV.st, out vec4 fragColor, TDOutputSwizzle(), no #version directive

uniform float uTime;        // absTime.seconds
uniform float uTransient;   // op('audio_ref')['transient'] — fracture amplitude
uniform float uEnergy;      // op('audio_ref')['energy'] — wave distortion intensity
uniform float uSubBass;     // op('audio_ref')['sub_bass'] — grid density pulse
uniform float uBrightness;  // ctrl_scene.brightness (base 1.2)
uniform float uGridScale;   // ctrl_scene.grid_scale (base 8.0)
uniform float uWaveAmp;     // ctrl_scene.wave_amp (base 0.15)

out vec4 fragColor;

float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1,311.7)))*43758.5453); }
float noise(vec2 p) {
    vec2 i=floor(p); vec2 f=fract(p); f=f*f*(3.0-2.0*f);
    return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),
               mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y);
}

void main() {
    vec2 uv = vUV.st * 2.0 - 1.0;
    float aspect = 720.0 / 1280.0;
    uv.x *= aspect;

    // Wave distortion: multiple overlapping sine waves (energy driven)
    float waveScale = uWaveAmp * (1.0 + uEnergy * 1.5);
    float dx = sin(uv.y * 4.2 + uTime * 1.1) * waveScale
             + sin(uv.y * 7.8 + uTime * 0.7) * waveScale * 0.4;
    float dy = sin(uv.x * 3.6 + uTime * 0.9) * waveScale
             + sin(uv.x * 9.1 + uTime * 1.3) * waveScale * 0.3;
    vec2 wuv = uv + vec2(dx, dy);

    // Transient fracture — discrete block shift
    float fracAmt = uTransient * 0.15;
    float blockRow = floor(wuv.y * 12.0);
    float blockShift = (hash(vec2(blockRow, floor(uTime * 20.0))) * 2.0 - 1.0);
    wuv.x += blockShift * fracAmt;

    // Grid: sub-bass slightly increases density (tighter grid = more confrontational)
    float gridScale = uGridScale + uSubBass * 2.0;
    vec2 grid = fract(wuv * gridScale);

    // Line width: thin lines, sharp edges
    float lineW = 0.04 + uTransient * 0.08;
    float lineX = smoothstep(0.0, lineW, grid.x) * (1.0 - smoothstep(1.0-lineW, 1.0, grid.x));
    float lineY = smoothstep(0.0, lineW, grid.y) * (1.0 - smoothstep(1.0-lineW, 1.0, grid.y));
    float gridMask = 1.0 - lineX * lineY;  // 1 = on a line, 0 = inside cell

    // Cell interior: subtle FBM noise for texture
    float cellNoise = noise(wuv * gridScale * 0.5 + vec2(uTime * 0.1));

    // COLD PALETTE — no warm colors
    vec3 lineCol  = vec3(0.20, 0.30, 0.60);   // cold blue grid lines
    vec3 cellCol  = vec3(0.01, 0.01, 0.06);   // almost-black cell interiors
    vec3 noiseCol = vec3(0.04, 0.05, 0.14);   // subtle cold variation
    vec3 fractCol = vec3(0.50, 0.65, 1.00);   // icy blue fracture flash

    vec3 color = mix(cellCol + noiseCol * cellNoise * 0.5, lineCol, gridMask);
    // Fracture flash on transient — cold white-blue
    color += fractCol * uTransient * 0.5 * gridMask;

    // Energy brightens lines
    color *= uBrightness * (1.0 + uEnergy * 0.4);

    // Hard vignette — claustrophobic crop
    float r = length(uv);
    float vig = 1.0 - smoothstep(0.25, 0.85, r);
    color *= vig;

    fragColor = TDOutputSwizzle(vec4(clamp(color, 0.0, 1.0), 1.0));
}
