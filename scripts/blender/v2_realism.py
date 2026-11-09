"""v2 realism pass (2026-10-20, overnight, in hohlweg_3_realism.blend only). Nick: "scan through everything and make sure
it all looks realistic." One function per element; every node is named V2R_*, so build() can run again.

    ns = {}; exec(open(PATH).read(), ns); ns["build"]()          # or ns["walls"]() etc. one at a time
"""
import bpy

GROUND = "LaneGround"


def _node(nt, kind, name, x=0, y=0):
    n = nt.nodes.new(kind); n.name = n.label = "V2R_" + name; n.location = (x, y)
    return n


def _math(nt, op, a, b, name, c=None):
    n = _node(nt, "ShaderNodeMath", name); n.operation = op
    for i, v in enumerate((a, b, c)):
        if v is None: continue
        if isinstance(v, (int, float)): n.inputs[i].default_value = v
        else: nt.links.new(v, n.inputs[i])
    return n.outputs[0]


def _maprange(nt, v, fmin, fmax, tmin, tmax, name):
    n = _node(nt, "ShaderNodeMapRange", name); n.clamp = True
    n.inputs["From Min"].default_value, n.inputs["From Max"].default_value = fmin, fmax
    n.inputs["To Min"].default_value, n.inputs["To Max"].default_value = tmin, tmax
    nt.links.new(v, n.inputs["Value"])
    return n.outputs["Result"]


def _noise(nt, vec, scale, detail, name, rough=0.55):
    n = _node(nt, "ShaderNodeTexNoise", name); n.inputs["Scale"].default_value = scale
    n.inputs["Detail"].default_value = detail; n.inputs["Roughness"].default_value = rough
    nt.links.new(vec, n.inputs["Vector"])
    return n.outputs["Fac"]


def _unhook(nt, prefix, restore):
    """Remove nodes named prefix*; restore = [(socket, node_name, input_index)] re-feeds a socket from what fed that
    node's input before removal."""
    for sock, nn, idx in restore:
        n = nt.nodes.get(nn)
        if n and n.inputs[idx].is_linked: nt.links.new(n.inputs[idx].links[0].from_socket, sock)
    for n in [n for n in nt.nodes if n.name.startswith(prefix)]: nt.nodes.remove(n)


# ---------------------------------------------------------------- walls
WALL = dict(steep=(0.42, 0.25),        # |normal.z| from -> to: 0 below ~65 deg, 1 from ~75 deg
            loam=(0.055, 0.038, 0.024), loam_dark=(0.02, 0.014, 0.009), moss=(0.016, 0.026, 0.008),
            groove_scale=(3.0, 3.0, 0.15), groove_amt=0.5, strata_scale=2.2, moss_share=0.34, rough=0.7,
            stain_scale=(14.0, 14.0, 0.07))


