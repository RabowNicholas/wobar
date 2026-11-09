"""v2 material realism (2026-10-20). Nick: "i just want the colors to be realstic for the actual models. the goal is to
not have it look like CG" ... "sounds like we need variability in the greens."

The Diffuse Color pass showed every green at one bright yellow-green (~0.07-0.10 linear, saturation ~0.77), the lane
soil under 0.02, and identical colour on every scattered copy. Real conifer needles sit darker and bluer than ferns.

  firs + fir saplings  ~40% darker, nudged blue-green, a little less saturated; each copy varies in value and hue
  ferns                ~15% darker, less saturated, each copy varying in value and hue; ~25% yellowed, ~8% browning
  grass, nettles       some dead blades (their own Dead Amount input)
  moss, shrubs         a touch darker and less saturated
  lane soil            ~3x lighter (wet dark soil, not a black hole): mud_forest, SlideGround, LaneGround

Every change is a node named V2_*, so build() can run again (it removes its own nodes first).

    ns = {}; exec(open(PATH).read(), ns); ns["build"]()
"""
import bpy

FIRS = ("fir_tree_01_twig", "fir_sapling_medium_twigs", "fir_sapling_medium_branches")
FERN = "fern_02"
GRASS_DEAD = {"grass_medium_01": 0.25, "grass_medium_02": 0.25, "nettle_plant": 0.2}
GROUP_HSV = {"moss_01": (0.9, 0.88), "shrub_02": (0.88, 0.85)}     # value, saturation multipliers
MUD = ("mud_forest", "SlideGround", "LaneGround")
FIR = dict(value=0.6, value_var=0.28, hue=0.52, hue_var=0.022, sat=0.82)
FERN_V = dict(value=0.85, sat=0.85, value_var=0.22, hue_var=0.025, yellow_share=0.25, brown_share=0.08)
MUD_GAIN = 3.0


def _clear(nt):
    for n in [n for n in nt.nodes if n.name.startswith("V2_")]:
        nt.nodes.remove(n)


def _node(nt, kind, name, x=0, y=0):
    n = nt.nodes.new(kind); n.name = n.label = "V2_" + name; n.location = (x, y)
    return n


def _math(nt, op, a, b, name, c=None):
    n = _node(nt, "ShaderNodeMath", name); n.operation = op
    for i, v in enumerate((a, b, c)):
        if v is None: continue
        if isinstance(v, (int, float)): n.inputs[i].default_value = v
        else: nt.links.new(v, n.inputs[i])
    return n.outputs[0]


def _rand(nt, name, seed):
    """A second, independent per-copy random from Object Info > Random."""
    oi = _node(nt, "ShaderNodeObjectInfo", name + "_oi")
    return _math(nt, "FRACT", _math(nt, "MULTIPLY", oi.outputs["Random"], seed, name + "_mul"), None, name)


def _insert_before(nt, socket, node_out):
    """Feed `socket` (a linked input) through node_out's node: source -> node.inputs['Color'] -> socket."""
    src = socket.links[0].from_socket
    nt.links.new(src, node_out.node.inputs["Color"])
    nt.links.new(node_out, socket)


