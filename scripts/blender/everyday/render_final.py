"""Final Everyday render settings. Called by render_final.sh; can also run alone:
  blender -b /Volumes/music/blender/everyday_tunnel_v1.blend -P render_final.py -- [FIRST LAST]

Spec (2026-11-09 quality test, reference/blender_cases/EVERYDAY.md § Render):
  2160x3840, EEVEE 64 samples, motion blur on (shutter 0.5 as saved), 16-bit RGB PNG, frames 1-6583.
Resumable and shareable: existing frames are skipped and a placeholder is written when a frame starts,
so a restart continues where it stopped, and two machines can render into the same folder at once
without doing the same frame twice.
"""
import sys
import bpy

OUT = "/Volumes/music/blender/renders/everyday_final_4k/f_####"
SAMPLES = 64
first, last = 1, 6583
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if len(args) >= 2:
    first, last = int(args[0]), int(args[1])

sc = bpy.context.scene
r = sc.render
try:
    r.engine = "BLENDER_EEVEE"
except TypeError as e:
    print("ENGINE", e)
sc.eevee.taa_render_samples = SAMPLES
r.resolution_x, r.resolution_y, r.resolution_percentage = 2160, 3840, 100
r.use_motion_blur = True
r.image_settings.file_format = "PNG"
r.image_settings.color_mode = "RGB"
r.image_settings.color_depth = "16"
r.image_settings.compression = 15
r.use_overwrite = False
r.use_placeholder = True
sc.frame_start, sc.frame_end, sc.frame_step = first, last, 1
r.filepath = OUT
print(f"FINAL RENDER frames {first}-{last} | {r.resolution_x}x{r.resolution_y} | {SAMPLES} samples | "
      f"motion blur {r.use_motion_blur} shutter {r.motion_blur_shutter} | view {sc.view_settings.view_transform} | -> {OUT}",
      flush=True)
bpy.ops.render.render(animation=True)
print("FINAL RENDER DONE", flush=True)
