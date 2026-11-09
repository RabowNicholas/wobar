"""Build (or rebuild) the `LaneGround` material: one blended ground for the lane and forest floor.

Run inside Blender:  ns = {}; exec(open(PATH).read(), ns); ns["build"]()
Tune by passing overrides, e.g. ns["build"](needle_value=0.5, moss_lo=0.40).

Needs the three Poly Haven texture materials already imported (see SETS) and the mesh
attributes written by the LaneSweep / ForestFloor node groups: `UVMap` (metres) and `lat`
(metres from the lane centre; on the forest floor, distance from the spine).

Layers, bottom to top:
  needle litter (flat ground)  ->  bare soil where the surface is steep  ->  moss patches
  ->  the path: mud with patches of needle litter.
"""
import bpy

SETS = {"mud": ("mud_forest", 2.35), "needle": ("forrest_ground_03", 2.0), "moss": ("forest_leaves_02", 3.0)}

DEFAULTS = dict(
    needle_value=0.42,      # needle litter is pale in the scan; pull it down
    soil_value=0.5,         # bare soil on steep banks (uses the mud texture)
    moss_value=0.38,        # the 'moss' scan is ochre leaf litter with moss in it; it lightens banks unless pulled down
    moss_hue=0.57, moss_sat=0.9,    # 0.5 = unchanged; above pushes the ochre toward green
    steep_lo=0.80, steep_hi=0.93,   # normal.z below lo = fully soil, above hi = fully needles
    moss_lo=0.36, moss_hi=0.52,     # noise thresholds; lower = more moss
    moss_scale=0.28,
    litter_scale=3.5, litter_lo=0.56, litter_hi=0.72, litter_max=0.5,
    path_half=1.0, path_soft=2.1, edge_jitter=0.9,
    path_wet=0.78,          # roughness multiplier on the path
    normal_strength=1.3,
    # after rain: everything is darker and glossier; the ruts most of all
    rain_rough=1.3, rain_value=0.3,   # wetness now comes from the coat, not from lowering base roughness
    coat=0.03, coat_rough=0.35,   # more than ~0.15 and backlit moonlit ground blows out to white, like snow
    rut_rough=0.85, rut_value=0.55,   # was 0.3: once ruts were filled in stretches (RutFill) the exposed glossy mud glittered; the water carries the gloss
    ridge_moss=0.85,        # how mossy the centre ridge between the ruts is
    edge_litter=0.55,       # extra litter gathered along the path edges
    # relief: the scans' height maps drive the blends, a bump, cavity shading and where water sits
    second_scale=0.77,      # the anti-tiling second sample; 0.43 enlarged the scan 2.3x and blurred it
    height_blend=0.8,       # how strongly height decides which layer wins (0 = soft noise blends)
    blend_soft=0.12,        # edge softness of a height blend
    bump_distance=0.035,    # metres of relief the height map stands for
    cavity_value=0.5,       # colour multiplier in the deepest hollows
    hollow_rough=0.55,      # roughness multiplier in hollows: water sits low
    # blotchiness: wet soil is never one colour or one sheen
    saturation=1.1,
    # the deep walls of ABGRUND: near-vertical earth. The lane's UVs are laid out before the walls are
    # raised, so the scans stretch 2-3x up the wall; walls take a box-projected sample instead.
    wall=1.0, wall_from=990.0, wall_value=0.42, wall_hue=0.52, wall_sat=0.95,
    wall_nz=(0.5, 0.3),     # normal.z above the first value: ground; below the second: wall
    wall_bump=0.06,
    spec_level=0.06,        # Principled 'Specular IOR Level'; most of what the moon shows on wet ground is sheen, not colour
    damp_scale=0.22,        # soaked / drained patches, ~4 m
    damp_dark=0.68, dry_light=1.15,     # value multiplier where soaked / where drained
    damp_rough=0.7, dry_rough=1.2,
    rot=0.45, rot_colour=(0.085, 0.040, 0.018),      # rust-brown where litter rots
    algae=0.4, algae_colour=(0.020, 0.040, 0.014),   # green film along the bank feet
)


def _maps(matname):
    out = {}
    for n in bpy.data.materials[matname].node_tree.nodes:
        if n.type == 'TEX_IMAGE' and n.image:
            nm = n.image.name.lower()
            key = ('diff' if 'diff' in nm else 'rough' if 'rough' in nm else 'nor' if 'nor' in nm
                   else 'disp' if 'disp' in nm else None)
            if key:
                out[key] = n.image
    return out