def walls():
    """Steep faces of the lane (sunken-lane walls, banks over ~65 deg) carried the leaf/needle floor texture - leaves
    lying on a vertical face. Replace them with bare loam: vertical erosion grooves, faint strata, moss patches."""
    m = bpy.data.materials[GROUND]; nt = m.node_tree; N, L = nt.nodes, nt.links
    bsdf = next(n for n in N if n.bl_idname == "ShaderNodeBsdfPrincipled")
    _unhook(nt, "V2R_Wall", [(bsdf.inputs["Base Color"], "V2R_WallColorMix", 6),
                             (bsdf.inputs["Roughness"], "V2R_WallRoughMix", 2),
                             (N["GroundRelief"].inputs["Normal"], "V2R_WallBump", "Normal")])
    geo = _node(nt, "ShaderNodeNewGeometry", "WallGeo", -2400, -1600)
    nz = _node(nt, "ShaderNodeSeparateXYZ", "WallNz"); L.new(geo.outputs["Normal"], nz.inputs[0])
    absz = _math(nt, "ABSOLUTE", nz.outputs["Z"], None, "WallAbsZ")
    mask = _maprange(nt, absz, WALL["steep"][0], WALL["steep"][1], 0, 1, "WallMaskN")
    ws = _node(nt, "ShaderNodeAttribute", "WallSteepAttr"); ws.attribute_name = "wsteep"     # pre-relief, LaneView only
    mask = _math(nt, "MAXIMUM", mask, ws.outputs["Fac"], "WallMask")
    pos = geo.outputs["Position"]
    sv = _node(nt, "ShaderNodeVectorMath", "WallGrooveVec"); sv.operation = "MULTIPLY"
    sv.inputs[1].default_value = WALL["groove_scale"]; L.new(pos, sv.inputs[0])
    groove = _noise(nt, sv.outputs[0], 1.0, 4, "WallGroove", rough=0.6)                 # long vertical runnels
    zonly = _node(nt, "ShaderNodeVectorMath", "WallStrataVec"); zonly.operation = "MULTIPLY"
    zonly.inputs[1].default_value = (0.08, 0.08, 1.0); L.new(pos, zonly.inputs[0])
    strata = _noise(nt, zonly.outputs[0], WALL["strata_scale"], 3, "WallStrata")       # horizontal layering
    blot = _noise(nt, pos, 0.35, 3, "WallBlot")                                           # large-scale wet/dry blotches
    mossn = _noise(nt, pos, 0.7, 6, "WallMossNoise", rough=0.7)
    mossm = _maprange(nt, mossn, 1 - WALL["moss_share"] - 0.04, 1 - WALL["moss_share"] + 0.06, 0, 1, "WallMossMask")
    # loam colour: light/dark loam by strata and blotches, darkened in the grooves
    tone = _math(nt, "MULTIPLY_ADD", strata, 0.6, "WallTone", c=_math(nt, "MULTIPLY", blot, 0.7, "WallBlotW"))
    tone = _maprange(nt, tone, 0.55, 0.95, 0, 1, "WallToneR")
    loam = _node(nt, "ShaderNodeMix", "WallLoam"); loam.data_type = "RGBA"
    loam.inputs[6].default_value = WALL["loam_dark"] + (1,); loam.inputs[7].default_value = WALL["loam"] + (1,)
    L.new(tone, loam.inputs[0])
    gdark = _maprange(nt, groove, 0.35, 0.65, 1 - WALL["groove_amt"], 1.0, "WallGrooveDark")
    gmul = _node(nt, "ShaderNodeMix", "WallGrooveMul"); gmul.data_type = "RGBA"; gmul.blend_type = "MULTIPLY"
    gmul.inputs[0].default_value = 1; L.new(loam.outputs[2], gmul.inputs[6])
    gc = _node(nt, "ShaderNodeCombineColor", "WallGrooveC")
    for i in range(3): L.new(gdark, gc.inputs[i])
    L.new(gc.outputs[0], gmul.inputs[7])
    stv = _node(nt, "ShaderNodeVectorMath", "WallStainVec"); stv.operation = "MULTIPLY"
    stv.inputs[1].default_value = WALL["stain_scale"]; L.new(pos, stv.inputs[0])
    stain = _maprange(nt, _noise(nt, stv.outputs[0], 1.0, 2, "WallStainNoise"), 0.58, 0.68, 0, 0.55, "WallStain")
    smul = _node(nt, "ShaderNodeMix", "WallStainMul"); smul.data_type = "RGBA"
    L.new(stain, smul.inputs[0]); L.new(gmul.outputs[2], smul.inputs[6]); smul.inputs[7].default_value = WALL["loam_dark"] + (1,)
    moss = _node(nt, "ShaderNodeMix", "WallMossMix"); moss.data_type = "RGBA"
    L.new(mossm, moss.inputs[0]); L.new(smul.outputs[2], moss.inputs[6]); moss.inputs[7].default_value = WALL["moss"] + (1,)
    # into the BSDF, after everything the floor already does (damp etc.)
    cm = _node(nt, "ShaderNodeMix", "WallColorMix"); cm.data_type = "RGBA"
    L.new(mask, cm.inputs[0]); L.new(bsdf.inputs["Base Color"].links[0].from_socket, cm.inputs[6])
    L.new(moss.outputs[2], cm.inputs[7]); L.new(cm.outputs[2], bsdf.inputs["Base Color"])
    rm = _node(nt, "ShaderNodeMix", "WallRoughMix"); rm.data_type = "FLOAT"
    L.new(mask, rm.inputs[0]); rm.inputs[3].default_value = WALL["rough"]
    L.new(bsdf.inputs["Roughness"].links[0].from_socket, rm.inputs[2]); L.new(rm.outputs[0], bsdf.inputs["Roughness"])
    # relief: the grooves and strata cut into the face
    bump = _node(nt, "ShaderNodeBump", "WallBump"); bump.inputs["Distance"].default_value = 0.09
    h = _math(nt, "MULTIPLY_ADD", groove, 0.8, "WallHeight", c=_math(nt, "MULTIPLY", strata, 0.3, "WallStrataH"))
    L.new(h, bump.inputs["Height"]); L.new(mask, bump.inputs["Strength"])
    gr = N["GroundRelief"]; L.new(gr.inputs["Normal"].links[0].from_socket, bump.inputs["Normal"])
    L.new(bump.outputs["Normal"], gr.inputs["Normal"])


