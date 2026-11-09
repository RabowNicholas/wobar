"""Cut motes: light test rig (2026-10-27). Standalone scene - no forest - to nail the form before it goes into
hohlweg_3.

    blender -b --factory-startup -P mote_rig.py -- --out DIR [--shape ico|octa|tetra] [--size 0.04]
        [--per-tick 1] [--spread 0.6] [--lead 0.3] [--peak 6.0] [--light-w 2.0] [--decay 0.08 0.25]
        [--mist 0.03] [--percent 50] [--frames 8740 8960]

ABGRUND's cut (6:04.8-6:11.6) is silent except one falling sound: a train of ticks sweeping ~9 kHz -> ~370 Hz,
slowing as it falls (cut_signal.json, scripts/post/cut_signal.py). Each tick ignites `per_tick` small wireframe
motes, fixed in space where the camera will be `lead` seconds later (offset off the lens), so the camera falls
past them and they streak UP through frame - falling reads as the world moving up past you. Pitch sets the
character (high: small, quick; low: slightly larger, slower decay), the tick's level sets brightness. Each mote has
a tiny point light so the mist glows around it. Camera: hohlweg_3's real camera, frames 8690-8970, baked.
"""
import bpy, sys, os, json, math, random, argparse
from mathutils import Matrix, Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
p = argparse.ArgumentParser()
p.add_argument("--out", required=True)
p.add_argument("--signal", default="/Volumes/music/blender/renders/cut_signal_01/cut_signal.json")
p.add_argument("--camera", default="/Volumes/music/blender/renders/cut_signal_01/cut_camera.json")
p.add_argument("--shape", default="ico")
p.add_argument("--size", type=float, default=0.04)
p.add_argument("--per-tick", type=int, default=1)
p.add_argument("--spread", type=float, default=0.6)       # m around the placement point
p.add_argument("--lead", type=float, default=0.3)         # s between ignition and the camera passing
p.add_argument("--offset", type=float, nargs=2, default=(0.9, 2.5))   # m off the lens: side, forward range
p.add_argument("--peak", type=float, default=6.0)         # emission strength at a full tick
p.add_argument("--light-w", type=float, default=2.0)      # point light W at a full tick
p.add_argument("--decay", type=float, nargs=2, default=(0.08, 0.25))  # half-life s at the top / bottom of the sweep
p.add_argument("--mist", type=float, default=0.03)
p.add_argument("--percent", type=int, default=50)
p.add_argument("--frames", type=int, nargs=2, default=(8740, 8960))
p.add_argument("--seed", type=int, default=7)
p.add_argument("--rise", type=float, nargs=2, default=(0.0, 0.0))   # m/s upward at the top / bottom of the sweep
p.add_argument("--depth", type=float, nargs=2, default=(2.5, 7.0))   # m in front of the lens at ignition
p.add_argument("--screen-v", type=float, nargs=2, default=(-0.9, 0.1)) # vertical screen range at ignition (-1 bottom)
p.add_argument("--life", type=float, default=0.0)        # s the mote moves for (0: static)
p.add_argument("--tail", type=float, default=0.0)        # tail length in s of travel (0: no tail)
p.add_argument("--into", action="store_true",
               help="add the motes to the open file (hohlweg_3 copy) instead of building the test scene; saves, no render")
a = p.parse_args(argv)

SIG = json.load(open(a.signal)); CAM = json.load(open(a.camera))
FPS = 24
LAV = CAM["form_rgb"]
rnd = random.Random(a.seed)


def frame_of(t):                      # master seconds -> scene frame (frame 1 = 0 s)
    return t * FPS + 1


