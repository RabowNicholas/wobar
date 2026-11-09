"""v2 water details (2026-10-20), after "water after light rain, not a downpour" (HOHLWEG_VISUALIZER.md).

  drips    drip rings 0.35 -> 0.08 of the ripple cells: the odd drop from the canopy, not rain
  creek    surface roughness varies with the flow (calm glassy runs, broken patches); thin drifting scum/leaf film
  damp     lane soil darker and glossier within ~15 cm of standing water (LaneView stores `wdist`, the distance to
           the rut and creek water surfaces; the ground materials read it)

Every node is named V2_*, so build() can run again.

    ns = {}; exec(open(PATH).read(), ns); ns["build"]()
"""
import bpy

DRIP_CHANCE = 0.08
CREEK_ROUGH = (0.01, 0.12)            # glossy roughness range across the creek
DAMP = dict(reach=0.15, darken=0.45, rough=0.25)
GROUNDS = ("mud_forest", "SlideGround", "LaneGround")


def _unwire(nt, socket, through):
    """If `socket` is fed by node `through` (about to be removed), feed it from what fed `through` instead."""
    if socket.is_linked and socket.links[0].from_node.name == through:
        t = nt.nodes[through]; up = t.inputs[through_input[t.bl_idname]].links
        nt.links.new(up[0].from_socket, socket)


through_input = {"ShaderNodeMixShader": 1, "ShaderNodeMix": 6, "GeometryNodeStoreNamedAttribute": 0}


def _clear(nt):
    for n in [n for n in nt.nodes if n.name.startswith("V2_")]:
        nt.nodes.remove(n)


def _node(nt, kind, name, x=0, y=0):
    n = nt.nodes.new(kind); n.name = n.label = "V2_" + name; n.location = (x, y)
    return n


def drips():
    for mn in ("CreekWater", "RutWater_real", "RutWater"):
        m = bpy.data.materials.get(mn)
        if m and "Rip_RippleChance" in m.node_tree.nodes:
            m.node_tree.nodes["Rip_RippleChance"].inputs[1].default_value = DRIP_CHANCE


def creek():
    nt = bpy.data.materials["CreekWater"].node_tree; N, L = nt.nodes, nt.links
    if "V2_FilmMix" in N: _unwire(nt, N["Mix Shader.001"].inputs[2], "V2_FilmMix")
    _clear(nt)
    flow = N["FlowFrame_vec"].outputs[0]
    rn = _node(nt, "ShaderNodeTexNoise", "CreekRoughNoise"); rn.inputs["Scale"].default_value = 0.8; rn.inputs["Detail"].default_value = 2
    L.new(flow, rn.inputs["Vector"])
    rr = _node(nt, "ShaderNodeMapRange", "CreekRough"); rr.clamp = True
    rr.inputs["From Min"].default_value, rr.inputs["From Max"].default_value = 0.42, 0.62
    rr.inputs["To Min"].default_value, rr.inputs["To Max"].default_value = CREEK_ROUGH
    L.new(rn.outputs["Fac"], rr.inputs["Value"]); L.new(rr.outputs["Result"], N["Glossy BSDF"].inputs["Roughness"])
    # film: drifting with the flow, a dull brown diffuse layer over a few percent of the surface
    fn = _node(nt, "ShaderNodeTexNoise", "FilmNoise"); fn.inputs["Scale"].default_value = 2.2; fn.inputs["Detail"].default_value = 4
    L.new(flow, fn.inputs["Vector"])
    fm = _node(nt, "ShaderNodeMapRange", "FilmMask"); fm.clamp = True
    fm.inputs["From Min"].default_value, fm.inputs["From Max"].default_value = 0.66, 0.72
    L.new(fn.outputs["Fac"], fm.inputs["Value"])
    film = _node(nt, "ShaderNodeBsdfDiffuse", "Film"); film.inputs["Color"].default_value = (0.035, 0.025, 0.015, 1)
    mix = _node(nt, "ShaderNodeMixShader", "FilmMix")
    src = N["Mix Shader.001"].inputs[2].links[0].from_socket          # the water (Add Shader) into the depth fade
    L.new(fm.outputs["Result"], mix.inputs[0]); L.new(src, mix.inputs[1]); L.new(film.outputs[0], mix.inputs[2])
    L.new(mix.outputs[0], N["Mix Shader.001"].inputs[2])


