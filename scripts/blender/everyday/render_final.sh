#!/bin/zsh
# Final Everyday render: 4K, 64 samples, motion blur, 16-bit PNG -> then the delivery encodes.
#
# usage:   scripts/blender/everyday/render_final.sh [FIRST LAST]
#          BLENDER=/path/to/Blender scripts/blender/everyday/render_final.sh     (if 5.2 lives elsewhere)
#          scripts/blender/everyday/render_final.sh encode                         (encodes only, frames done)
#
# - Must be Blender 5.2 (the file is 5.2; 4.5 misreads it - FOOTGUNS V-1).
# - Resumable: re-run the same command after any stop; finished frames are skipped.
# - Two machines can share it: run it on both at once, same folder - placeholders stop double work.
#   The encode step runs when this machine's range finishes; if the other machine is still going,
#   frames will be missing, so wait and run `render_final.sh encode` once every frame exists.
# - ~250 GB of frames (6583 x ~38 MB at 16-bit; measured on frame 3400). The drive had 365 GB free on 2026-11-09. Keep the Mac awake and the drive mounted (caffeinate does the first).
set -e
B=${BLENDER:-"/Applications/Blender 5.2.app/Contents/MacOS/Blender"}
DIR=${0:A:h}
BLEND=/Volumes/music/blender/everyday_tunnel_v1.blend
WAV="/Volumes/music/sessions/FINISHED/flips/everday_flip Project/master_102226_everday_flip.wav"
OUT=/Volumes/music/blender/renders/everyday_final_4k
N=6583
mkdir -p $OUT/delivery

[[ -x "$B" ]] || { echo "Blender not found at $B - set BLENDER=..."; exit 1; }
"$B" -b --version | head -1 | grep -q "Blender 5.2" || { echo "Not Blender 5.2: $("$B" -b --version | head -1)"; exit 1; }
[[ -f $BLEND ]] || { echo "Drive not mounted? $BLEND missing"; exit 1; }

if [[ "$1" != "encode" ]]; then
  start=$(date +%s)
  caffeinate -i "$B" -b $BLEND -P $DIR/render_final.py -- ${1:-1} ${2:-$N} 2>&1 | tee -a $OUT/_render.log | grep -E "FINAL RENDER|Error|Traceback" || true
  echo "render pass finished in $(( ($(date +%s) - start) / 60 )) min"
fi

have=$(ls $OUT/f_*.png 2>/dev/null | wc -l | tr -d ' ')
small=$(find $OUT -name 'f_*.png' -empty | wc -l | tr -d ' ')     # 0-byte placeholders = still rendering elsewhere
if [[ $have -lt $N || $small -gt 0 ]]; then
  echo "frames present $have / $N, unfinished placeholders $small - not encoding yet. Run: $0 encode"
  exit 0
fi

echo "encoding deliverables..."
# master: 4K ProRes 422 HQ (10-bit) - the archive copy everything else is made from
ffmpeg -loglevel error -y -framerate 30 -i $OUT/f_%04d.png -i "$WAV" -map 0:v -map 1:a \
  -c:v prores_ks -profile:v 3 -pix_fmt yuv422p10le -c:a pcm_s24le -shortest $OUT/delivery/everyday_4k_master_prores.mov
# YouTube: 4K H.264 high bitrate (upload in 4K so YouTube serves its better encode)
ffmpeg -loglevel error -y -i $OUT/delivery/everyday_4k_master_prores.mov -c:v libx264 -preset slow -crf 14 \
  -pix_fmt yuv420p -profile:v high -c:a aac -b:a 320k -movflags +faststart $OUT/delivery/everyday_4k_youtube.mp4
# IG / TikTok: downscaled 1080x1920 from the 4K master (cleaner than a native 1080 render)
ffmpeg -loglevel error -y -i $OUT/delivery/everyday_4k_master_prores.mov -vf "scale=1080:1920:flags=lanczos" \
  -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -profile:v high -c:a aac -b:a 320k -movflags +faststart \
  $OUT/delivery/everyday_1080_social.mp4
ls -la $OUT/delivery