WALL_RELIEF = dict(amp=0.38, scale=0.3, fine_amp=0.06, fine_scale=1.6, ledge_amp=0.14, ledge_scale=1.1)   # metres along the normal; noise scales


def wall_relief():
    """The walls were a perfect sweep. Push steep faces in and out along their normal (bulges, hollows, slumps), in
    the rendered window copy only (LaneView), so scatter, water and camera clearance built on `Lane` are untouched."""
    g = bpy.data.node_groups["ViewWindow_Lane"]; N, L = g.nodes, g.links
    out = next(n for n in N if n.bl_idname == "NodeGroupOutput")
    first = N.get("V2R_WallStoreSteep") or N.get("V2R_WallRelief")          # head of the chain from an earlier run
    if first: L.new(first.inputs["Geometry"].links[0].from_socket, out.inputs[0])
    for n in [n for n in N if n.name.startswith("V2R_")]: N.remove(n)
    last = out.inputs[0].links[0].from_socket
    nrm = _node(g, "GeometryNodeInputNormal", "WallN"); pos = _node(g, "GeometryNodeInputPosition", "WallP")
    sep = _node(g, "ShaderNodeSeparateXYZ", "WallNz"); L.new(nrm.outputs[0], sep.inputs[0])
    absz = _math(g, "ABSOLUTE", sep.outputs["Z"], None, "WallAbsZ")
    mask = _maprange(g, absz, 0.5, 0.3, 0, 1, "WallMask")
    # none at the wall foot, where plants and moss sit on the original surface (prof_h: 0 floor .. ~4 rim)
    ph = _node(g, "GeometryNodeInputNamedAttribute", "WallPH"); ph.data_type = "FLOAT"; ph.inputs["Name"].default_value = "prof_h"
    mask = _math(g, "MULTIPLY", mask, _maprange(g, ph.outputs[0], 0.5, 1.2, 0, 1, "WallFoot"), "WallMaskFoot")
    sq = _node(g, "ShaderNodeVectorMath", "WallSquash"); sq.operation = "MULTIPLY"     # slumps longer than tall
    sq.inputs[1].default_value = (1.0, 1.0, 1.6); L.new(pos.outputs[0], sq.inputs[0])
    big = _noise(g, sq.outputs[0], WALL_RELIEF["scale"], 2, "WallBig")
    fine = _noise(g, pos.outputs[0], WALL_RELIEF["fine_scale"], 1, "WallFine")
    d = _math(g, "MULTIPLY_ADD", _math(g, "SUBTRACT", big, 0.5, "WallBigC"), 2 * WALL_RELIEF["amp"], "WallD",
              c=_math(g, "MULTIPLY", _math(g, "SUBTRACT", fine, 0.5, "WallFineC"), 2 * WALL_RELIEF["fine_amp"], "WallFineD"))
    zv = _node(g, "ShaderNodeVectorMath", "WallLedgeVec"); zv.operation = "MULTIPLY"      # layers: ridges along the wall
    zv.inputs[1].default_value = (0.06, 0.06, 1.0); L.new(pos.outputs[0], zv.inputs[0])
    ledge = _noise(g, zv.outputs[0], WALL_RELIEF["ledge_scale"], 2, "WallLedge")
    d = _math(g, "MULTIPLY_ADD", _math(g, "SUBTRACT", ledge, 0.5, "WallLedgeC"), 2 * WALL_RELIEF["ledge_amp"], "WallD2", c=d)
    # inward only: never push the face out past where it was, or the hanging roots (and the pluck beads on
    # BankRootsFine) get swallowed - measured at 4:45, most of the root curtain vanished into the bulges
    reach = WALL_RELIEF["amp"] + WALL_RELIEF["fine_amp"] + WALL_RELIEF["ledge_amp"]
    d = _math(g, "SUBTRACT", d, reach, "WallInward")
    off = _node(g, "ShaderNodeVectorMath", "WallOff"); off.operation = "SCALE"
    L.new(nrm.outputs[0], off.inputs[0]); L.new(_math(g, "MULTIPLY", d, mask, "WallDM"), off.inputs["Scale"])
    # remember which faces were wall before the relief tilts them: the shader's wall mask reads `wsteep`
    st = _node(g, "GeometryNodeStoreNamedAttribute", "WallStoreSteep"); st.data_type = "FLOAT"; st.domain = "POINT"
    st.inputs["Name"].default_value = "wsteep"; L.new(last, st.inputs["Geometry"])
    L.new(_maprange(g, absz, WALL["steep"][0], WALL["steep"][1], 0, 1, "WallSteepAttr"), st.inputs["Value"])
    sp = _node(g, "GeometryNodeSetPosition", "WallRelief")
    L.new(st.outputs[0], sp.inputs["Geometry"]); L.new(off.outputs[0], sp.inputs["Offset"]); L.new(sp.outputs[0], out.inputs[0])


