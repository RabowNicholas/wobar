"""Lighting pass v3 (Nick, 2026-10-26, review pass): night everywhere, moon always on, the fall back to the dark test.

    cp hohlweg_3.blend hohlweg_3_light.blend
    blender -b hohlweg_3_light.blend -P light_v3.py      (saves the file it runs on; run once, on a fresh copy)

1. TrenchFill removed (energy keys dropped, hidden): it lit the trench walls with no source and dropped
   frames to black when it went underground in the fall.
2. Moon always on: the 0.15 dip through ABGRUND is gone. 1.2 everywhere except the open landslide stretch:
   0.35 at the edge (5:16-5:30, so the valley's fog sea stays a dim textured layer) rising to 0.6 for the fall
   (5:40-6:15), so the open valley does not out-shine everything and the forms read against it. The 20 deg re-aim for GRUND moves from 4:14-7:34 into the trench stretch 4:14-5:15, where the banks hide it.
3. Mist below the lane: the trench layer (0.1/m) applied to everything below lane level, so the landslide bowl
   and the valley beyond it filled with trench-thick fog (a white sheet). More than ~3 m below the lane it is now
   a thin patchy pool (0.004/m, 0.010/m in the slide); inside the slide the pool keeps the dark test's top ~25 m under the near lane.
   The Mist box is deepened to the slip floor; below the old bottom (z -31) nothing changes on the GRUND side.
   Haze and the forest layer are thinned x0.35 inside the slide window. Inside the slide the trench layer
   (which there measures from the far lane at -30 m and lay as a sheet across the bowl) is kept at 10%, and at
   full only through the cut, keyed, so the cut is faint moonlit mist rather than black.
4. GRUND approach (from 9:34, camera y ~1795): the valley fog/haze ramps toward the clearing come back down
   (fog x2.2 -> x1.0, haze x5 -> x1.2) and the mist's forward scattering drops 0.4 -> 0.15, so looking into the
   moon through haze is not a white bloom. The GRUND forest before 9:34 is unchanged.
5. Night sky: the camera sees the sky at 35% (moonlight and world light on surfaces unchanged); the far
   valley's distance haze colour follows it. Stars unchanged.
All new nodes are named V3_*.
"""
import bpy

sc = bpy.context.scene
P = dict(
    moon=1.2, moon_keys=((7552, 1.2), (7600, 0.35), (7920, 0.35), (8160, 0.6), (9000, 0.6), (9048, 1.2)),
    reaim=(6100, 7560), sky_camera=0.35,
    slide_y=(1225.0, 1245.0, 1385.0, 1405.0),  # landslide window along world Y (ramp in, full, full, ramp out)
    below_lane=(-3.0, -8.0),                    # Z_above_lane: trench layer -> pool
    pool_density=(0.004, 0.010), pool_top=-25.0, slide_thin=0.35,   # pool: outside / inside the slide
    slide_trench_keys=((8740, 0.10), (8770, 1.0), (8919, 1.0), (8950, 0.10)),  # trench layer left in the slide:
                                                # 10% (edge, fall), full through the cut 6:04.8-6:11.6
    box_bottom=-60.0, old_bottom=-31.0,
    approach_y=(1785.0, 1815.0),                 # camera y at 9:33 -> 9:39; the approved GRUND forest is before it
    approach_fog=1.0 / 2.2, approach_haze=1.2 / 5.0, aniso=(0.4, 0.15),
)


def channelbags(idb):
    ad = idb.animation_data
    if not ad or not ad.action:
        return []
    return [cb for lay in ad.action.layers for st in lay.strips for cb in st.channelbags]


def drop_fc(idb, path):
    for cb in channelbags(idb):
        for fc in [f for f in cb.fcurves if f.data_path == path]:
            cb.fcurves.remove(fc)


assert "light_v3" not in sc, "already applied - run on a fresh copy of hohlweg_3"

# 1. TrenchFill
tf = bpy.data.objects["TrenchFill"]
drop_fc(tf.data, "energy")
tf.data.energy = 0.0
tf.hide_render = True

# 2. Moon
moon = bpy.data.objects["Moon"]
drop_fc(moon.data, "energy")
for f, e in P["moon_keys"]:
    moon.data.energy = e
    moon.data.keyframe_insert("energy", frame=f)
