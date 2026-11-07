"""Assemble partial kits into the asset library file.  usage: blender -b --factory-startup -P assemble.py -- OUT PART..."""
import bpy, sys, os, uuid

args = sys.argv[sys.argv.index("--") + 1:]
out, parts = args[0], args[1:]
D = bpy.data
for o in list(D.objects):
    D.objects.remove(o)
sc = bpy.context.scene

for p in parts:
    with D.libraries.load(p, link=False) as (src, dst):
        dst.collections = [c for c in src.collections if c.startswith("KIT_")]
        dst.worlds = list(src.worlds)
        dst.node_groups = [n for n in src.node_groups if n in ("TunnelComp", "MakyoComp")]

# link only top-level KIT collections into the scene (children come along)
child_names = {ch.name for c in D.collections for ch in c.children}
for c in D.collections:
    if c.name.startswith("KIT_") and c.name not in child_names:
        sc.collection.children.link(c)

# strip dependencies that are not kit: legacy source collections, the MAKYO song
for c in [c for c in D.collections if not c.name.startswith("KIT_")]:
    print("REMOVE collection", c.name, [o.name for o in c.objects][:5])
    D.collections.remove(c)
for s in list(D.sounds):
    print("REMOVE sound", s.name)
    D.sounds.remove(s)

CATS = ["WOBAR", "WOBAR/Tunnel", "WOBAR/MAKYO", "WOBAR/Control", "WOBAR/Compositor", "WOBAR/World", "WOBAR/NodeGroups"]
cat_id = {c: str(uuid.uuid5(uuid.NAMESPACE_URL, "wobar-kit/" + c)) for c in CATS}

ASSETS = {
    ("collections", "KIT_Tunnel"): ("WOBAR/Tunnel", "Three nested TunnelWalls tunnels + vanishing light/orb + camera. tunnel_v1 look. Loops every 206 frames.", ["tunnel", "loop", "kaleido"]),
    ("collections", "KIT_MAKYO_Shards"): ("WOBAR/MAKYO", "ShardStream: 3000 mirror shards streaming past camera, kick-driven breaks (simulation zone - bake before render). Needs KIT_CTRL.", ["makyo", "shards", "audio"]),
    ("collections", "KIT_MAKYO_Dust"): ("WOBAR/MAKYO", "HatDust: 7000 hat-driven dust specks on the same stream. Needs KIT_CTRL.", ["makyo", "dust", "hats", "audio"]),
    ("collections", "KIT_MAKYO_Mirror"): ("WOBAR/MAKYO", "Cracked mirror that holds, then shatters toward camera at Drop Frame. Needs KIT_CTRL.", ["makyo", "mirror", "drop"]),
    ("collections", "KIT_MAKYO_Light"): ("WOBAR/MAKYO", "White-hot core, core light, halo, haze volume, kick rim light. Snare-driven brightness. Needs KIT_CTRL.", ["makyo", "light", "snare"]),
    ("collections", "KIT_MAKYO_Cam"): ("WOBAR/MAKYO", "28mm camera with kick jolt drivers. Needs KIT_CTRL.", ["makyo", "camera", "shake"]),
    ("collections", "KIT_CTRL"): ("WOBAR/Control", "WOBAR_CTRL empty: the audio control channels every driven part reads. Bake song curves onto its custom props.", ["control", "audio", "drivers"]),
    ("worlds", "TunnelWorld"): ("WOBAR/World", "Tunnel world: camera sees black, lighting sees white.", ["world"]),
    ("worlds", "MakyoWorld"): ("WOBAR/World", "MAKYO world: patina #5C7470 at 0.004 to camera, HDRI for reflections.", ["world", "hdri"]),
    ("node_groups", "TunnelComp"): ("WOBAR/Compositor", "Bloom + 4-way mirror kaleidoscope.", ["compositor", "kaleido"]),
    ("node_groups", "MakyoComp"): ("WOBAR/Compositor", "Two-stage bloom (thresholds 20 and 2).", ["compositor", "bloom"]),
    ("node_groups", "TunnelWalls"): ("WOBAR/NodeGroups", "Tunnel ring generator (geometry nodes).", ["gn", "tunnel"]),
    ("node_groups", "WireTubes"): ("WOBAR/NodeGroups", "Edges to tubes, Wire Radius.", ["gn", "wire"]),
    ("node_groups", "ShardStream"): ("WOBAR/NodeGroups", "Shard stream with simulation-zone breaks.", ["gn", "shards"]),
    ("node_groups", "HatDust"): ("WOBAR/NodeGroups", "Dust stream.", ["gn", "dust"]),
    ("node_groups", "MirrorShatter"): ("WOBAR/NodeGroups", "Mesh-island shatter at Drop Frame.", ["gn", "shatter"]),
}
for (kind, name), (cat, desc, tags) in ASSETS.items():
    idb = getattr(D, kind).get(name)
    if idb is None:
        print("MISSING", kind, name)
        continue
    idb.asset_mark()
    idb.asset_data.description = desc
    idb.asset_data.catalog_id = cat_id[cat]
    for t in tags:
        idb.asset_data.tags.new(t, skip_if_exists=True)
    idb.use_fake_user = True

with open(os.path.join(os.path.dirname(out), "blender_assets.cats.txt"), "w") as f:
    f.write("# This is an Asset Catalog Definition file for Blender.\nVERSION 1\n\n")
    for c in CATS:
        f.write(f"{cat_id[c]}:{c}:{c.replace('/', '-')}\n")

sc.world = D.worlds.get("TunnelWorld")
bpy.ops.wm.save_as_mainfile(filepath=out, compress=True)
print("SAVED", out, "assets:", sum(1 for kind in ("collections", "worlds", "node_groups") for i in getattr(D, kind) if i.asset_data))