MOSS = dict(scale=(0.9, 1.8), hue=0.5, sat=0.7, value=0.45, translucency=0.15)


def moss():
    """The yellow-green strip down the lane middle is moss_01 mats scattered at 2-4x their scanned size: big flat
    plates with hard edges. Back to near life size, darker and duller (wet ground moss at night is deep olive)."""
    g = bpy.data.node_groups["Scatter_Cover"]
    for n in g.nodes:
        if n.bl_idname == "GeometryNodeCollectionInfo" and n.inputs["Collection"].default_value.name == "moss_01_LOD0":
            iop = [l.to_node for o in n.outputs for l in o.links][0]
            rv = iop.inputs["Scale"].links[0].from_node
            fl = [i for i in rv.inputs if i.name in ("Min", "Max") and i.type == "VALUE"]     # the float pair
            fl[0].default_value, fl[1].default_value = MOSS["scale"]
    # moss mats are ground plates: drop the ones whose point sits on a steep face (up axis of `rot` under ~55 deg),
    # which also floated in front of the recessed walls (wall_relief)
    N, L = g.nodes, g.links
    for n in [n for n in N if n.name.startswith("V2R_Moss")]:
        if n.bl_idname == "GeometryNodeDeleteGeometry":
            L.new(n.inputs["Geometry"].links[0].from_socket, n.outputs[0].links[0].to_socket)
    for n in [n for n in N if n.name.startswith("V2R_Moss")]: N.remove(n)
    for k, n in enumerate([n for n in N if n.bl_idname == "GeometryNodeCollectionInfo"
                           and n.inputs["Collection"].default_value.name == "moss_01_LOD0"]):
        iop = [l.to_node for o in n.outputs for l in o.links][0]
        src = iop.inputs["Points"].links[0].from_socket
        rot = _node(g, "GeometryNodeInputNamedAttribute", f"MossRot{k}"); rot.data_type = "QUATERNION"
        rot.inputs["Name"].default_value = "rot"
        up = _node(g, "FunctionNodeRotateVector", f"MossUp{k}"); up.inputs["Vector"].default_value = (0, 0, 1)
        L.new(rot.outputs[0], up.inputs["Rotation"])
        sz = _node(g, "ShaderNodeSeparateXYZ", f"MossUpZ{k}"); L.new(up.outputs[0], sz.inputs[0])
        steep = _math(g, "LESS_THAN", sz.outputs["Z"], 0.57, f"MossSteep{k}")
        dl = _node(g, "GeometryNodeDeleteGeometry", f"MossDel{k}"); dl.domain = "POINT"
        L.new(src, dl.inputs["Geometry"]); L.new(steep, dl.inputs["Selection"]); L.new(dl.outputs[0], iop.inputs["Points"])
    m = bpy.data.materials["moss_01"]
    for gr in [n for n in m.node_tree.nodes if n.bl_idname == "ShaderNodeGroup"]:
        for k in ("hue", "sat", "value", "translucency"):
            key = {"hue": "Hue", "sat": "Saturation", "value": "Value", "translucency": "Translucency"}[k]
            if key in gr.inputs: gr.inputs[key].default_value = MOSS[k]


