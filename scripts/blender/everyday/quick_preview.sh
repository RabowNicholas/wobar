#!/bin/zsh
# Quick preview of the Everyday tunnel: render a bar range headless, mux the master audio, open in QuickTime.
# usage: quick_preview.sh <first_bar> <last_bar> [percent=100] [samples=8] [name]
# Bars are 1-based at 140 BPM, 30 fps (bar n starts at frame round((n-1)*51.4286)+1).
set -e
B="/Applications/Blender 5.2.app/Contents/MacOS/Blender"     # not Blender.app (4.5) - FOOTGUNS V-1
BLEND=/Volumes/music/blender/everyday_tunnel_v1.blend
WAV="/Volumes/music/sessions/WIP (ACTIVE)/everday_flip Project/master_102226_everday_flip.wav"
RENDERS=/Volumes/music/blender/renders
b1=$1; b2=$2; pct=${3:-100}; smp=${4:-8}
f0=$(python3 -c "print(round(($b1-1)*60/140*4*30)+1)")
f1=$(python3 -c "print(round($b2*60/140*4*30))")
name=${5:-everyday_q_bars$(printf %03d $b1)-$(printf %03d $b2)_p${pct}_s${smp}_$(date +%H%M%S)}
out=$RENDERS/$name; mkdir -p $out
cat > $out/_render.py <<EOF
import bpy
sc = bpy.context.scene; r = sc.render
sc.eevee.taa_render_samples = $smp; r.resolution_percentage = $pct
r.image_settings.file_format = "JPEG"; r.image_settings.quality = 92
sc.frame_start, sc.frame_end = $f0, $f1
r.filepath = "$out/f_####"
bpy.ops.render.render(animation=True)
EOF
start=$(date +%s)
"$B" -b $BLEND -P $out/_render.py > $out/_render.log 2>&1
ss=$(python3 -c "print(($f0-1)/30)"); dur=$(python3 -c "print(($f1-$f0+1)/30)")
ffmpeg -loglevel error -y -framerate 30 -start_number $f0 -i $out/f_%04d.jpg -ss $ss -t $dur -i "$WAV" \
  -map 0:v -map 1:a -c:v libx264 -pix_fmt yuv420p -crf 16 -c:a aac -b:a 256k -shortest $out.mp4
echo "frames $f0-$f1 ($((f1-f0+1))) in $(( $(date +%s) - start ))s -> $out.mp4"
open -a "QuickTime Player" $out.mp4
