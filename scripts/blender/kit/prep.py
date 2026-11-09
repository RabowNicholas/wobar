"""Prep one source file into a partial kit .blend.  usage: blender -b SRC -P prep.py -- tunnel|makyo|everyday OUT"""
import bpy, sys

mode, out = sys.argv[sys.argv.index("--") + 1:][:2]
sc = bpy.context.scene
D = bpy.data


def coll(name, objs, parent=None):
    c = D.collections.new(name)
    (parent.children if parent else sc.collection.children).link(c)
    for o in objs:
        o = D.objects[o] if isinstance(o, str) else o
        c.objects.link(o)
    return c


def set_inputs(obj, values):
    m = next(m for m in obj.modifiers if m.type == "NODES")
    ins = m.properties.inputs
    for it in m.node_group.interface.items_tree:
        if it.item_type == "SOCKET" and it.in_out == "INPUT" and it.name in values:
            getattr(ins, it.identifier).value = values[it.name]


def lc_flags(c, lc=None):
    lc = lc or bpy.context.view_layer.layer_collection
    if lc.collection == c:
        return lc.exclude, lc.hide_viewport
    for ch in lc.children:
        r = lc_flags(c, ch)
        if r:
            return r


ids = set()

if mode == "tunnel":
    # Source = tunnel_v1_rounded_squares (newest TunnelWalls, superset). Restore tunnel_v1's look.
    v1 = {
        "Tunnel": dict(Width=6.0, Height=10.6, **{"Shape Spacing": 0.9, "Rings": 120, "Ring Gap": 1.0, "Shape Size": 0.7, "Rings Per Loop": 16, "Color Bands": 4.0, "Shrink From": 16.0, "Gone At": 7.0, "Color Offset": 0.0, "Spiral Arms": 2}),
        "Tunnel_Mid": dict(Width=3.6, Height=6.36, **{"Shape Spacing": 1.0, "Rings": 60, "Ring Gap": 2.0, "Shape Size": 0.45, "Rings Per Loop": 8, "Color Bands": 3.0, "Shrink From": 10.0, "Gone At": 4.0, "Color Offset": 0.33, "Spiral Arms": 2}),
        "Tunnel_Inner": dict(Width=2.1, Height=3.7, **{"Shape Spacing": 0.8, "Rings": 60, "Ring Gap": 2.0, "Shape Size": 0.3, "Rings Per Loop": 8, "Color Bands": 3.0, "Shrink From": 6.0, "Gone At": 2.5, "Color Offset": 0.66, "Spiral Arms": 5}),
    }
    for n, vals in v1.items():
        vals.update({"Round Rings": False, "Face Centre": False, "Ring Spin": 0})
        set_inputs(D.objects[n], vals)
    ng = D.node_groups["TunnelWalls"]
    src = next(n for n in ng.nodes if n.bl_idname == "GeometryNodeObjectInfo")
    src.inputs[0].default_value = D.objects["Shape_GlassSolid"]
    D.objects["Camera"].name = "TunnelCam"
    sc.world.name = "TunnelWorld"
    top = coll("KIT_Tunnel", ["Tunnel", "Tunnel_Mid", "Tunnel_Inner", "VanishingLight", "VanishingOrb", "TunnelCam"])
    shapes = coll("KIT_Tunnel_Shapes", [o for o in D.objects if o.name.startswith("Shape_")], parent=top)
    comp = sc.compositing_node_group
    print("TUNNEL comp", comp.name if comp else None)
    ids |= {top, sc.world}
    if comp:
        ids.add(comp)