sc = bpy.context.scene
mats = {int(k): Matrix(v) for k, v in CAM["frames"].items()}
if not a.into:
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob)
    sc.render.engine = "BLENDER_EEVEE" if "BLENDER_EEVEE" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE_NEXT"
    sc.render.fps = FPS
    sc.render.resolution_x, sc.render.resolution_y = CAM["res"]
    sc.render.resolution_percentage = a.percent
    sc.render.use_motion_blur = True
    sc.render.motion_blur_shutter = CAM["mblur"][1]
    sc.view_settings.view_transform = "AgX"
    sc.eevee.taa_render_samples = 16
    sc.eevee.volumetric_tile_size = "4"
    sc.eevee.volumetric_samples = 64
    sc.eevee.volumetric_end = 160.0
    sc.frame_start, sc.frame_end = a.frames

    # world: the night sky colour (camera sees 35%)
    w = bpy.data.worlds.new("W") if not sc.world else sc.world
    sc.world = w; w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs[0].default_value = (0.011, 0.015, 0.023, 1); bg.inputs[1].default_value = 0.35

    # camera, baked from hohlweg_3
    cd = bpy.data.cameras.new("Cam"); cd.lens = CAM["lens"]; cd.sensor_width = CAM["sensor"]
    cd.clip_start, cd.clip_end = CAM["clip"]
    cam = bpy.data.objects.new("Cam", cd); sc.collection.objects.link(cam); sc.camera = cam
    cam.rotation_mode = "XYZ"
    prev = None
    mats = {int(k): Matrix(v) for k, v in CAM["frames"].items()}
    for f in sorted(mats):
        m = mats[f]
        cam.location = m.to_translation()
        e = m.to_euler("XYZ", prev) if prev else m.to_euler("XYZ")
        cam.rotation_euler = e; prev = e
        cam.keyframe_insert("location", frame=f); cam.keyframe_insert("rotation_euler", frame=f)

    # moon
    md = bpy.data.lights.new("Moon", "SUN"); md.energy = 0.6; md.color = CAM["moon_color"][:3]; md.angle = CAM["moon_angle"]
    moon = bpy.data.objects.new("Moon", md); sc.collection.objects.link(moon); moon.matrix_world = Matrix(CAM["moon_mat"])

    # mist: a box around the path
    pts = [m.to_translation() for m in mats.values()]
    lo = Vector([min(v[i] for v in pts) for i in range(3)]) - Vector((40, 40, 30))
    hi = Vector([max(v[i] for v in pts) for i in range(3)]) + Vector((40, 40, 10))
    bpy.ops.mesh.primitive_cube_add(location=(lo + hi) / 2)
    box = bpy.context.object; box.name = "Mist"; box.scale = (hi - lo) / 2
    mm = bpy.data.materials.new("Mist"); mm.use_nodes = True; nt = mm.node_tree; nt.nodes.clear()
    vs = nt.nodes.new("ShaderNodeVolumeScatter"); vs.inputs["Density"].default_value = a.mist
    vs.inputs["Color"].default_value = (0.93, 0.94, 0.95, 1); vs.inputs["Anisotropy"].default_value = 0.4
    o = nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(vs.outputs[0], o.inputs["Volume"])
    box.data.materials.append(mm)


# mote material: emission strength from the object's own keyed "glow"
fm = bpy.data.materials.new("MoteWire"); fm.use_nodes = True; nt = fm.node_tree; nt.nodes.clear()
at = nt.nodes.new("ShaderNodeAttribute"); at.attribute_type = "OBJECT"; at.attribute_name = "glow"
em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (*LAV, 1)
mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = a.peak
nt.links.new(at.outputs["Fac"], mul.inputs[0]); nt.links.new(mul.outputs[0], em.inputs["Strength"])
mix = nt.nodes.new("ShaderNodeMixShader"); tr = nt.nodes.new("ShaderNodeBsdfTransparent")
gate = nt.nodes.new("ShaderNodeMath"); gate.operation = "GREATER_THAN"; gate.inputs[1].default_value = 0.01
nt.links.new(at.outputs["Fac"], gate.inputs[0]); nt.links.new(gate.outputs[0], mix.inputs[0])
nt.links.new(tr.outputs[0], mix.inputs[1]); nt.links.new(em.outputs[0], mix.inputs[2])
out = nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(mix.outputs[0], out.inputs["Surface"])


def mote_mesh(shape, r):
    import bmesh
    bm = bmesh.new()
    if shape == "octa":
        vs_ = [bm.verts.new(v) for v in ((r, 0, 0), (-r, 0, 0), (0, r, 0), (0, -r, 0), (0, 0, r), (0, 0, -r))]
        for f_ in ((0, 2, 4), (2, 1, 4), (1, 3, 4), (3, 0, 4), (2, 0, 5), (1, 2, 5), (3, 1, 5), (0, 3, 5)):
            bm.faces.new([vs_[i] for i in f_])
    elif shape == "tetra":
        s = r / math.sqrt(3)
        vs_ = [bm.verts.new(v) for v in ((s, s, s), (s, -s, -s), (-s, s, -s), (-s, -s, s))]
        for f_ in ((0, 1, 2), (0, 3, 1), (0, 2, 3), (1, 3, 2)):
            bm.faces.new([vs_[i] for i in f_])
    else:
        bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    me = bpy.data.meshes.new("mote_" + shape); bm.to_mesh(me); bm.free()
    return me


