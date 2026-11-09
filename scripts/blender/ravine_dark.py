"""ABGRUND breakdown — dark test of the landslide crossing in EEVEE (2026-10-19).

Opens the grey blockout (ravine_blockout.py output) and turns it into night: sky glow + stars,
ABGRUND's faint moon, mist pooled in the slide bowl, and the bottom forms as lavender wire cages
with their own lights, flashing on the real kick (toppled trunks) and snare (boulders) hits.
The question it answers: when the camera looks down into the bowl, does the dark read?

    Blender -b --factory-startup abgrund_ravine_blockout.blend --python ravine_dark.py -- [stills|anim]
"""
import bpy, json, math, sys
import numpy as np
from mathutils import Vector

P = dict(
    t_start=320.0, fps=24,
    hits="/Volumes/music/blender/hohlweg_assets/audio/hohlweg_hits.json",
    fade=0.35,                                   # seconds to ~5%, as FORM_CTRL
    colour=(0.816, 0.682, 0.886),                # ABGRUND lavender #D0AEE2
    wire_peak=0.7, wire_thick=0.04,
    kick_w=400.0, kick_reach=22.0, snare_w=200.0, snare_reach=14.0, vol_factor=1.0,
    sky=(0.011, 0.015, 0.023), star_gain=1.5, moon=0.15,
    mist_top=-25.0, mist_density=0.015, haze=0.0004,
    samples=8, res=(960, 540),
    out="/Volumes/music/blender/renders/ravine_dark_01/f_",
    stills_dir="/Volumes/music/blender/renders/ravine_dark_04_stills/",
)
sc = bpy.context.scene
sc.render.engine = "BLENDER_EEVEE"
sc.eevee.taa_render_samples = P["samples"]
sc.render.resolution_x, sc.render.resolution_y = P["res"]
sc.eevee.volumetric_tile_size = "8"
sc.eevee.volumetric_samples = 64
sc.eevee.volumetric_start = 0.3
sc.eevee.volumetric_end = 300.0
try:
    sc.view_settings.view_transform = "AgX"
except TypeError as e:
    print("view transform:", e)


def mat(name, base, rough=0.9, emit=None):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*base, 1)
    b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = 0.0
    return m


def assign(ob, m):
    ob.data.materials.clear()
    ob.data.materials.append(m)


assign(bpy.data.objects["Terrain"], mat("Soil", (0.045, 0.038, 0.032)))
assign(bpy.data.objects["Trees"], mat("Bark", (0.03, 0.03, 0.028)))
assign(bpy.data.objects["YoungGrowth"], mat("Young", (0.02, 0.035, 0.022), 0.7))
assign(bpy.data.objects["LaneProps"], mat("Roots", (0.06, 0.055, 0.05)))
assign(bpy.data.objects["Stream"], mat("Water", (0.005, 0.006, 0.007), 0.08))
bpy.data.objects["MistTop"].hide_render = True