STARS = dict(keep=0.5, size=0.1, power=5.0, gain=5.0, horizon=0.7, warm=(1.0, 0.86, 0.72, 1), cool=(0.78, 0.86, 1.0, 1))


def stars():
    """Every Voronoi cell held a star: an even grid of same-sized dots, denser than a moonlit sky shows. Keep ~30%
    of cells, smaller points, a steeper brightness spread (few bright, many faint), and star colour from warm to
    blue-white."""
    nt = bpy.context.scene.world.node_tree; N, L = nt.nodes, nt.links
    if "V2R_StarKeepMul" in N:
        L.new(N["V2R_StarKeepMul"].inputs[0].links[0].from_socket, N["StarGain"].inputs[0])
    for n in [n for n in N if n.name.startswith("V2R_")]: N.remove(n)
    N["StarSize"].inputs["From Max"].default_value = STARS["size"]
    N["StarBrightnessSpread"].inputs[1].default_value = STARS["power"]
    N["StarGain"].inputs[1].default_value = STARS["gain"]
    sep = N["Separate Color"]
    keep = _math(nt, "LESS_THAN", sep.outputs[1], STARS["keep"], "StarKeep")
    src = N["StarGain"].inputs[0].links[0].from_socket
    L.new(_math(nt, "MULTIPLY", src, keep, "StarKeepMul"), N["StarGain"].inputs[0])
    tint = _node(nt, "ShaderNodeMix", "StarTint"); tint.data_type = "RGBA"
    tint.inputs[6].default_value = STARS["warm"]; tint.inputs[7].default_value = STARS["cool"]
    L.new(sep.outputs[2], tint.inputs[0]); L.new(tint.outputs[2], N["Stars"].inputs["Color"])
    # sky brighter toward the horizon (airglow, haze, scattered moonlight); was one flat colour
    tc = _node(nt, "ShaderNodeTexCoord", "SkyTC"); sz = _node(nt, "ShaderNodeSeparateXYZ", "SkyZ")
    L.new(tc.outputs["Generated"], sz.inputs[0])
    hz = _maprange(nt, sz.outputs["Z"], 0.0, 0.45, STARS["horizon"], 0.0, "SkyHorizon")
    cam = N["AmbientLightPath"].outputs["Is Camera Ray"]                 # what the camera sees only, not the light
    if N["SkyGlow"].inputs["Strength"].is_linked: L.remove(N["SkyGlow"].inputs["Strength"].links[0])
    L.new(_math(nt, "MULTIPLY_ADD", hz, cam, "SkyHorizonCam", c=1.0), N["SkyGlow"].inputs["Strength"])


PEBBLE = dict(mud=(0.03, 0.021, 0.014, 1), coat_lo=0.25, coat_hi=0.85)


def pebbles():
    """Pebbles on the lane read as clean white stones. Stones in wet mud carry a mud skin, thickest low down and
    differing stone to stone: mix toward wet soil by height on the stone and a per-copy random."""
    m = bpy.data.materials["rock_moss_set_02_pebble"]; nt = m.node_tree; N, L = nt.nodes, nt.links
    bsdf = next(n for n in N if n.bl_idname == "ShaderNodeBsdfPrincipled")
    if "V2R_PebMud" in N: L.new(N["V2R_PebMud"].inputs[6].links[0].from_socket, bsdf.inputs["Base Color"])
    for n in [n for n in N if n.name.startswith("V2R_")]: N.remove(n)
    tc = _node(nt, "ShaderNodeTexCoord", "PebTC"); oi = _node(nt, "ShaderNodeObjectInfo", "PebOI")
    sep = _node(nt, "ShaderNodeSeparateXYZ", "PebZ"); L.new(tc.outputs["Generated"], sep.inputs[0])
    low = _maprange(nt, sep.outputs["Z"], 0.65, 0.2, 0, 1, "PebLow")                  # lower part of each stone
    r = _maprange(nt, oi.outputs["Random"], 0, 1, PEBBLE["coat_lo"], PEBBLE["coat_hi"], "PebR")
    f = _math(nt, "MAXIMUM", low, r, "PebF")
    mix = _node(nt, "ShaderNodeMix", "PebMud"); mix.data_type = "RGBA"
    L.new(f, mix.inputs[0]); L.new(bsdf.inputs["Base Color"].links[0].from_socket, mix.inputs[6])
    mix.inputs[7].default_value = PEBBLE["mud"]; L.new(mix.outputs[2], bsdf.inputs["Base Color"])


