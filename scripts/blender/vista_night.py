"""The vista at the edge reads as night, not a bright blue CG valley (2026-10-28; Nick: "it is very bright that is part
of what makes it looks fake. then do the stars thing and the tree thing" - no added complexity: values and keys only).

    blender -b hohlweg_3_vista.blend -P vista_night.py      (saves; safe to re-run)

Brightness (open window 5:16.6-6:11.6): 56-70% of the vista was moonlit mist, the rest the camera sky.
  moon 0.35 -> 0.1 over the vista (7600-8040), then the old ramp to the fall's 0.6 by 8160 (the fall is unchanged);
  camera sky K 0.35 -> 0.1 (7600-8950); ambient back to 0.08 (7600-8919; the 0.4 hold from ambient_cover.py had
  lifted the approved fall x1.1-1.3); far haze colour x0.1/0.35 so the hazed skyline does not glow against the sky.
Stars (whole piece): disc 0.1 -> 0.065, brightness spread power 5 -> 7, gain 5 -> 14, kept 50% -> 40%: fewer, smaller,
  most faint, a few bright.
Far firs (FarForest, window only): crowns x1.6 wider (were ~3.5:1 spires), scale 0.55-1.3 -> 0.45-1.4,
  stands 0.6-1.35 -> 0.5-1.4, lean +-0.04 -> +-0.09 rad.
"""
import bpy, os, mathutils

MOON, SKY, AMB = 0.1, 0.1, 0.08
HAZE_COL = (0.019, 0.026, 0.039)            # far_valley.py Q["haze_col"], matched to the old 0.35 camera sky
STARS = dict(size=0.065, gain=14.0, keep=0.4, power=7.0)
TREES = dict(tilt=0.09, smin=0.45, smax=1.4, stmin=0.5, stmax=1.4, wide=1.6)

sc = bpy.context.scene
w = sc.world.node_tree


def fcurves(ad):
    for L in ad.action.layers:
        for s in L.strips:
            for cb in s.channelbags:
                yield from cb.fcurves


def rekey(fc, lo, hi, pts):
    """drop the keys strictly inside (lo, hi), then key pts"""
    while True:
        ks = [k for k in fc.keyframe_points if lo < k.co[0] < hi]
        if not ks:
            break
        fc.keyframe_points.remove(ks[0])
    for f, v in pts:
        fc.keyframe_points.insert(f, v, options={'FAST'})
    fc.update()


# ambient
for fc in fcurves(w.animation_data):
    if "AmbientScale" in fc.data_path:
        rekey(fc, 7552, 8990, [(7552, 0.4), (7600, AMB), (8919, AMB), (8990, 0.4)])
# camera sky (K is the unlinked input of V3_SkyCamK)
ki = next(i for i in w.nodes["V3_SkyCamK"].inputs if not i.is_linked)
for f, v in [(7552, 0.35), (7600, SKY), (8950, SKY), (9000, 0.35)]:
    ki.default_value = v; ki.keyframe_insert("default_value", frame=f)
# moon: the keys are 7552 1.2, 7600 0.35, 7920 0.35, 8160 0.6 ...
for fc in fcurves(bpy.data.objects["Moon"].data.animation_data):
    if fc.data_path == "energy":
        rekey(fc, 7552, 8160, [(7600, MOON), (7920, MOON), (8040, MOON)])
# far haze
hk = SKY / 0.35
for m in bpy.data.materials:
    if m.node_tree:
        for n in m.node_tree.nodes:
            if n.name.startswith("FV_HazeCol"):
                n.outputs[0].default_value = (*(c * hk for c in HAZE_COL), 1.0)
# stars
w.nodes["StarSize"].inputs["From Max"].default_value = STARS["size"]
w.nodes["StarGain"].inputs[1].default_value = STARS["gain"]
w.nodes["V2R_StarKeep"].inputs[1].default_value = STARS["keep"]
w.nodes["StarBrightnessSpread"].inputs[1].default_value = STARS["power"]
# far firs: the instancing values in FarForest (far_valley.forest), found by their built values or the vector lean
g = bpy.data.objects["FarForest"].modifiers["FarForest"].node_group
t = TREES
for n in g.nodes:
    if n.bl_idname == "FunctionNodeRandomValue" and n.data_type == "FLOAT_VECTOR":
        for i in n.inputs:
            if i.enabled and i.type == "VECTOR" and i.name == "Max": i.default_value = (t["tilt"], t["tilt"], 6.283)
            if i.enabled and i.type == "VECTOR" and i.name == "Min": i.default_value = (-t["tilt"], -t["tilt"], 0)
    if n.bl_idname == "FunctionNodeRandomValue" and n.data_type == "FLOAT":
        for i in n.inputs:
            if i.enabled and i.type == "VALUE" and i.name == "Min" and abs(i.default_value - 0.55) < 1e-3: i.default_value = t["smin"]
            if i.enabled and i.type == "VALUE" and i.name == "Max" and abs(i.default_value - 1.3) < 1e-3: i.default_value = t["smax"]
    if n.bl_idname == "ShaderNodeMapRange" and abs(n.inputs["To Min"].default_value - 0.6) < 1e-3 and abs(n.inputs["To Max"].default_value - 1.35) < 1e-3:
        n.inputs["To Min"].default_value, n.inputs["To Max"].default_value = t["stmin"], t["stmax"]
if not sc.get("vista_night_wide"):
    for k in range(3):
        bpy.data.meshes[f"FarFir_{k}"].transform(mathutils.Matrix.Diagonal((t["wide"], t["wide"], 1, 1)))
    sc["vista_night_wide"] = t["wide"]
sc["vista_night_applied"] = "2026-10-28"
print("VN applied", flush=True)

if bpy.app.background and not os.environ.get("VN_NOSAVE"):
    bpy.ops.wm.save_mainfile(); print("VN saved", bpy.data.filepath, flush=True)