# ---------------------------------------------------------------- world: sky glow + stars
w = sc.world
w.use_nodes = True
nt = w.node_tree
nt.nodes.clear()
out = nt.nodes.new("ShaderNodeOutputWorld")
bg = nt.nodes.new("ShaderNodeBackground")
tc = nt.nodes.new("ShaderNodeTexCoord")
vor = nt.nodes.new("ShaderNodeTexVoronoi")
vor.inputs["Scale"].default_value = 220
mr = nt.nodes.new("ShaderNodeMapRange")
mr.interpolation_type = "SMOOTHERSTEP"
mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = 0.12, 0.0
gain = nt.nodes.new("ShaderNodeMath"); gain.operation = "MULTIPLY"; gain.inputs[1].default_value = P["star_gain"]
add = nt.nodes.new("ShaderNodeMath"); add.operation = "ADD"; add.inputs[1].default_value = 1.0
mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"
nt.links.new(tc.outputs["Generated"], vor.inputs["Vector"])
nt.links.new(vor.outputs["Distance"], mr.inputs["Value"])
nt.links.new(mr.outputs["Result"], gain.inputs[0])
sky = nt.nodes.new("ShaderNodeRGB"); sky.outputs[0].default_value = (*P["sky"], 1)
star_col = nt.nodes.new("ShaderNodeMix"); star_col.data_type = "RGBA"; star_col.blend_type = "ADD"
star_col.inputs["Factor"].default_value = 1.0
starv = nt.nodes.new("ShaderNodeCombineColor")
nt.links.new(gain.outputs[0], starv.inputs[0]); nt.links.new(gain.outputs[0], starv.inputs[1]); nt.links.new(gain.outputs[0], starv.inputs[2])
nt.links.new(sky.outputs[0], star_col.inputs["A"])
nt.links.new(starv.outputs[0], star_col.inputs["B"])
nt.links.new(star_col.outputs["Result"], bg.inputs["Color"])
nt.links.new(bg.outputs[0], out.inputs["Surface"])

# moon: ahead and to the right, 40 deg up, faint (ABGRUND)
md = bpy.data.lights.new("Moon", "SUN")
md.energy = P["moon"]
md.color = (0.78, 0.84, 0.93)
md.angle = math.radians(0.6)
moon = bpy.data.objects.new("Moon", md)
sc.collection.objects.link(moon)
az, el = math.radians(32), math.radians(40)
to_moon = Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
moon.rotation_euler = (-to_moon).to_track_quat("-Z", "Y").to_euler()

# ---------------------------------------------------------------- mist pooled in the bowl
me = bpy.data.meshes.new("MistBox")
import bmesh
bm = bmesh.new()
bmesh.ops.create_cube(bm, size=1.0)
bm.to_mesh(me); bm.free()
mist = bpy.data.objects.new("Mist", me)
sc.collection.objects.link(mist)
mist.location = (45, 87, -50)
mist.scale = (220, 240, 90)
mm = bpy.data.materials.new("MistVolume")
mm.use_nodes = True
mt = mm.node_tree
mt.nodes.clear()
mo = mt.nodes.new("ShaderNodeOutputMaterial")
vs = mt.nodes.new("ShaderNodeVolumeScatter")
vs.inputs["Color"].default_value = (0.93, 0.94, 0.95, 1)
vs.inputs["Anisotropy"].default_value = 0.4
geo = mt.nodes.new("ShaderNodeNewGeometry")
sep = mt.nodes.new("ShaderNodeSeparateXYZ")
# density: full below the mist top, falling off over 3 m above it, plus a faint haze everywhere; patchy
fall = mt.nodes.new("ShaderNodeMapRange")
fall.interpolation_type = "SMOOTHSTEP"
fall.inputs["From Min"].default_value, fall.inputs["From Max"].default_value = P["mist_top"] + 3.0, P["mist_top"] - 1.0
fall.inputs["To Min"].default_value, fall.inputs["To Max"].default_value = P["haze"], P["mist_density"]
noi = mt.nodes.new("ShaderNodeTexNoise")
noi.inputs["Scale"].default_value = 0.08
nmr = mt.nodes.new("ShaderNodeMapRange")
nmr.inputs["From Min"].default_value, nmr.inputs["From Max"].default_value = 0.35, 0.7
nmr.inputs["To Min"].default_value, nmr.inputs["To Max"].default_value = 0.3, 1.0
mul = mt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"
mt.links.new(geo.outputs["Position"], sep.inputs[0])
mt.links.new(sep.outputs["Z"], fall.inputs["Value"])
mt.links.new(geo.outputs["Position"], noi.inputs["Vector"])
mt.links.new(noi.outputs["Fac"], nmr.inputs["Value"])
mt.links.new(fall.outputs["Result"], mul.inputs[0])
mt.links.new(nmr.outputs["Result"], mul.inputs[1])
mt.links.new(mul.outputs[0], vs.inputs["Density"])
mt.links.new(vs.outputs[0], mo.inputs["Volume"])
mist.data.materials.append(mm)