RIDGE = dict(weight=0.55, patch=(0.5, 0.6))     # was 0.85 and (0.3, 0.55): a continuous band


def ridge():
    """The hump between the wheel ruts carried a continuous yellow-green band with straight edges (the ridge layer of
    LaneGround). Real tracks have moss and grass there in broken patches: lower weight, sparser patch noise."""
    N = bpy.data.materials[GROUND].node_tree.nodes
    N["Math.009"].inputs[1].default_value = RIDGE["weight"]
    N["Map Range.007"].inputs["From Min"].default_value, N["Map Range.007"].inputs["From Max"].default_value = RIDGE["patch"]


SHEEN = dict(min_rough=0.55, normal=0.9)        # normal map strength was 1.3


def wet_sheen():
    """The lane's colour is right (dark mud and leaf litter, ~1.6% median), but its wet surface went near-mirror
    and reflected the lit fog as a grey sheen, broken by the normal map into white glitter - it read as frost or
    gravel. Wet mud is satin: floor the roughness and soften the normal map. Puddles (their own material) keep the
    mirror and the glints."""
    nt = bpy.data.materials[GROUND].node_tree; N, L = nt.nodes, nt.links
    bsdf = next(n for n in N if n.bl_idname == "ShaderNodeBsdfPrincipled")
    if "V2R_SheenFloor" in N: L.new(N["V2R_SheenFloor"].inputs[0].links[0].from_socket, bsdf.inputs["Roughness"])
    for n in [n for n in N if n.name.startswith("V2R_Sheen")]: N.remove(n)
    L.new(_math(nt, "MAXIMUM", bsdf.inputs["Roughness"].links[0].from_socket, SHEEN["min_rough"], "SheenFloor"),
          bsdf.inputs["Roughness"])
    N["Normal Map"].inputs["Strength"].default_value = SHEEN["normal"]


def unsheen():
    """Undo wet_sheen(): measured on the 1:40 lane it changed nothing (the roughness there is already over 0.55);
    the grey is moonlight and the fog veil on dark mud. Kept as a record so it is not retried."""
    nt = bpy.data.materials[GROUND].node_tree; N, L = nt.nodes, nt.links
    bsdf = next(n for n in N if n.bl_idname == "ShaderNodeBsdfPrincipled")
    if "V2R_SheenFloor" in N:
        L.new(N["V2R_SheenFloor"].inputs[0].links[0].from_socket, bsdf.inputs["Roughness"]); N.remove(N["V2R_SheenFloor"])
    N["Normal Map"].inputs["Strength"].default_value = 1.3


ROOTS = dict(value=0.5, wet=0.6, soil=(0.3, 0.8), normal=0.55)


def roots():
    """BankRoots (bank and scarp roots, fir bark on swept curves) read as pale grey rope with even stripes. Exposed
    roots in a wet bank are dark and soil-caked: darker bark, more soil cake, a softer bark relief."""
    N = bpy.data.materials["RootBark"].node_tree.nodes
    N["Hue/Saturation/Value"].inputs["Value"].default_value = ROOTS["value"]
    N["WetDarken"].inputs["Value"].default_value = ROOTS["wet"]
    N["SoilMask"].inputs["To Min"].default_value, N["SoilMask"].inputs["To Max"].default_value = ROOTS["soil"]
    N["Normal Map"].inputs["Strength"].default_value = ROOTS["normal"]


def build():
    walls(); wall_relief(); moss(); stars(); pebbles(); ridge(); roots()
    print("v2 realism applied")
