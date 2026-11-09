#!/bin/zsh
# Runs render_piece.py in Blender launch after launch until every frame in the range is done (2026-10-21).
# Gives up after 3 launches in a row that finish no new frame. Pause with: touch <out>/STOP (delete it to resume).
#
#   render_piece.sh [--blend FILE] [--out DIR] [--start N] [--end N] [--chunk N] [--min-free-gb N] [--no-forms]
#
# Defaults: the locked copy /Volumes/music/blender/hohlweg_final.blend, out /Volumes/music/assets/visualizers/hohlweg_v2.
# Everything except --blend is passed to render_piece.py.
set -u
HERE=${0:A:h}
BLENDER=/Applications/Blender.app/Contents/MacOS/Blender
BLEND=/Volumes/music/blender/hohlweg_final.blend
OUT=/Volumes/music/assets/visualizers/hohlweg_v2
PASS=()
while (( $# )); do
  case $1 in
    --blend) BLEND=$2; shift 2 ;;
    --out) OUT=$2; PASS+=(--out $2); shift 2 ;;
    *) PASS+=($1); shift ;;
  esac
done
[[ " ${PASS[*]} " == *" --out "* ]] || PASS+=(--out $OUT)
mkdir -p $OUT
LOG=$OUT/render_launches.log
stalls=0
remaining() { python3 $HERE/render_piece.py "${PASS[@]}" | sed -n 's/^\([0-9]*\)\/\([0-9]*\) frames.*/\2 \1/p' | awk '{print $1-$2}'; }
before=$(remaining)
echo "$(date '+%F %T') start: $before frames to do, blend $BLEND" | tee -a $LOG
while (( before > 0 )); do
  [[ -e $OUT/STOP ]] && { echo "$(date '+%F %T') STOP file present; not launching" | tee -a $LOG; exit 0; }
  $BLENDER -b $BLEND -P $HERE/render_piece.py -- "${PASS[@]}" 2>&1 | grep --line-buffered -E '^RP |Error|Traceback' | tee -a $LOG
  (( ${pipestatus[1]} == 3 )) && { echo "$(date '+%F %T') disk low; stopping" | tee -a $LOG; exit 3; }
  after=$(remaining)
  echo "$(date '+%F %T') launch exited: $after frames left (was $before)" | tee -a $LOG
  if (( after >= before )); then
    (( stalls++ ))
    (( stalls >= 3 )) && { echo "$(date '+%F %T') 3 launches without progress; stopping" | tee -a $LOG; exit 1; }
  else
    stalls=0
  fi
  before=$after
done
python3 $HERE/render_piece.py "${PASS[@]}"
echo "$(date '+%F %T') all frames done" | tee -a $LOG
