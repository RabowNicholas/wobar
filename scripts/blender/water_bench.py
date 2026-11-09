# v4 = v3 (see-through + mirror + mist glow) + per-song glow, shallow-edge fade, wet band on the ground, floating twigs
import bpy, sys
args = sys.argv[sys.argv.index("--") + 1:]
out, frames, variant = args[0], [int(f) for f in args[1].split(",")], args[2]
P = dict(tint=(0.55, 0.45, 0.32), mirror_rough=0.02, fresnel_ior=1.33,
         glow=(0.0, 0.006, 0.009),          # ERNSTFALL, ABGRUND, GRUND
         shallow=0.035,                     # m of depth over which the edge fades to clear
         wet_band=(-0.085, -0.04), wet_dark=0.6, wet_rough=0.35,
         twigs=0.5)                         # floating twigs per m2 of water
for kv in args[3:]:
    k, v = kv.split("="); P[k] = eval(v)
sc = bpy.context.scene
sc.render.resolution_x = sc.render.resolution_y = 1920
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_depth = "16"
try:
    for n in sc.compositing_node_group.nodes:
        if n.bl_idname == "CompositorNodeOutputFile": n.mute = True
except Exception: pass
lane = bpy.data.objects["Lane"]

def depth_and_twigs(obj, twigs):
    g = obj.modifiers[0].node_group
    sm = g.nodes["Set Material"]; outn = next(n for n in g.nodes if n.type == "GROUP_OUTPUT")
    src = sm.outputs["Geometry"]
    oi = g.nodes.new("GeometryNodeObjectInfo"); oi.inputs["Object"].default_value = lane; oi.transform_space = "RELATIVE"
    pos = g.nodes.new("GeometryNodeInputPosition")
    rc = g.nodes.new("GeometryNodeRaycast"); rc.name = "W_depth"
    rc.inputs["Ray Direction"].default_value = (0, 0, -1); rc.inputs["Ray Length"].default_value = 2.0
    g.links.new(oi.outputs["Geometry"], rc.inputs["Target Geometry"]); g.links.new(pos.outputs[0], rc.inputs["Source Position"])
    sw = g.nodes.new("GeometryNodeSwitch"); sw.input_type = "FLOAT"
    sw.inputs["False"].default_value = 1.0
    g.links.new(rc.outputs["Is Hit"], sw.inputs["Switch"]); g.links.new(rc.outputs["Hit Distance"], sw.inputs["True"])
    st = g.nodes.new("GeometryNodeStoreNamedAttribute"); st.data_type = "FLOAT"; st.domain = "POINT"
    st.inputs["Name"].default_value = "wdepth"
    g.links.new(src, st.inputs["Geometry"]); g.links.new(sw.outputs[0], st.inputs["Value"])
    last = st.outputs["Geometry"]
    if twigs > 0:
        dp = g.nodes.new("GeometryNodeDistributePointsOnFaces"); dp.inputs["Density"].default_value = twigs
        g.links.new(last, dp.inputs["Mesh"])
        rd = g.nodes.new("GeometryNodeInputNamedAttribute"); rd.data_type = "FLOAT"; rd.inputs["Name"].default_value = "wdepth"
        lt = g.nodes.new("FunctionNodeCompare"); lt.data_type = "FLOAT"; lt.operation = "LESS_THAN"; lt.inputs["B"].default_value = 0.025
        g.links.new(rd.outputs["Attribute"], lt.inputs["A"])
        de = g.nodes.new("GeometryNodeDeleteGeometry"); g.links.new(dp.outputs["Points"], de.inputs["Geometry"]); g.links.new(lt.outputs[0], de.inputs["Selection"])
        ci = g.nodes.new("GeometryNodeCollectionInfo"); ci.inputs["Collection"].default_value = bpy.data.collections["TWIGS_SMALL"]
        ci.inputs["Separate Children"].default_value = True; ci.inputs["Reset Children"].default_value = True
        ip = g.nodes.new("GeometryNodeInstanceOnPoints"); ip.inputs["Pick Instance"].default_value = True
        g.links.new(de.outputs["Geometry"], ip.inputs["Points"]); g.links.new(ci.outputs[0], ip.inputs["Instance"])
        rr = g.nodes.new("FunctionNodeRandomValue"); rr.data_type = "FLOAT_VECTOR"
        rr.inputs["Min"].default_value = (0, 0, 0); rr.inputs["Max"].default_value = (0, 0, 6.283)
        rs = g.nodes.new("FunctionNodeRandomValue"); rs.data_type = "FLOAT"; rs.inputs["Min"].default_value = 0.3; rs.inputs["Max"].default_value = 0.9
        rs.inputs["Seed"].default_value = 7
        g.links.new(rr.outputs["Value"], ip.inputs["Rotation"]); g.links.new(rs.outputs["Value"], ip.inputs["Scale"])
        tr = g.nodes.new("GeometryNodeTranslateInstances"); tr.inputs["Translation"].default_value = (0, 0, -0.004)  # sitting in the surface
        g.links.new(ip.outputs["Instances"], tr.inputs["Instances"])
        jo = g.nodes.new("GeometryNodeJoinGeometry")
        g.links.new(tr.outputs["Instances"], jo.inputs["Geometry"]); g.links.new(last, jo.inputs["Geometry"])
        last = jo.outputs["Geometry"]
    for l in list(g.links):
        if l.to_node == outn: g.links.remove(l)
    g.links.new(last, outn.inputs[0])

