"""usage: blender -b [FILE] -P verify_kit.py -- MODE KIT OUTDIR
MODE integrity : open KIT, check refs/drivers/actions
MODE tunnel_kit / tunnel_orig : render tunnel frame 100 @20%
MODE makyo_kit / makyo_orig  : count instances + render frame 900 @10%"""
import bpy, sys, json
a = sys.argv[sys.argv.index("--") + 1:]
mode, kit, outd = a[0], a[1], a[2]
D = bpy.data
sc = bpy.context.scene


def append_collections(names, worlds=(), groups=()):
    with D.libraries.load(kit, link=False) as (src, dst):
        dst.collections = list(names)
        dst.worlds = list(worlds)
        dst.node_groups = list(groups)
    for c in dst.collections:
        sc.collection.children.link(c)
    return dst


def drivers_of(idb):
    for ad in (getattr(idb, "animation_data", None), getattr(getattr(idb, "node_tree", None), "animation_data", None)):
        if ad:
            for d in ad.drivers:
                yield d


def instance_counts():
    dg = bpy.context.evaluated_depsgraph_get()
    cnt = {}
    for inst in dg.object_instances:
        if inst.is_instance:
            p = inst.parent.original.name if inst.parent else None
            cnt[p] = cnt.get(p, 0) + 1
    return cnt


if mode == "integrity":
    bad = 0
    for ng in D.node_groups:
        for n in ng.nodes:
            if n.bl_idname in ("GeometryNodeObjectInfo", "GeometryNodeCollectionInfo") and not n.inputs[0].is_linked:
                v = n.inputs[0].default_value
                ok = v is not None and v.library is None
                print("REF", ng.name, n.name, v.name if v else None, "OK" if ok else "BROKEN")
                bad += not ok
    targets = {}
    for coll in (D.objects, D.node_groups, D.materials, D.lights, D.worlds):
        for i in coll:
            for d in drivers_of(i):
                for v in d.driver.variables:
                    t = v.targets[0].id
                    targets[t.name if t else None] = targets.get(t.name if t else None, 0) + 1
                if not d.is_valid:
                    print("INVALID DRIVER", i.name, d.data_path); bad += 1
    print("DRIVER TARGETS", targets)
    acts = [x.name for x in D.actions if x.users]
    print("ACTIONS WITH USERS", acts)
    print("SOUNDS", [s.name for s in D.sounds])
    print("OBJECTS", len(D.objects), "COLLECTIONS", sorted(c.name for c in D.collections))
    print("ASSETS", sorted((type(i).__name__, i.name) for k in ("collections", "worlds", "node_groups", "materials", "objects") for i in getattr(D, k) if i.asset_data))
    print("BAD", bad)

elif mode.startswith("tunnel"):
    if mode == "tunnel_kit":
        for o in list(D.objects):
            D.objects.remove(o)
        dst = append_collections(["KIT_Tunnel"], ["TunnelWorld"], ["TunnelComp"])
        sc.world = D.worlds["TunnelWorld"]
        sc.compositing_node_group = D.node_groups["TunnelComp"]
        sc.camera = D.objects["TunnelCam"]
        r = sc.render
        r.resolution_x, r.resolution_y, r.fps = 1080, 1920, 30
        sc.frame_start, sc.frame_end = 1, 206
        sc.view_settings.view_transform = "Standard"
        try:
            r.engine = "BLENDER_EEVEE"
        except TypeError as e:
            print("ENGINE", e)
    r = sc.render
    r.resolution_percentage = 20
    r.image_settings.file_format = "PNG"; r.image_settings.color_depth = "8"; r.image_settings.color_mode = "RGB"
    sc.frame_set(100)
    r.filepath = f"{outd}/{mode}_f100.png"
    bpy.ops.render.render(write_still=True)
    print("RENDERED", r.filepath, r.engine, sc.view_settings.view_transform)

elif mode.startswith("makyo"):
    curves = json.load(open("/Volumes/music/blender/makyo_assets/makyo_curves.json"))
    F = 900
    if mode == "makyo_kit":
        orig_scene = sc
        for o in list(D.objects):
            D.objects.remove(o)
        append_collections(["KIT_MAKYO_Shards", "KIT_MAKYO_Dust", "KIT_MAKYO_Mirror", "KIT_MAKYO_Light", "KIT_MAKYO_Cam", "KIT_CTRL"], ["MakyoWorld"], ["MakyoComp"])
        sc.world = D.worlds["MakyoWorld"]
        sc.compositing_node_group = D.node_groups["MakyoComp"]
        sc.camera = D.objects["MakyoCam"]
        r = sc.render
        r.resolution_x, r.resolution_y, r.fps = 2160, 3840, 30
        sc.frame_start, sc.frame_end = 1, 5452
        sc.view_settings.view_transform = "AgX"
        try:
            r.engine = "BLENDER_EEVEE"
        except TypeError as e:
            print("ENGINE", e)
        ctrl = D.objects["WOBAR_CTRL"]
        for k in curves:
            if isinstance(curves[k], list) and k in ctrl.keys():
                ctrl[k] = curves[k][F - 1]
        # hide_render keys from intro (dust hidden pre-drop) are stripped in the kit; F=900 is post-drop
    sc.frame_set(F)
    if mode == "makyo_kit":
        ctrl = D.objects["WOBAR_CTRL"]
        for k in curves:
            if isinstance(curves[k], list) and k in ctrl.keys():
                ctrl[k] = curves[k][F - 1]
        sc.frame_set(F)
    c = D.objects.get("WOBAR_CTRL") or D.objects.get("MAKYO_CTRL")
    print("CTRL@F", {k: round(c[k], 3) for k in ("kick_acc", "snare", "sec_density", "intact", "stream_base", "hat_env")})
    print("INSTANCES", instance_counts())
    r = sc.render
    r.resolution_percentage = 10
    r.image_settings.file_format = "PNG"; r.image_settings.color_depth = "8"; r.image_settings.color_mode = "RGB"
    r.filepath = f"{outd}/{mode}_f{F}.png"
    bpy.ops.render.render(write_still=True)
    print("RENDERED", r.filepath)