# ---------------------------------------------------------------- forms: split, cage, light
forms = bpy.data.objects["Forms"]
bpy.context.view_layer.objects.active = forms
for o in bpy.context.selected_objects:
    o.select_set(False)
forms.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.separate(type="LOOSE")
bpy.ops.object.mode_set(mode="OBJECT")
parts = [o for o in sc.objects if o.name.startswith("Forms")]
rock = mat("Rock", (0.05, 0.05, 0.05), 0.8)
wire = {k: mat(f"FormWire_{k}", (0, 0, 0), 1.0, emit=P["colour"]) for k in ("kick", "snare")}
ld = {}
for k in ("kick", "snare"):
    d = bpy.data.lights.new(f"FormLight_{k}", "POINT")
    d.color = P["colour"]
    d.energy = 0.0
    d.use_shadow = False
    d.specular_factor = 0.0
    d.volume_factor = P["vol_factor"]
    d.use_custom_distance = True
    d.cutoff_distance = P[f"{k}_reach"]
    d.shadow_soft_size = 0.5
    ld[k] = d
counts = {"kick": 0, "snare": 0}
for o in parts:
    k = "snare" if len(o.data.vertices) == 8 else "kick"   # boxes are boulders (snare); cylinders are trunks (kick)
    counts[k] += 1
    assign(o, rock)
    wo = o.copy()
    wo.data = o.data.copy()
    sc.collection.objects.link(wo)
    c = sum((o.matrix_world @ v.co for v in o.data.vertices), Vector()) / len(o.data.vertices)
    for v in wo.data.vertices:  # inflate the cage a little off the surface
        v.co = c + (v.co - c) * 1.06
    mod = wo.modifiers.new("Wire", "WIREFRAME")
    mod.thickness = P["wire_thick"]
    assign(wo, wire[k])
    lo = bpy.data.objects.new(f"L_{o.name}", ld[k])
    lo.location = c + Vector((0, 0, 0.8))
    sc.collection.objects.link(lo)
print("forms:", counts)

# ---------------------------------------------------------------- hits -> per-frame envelopes
hits = json.load(open(P["hits"]))
f0, f1 = sc.frame_start, sc.frame_end
for k in ("kick", "snare"):
    hs = [(round((t - P["t_start"]) * P["fps"]) + 1, v) for t, v in hits[k] if P["t_start"] - 2 <= t <= P["t_start"] + (f1 + 24) / P["fps"]]
    env = np.zeros(f1 + 2)
    for f in range(f0, f1 + 1):
        last = [h for h in hs if h[0] <= f]
        if last:
            hf, v = last[-1]
            env[f] = v * math.exp(-3.0 * (f - hf) / (P["fade"] * P["fps"]))
    b = next(n for n in wire[k].node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    sock = b.inputs["Emission Strength"]
    for f in range(f0, f1 + 1):
        sock.default_value = P["wire_peak"] * env[f]
        sock.keyframe_insert("default_value", frame=f)
        ld[k].energy = P[f"{k}_w"] * env[f]
        ld[k].keyframe_insert("energy", frame=f)
    print(k, "hits in range:", len([h for h in hs if f0 <= h[0] <= f1]))

mode = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else "stills"
if mode == "stills":
    import os
    os.makedirs(P["stills_dir"], exist_ok=True)
    for t in (348.5, 352.75, 356.4, 358.5, 359.9, 361.0, 362.0, 363.5):
        f = round((t - P["t_start"]) * P["fps"]) + 1
        sc.frame_set(f)
        sc.render.filepath = P["stills_dir"] + f"s_{t:07.2f}.png"
        bpy.ops.render.render(write_still=True)
else:
    sc.render.filepath = P["out"]
    sc.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(animation=True)
