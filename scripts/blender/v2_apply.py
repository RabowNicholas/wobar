"""v2 locked decisions applied to hohlweg_3 (2026-10-20). See HOHLWEG_VISUALIZER.md, the v2 sign-off entries.

  moon     current aim through ERNSTFALL; swings to M2 (rotation z +20 deg) while dim in ABGRUND (energy 0.15, 6049-10940)
  ambient  world AmbientScale keys halved
  water    ruts -5 cm, creek -7 cm, puddle noise 2.5x finer, mist glow off, mirror Fresnel
  fog B    clumpier ground wisps, haze aloft x4 broken by its own noise
  render   3840x2160, volumetric tile 4, Z + Volume Direct passes (for the fog-light smoothing)

Guarded by scene["v2_applied"] so a second run does nothing.

    ns = {}; exec(open(PATH).read(), ns); ns["build"]()
"""
import bpy, math

MOON_Z = (6100, 10890, 20.0)          # first key, second key, degrees added
WATER_DROP = {"RutWater": 0.05, "CreekWater": 0.07}
PUDDLE_FINER = 2.5


def _fcurves(idblock):
    ad = idblock.animation_data
    for L in ad.action.layers:
        for st in L.strips:
            yield from st.channelbag(ad.action_slot).fcurves


def moon():
    ob = bpy.data.objects["Moon"]; z0 = ob.rotation_euler.z
    ob.keyframe_insert("rotation_euler", index=2, frame=MOON_Z[0])
    ob.rotation_euler.z = z0 + math.radians(MOON_Z[2])
    ob.keyframe_insert("rotation_euler", index=2, frame=MOON_Z[1])


def ambient():
    for fc in _fcurves(bpy.context.scene.world.node_tree):
        if "AmbientScale" in fc.data_path:
            for k in fc.keyframe_points:
                k.co[1] *= 0.5; k.handle_left[1] *= 0.5; k.handle_right[1] *= 0.5
            fc.update()


def water():
    for mn in ("CreekWater", "RutWater", "RutWater_real"):
        m = bpy.data.materials.get(mn)
        if not m: continue
        nt = m.node_tree
        if "W_mistglow_amt" in nt.nodes:
            if nt.animation_data and nt.animation_data.action:
                for fc in _fcurves(nt):
                    if "W_mistglow_amt" in fc.data_path: fc.mute = True
            nt.nodes["W_mistglow_amt"].inputs[1].default_value = 0.0
        if "Fresnel" in nt.nodes: nt.nodes["Fresnel"].inputs["IOR"].default_value = 1000.0
    for gn, d in WATER_DROP.items():
        t = bpy.data.node_groups[gn].nodes["Transform Geometry"]
        tr = list(t.inputs["Translation"].default_value); tr[2] -= d; t.inputs["Translation"].default_value = tr
    bpy.data.node_groups["RutWater"].nodes["Noise Texture"].inputs["Scale"].default_value *= PUDDLE_FINER


def fog():
    nt = bpy.data.materials["MistVolume"].node_tree; N, L = nt.nodes, nt.links
    N["Math.013"].inputs[1].default_value = 2.4         # wisps: rarer, denser
    N["Math.014"].inputs[1].default_value = 3.4
    N["WispContrast"].inputs[0].default_value = 0.08
    N["PatchContrast"].inputs["To Min"].default_value = 0.05
    N["HazeDensity"].inputs[1].default_value = 0.0012   # haze aloft x4, broken up by its own noise
    tex = N.new("ShaderNodeTexNoise"); tex.name = tex.label = "V2_HazeNoise"; tex.noise_dimensions = "4D"
    tex.inputs["Scale"].default_value = 0.3; tex.inputs["Detail"].default_value = 3.0
    L.new(N["MistLayering"].outputs[0], tex.inputs["Vector"]); L.new(N["EvolveSpeed"].outputs[0], tex.inputs["W"])
    mr = N.new("ShaderNodeMapRange"); mr.name = mr.label = "V2_HazeBreak"; mr.clamp = True
    mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = 0.38, 0.66
    mr.inputs["To Min"].default_value, mr.inputs["To Max"].default_value = 0.1, 1.9
    L.new(tex.outputs["Fac"], mr.inputs["Value"])
    mul = N.new("ShaderNodeMath"); mul.name = mul.label = "V2_HazeMul"; mul.operation = "MULTIPLY"
    L.new(N["Valley_haze_mul"].outputs[0], mul.inputs[0]); L.new(mr.outputs["Result"], mul.inputs[1])
    L.new(mul.outputs[0], N["MistTotal"].inputs[1])


def render():
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 3840, 2160, 100
    sc.eevee.volumetric_tile_size = "4"
    vl = sc.view_layers[0]; vl.use_pass_z = True; vl.eevee.use_pass_volume_direct = True


def build():
    sc = bpy.context.scene
    if sc.get("v2_applied"):
        print("v2 already applied"); return
    moon(); ambient(); water(); fog(); render()
    sc["v2_applied"] = True
    print("v2 applied")