for cb in channelbags(moon.data) + channelbags(moon):
    for fc in cb.fcurves:
        if fc.data_path == "energy":
            for k in fc.keyframe_points:
                k.interpolation = "BEZIER"; k.easing = "EASE_IN_OUT"
        if fc.data_path == "rotation_euler" and fc.array_index == 2:
            ks = sorted(fc.keyframe_points, key=lambda k: k.co[0])
            for k, f in ((ks[0], P["reaim"][0]), (ks[-1], P["reaim"][1])):
                dx = f - k.co[0]
                k.co[0] = f; k.handle_left[0] += dx; k.handle_right[0] += dx
            fc.update()

# 3. Mist below the lane
nt = bpy.data.materials["MistVolume"].node_tree
N, L = nt.nodes, nt.links


def node(kind, name, **kw):
    n = N.new(kind); n.name = n.label = name
    for k, v in kw.items():
        setattr(n, k, v)
    return n


def math(name, op, a=None, b=None):
    n = node("ShaderNodeMath", name, operation=op)
    for i, v in ((0, a), (1, b)):
        if v is None:
            continue
        if isinstance(v, (int, float)):
            n.inputs[i].default_value = v
        else:
            L.new(v, n.inputs[i])
    return n


def mapr(name, src, fmin, fmax, tmin, tmax):
    n = node("ShaderNodeMapRange", name, interpolation_type="SMOOTHSTEP", clamp=True)
    L.new(src, n.inputs["Value"])
    n.inputs["From Min"].default_value, n.inputs["From Max"].default_value = fmin, fmax
    n.inputs["To Min"].default_value, n.inputs["To Max"].default_value = tmin, tmax
    return n


def splice(to_node, to_index, fn):
    """Replace the link into to_node.inputs[to_index] with fn(old_source_socket)."""
    lk = [l for l in L if l.to_node == to_node and l.to_socket == to_node.inputs[to_index]][0]
    src = lk.from_socket; L.remove(lk)
    L.new(fn(src), to_node.inputs[to_index])


sep = N["Separate XYZ"]            # raw position (world == object space: Mist sits at the origin, unscaled)
Y, Z = sep.outputs["Y"], sep.outputs["Z"]
zrel = N["Z_above_lane"].outputs[0]
y0, y1, y2, y3 = P["slide_y"]
in_slide = math("V3_InSlide", "MULTIPLY", mapr("V3_SlideIn", Y, y0, y1, 0, 1).outputs[0],
                mapr("V3_SlideOut", Y, y2, y3, 1, 0).outputs[0]).outputs[0]
after_slide = mapr("V3_AfterSlide", Y, y2, y3, 0, 1).outputs[0]
deep = mapr("V3_BelowLane", zrel, P["below_lane"][0], P["below_lane"][1], 0, 1).outputs[0]
keep = math("V3_TrenchKeep", "SUBTRACT", 1.0, deep).outputs[0]
# inside the slide the trench layer measures from the far lane (-30 m), so it lay as a trench-thick sheet across
# the bowl: keep 10% of it there, full only through the cut (Nick: B - faint moonlit mist, never black)
st = node("ShaderNodeValue", "V3_SlideTrench")
for f, v in P["slide_trench_keys"]:
    st.outputs[0].default_value = v
    st.outputs[0].keyframe_insert("default_value", frame=f)
keep = math("V3_TrenchKeepSlide", "MULTIPLY", keep, math("V3_SlideTrenchF", "SUBTRACT", 1.0,
            math("V3_SlideTrenchCut", "MULTIPLY", in_slide, math("V3_SlideTrenchInv", "SUBTRACT", 1.0, st.outputs[0]).outputs[0]).outputs[0]).outputs[0]).outputs[0]
# trench layer, faded out deep below the lane
tl = N["TrenchDensity"]
for lk in [l for l in L if l.from_node == tl]:
    to = lk.to_socket; L.remove(lk)
    L.new(math("V3_TrenchMasked", "MULTIPLY", tl.outputs[0], keep).outputs[0], to)
# pool: thin everywhere deep below the lane; inside the slide only under its uneven top
top = math("V3_PoolTopZ", "ADD", N["TopUnevenness_m"].outputs[0], P["pool_top"]).outputs[0]
under = mapr("V3_UnderTop", math("V3_DepthUnderTop", "SUBTRACT", top, Z).outputs[0], 0.0, 2.0, 0, 1).outputs[0]
notunder = math("V3_NotUnderTop", "SUBTRACT", 1.0, under).outputs[0]
topcut = math("V3_TopCut", "SUBTRACT", 1.0, math("V3_TopCutSlide", "MULTIPLY", in_slide, notunder).outputs[0]).outputs[0]
pd = math("V3_PoolDens", "ADD", math("V3_PoolDensSlide", "MULTIPLY", in_slide, P["pool_density"][1] - P["pool_density"][0]).outputs[0],
          P["pool_density"][0]).outputs[0]