def damp_attr():
    g = bpy.data.node_groups["ViewWindow_Lane"]; N, L = g.nodes, g.links
    out = next(n for n in N if n.bl_idname == "NodeGroupOutput")
    if "V2_StoreWdist" in N: _unwire(g, out.inputs[0], "V2_StoreWdist")
    _clear(g); last = out.inputs[0].links[0].from_socket
    join = _node(g, "GeometryNodeJoinGeometry", "WaterJoin")
    for nm in ("RutWater", "CreekWater"):
        oi = _node(g, "GeometryNodeObjectInfo", "Obj" + nm); oi.inputs["Object"].default_value = bpy.data.objects[nm]
        oi.transform_space = "RELATIVE"; L.new(oi.outputs["Geometry"], join.inputs[0])
    prox = _node(g, "GeometryNodeProximity", "WaterProx"); prox.target_element = "FACES"
    L.new(join.outputs[0], prox.inputs[0])
    st = _node(g, "GeometryNodeStoreNamedAttribute", "StoreWdist"); st.data_type = "FLOAT"; st.domain = "POINT"
    st.inputs["Name"].default_value = "wdist"
    L.new(last, st.inputs["Geometry"]); L.new(prox.outputs["Distance"], st.inputs["Value"])
    L.new(st.outputs[0], out.inputs[0])


def damp_shader():
    for mn in GROUNDS:
        m = bpy.data.materials.get(mn)
        if not m: continue
        nt = m.node_tree; N, L = nt.nodes, nt.links
        bsdf = next(n for n in N if n.bl_idname == "ShaderNodeBsdfPrincipled")
        if "V2_DampColor" in N:
            _unwire(nt, bsdf.inputs["Base Color"], "V2_DampColor")
            r = N["V2_DampRough"].inputs[2]
            if r.is_linked: L.new(r.links[0].from_socket, bsdf.inputs["Roughness"])
            else: bsdf.inputs["Roughness"].default_value = r.default_value
        for n in [n for n in N if n.name.startswith("V2_Damp")]: N.remove(n)
        at = _node(nt, "ShaderNodeAttribute", "DampAttr"); at.attribute_name = "wdist"
        mr = _node(nt, "ShaderNodeMapRange", "DampAmt"); mr.clamp = True      # 1 at the water's edge, 0 beyond reach
        mr.inputs["From Max"].default_value = DAMP["reach"]; mr.inputs["To Min"].default_value = 1; mr.inputs["To Max"].default_value = 0
        L.new(at.outputs["Fac"], mr.inputs["Value"])
        has = _node(nt, "ShaderNodeMath", "DampHas"); has.operation = "GREATER_THAN"; has.inputs[1].default_value = 0
        L.new(at.outputs["Fac"], has.inputs[0])                              # no attribute (other objects) -> dry
        amt = _node(nt, "ShaderNodeMath", "DampMask"); amt.operation = "MULTIPLY"
        L.new(mr.outputs["Result"], amt.inputs[0]); L.new(has.outputs[0], amt.inputs[1])
        dk = _node(nt, "ShaderNodeMix", "DampColor"); dk.data_type = "RGBA"; dk.blend_type = "MULTIPLY"
        L.new(amt.outputs[0], dk.inputs[0]); dk.inputs[7].default_value = (1 - DAMP["darken"],) * 3 + (1,)
        src = bsdf.inputs["Base Color"].links[0].from_socket
        L.new(src, dk.inputs[6]); L.new(dk.outputs[2], bsdf.inputs["Base Color"])
        rg = _node(nt, "ShaderNodeMix", "DampRough"); rg.data_type = "FLOAT"
        L.new(amt.outputs[0], rg.inputs[0]); rg.inputs[3].default_value = DAMP["rough"]
        rs = bsdf.inputs["Roughness"]
        if rs.is_linked: L.new(rs.links[0].from_socket, rg.inputs[2])
        else: rg.inputs[2].default_value = rs.default_value
        L.new(rg.outputs[0], rs)


def build():
    drips(); creek(); damp_attr(); damp_shader()
    print("v2 water applied")