def firs():
    for mn in FIRS:
        m = bpy.data.materials.get(mn)
        if not m: continue
        nt = m.node_tree; _clear(nt)
        bsdf = next(n for n in nt.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled")
        hs = _node(nt, "ShaderNodeHueSaturation", "FirTone")
        r1, r2 = _rand(nt, "FirR1", 1.0), _rand(nt, "FirR2", 7.13)
        vvar = _math(nt, "MULTIPLY_ADD", r1, 2 * FIR["value_var"], "FirVvar", c=1 - FIR["value_var"])   # value_var either side of 1
        nt.links.new(_math(nt, "MULTIPLY", vvar, FIR["value"], "FirV"), hs.inputs["Value"])
        hv = _math(nt, "MULTIPLY_ADD", r2, 2 * FIR["hue_var"], "FirH", c=FIR["hue"] - FIR["hue_var"])
        nt.links.new(hv, hs.inputs["Hue"]); hs.inputs["Saturation"].default_value = FIR["sat"]
        _insert_before(nt, bsdf.inputs["Base Color"], hs.outputs["Color"])
        for tr in [n for n in nt.nodes if n.bl_idname == "ShaderNodeBsdfTranslucent" and n.inputs["Color"].is_linked]:
            nt.links.new(hs.outputs["Color"], tr.inputs["Color"])


def ferns():
    m = bpy.data.materials.get(FERN)
    if not m: return
    nt = m.node_tree; _clear(nt)
    bsdf = next(n for n in nt.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled")
    tone = _node(nt, "ShaderNodeHueSaturation", "FernTone"); tone.inputs["Saturation"].default_value = FERN_V["sat"]
    rv, rh = _rand(nt, "FernRV", 2.71), _rand(nt, "FernRH", 9.17)      # on top of the fern's own FernVary
    vvar = _math(nt, "MULTIPLY_ADD", rv, 2 * FERN_V["value_var"], "FernVvar", c=1 - FERN_V["value_var"])
    nt.links.new(_math(nt, "MULTIPLY", vvar, FERN_V["value"], "FernV"), tone.inputs["Value"])
    nt.links.new(_math(nt, "MULTIPLY_ADD", rh, 2 * FERN_V["hue_var"], "FernH", c=0.5 - FERN_V["hue_var"]), tone.inputs["Hue"])
    _insert_before(nt, bsdf.inputs["Base Color"], tone.outputs["Color"])
    yel = _node(nt, "ShaderNodeHueSaturation", "FernYellow")
    yel.inputs["Hue"].default_value = 0.45; yel.inputs["Saturation"].default_value = 0.7; yel.inputs["Value"].default_value = 0.85
    nt.links.new(tone.outputs["Color"], yel.inputs["Color"])
    mix = _node(nt, "ShaderNodeMix", "FernYellowMix"); mix.data_type = "RGBA"
    r = _rand(nt, "FernR", 5.31)
    nt.links.new(_math(nt, "MULTIPLY", _math(nt, "GREATER_THAN", r, 1 - FERN_V["yellow_share"], "FernPick"), 0.8, "FernAmt"), mix.inputs["Factor"])
    nt.links.new(tone.outputs["Color"], mix.inputs[6]); nt.links.new(yel.outputs["Color"], mix.inputs[7])
    brown = _node(nt, "ShaderNodeHueSaturation", "FernBrown")             # dying fronds: brown, dull, darker
    brown.inputs["Hue"].default_value = 0.38; brown.inputs["Saturation"].default_value = 0.8; brown.inputs["Value"].default_value = 0.75
    nt.links.new(tone.outputs["Color"], brown.inputs["Color"])
    mix2 = _node(nt, "ShaderNodeMix", "FernBrownMix"); mix2.data_type = "RGBA"
    nt.links.new(_math(nt, "LESS_THAN", r, FERN_V["brown_share"], "FernPickB"), mix2.inputs["Factor"])
    nt.links.new(mix.outputs[2], mix2.inputs[6]); nt.links.new(brown.outputs["Color"], mix2.inputs[7])
    nt.links.new(mix2.outputs[2], bsdf.inputs["Base Color"])
    for tr in [n for n in nt.nodes if n.bl_idname == "ShaderNodeBsdfTranslucent" and n.inputs["Color"].is_linked]:
        nt.links.new(mix2.outputs[2], tr.inputs["Color"])


def groups():
    for mn, dead in GRASS_DEAD.items():
        m = bpy.data.materials.get(mn)
        if not m: continue
        for g in [n for n in m.node_tree.nodes if n.bl_idname == "ShaderNodeGroup" and "Dead Amount" in n.inputs]:
            g.inputs["Dead Amount"].default_value = dead
    for mn, (v, s) in GROUP_HSV.items():
        m = bpy.data.materials.get(mn)
        if not m: continue
        for g in [n for n in m.node_tree.nodes if n.bl_idname == "ShaderNodeGroup"]:
            for key, k in (("Value", v), ("Saturation", s)):     # scaled from the value first seen, so re-runs don't compound
                if key in g.inputs and not g.inputs[key].is_linked:
                    base = m.get(f"V2_base_{key}", g.inputs[key].default_value); m[f"V2_base_{key}"] = base
                    g.inputs[key].default_value = base * k


def mud():
    for mn in MUD:
        m = bpy.data.materials.get(mn)
        if not m: continue
        nt = m.node_tree; _clear(nt)
        bsdf = next(n for n in nt.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled")
        hs = _node(nt, "ShaderNodeHueSaturation", "MudLift"); hs.inputs["Value"].default_value = MUD_GAIN
        _insert_before(nt, bsdf.inputs["Base Color"], hs.outputs["Color"])


def build():
    firs(); ferns(); groups(); mud()
    print("v2 materials applied")