elif mode == "everyday":
    # Source = everyday_tunnel_v1 (2026-11-09). The audio-reactive tunnel: TunnelWalls_AV (+ chaos and reveal
    # stages), ColorGlass with psych / glint / reveal flash / void, the snare-driven light, orb and glow.
    # Names that clash with KIT_Tunnel get an EV_ prefix. WOBAR_CTRL is NOT put in a collection: it comes along
    # as a driver dependency and assemble.py merges it into the one kit WOBAR_CTRL.
    ctrl = D.objects["WOBAR_CTRL"]
    animated = {fc.data_path[2:-2] for l in ctrl.animation_data.action.layers for s in l.strips
                for cb in s.channelbags for fc in cb.fcurves}
    ctrl.animation_data.action = None
    for k in animated:                      # song channels -> neutral; tuning constants keep Everyday's values
        ctrl[k] = 1.0 if k in ("reveal_r", "reveal_h") else 0.0   # reveal 1 = the whole tunnel shows
    ren = {"Tunnel": "EV_Tunnel", "Tunnel_Mid": "EV_Tunnel_Mid", "Tunnel_Inner": "EV_Tunnel_Inner",
           "VanishingLight": "EV_VanishingLight", "VanishingOrb": "EV_VanishingOrb", "Camera": "EverydayCam"}
    for o in [o for o in D.objects if o.name.startswith("Shape_")]:
        ren[o.name] = "EV_" + o.name
    for old, new in ren.items():
        o = D.objects[old]; o.name = new
        if o.data is not None and o.type in ("LIGHT", "CAMERA"):
            o.data.name = new
    for m in ("ColorGlass", "OrbGlow", "PillGlass", "TunnelGlow"):
        if m in D.materials:
            D.materials[m].name = "EV_" + m
    comp = sc.compositing_node_group
    comp.name = "EverydayComp"
    sc.world.name = "EverydayWorld"
    top = coll("KIT_Everyday", ["EV_Tunnel", "EV_Tunnel_Mid", "EV_Tunnel_Inner", "EV_VanishingLight",
                                "EV_VanishingOrb", "EverydayCam"])
    coll("KIT_Everyday_Shapes", [o for o in D.objects if o.name.startswith("EV_Shape_")], parent=top)
    for o in D.objects:
        if o.name.startswith("EV_Shape_"):
            o.hide_render = True
    print("EVERYDAY neutralised", len(animated), "channels; renamed", len(ren))
    ids |= {top, sc.world, comp}

else:
    # Source = makyo_intro (latest MAKYO save, Nov 4). Strip song-specific animation.
    for c in ("ShardKit", "FracPieces", "FracTables", "Collection"):
        print("VIS", c, "exclude/hide", lc_flags(D.collections[c]), "coll.hide_render", D.collections[c].hide_render)
    print("K_speck hide_render", D.objects["K_speck"].hide_render, "K_shard_0 hide_render", D.objects["K_shard_0"].hide_render)

    ctrl = D.objects["MAKYO_CTRL"]
    ctrl.name = "WOBAR_CTRL"
    ctrl.animation_data.action = None
    hd = D.objects["HatDust"]
    if hd.animation_data:
        hd.animation_data.action = None
    hd.hide_render = hd.hide_viewport = False
    # neutral signal values; tuning constants kept as MAKYO shipped them
    neutral = dict(snare=0.0, kick_acc=0.0, kick_idx=0.0, kick_vel=0.0, kick_flash=0.0, vortex_acc=0.0, low=0.0,
                   hat_env=0.0, hat_idx=0.0, hat_bright=0.0, sec_density=1.0, sec_glow=1.0, sec_core=1.0,
                   stream_base=0.0, intact=0.0, crack=0.0, drop_flash=0.0, jolt_x=0.0, jolt_z=0.0, jolt_r=0.0, break_on=1.0)
    for k, v in neutral.items():
        ctrl[k] = v
    D.objects["Cam"].name = "MakyoCam"

    # source collections: mirror their original "excluded" state as collection-level hide_render
    for c in ("ShardKit", "FracPieces", "FracTables"):
        ex = lc_flags(D.collections[c])
        if ex and ex[0]:
            D.collections[c].hide_render = True
    D.collections["ShardKit"].name = "KIT_MAKYO_ShardKit"
    D.collections["FracPieces"].name = "KIT_MAKYO_FracPieces"
    D.collections["FracTables"].name = "KIT_MAKYO_FracTables"

    shards = coll("KIT_MAKYO_Shards", ["ShardStream"])
    for c in ("KIT_MAKYO_ShardKit", "KIT_MAKYO_FracPieces", "KIT_MAKYO_FracTables"):
        # re-parent under the shard part
        for parent in [sc.collection] + list(D.collections):
            if parent != shards and D.collections[c].name in parent.children:
                parent.children.unlink(D.collections[c])
        shards.children.link(D.collections[c])
    dust = coll("KIT_MAKYO_Dust", ["HatDust"])
    coll("KIT_MAKYO_DustSrc", ["K_speck"], parent=dust)
    D.objects["K_speck"].hide_render = True
    mirror = coll("KIT_MAKYO_Mirror", ["MirrorPieces", "MirrorCracks", "IntactMirror"])
    light = coll("KIT_MAKYO_Light", ["Core", "CoreLight", "Halo", "Haze", "KickRim"])
    cam = coll("KIT_MAKYO_Cam", ["MakyoCam"])
    ctl = coll("KIT_CTRL", ["WOBAR_CTRL"])
    comp = sc.compositing_node_group
    print("MAKYO comp", comp.name if comp else None)
    ids |= {shards, dust, mirror, light, cam, ctl, sc.world}
    if comp:
        ids.add(comp)

bpy.data.libraries.write(out, ids, fake_user=True)
print("WROTE", out, sorted(i.name for i in ids))
