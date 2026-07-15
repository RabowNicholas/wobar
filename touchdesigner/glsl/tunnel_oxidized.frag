// tunnel_oxidized.frag  —  WOBAR visualizer reset, the tunnel-inward spine (first piece)
//
// v3 — RAYMARCHED + ALIVE.  Adds the three things that were missing once v2 made it a real
// place: passing lamps (rhythm), volumetric haze (atmosphere), breathing walls (the place
// reacting rather than the image reacting).
//
// LINEAGE — what each version fixed, so none of it gets re-broken:
//   v1  2D polar 1/r + kaleido fold. REJECTED: read as a Milkdrop mandala. Colour ramped
//       straight off a scalar noise = no normals, no light, no surface.
//   v2  Raymarched. Real geometry, real normals, real light. Two traps found:
//        - killing kaleido() was NOT enough — angular plate seams project as straight
//          spokes from the vanishing point, i.e. the rosette rebuilt in 3D. ANY angular
//          repeat on a tube does this. All angular structure must be IRREGULAR.
//        - a pipe's wall normal is RADIAL and a camera lamp shines AXIALLY, so
//          dot(n,ld) ~ 0 everywhere: a diffuse-weighted tunnel renders BLACK no matter how
//          bright the lamp. Pipes read via proximity + grazing specular/fresnel.
//   v3  (this) lamps + haze + breathing walls.
//
// TIME — uTime is now me.time.seconds (SONG time), NOT absTime.seconds.
//   The timeline is 16458 frames = exactly the 4:34 track, so me.time.seconds IS song
//   position and runs monotonic across a full render. Beat-sync is impossible on absTime
//   (wall-clock has no relationship to the playhead). When it wraps, it wraps because the
//   song restarted — coherent. NOTE: v1 correctly used absTime *at the time*, because the
//   timeline was then 600 frames and looped every 10s, which sawtoothed the clock.
//
// Register: Act 2 / DESCENSION affinity, oxidized cool-metal grind.
// Portrait 720x1280, rgba16float. Grain + vignette live in node post.
//
// Uniforms (glslTOP VECTORS page — vec0name/vec0valuex ...; NOT the color page, which is
// vec4 colour uniforms. `par.vec` is NOT a count: reads 0, setting it is a no-op):
//   uTime       me.time.seconds                              (song time — see TIME above)
//   uSubBass    base_audio_react/null_out ['sub_bass_n']     bore + wall breathing
//   uEnergy     base_audio_react/null_out ['energy_n']       light reach (arrangement)
//   uTransient  base_audio_react/null_out ['transient_n']    specular flare (attack)
//               percentile-normalized (_n), guarded:
//                 op('/project1/base_audio_react/null_out')['x_n']
//                   if (op('...') and op('...').numChans > 0) else 0
//               — the `op(...) and` guard is required; without it the expression raises
//               AttributeError on None, in exactly the no-audio case it exists for.
//               Normalized channels go NEGATIVE below p10 by construction; the clamp()s in
//               main() absorb it, but any pow() in a TD *expression* needs max(0.0, x).
//   uDrift      ctrl_scene.Driftamt     0.60   centreline curvature (the wander)
//   uScroll     ctrl_scene.Scrollspeed  0.06   SLOW, hypnotic (0.04-0.08)
//   uMirrorAmt  ctrl_scene.Mirroramt    0.88   imperfect; never 1.0
//   uFolds      ctrl_scene.Foldcount    6.0    ring-weld frequency (repurposed twice; par
//                                              name kept so bindings survive)
//   uBrightness ctrl_scene.Brightness   1.3    exposure into the tonemap
//   uLampSecs   ctrl_scene: 60.0/Bpm*Lampbeats — SECONDS between lamps passing. Deriving
//               spacing from TIME (not distance) keeps lamps beat-locked no matter what
//               Scrollspeed is dialled to.
//   uPhase      ctrl_scene.Beatphase    0.0    seconds; nudge so lamps land on the downbeat
//   uHaze       ctrl_scene.Haze         0.50   volumetric density
//
//   BPM = 140, CONFIRMED BY NICK 2026-07-14. Do not trust auto-detection here: both
//   autocorrelation and a phase-aligned comb FAILED on this track, because the `transient`
//   channel is already lagged/filtered so its onsets are smeared. Raw autocorrelation's
//   global max was a bogus 200 BPM — that was just the monotonic decay of a smoothed
//   envelope, not a beat. Beat-sync needs the EXACT value: 1% off drifts a full beat in 40s.
//   If a future track needs tempo, ask the producer or analyse the RAW audio, not `transient`.
//
//   Lampbeats = 8 (2 bars), not 4: at 4 beats the spacing works out to ~1.03 units against
//   a tunnel radius of ~1.0, which reads as a continuous strip rather than discrete lamps
//   passing. Spacing derives from TIME so it stays beat-locked at any Scrollspeed.
//
//   Modulation sources chosen from the kekkai-2--6-17 recording (16458 frames @ 60fps).
//   sub_pressure and growl UNUSED: r=0.97 vs sub_bass, r=0.98 vs bass — duplicates.
//   `high` UNUSED: cannot separate breakdown from drop here (0.029 vs 0.033 = 1.14x) and
//   needs gain 49 (noise amplifier).