pool = math("V3_Pool", "MULTIPLY", math("V3_PoolDeep", "MULTIPLY", deep, pd).outputs[0], topcut).outputs[0]
splice(N["Math.017"], 0, lambda s: math("V3_AddPool", "ADD", s, pool).outputs[0])   # pool gets the patch break-up
# haze and forest layer thinned inside the slide window
thin = math("V3_SlideThin", "SUBTRACT", 1.0, math("V3_SlideThinF", "MULTIPLY", in_slide, 1.0 - P["slide_thin"]).outputs[0]).outputs[0]
splice(N["MistTotal"], 1, lambda s: math("V3_HazeThin", "MULTIPLY", s, thin).outputs[0])
splice(N["Math.016"], 1, lambda s: math("V3_ForestThin", "MULTIPLY", s, thin).outputs[0])
# below the old box bottom on the GRUND side: nothing, as before the box was deepened
old = mapr("V3_BelowOldBox", Z, P["old_bottom"], P["old_bottom"] - 0.5, 0, 1).outputs[0]
gate = math("V3_Gate", "SUBTRACT", 1.0, math("V3_GateCut", "MULTIPLY", old, after_slide).outputs[0]).outputs[0]
tot = N["MistTotal"]
for lk in [l for l in L if l.from_node == tot]:
    to = lk.to_socket; L.remove(lk)
    L.new(math("V3_GatedTotal", "MULTIPLY", tot.outputs[0], gate).outputs[0], to)
me = bpy.data.objects["Mist"].data
zmin = min(v.co.z for v in me.vertices)
for v in me.vertices:
    if abs(v.co.z - zmin) < 1e-3:
        v.co.z = P["box_bottom"]
me.update()

# 4. GRUND approach only (the GRUND forest before it keeps its approved fog)
vy = N["Valley_sep"].outputs["Y"]
for name, node_name, k in (("Fog", "Valley_fog_mul", P["approach_fog"]), ("Haze", "Valley_haze_mul", P["approach_haze"])):
    f = mapr(f"V3_Approach{name}", vy, *P["approach_y"], 1.0, k).outputs[0]
    for lk in [l for l in L if l.from_node == N[node_name]]:
        to = lk.to_socket; L.remove(lk)
        L.new(math(f"V3_Approach{name}Mul", "MULTIPLY", N[node_name].outputs[0], f).outputs[0], to)
an = mapr("V3_ApproachAniso", vy, *P["approach_y"], *P["aniso"])
L.new(an.outputs[0], N["MistScatter"].inputs["Anisotropy"])

# 5. Night sky: the camera sees the sky at 35% (the light it casts on the scene is unchanged); the far valley's
#    distance haze, colour-matched to the horizon sky, follows it
W = sc.world.node_tree
def wmath(name, op, a, b):
    n = W.nodes.new("ShaderNodeMath"); n.name = n.label = name; n.operation = op
    for i, v in ((0, a), (1, b)):
        if isinstance(v, (int, float)): n.inputs[i].default_value = v
        else: W.links.new(v, n.inputs[i])
    return n.outputs[0]
h = W.nodes["V2R_SkyHorizon"].outputs[0]
cam = W.nodes["AmbientLightPath"].outputs["Is Camera Ray"]
k = P["sky_camera"]
strength = wmath("V3_SkyStrength", "ADD", wmath("V3_SkyCamOnly", "MULTIPLY", cam,
                 wmath("V3_SkyCamMinus1", "SUBTRACT", wmath("V3_SkyCamK", "MULTIPLY", wmath("V3_SkyHorizon1", "ADD", h, 1.0), k), 1.0)), 1.0)
glow = W.nodes["SkyGlow"].inputs["Strength"]
for lk in [l for l in W.links if l.to_socket == glow]:
    W.links.remove(lk)
W.links.new(strength, glow)                                   # camera: k * (1 + horizon); everything else: 1
for m in bpy.data.materials:
    if m.node_tree:
        for n in m.node_tree.nodes:
            if n.name.startswith("FV_HazeCol"):
                c = n.outputs[0].default_value
                n.outputs[0].default_value = (c[0] * k, c[1] * k, c[2] * k, 1.0)

sc["light_v3"] = str(P)
print("LV3 applied", P, flush=True)
if bpy.app.background:
    import os, sys
    bpy.ops.wm.save_mainfile()
    print("LV3 saved", bpy.data.filepath, flush=True)
    sys.stdout.flush()
    os._exit(0)
