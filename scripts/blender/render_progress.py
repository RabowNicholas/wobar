"""Progress bar + ETA for a Blender -a render, read from its log (2026-10-26).

    python3 render_progress.py [LOG] [--watch [SECS]]

LOG defaults to /Volumes/music/blender/renders/tunnel_v1_final/render.log.
Reads the frame range from "Rendering animation (frames A..B)", counts "Saved:" lines,
and times the ETA off the mean of the last 10 frame times.
"""
import re
import sys
import time
from pathlib import Path

DEFAULT_LOG = "/Volumes/music/blender/renders/tunnel_v1_final/render.log"
RANGE = re.compile(r"Rendering animation \(frames (\d+)\.\.(\d+)\)")
SAVED = re.compile(r"Saved: '.*?(\d+)\.\w+'")
TIME = re.compile(r"\| Time: (?:(\d+):)?(\d+):(\d+\.\d+)")
SAMPLES = re.compile(r"Fra: (\d+) \| Rendering (\d+) / (\d+) samples")


def fmt(secs):
    h, rem = divmod(int(secs), 3600)
    m, s = divmod(rem, 60)
    return f"{h}h{m:02d}m" if h else f"{m}m{s:02d}s"


def status(log):
    text = Path(log).read_text(errors="replace")
    rng = RANGE.search(text)
    if not rng:
        return f"{log}: no frame range in log yet"
    start, end = int(rng[1]), int(rng[2])
    total = end - start + 1
    done = len(SAVED.findall(text))
    times = [int(h or 0) * 3600 + int(m) * 60 + float(s) for h, m, s in TIME.findall(text)]
    recent = times[-10:]
    per = sum(recent) / len(recent) if recent else 0

    # fraction of the frame in flight, from its last sample line
    partial = 0.0
    samples = SAMPLES.findall(text)
    if samples and done < total:
        _, n, of = samples[-1]
        partial = int(n) / int(of)

    frac = min((done + partial) / total, 1.0)
    width = 40
    fill = int(frac * width)
    bar = "█" * fill + "░" * (width - fill)
    line = f"[{bar}] {frac:6.1%}  {done}/{total} frames"
    if done >= total:
        return line + "  done"
    idle = time.time() - Path(log).stat().st_mtime
    if per and idle > max(3 * per, 120):
        return line + f"  STALLED: log silent for {fmt(idle)}"
    if per:
        eta = (total - done - partial) * per
        line += f"  {per:.1f}s/frame  ETA {fmt(eta)} (~{time.strftime('%H:%M', time.localtime(time.time() + eta))})"
    return line


def main():
    args = sys.argv[1:]
    watch = None
    if "--watch" in args:
        i = args.index("--watch")
        nxt = args[i + 1] if i + 1 < len(args) else ""
        watch = float(nxt) if nxt.replace(".", "", 1).isdigit() else 5.0
        del args[i : i + (2 if nxt.replace(".", "", 1).isdigit() else 1)]
    log = args[0] if args else DEFAULT_LOG
    if watch is None:
        print(status(log))
        return
    try:
        while True:
            line = status(log)
            print("\r\033[K" + line, end="", flush=True)
            if line.endswith("done"):
                print()
                return
            time.sleep(watch)
    except KeyboardInterrupt:
        print()


if __name__ == "__main__":
    main()