def env_keys(f0, peak, half):
    """(frame, value): 0 before, peak at the tick frame, exponential decay with the given half-life, 0 after."""
    n = int(math.ceil(half * FPS * 6)) + 1
    for k in range(-1, n + 1):
        f = f0 + k
        v = 0.0 if k < 0 or k == n else peak * 0.5 ** (k / (half * FPS))
        yield f, v


ticks = SIG["ticks"]
frames_sig = SIG["frames"]
def pitch01_at(t):
    best = min(frames_sig, key=lambda fr: abs(fr["t"] - t))
    return best["pitch01"] if best["pitch01"] is not None else 0.0

col = bpy.data.collections.new("Motes"); sc.collection.children.link(col)
tails = []
_tail_mats = {}


def tail_mat(L_):
    """Mote colour, fading from the head (local z 0) to nothing at the tail end (local z -L)."""
    m = bpy.data.materials.new("MoteTail"); m.use_nodes = True; t = m.node_tree; t.nodes.clear()
    tc_ = t.nodes.new("ShaderNodeTexCoord"); sx = t.nodes.new("ShaderNodeSeparateXYZ")
    t.links.new(tc_.outputs["Object"], sx.inputs[0])
    mr = t.nodes.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = -L_; mr.inputs["From Max"].default_value = 0.0
    t.links.new(sx.outputs["Z"], mr.inputs["Value"])
    pw = t.nodes.new("ShaderNodeMath"); pw.operation = "POWER"; pw.inputs[1].default_value = 2.0
    t.links.new(mr.outputs[0], pw.inputs[0])
    at_ = t.nodes.new("ShaderNodeAttribute"); at_.attribute_type = "OBJECT"; at_.attribute_name = "glow"
    m1 = t.nodes.new("ShaderNodeMath"); m1.operation = "MULTIPLY"; m1.inputs[1].default_value = a.peak * 0.6
    t.links.new(at_.outputs["Fac"], m1.inputs[0])
    m2 = t.nodes.new("ShaderNodeMath"); m2.operation = "MULTIPLY"
    t.links.new(m1.outputs[0], m2.inputs[0]); t.links.new(pw.outputs[0], m2.inputs[1])
    em_ = t.nodes.new("ShaderNodeEmission"); em_.inputs["Color"].default_value = (*LAV, 1)
    t.links.new(m2.outputs[0], em_.inputs["Strength"])
    tr_ = t.nodes.new("ShaderNodeBsdfTransparent"); mx = t.nodes.new("ShaderNodeMixShader")
    g = t.nodes.new("ShaderNodeMath"); g.operation = "GREATER_THAN"; g.inputs[1].default_value = 0.01
    t.links.new(m2.outputs[0], g.inputs[0]); t.links.new(g.outputs[0], mx.inputs[0])
    t.links.new(tr_.outputs[0], mx.inputs[1]); t.links.new(em_.outputs[0], mx.inputs[2])
    o_ = t.nodes.new("ShaderNodeOutputMaterial"); t.links.new(mx.outputs[0], o_.inputs["Surface"])
    return m