def water(m, section_keys):
    nt = m.node_tree
    b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    normal = b.inputs["Normal"].links[0].from_socket if b.inputs["Normal"].is_linked else None
    outn = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent"); tr.inputs["Color"].default_value = (*P["tint"], 1)
    gl = nt.nodes.new("ShaderNodeBsdfGlossy"); gl.inputs["Roughness"].default_value = P["mirror_rough"]
    fr = nt.nodes.new("ShaderNodeFresnel"); fr.inputs["IOR"].default_value = P["fresnel_ior"]
    mix = nt.nodes.new("ShaderNodeMixShader")
    if normal:
        nt.links.new(normal, gl.inputs["Normal"]); nt.links.new(normal, fr.inputs["Normal"])
    nt.links.new(fr.outputs[0], mix.inputs[0]); nt.links.new(tr.outputs[0], mix.inputs[1]); nt.links.new(gl.outputs[0], mix.inputs[2])
    # mist glow (EEVEE leaves volumes out of reflections), weighted like the mirror, keyed per song
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (0.90, 0.92, 0.95, 1)
    amt = nt.nodes.new("ShaderNodeMath"); amt.operation = "MULTIPLY"; amt.name = "W_mistglow_amt"
    nt.links.new(fr.outputs[0], amt.inputs[0]); nt.links.new(amt.outputs[0], em.inputs["Strength"])
    for f, v in section_keys:
        amt.inputs[1].default_value = v; amt.inputs[1].keyframe_insert("default_value", frame=f)
    add = nt.nodes.new("ShaderNodeAddShader"); nt.links.new(mix.outputs[0], add.inputs[0]); nt.links.new(em.outputs[0], add.inputs[1])
    # shallow edges fade to clear: the mud shows through and there is no cut line
    at = nt.nodes.new("ShaderNodeAttribute"); at.attribute_name = "wdepth"
    mr = nt.nodes.new("ShaderNodeMapRange"); mr.interpolation_type = "SMOOTHSTEP"
    mr.inputs["From Min"].default_value = 0.0; mr.inputs["From Max"].default_value = P["shallow"]
    nt.links.new(at.outputs["Fac"], mr.inputs["Value"])
    clear = nt.nodes.new("ShaderNodeBsdfTransparent")
    edge = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(mr.outputs["Result"], edge.inputs[0]); nt.links.new(clear.outputs[0], edge.inputs[1]); nt.links.new(add.outputs[0], edge.inputs[2])
    nt.links.new(edge.outputs[0], outn.inputs["Surface"])
    m.surface_render_method = "DITHERED"

def wet_band(m):
    nt = m.node_tree
    b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    geo = nt.nodes.new("ShaderNodeNewGeometry"); sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Position"], sep.inputs[0])
    band = nt.nodes.new("ShaderNodeMapRange"); band.interpolation_type = "SMOOTHSTEP"; band.name = "W_wetband"
    band.inputs["From Min"].default_value, band.inputs["From Max"].default_value = P["wet_band"][1], P["wet_band"][0]   # 1 at the waterline, 0 a few cm above
    nt.links.new(sep.outputs["Z"], band.inputs["Value"])
    # colour x (1 - band*(1-dark))
    dk = nt.nodes.new("ShaderNodeMapRange"); dk.inputs["To Min"].default_value = 1.0; dk.inputs["To Max"].default_value = P["wet_dark"]
    nt.links.new(band.outputs["Result"], dk.inputs["Value"])
    src = b.inputs["Base Color"].links[0].from_socket
    mc = nt.nodes.new("ShaderNodeMix"); mc.data_type = "RGBA"; mc.blend_type = "MULTIPLY"; mc.inputs["Factor"].default_value = 1.0
    nt.links.new(src, mc.inputs["A"]); cc = nt.nodes.new("ShaderNodeCombineColor")
    for i in range(3): nt.links.new(dk.outputs["Result"], cc.inputs[i])
    nt.links.new(cc.outputs[0], mc.inputs["B"]); nt.links.new(mc.outputs["Result"], b.inputs["Base Color"])
    rk = nt.nodes.new("ShaderNodeMapRange"); rk.inputs["To Min"].default_value = 1.0; rk.inputs["To Max"].default_value = P["wet_rough"]
    nt.links.new(band.outputs["Result"], rk.inputs["Value"])
    rsrc = b.inputs["Roughness"].links[0].from_socket
    rm = nt.nodes.new("ShaderNodeMath"); rm.operation = "MULTIPLY"
    nt.links.new(rsrc, rm.inputs[0]); nt.links.new(rk.outputs["Result"], rm.inputs[1]); nt.links.new(rm.outputs[0], b.inputs["Roughness"])

if variant != "base":
    g0, g1, g2 = P["glow"]
    keys = [(1, g0), (5641, g0), (5737, g1), (10935, g1), (10983, g2)]   # 3:55-3:59 into ABGRUND, 7:35.6-7:37.6 into GRUND
    water(bpy.data.materials["RutWater_real"], keys); water(bpy.data.materials["CreekWater"], keys)
    for nm in ("RutWater", "CreekWater"):
        bpy.data.objects[nm].visible_shadow = False
    depth_and_twigs(bpy.data.objects["RutWater"], P["twigs"])
    depth_and_twigs(bpy.data.objects["CreekWater"], P["twigs"] * 0.6)
    wet_band(bpy.data.materials["LaneGround"])
    print("v4 applied", P)
for f in frames:
    sc.frame_set(f); sc.render.filepath = f"{out}/{variant}_{f:05d}.png"
    bpy.ops.render.render(write_still=True)