def build(**overrides):
    p = dict(DEFAULTS, **overrides)
    imgs = {k: _maps(v[0]) for k, v in SETS.items()}
    mat = bpy.data.materials.get("LaneGround") or bpy.data.materials.new("LaneGround")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    N, L = nt.nodes, nt.links

    def M(op, a, b=None):
        n = N.new('ShaderNodeMath')
        n.operation = op
        for i, v in enumerate((a, b)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                L.new(v, n.inputs[i])
        return n.outputs[0]

    def ramp(v, a, b, lo=0.0, hi=1.0):
        n = N.new('ShaderNodeMapRange')
        n.interpolation_type = 'SMOOTHSTEP'
        L.new(v, n.inputs['Value'])
        n.inputs['From Min'].default_value = a
        n.inputs['From Max'].default_value = b
        n.inputs['To Min'].default_value = lo
        n.inputs['To Max'].default_value = hi
        return n.outputs['Result']

    def noise(scale, detail=2.0, vec=None):
        n = N.new('ShaderNodeTexNoise')
        n.inputs['Scale'].default_value = scale
        n.inputs['Detail'].default_value = detail
        if vec is not None:
            L.new(vec, n.inputs['Vector'])
        return n.outputs[0]

    def mix(kind, fac, a, b):
        n = N.new('ShaderNodeMix')
        n.data_type = kind
        ia, ib, o = {'RGBA': (6, 7, 2), 'FLOAT': (2, 3, 0)}[kind]
        if isinstance(fac, (int, float)):
            n.inputs[0].default_value = fac
        else:
            L.new(fac, n.inputs[0])
        L.new(a, n.inputs[ia])
        L.new(b, n.inputs[ib])
        return n.outputs[o]

    def value(col, v, hue=0.5, sat=1.0):
        n = N.new('ShaderNodeHueSaturation')
        L.new(col, n.inputs['Color'])
        n.inputs['Value'].default_value = v
        n.inputs['Hue'].default_value = hue
        n.inputs['Saturation'].default_value = sat
        return n.outputs['Color']

    uv = N.new('ShaderNodeAttribute')
    uv.attribute_name = "UVMap"
    geo = N.new('ShaderNodeNewGeometry')
    P = geo.outputs['Position']
    nz = N.new('ShaderNodeSeparateXYZ')
    L.new(geo.outputs['Normal'], nz.inputs[0])
    lat_n = N.new('ShaderNodeAttribute')
    lat_n.attribute_name = "lat"
    alat = M('ABSOLUTE', lat_n.outputs['Fac'])
    big = noise(0.035, 2.0, P)   # ~30 m: picks between the two tiling samples, drives value drift
    rut_n = N.new('ShaderNodeAttribute')     # 0..1, written by LaneSweep; 0 on meshes without it
    rut_n.attribute_name = "rut"
    rut = rut_n.outputs['Fac']
    ridge_n = N.new('ShaderNodeAttribute')
    ridge_n.attribute_name = "ridge"
    ridge = ridge_n.outputs['Fac']

    MAPS = ('diff', 'rough', 'nor', 'disp')

    def sample(key):
        real = SETS[key][1]
        res = []
        for scale, rot, loc in ((1.0 / real, 0.0, (0, 0, 0)), (p['second_scale'] / real, 0.65, (0.31, 0.17, 0))):
            mp = N.new('ShaderNodeMapping')
            mp.vector_type = 'POINT'
            mp.inputs['Scale'].default_value = (scale, scale, scale)
            mp.inputs['Rotation'].default_value = (0, 0, rot)
            mp.inputs['Location'].default_value = loc
            L.new(uv.outputs['Vector'], mp.inputs['Vector'])
            o = {}
            for m in MAPS:
                t = N.new('ShaderNodeTexImage')
                t.image = imgs[key][m]
                if m != 'diff':
                    t.image.colorspace_settings.name = 'Non-Color'
                L.new(mp.outputs['Vector'], t.inputs['Vector'])
                o[m] = t.outputs['Color']
            res.append(o)
        f = ramp(big, 0.42, 0.58)
        return {m: mix('RGBA', f, res[0][m], res[1][m]) for m in MAPS}

    mud, needle, moss = sample("mud"), sample("needle"), sample("moss")
    needle_d = dict(needle, diff=value(needle['diff'], p['needle_value']))
    soil = dict(mud, diff=value(mud['diff'], p['soil_value']))
    moss_d = dict(moss, diff=value(moss['diff'], p['moss_value'], p['moss_hue'], p['moss_sat']))

    jitter = M('MULTIPLY', M('SUBTRACT', noise(1.1, 3.0, P), 0.5), p['edge_jitter'])
    path_fac = ramp(M('ADD', alat, jitter), p['path_half'], p['path_soft'], 1.0, 0.0)
    litter_fac = M('MULTIPLY', ramp(noise(p['litter_scale'], 4.0, P), p['litter_lo'], p['litter_hi']), p['litter_max'])
    edge_band = M('MULTIPLY', M('MULTIPLY', ramp(alat, 0.95, 1.3), ramp(noise(0.8, 2.0, P), 0.35, 0.6)), p['edge_litter'])
    litter_fac = M('MAXIMUM', litter_fac, edge_band)
    ridge_fac = M('MULTIPLY', M('MULTIPLY', ridge, ramp(noise(0.6, 3.0, P), 0.3, 0.55)), p['ridge_moss'])
    steep_fac = ramp(M('ADD', nz.outputs['Z'], M('MULTIPLY', M('SUBTRACT', noise(0.7, 3.0, P), 0.5), 0.12)),
                     p['steep_lo'], p['steep_hi'], 1.0, 0.0)
    moss_bank = M('MULTIPLY', ramp(alat, 1.2, 2.2), ramp(alat, 3.2, 6.0, 1.0, 0.35))
    moss_fac = M('MULTIPLY', ramp(noise(p['moss_scale'], 3.0, P), p['moss_lo'], p['moss_hi']), moss_bank)

    def hblend(fac, ha, hb):
        # Height blend: where two layers meet, the one standing higher wins, so edges follow
        # the relief of the scans (needles lying on mud, moss in the hollows) and not a soft noise.
        k = p['height_blend']
        v = M('ADD', M('SUBTRACT', M('MULTIPLY', fac, 1.0 + 2.0 * k), k), M('MULTIPLY', M('SUBTRACT', hb, ha), k))
        return ramp(v, 0.5 - p['blend_soft'], 0.5 + p['blend_soft'])

    f_steep = hblend(steep_fac, needle['disp'], mud['disp'])
    h_g = mix('FLOAT', f_steep, needle['disp'], mud['disp'])
    f_moss = hblend(moss_fac, h_g, moss['disp'])
    h_g = mix('FLOAT', f_moss, h_g, moss['disp'])
    f_litter = hblend(litter_fac, mud['disp'], needle['disp'])
    h_p = mix('FLOAT', f_litter, mud['disp'], needle['disp'])
    f_ridge = hblend(ridge_fac, h_p, moss['disp'])
    h_p = mix('FLOAT', f_ridge, h_p, moss['disp'])
    f_path = hblend(path_fac, h_g, h_p)
    height = mix('FLOAT', f_path, h_g, h_p)

    def layer(m):
        g = mix('RGBA', f_steep, needle_d[m], soil[m])
        g = mix('RGBA', f_moss, g, moss_d[m])
        pth = mix('RGBA', f_litter, mud[m], needle_d[m])
        pth = mix('RGBA', f_ridge, pth, moss_d[m])
        return mix('RGBA', f_path, g, pth)

    col, rough, nor = layer('diff'), layer('rough'), layer('nor')

    def tint(fac, base, colour):
        c = N.new('ShaderNodeRGB')
        c.outputs[0].default_value = (*colour, 1.0)
        return mix('RGBA', fac, base, c.outputs[0])

    damp = ramp(M('ADD', M('MULTIPLY', noise(p['damp_scale'], 3.0, P), 0.75), M('MULTIPLY', noise(1.3, 2.0, P), 0.25)),
                0.38, 0.62)
    rot_fac = M('MULTIPLY', ramp(noise(1.7, 3.0, P), 0.5, 0.68), p['rot'])
    algae_fac = M('MULTIPLY', M('MULTIPLY', ramp(alat, 0.9, 1.4), ramp(alat, 2.0, 3.0, 1.0, 0.0)),
                  M('MULTIPLY', ramp(noise(0.9, 2.0, P), 0.4, 0.62), p['algae']))
    col = tint(algae_fac, tint(rot_fac, col, p['rot_colour']), p['algae_colour'])

    # wall layer: box projection in object space, so a 9 m wall shows the scan at its real size
    tc = N.new('ShaderNodeTexCoord')
    wmp = N.new('ShaderNodeMapping')
    ws = 1.0 / SETS['mud'][1]
    wmp.inputs['Scale'].default_value = (ws, ws, ws)
    L.new(tc.outputs['Object'], wmp.inputs['Vector'])
    wall_t = {}
    for m in ('diff', 'rough', 'disp'):
        tx = N.new('ShaderNodeTexImage')
        tx.image = imgs['mud'][m]
        tx.projection = 'BOX'
        tx.projection_blend = 0.3
        L.new(wmp.outputs['Vector'], tx.inputs['Vector'])
        wall_t[m] = tx.outputs['Color']
    wal = N.new('ShaderNodeAttribute')
    wal.attribute_name = "along"
    wall_fac = M('MULTIPLY', M('MULTIPLY', ramp(nz.outputs['Z'], p['wall_nz'][1], p['wall_nz'][0], 1.0, 0.0),
                                ramp(wal.outputs['Fac'], p['wall_from'] - 10.0, p['wall_from'])), p['wall'])
    col = mix('RGBA', wall_fac, col, value(wall_t['diff'], p['wall_value'], p['wall_hue'], p['wall_sat']))
    rough = mix('RGBA', wall_fac, rough, wall_t['rough'])
    hsv = N.new('ShaderNodeHueSaturation')
    L.new(col, hsv.inputs['Color'])
    wet_val = M('MULTIPLY', p['rain_value'], ramp(rut, 0.15, 0.7, 1.0, p['rut_value']))
    cavity = ramp(height, 0.25, 0.6, p['cavity_value'], 1.0)
    blotch = ramp(damp, 0.0, 1.0, p['dry_light'], p['damp_dark'])
    L.new(M('MULTIPLY', M('MULTIPLY', M('MULTIPLY', ramp(big, 0.3, 0.7, 0.78, 1.08), wet_val), cavity), blotch),
          hsv.inputs['Value'])
    hsv.inputs['Saturation'].default_value = p['saturation']
    rgh = N.new('ShaderNodeSeparateColor')
    L.new(rough, rgh.inputs[0])
    wet = mix('FLOAT', path_fac, rgh.outputs[0], M('MULTIPLY', rgh.outputs[0], p['path_wet']))
    wet = M('MULTIPLY', wet, M('MULTIPLY', p['rain_rough'], ramp(rut, 0.15, 0.7, 1.0, p['rut_rough'] / p['rain_rough'])))
    wet = M('MULTIPLY', wet, ramp(height, 0.2, 0.5, p['hollow_rough'], 1.0))
    wet = M('MULTIPLY', wet, ramp(damp, 0.0, 1.0, p['dry_rough'], p['damp_rough']))
    nm = N.new('ShaderNodeNormalMap')
    nm.uv_map = "UVMap"
    nm.inputs['Strength'].default_value = p['normal_strength']
    L.new(nor, nm.inputs['Color'])
    bsdf = N.new('ShaderNodeBsdfPrincipled')
    # A film of water: a smooth clear coat over the rough ground. Its normal is left unconnected
    # on purpose, so the sheen follows the surface shape, not the fine normal map (which glitters).
    # the film of water: none on raised, drained ground, most in soaked hollows (never above ~1.5x coat)
    L.new(M('MULTIPLY', M('MULTIPLY', p['coat'], ramp(damp, 0.0, 1.0, 0.15, 1.5)), ramp(height, 0.3, 0.6, 1.0, 0.2)),
          bsdf.inputs['Coat Weight'])
    bsdf.inputs['Coat Roughness'].default_value = p['coat_rough']
    bsdf.inputs['Specular IOR Level'].default_value = p['spec_level']
    out = N.new('ShaderNodeOutputMaterial')
    L.new(hsv.outputs['Color'], bsdf.inputs['Base Color'])
    L.new(wet, bsdf.inputs['Roughness'])
    bump = N.new('ShaderNodeBump')
    bump.name = "GroundRelief"
    bump.inputs['Strength'].default_value = 1.0
    bump.inputs['Distance'].default_value = p['bump_distance']
    L.new(height, bump.inputs['Height'])
    wb = N.new('ShaderNodeBump')
    wb.inputs['Distance'].default_value = p['wall_bump']
    L.new(wall_t['disp'], wb.inputs['Height'])
    nmix = N.new('ShaderNodeMix')
    nmix.data_type = 'VECTOR'
    L.new(wall_fac, nmix.inputs[0])
    L.new(nm.outputs['Normal'], nmix.inputs[4])
    L.new(wb.outputs['Normal'], nmix.inputs[5])
    L.new(nmix.outputs[1], bump.inputs['Normal'])
    L.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    L.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    mat.use_fake_user = True
    return mat