n_m = 0
for ti, (t, lvl) in enumerate(ticks):
    f_tick = frame_of(t)
    f_pass = int(round(f_tick + a.lead * FPS))
    f_pass = min(max(f_pass, min(mats)), max(mats))
    M = mats[f_pass]
    cpos = M.to_translation()
    right = M.to_3x3() @ Vector((1, 0, 0)); fwd = M.to_3x3() @ Vector((0, 0, -1)); up = M.to_3x3() @ Vector((0, 1, 0))
    p01 = pitch01_at(t)
    size = a.size * (1.0 + 0.6 * (1 - p01))                       # lower pitch -> a little larger
    half = a.decay[0] + (a.decay[1] - a.decay[0]) * (1 - p01)      # lower pitch -> slower decay
    for j in range(a.per_tick):
        side = rnd.choice((-1, 1)) * rnd.uniform(a.offset[0], a.offset[0] + 0.6)
        ahead = rnd.uniform(*a.offset) if a.offset[1] > a.offset[0] else a.offset[0]
        jitter = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))) * a.spread
        pos = cpos + right * side + fwd * ahead + up * rnd.uniform(-0.3, 0.3) + jitter
        rise = a.rise[0] + (a.rise[1] - a.rise[0]) * (1 - p01)
        if rise > 0:                                   # launched upward from below the camera at the tick
            # placed by screen position at ignition (in frame, mostly the lower part), a few metres out
            Mt = mats[min(max(int(round(f_tick)), min(mats)), max(mats))]
            th = math.atan(CAM["sensor"] / 2 / CAM["lens"]); tv = th * CAM["res"][1] / CAM["res"][0]
            d = rnd.uniform(*a.depth); u = rnd.uniform(-0.8, 0.8); v = rnd.uniform(*a.screen_v)
            pos = Mt @ Vector((u * d * math.tan(th), v * d * math.tan(tv), -d))
        me = mote_mesh(a.shape, size); me.materials.append(fm)
        ob = bpy.data.objects.new(f"mote_{ti:02d}_{j}", me); col.objects.link(ob); ob.location = pos
        ob.rotation_euler = (rnd.uniform(0, 6.28), rnd.uniform(0, 6.28), rnd.uniform(0, 6.28))
        wf = ob.modifiers.new("Beams", "WIREFRAME"); wf.thickness = size * 0.12; wf.use_replace = True
        ob.visible_shadow = False
        ob["glow"] = 0.0
        if rise > 0 and a.life > 0:
            f0 = int(round(f_tick)); f1 = f0 + int(round(a.life * FPS))
            ob.keyframe_insert("location", frame=f0)
            ob.location = pos + Vector((0, 0, rise * a.life)); ob.keyframe_insert("location", frame=f1)
            for fc in ob.animation_data.action.layers[0].strips[0].channelbags[0].fcurves:
                if fc.data_path == "location":
                    for k in fc.keyframe_points: k.interpolation = "LINEAR"
            ob.location = pos
        if a.tail > 0 and rise > 0:                    # a tapering wire tail trailing below the mote
            L_ = rise * a.tail
            tm = bpy.data.meshes.new("tail"); import bmesh
            bm = bmesh.new()
            bmesh.ops.create_cone(bm, cap_ends=False, segments=6, radius1=size * 0.12, radius2=0.0, depth=L_)
            bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0, -L_ / 2))
            bm.to_mesh(tm); bm.free(); tm.materials.append(tail_mat(L_))
            tob = bpy.data.objects.new(ob.name + "_tail", tm); col.objects.link(tob)
            cl = tob.constraints.new("COPY_LOCATION"); cl.target = ob       # follows the mote, stays upright
            tob["glow"] = 0.0; tob.visible_shadow = False; tob["mote"] = ob.name
            tails.append(tob)
        ld = bpy.data.lights.new(f"moteL_{ti:02d}_{j}", "POINT"); ld.color = LAV; ld.shadow_soft_size = size
        ld.use_shadow = False
        lo_ = bpy.data.objects.new(ld.name, ld); col.objects.link(lo_); lo_.location = pos
        if rise > 0 and a.life > 0:
            lo_.parent = ob; lo_.matrix_parent_inverse = Matrix.Identity(4); lo_.location = (0, 0, 0)
        for f, v in env_keys(int(round(f_tick)), lvl, half):
            ob["glow"] = v; ob.keyframe_insert('["glow"]', frame=f)
            ld.energy = v * a.light_w; ld.keyframe_insert("energy", frame=f)
            if tails and tails[-1].get("mote") == ob.name:
                tails[-1]["glow"] = v; tails[-1].keyframe_insert('["glow"]', frame=f)
        n_m += 1
print(f"MR {n_m} motes for {len(ticks)} ticks", flush=True)

if a.into:
    sc["cut_motes"] = str(vars(a))
    bpy.ops.wm.save_mainfile()
    print("MR saved into", bpy.data.filepath, flush=True)
    sys.stdout.flush(); os._exit(0)

# render
os.makedirs(a.out, exist_ok=True)
sc.render.filepath = os.path.join(a.out, "m_")
sc.render.image_settings.file_format = "PNG"
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(a.out, "mote_rig.blend"))
bpy.ops.render.render(animation=True)
print("MR rendered", flush=True)
sys.stdout.flush()
os._exit(0)
