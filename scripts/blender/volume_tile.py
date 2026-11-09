"""Volume tile 8 for the native 4K render (Nick, 2026-11-02: "tile 8 is good").

    blender -b hohlweg_3.blend -P volume_tile.py      (saves; safe to re-run)

At native 4K, tile 4 laid a diagonal woven striping over the GRUND fog and the ferns in front of it (9:14); tile 8
removes it, shafts slightly softer but distinct. ERNSTFALL 2:00 comes out x1.09 brighter (grade absorbs it); 5:52 and
10:40 unchanged (0.4% / 2.1% pixel change). Speed is not a factor: two identical tile-4 runs differed by up to 10%.
Sheet: renders/sh_tile_02/tile4_vs_8.png, zoom_914.png, zoom_200.png (tile4k_04 vs tile4k_08).
volumetric_tile_size is an ENUM: assign the string '8'; an int is silently ignored.
"""
import bpy, os

sc = bpy.context.scene
sc.eevee.volumetric_tile_size = "8"
assert sc.eevee.volumetric_tile_size == "8", sc.eevee.volumetric_tile_size
sc["volume_tile_applied"] = "2026-11-02 tile 8"
print("VT tile", sc.eevee.volumetric_tile_size, "samples", sc.eevee.volumetric_samples, flush=True)

if bpy.app.background and not os.environ.get("VT_NOSAVE"):
    bpy.ops.wm.save_mainfile(); print("VT saved", bpy.data.filepath, flush=True)