uniform float uTime;
uniform float uSubBass;
uniform float uEnergy;
uniform float uTransient;
uniform float uDrift;
uniform float uScroll;
uniform float uMirrorAmt;
uniform float uFolds;
uniform float uBrightness;
uniform float uLampSecs;
uniform float uPhase;
uniform float uHaze;

out vec4 fragColor;

// --- palette (WOBAR_TD_REFERENCE §4; desaturated psychedelic, mirror metallics) ---
const vec3 OFFBLACK_PURPLE  = vec3(0.055, 0.031, 0.075); // #0E0813 — where blacks sit
const vec3 PETROL           = vec3(0.173, 0.271, 0.329); // #2C4554 — the patina
const vec3 TARNISHED_SILVER = vec3(0.431, 0.431, 0.451); // #6E6E73
const vec3 PEWTER           = vec3(0.557, 0.557, 0.580); // #8E8E94 — bare metal
const vec3 BONE             = vec3(0.780, 0.733, 0.651); // #C7BBA6 — highlight cap, no pure white

// Lamp colour = BONE. Slightly warm neutral against the cool petrol walls, and it is the
// no-pure-white cap colour, so the lamps can never legally blow past the palette.
const vec3 LAMPCOL = BONE;

// --- utils (WOBAR_GLSL_PATTERNS) ---
float hash(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float noise(vec2 p){
    vec2 i = floor(p); vec2 f = fract(p); f = f*f*(3.0-2.0*f);
    return mix(mix(hash(i),         hash(i+vec2(1,0)), f.x),
               mix(hash(i+vec2(0,1)), hash(i+vec2(1,1)), f.x), f.y);
}
// 3 octaves: this runs ~3x per pixel for the bump gradient, so octave count is the main
// cost dial. The volumetric loop deliberately uses single-octave noise() instead.
float fbm(vec2 p){
    float v = 0.0; float a = 0.5;
    for (int i = 0; i < 3; i++){ v += a * noise(p); p *= 2.1; a *= 0.5; }
    return v;
}

float gRadius  = 1.0;   // sub-bass breathes the bore
float gSwell   = 0.0;   // sub-bass amplitude of the travelling wall swells
float gTime    = 0.0;
float gSpeed   = 0.6;
float gSpacing = 1.0;   // metres between lamps = gSpeed * uLampSecs

// THE CENTRELINE — the tunnel genuinely bends. Incommensurate rates so the path never
// retraces inside the 4:34 track. Real 3D curvature, so the wander comes with parallax.
vec2 path(float z){
    return vec2(
        sin(z * 0.140)        * 1.0 + sin(z * 0.087 + 2.1) * 0.6,
        cos(z * 0.110 + 1.7)  * 0.8 + sin(z * 0.063 + 0.4) * 0.5
    ) * uDrift;
}

// Tunnel SDF. NO noise here on purpose — the march would cost ~64 x fbm per pixel. The
// material is applied as a BUMP at the hit point instead (~30 noise evals, once).
// The swell IS in the SDF though: cheap (2 sins) and it must move the real silhouette.
float mapSmooth(vec3 p){
    float r = length(p.xy - path(p.z));
    // WALLS BREATHE — travelling swells push down the metal, driven by sub-bass. §3 asks
    // for "walls breathe with the bass"; scaling the bore radius uniformly is a BORE, not
    // breathing. In the SDF so silhouette, parallax and lamp highlights all flex with it.
    // Axial only (no angular term): an angular swell would reintroduce radial symmetry.
    float swell = (sin(p.z * 0.55 - gTime * 2.2) * 0.65
                 + sin(p.z * 0.29 + 1.3 - gTime * 1.4) * 0.35) * gSwell;
    return (gRadius + swell) - r;
}

// Lamp k, recessed into the wall. The golden angle spirals them around the bore so they
// never line up into a stripe — a fixed angle would read as a straight rail, and a
// regular angular pattern is the rosette trap again.
vec3 lampPos(float k){
    float z   = k * gSpacing + uPhase * gSpeed;
    float ang = k * 2.399963;                    // golden angle
    vec2  c   = path(z);
    return vec3(c + vec2(cos(ang), sin(ang)) * gRadius * 0.92, z);
}

// THE MATERIAL — height field on the wall. Ring welds + corrosion + pitting + grain.
// RING SEGMENTS ONLY: any *angular* repeat on a tube projects as spokes from the vanishing
// point. All angular structure here is irregular by construction.
float detail(float a, float z){
    float zi   = z * max(uFolds, 1.0) * 0.12;
    float ring = floor(zi);
    float rr   = hash(vec2(ring, 7.3));

    float fz = abs(fract(zi) - 0.5) * 2.0;
    float seamCut = smoothstep(0.86 - rr * 0.06, 0.995, fz);

    float h = 0.0;
    h += (rr - 0.5) * 0.22;         // each ring sits slightly proud or sunk — never flush
    h -= seamCut * 0.50;            // welds recessed

    // corrosion — the ONLY angular structure, irregular by construction
    float corr = fbm(vec2(a * 2.2, z * 0.8));
    h -= smoothstep(0.45, 0.85, corr) * 0.45;

    // pitting — oxidized metal is cratered, not smooth
    float pit = fbm(vec2(a * 9.0, z * 4.0) + 11.0);
    h -= smoothstep(0.55, 0.95, pit) * 0.30;

    // fine grain stretched along the axis = drawn/brushed metal (anisotropic).
    // v1's isotropic fbm is exactly what made it read as smoke.
    h += (fbm(vec2(a * 26.0, z * 2.0)) - 0.5) * 0.08;

    return h;
}

void main(){
    // ---- audio conditioning -------------------------------------------------------
    // Curve 1.2 NOT 2.5: sub_bass crest (p99/p90) here is 1.05 — compressed and sustained.
    // At 2.5 the normalized median lands at 0.043 and the bore sits shut except at drops.
    float sub = pow(clamp(uSubBass,   0.0, 1.0), 1.2);
    // energy = the arrangement axis (breakdown 0.084 vs drop 0.689 = 8.2x on this track)
    float en  = pow(clamp(uEnergy,    0.0, 1.0), 1.5);
    // transient = the only band independent of sub_bass (r=0.42); crest 1.59. Curve 2.5 is
    // correct HERE: only the peaks, not the body.
    float tr  = pow(clamp(uTransient, 0.0, 1.0), 2.5);

    gTime    = uTime;
    gRadius  = 1.0 + sub * 0.22;      // bore
    gSwell   = sub * 0.16;            // breathing amplitude
    gSpeed   = uScroll * 10.0;        // Scrollspeed 0.04-0.08 -> 0.4-0.8 units/sec
    gSpacing = gSpeed * max(uLampSecs, 0.05);

    // ---- camera on the centreline -------------------------------------------------
    float tt  = gTime * gSpeed;
    vec3 ro   = vec3(path(tt), tt);
    vec3 tgt  = vec3(path(tt + 2.0), tt + 2.0);
    vec3 fwd  = normalize(tgt - ro);
    vec3 rgt  = normalize(cross(vec3(0.0, 1.0, 0.0), fwd));
    vec3 upv  = cross(fwd, rgt);

    vec2 uv = vUV.st * 2.0 - 1.0;
    uv.x *= 720.0 / 1280.0;
    vec3 rd = normalize(uv.x * rgt + uv.y * upv + 1.5 * fwd);

    // ---- march --------------------------------------------------------------------
    float t = 0.0;
    bool hit = false;
    vec3 p = ro;
    for (int i = 0; i < 96; i++){
        p = ro + rd * t;
        float d = mapSmooth(p);
        if (d < 0.0015 * t){ hit = true; break; }
        t += d * 0.7;                 // 0.7: path curvature + swell make R-r approximate
        if (t > 60.0) break;
    }
    if (!hit) t = 60.0;

    vec3 col = vec3(0.0);

    if (hit){
        vec2 e = vec2(0.0015, 0.0);
        vec3 n = normalize(vec3(
            mapSmooth(p + e.xyy) - mapSmooth(p - e.xyy),
            mapSmooth(p + e.yxy) - mapSmooth(p - e.yxy),
            mapSmooth(p + e.yyx) - mapSmooth(p - e.yyx)));

        vec2 q = p.xy - path(p.z);
        float r = max(length(q), 0.001);

        // IMPERFECT MIRROR — bilateral, ONE axis, on the MATERIAL lookup only (geometry
        // stays a true tunnel). v1 folded 6 ways into a rosette; 88% of a mandala is still
        // a mandala. This is OBSCURA "reflection geometry": the wall's left half nearly
        // completes its right, with a seam at x=0. Never 1.0.
        float xm = mix(q.x, abs(q.x), uMirrorAmt);
        float a  = atan(q.y, xm);

        // bump — this is what makes it a surface. 0.085: at 0.035 it read as clean concrete.
        float da = 0.010;
        float dz = 0.010;
        float h0  = detail(a, p.z);
        float dHa = (detail(a + da, p.z) - h0) / (r * da);
        float dHz = (detail(a, p.z + dz) - h0) / dz;
        vec3 axis = vec3(0.0, 0.0, 1.0);
        vec3 tz = normalize(axis - n * dot(axis, n));
        vec3 ta = normalize(cross(n, tz));
        n = normalize(n - (ta * dHa + tz * dHz) * 0.085);

        // ---- material ---------------------------------------------------------------
        float ox = smoothstep(0.30, 0.72, fbm(vec2(a * 1.4, p.z * 0.5) + 5.0));
        vec3 albedo = mix(PEWTER, PETROL, ox);
        float rust = smoothstep(0.52, 0.88, fbm(vec2(a * 3.1, p.z * 1.3) + 19.0));
        albedo = mix(albedo, OFFBLACK_PURPLE * 1.6, rust * 0.75);
        albedo = mix(albedo, OFFBLACK_PURPLE, smoothstep(0.0, -0.8, h0));

        float ao = smoothstep(-0.9, 0.1, h0);
        ao = 0.35 + 0.65 * ao;

        // ---- light ------------------------------------------------------------------
        // Diffuse is a MINOR term on purpose (see the v2 note at the top: radial normal vs
        // axial light => dot ~ 0). Proximity + grazing spec/fresnel carry the read, and the
        // passing lamps rake highlights across the bump — which is what finally reveals the
        // pitting a static lamp left invisible.
        float breathLfo = 0.75 + 0.25 * sin(uTime * 0.6);
        float lightAmt  = mix(breathLfo, 0.45 + en * 1.10, step(0.001, uEnergy));

        vec3 vdir = normalize(ro - p);
        float prox = exp(-t * 0.16);

        // PASSING LAMPS — the rhythm. Spacing derives from TIME, so they stay beat-locked
        // whatever Scrollspeed is set to.
        vec3 lampAcc = vec3(0.0);
        float emis = 0.0;
        float k0 = floor((p.z - uPhase * gSpeed) / gSpacing);
        for (int i = -1; i <= 2; i++){
            vec3 lpos = lampPos(k0 + float(i));
            vec3 dl   = lpos - p;
            float dist = length(dl);
            vec3 ld   = dl / max(dist, 0.001);
            float att = 1.0 / (1.0 + 1.6 * dist * dist);
            float dif = max(dot(n, ld), 0.0);
            vec3 hv   = normalize(ld + vdir);
            float sp  = pow(max(dot(n, hv), 0.0), 48.0 + tr * 90.0);
            lampAcc += (dif * 0.9 + sp * (1.4 + tr * 2.2)) * att;
            emis    += exp(-dist * dist * 26.0);      // the housing itself
        }

        float fres = pow(1.0 - max(dot(n, vdir), 0.0), 3.0);

        col  = albedo * 0.10 * prox * ao * lightAmt;                  // soft ambient wash
        col += albedo * 0.05 * ao;                                    // floor, in palette
        col += albedo * lampAcc * ao * lightAmt * 0.85;               // the lamps
        col += mix(albedo, BONE, 0.6) * fres * prox * 0.5 * ao * lightAmt;
        col += LAMPCOL * emis * 1.6 * lightAmt;                       // lamp housings glow
        col += OFFBLACK_PURPLE * 0.10 * (1.0 - prox);                 // void fills in behind
    }

    // ---- volumetric haze ----------------------------------------------------------
    // Atmosphere. Marches the same ray accumulating lamp-lit fog, so each lamp throws a
    // visible shaft and depth reads as distance rather than as darkness. Single-octave
    // noise() here (not fbm) — this loop runs 20x per pixel and fbm would triple it.
    {
        const int VSTEPS = 20;
        float tmax = min(t, 45.0);
        float dt = tmax / float(VSTEPS);
        vec3 vol = vec3(0.0);
        for (int i = 0; i < VSTEPS; i++){
            float s = dt * (float(i) + 0.5);
            vec3 pv = ro + rd * s;
            float kk = floor((pv.z - uPhase * gSpeed) / gSpacing);
            float L = 0.0;
            for (int j = -1; j <= 1; j++){
                vec3 lpos = lampPos(kk + float(j));
                float dd = length(lpos - pv);
                L += 1.0 / (1.0 + 1.9 * dd * dd);
            }
            // drifting dust, thicker low in the bore
            float dust = 0.65 + 0.35 * noise(vec2(pv.z * 0.6 - gTime * 0.25, pv.x * 0.7));
            // Extinction 0.20 (was 0.06) and a 0.08 density scale. Lamps repeat every ~2
            // units down a 45-unit corridor, so L is roughly CONSTANT along the whole ray —
            // at 0.06 the integral came to ~4.6 and washed the frame to milk, brightest at
            // the far end, i.e. the void inverted into a glowing tube. Hard extinction keeps
            // the haze a NEAR-field effect: shafts around the close lamps, blackness beyond.
            vol += LAMPCOL * L * dust * dt * exp(-s * 0.20) * 0.08;
        }
        col += vol * uHaze;
    }

    // ---- finish -------------------------------------------------------------------
    // Soft-knee tonemap capped at BONE. v1 used min(col, BONE) which FLAT-CLIPPED whole
    // regions at drops and destroyed the material exactly when it mattered. This rolls off
    // asymptotically: highlights compress toward bone, never past it, never flat.
    col = (1.0 - exp(-col * uBrightness)) * BONE;

    // desaturation discipline (K1) — final desat + grain also in node post
    col = mix(vec3(dot(col, vec3(0.299, 0.587, 0.114))), col, 0.55);

    fragColor = TDOutputSwizzle(vec4(col, 1.0));
}
