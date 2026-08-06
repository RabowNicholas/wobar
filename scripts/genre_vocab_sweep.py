#!/usr/bin/env python3
"""Genre-vocabulary sweep for the WOBAR vault. Built 2026-08-06.

Measures two of the three layers in working/RESEARCH_GENRE_VOCABULARY.md:

  SUPPLY-SIDE  SoundCloud api-v2 `total_results` per term.
  INTENT       Google + YouTube autocomplete — who is typing the word.

WHAT THIS TOOL CANNOT DO -- so it is not rediscovered:

  1. Google Trends (demand-side) is NOT scriptable. Cloudflare blocks the
     endpoint and widget tokens are session-bound. It must be run from inside
     a trends.google.com page in a browser. Call sequence is documented in
     RESEARCH_GENRE_VOCABULARY.md section 3. Trends 429s at ~4 calls.
  2. Beatport (institutional) is Cloudflare-blocked to scripts. Browser only.
  3. iTunes/Apple `resultCount` is a SATURATING CAP, not a corpus size. At
     limit=200, "dubstep" returned 188 and "deep dubstep" returned 200 -- the
     bigger term returned the smaller number. Do not add it back.
  4. Autocomplete's `gl` (geo) param does NOT meaningfully differentiate US
     from GB. A null geo difference here is a METHOD ARTIFACT, never evidence.

CONTROL DISCIPLINE (vault standing rule, RESEARCH_STORYTELLING section 9):
  A scraped zero is not an absence until a control passes in the same pass.
  Every sweep below runs controls first and REFUSES to print results if they
  fail. Do not defeat that behaviour.

Usage:
  genre_vocab_sweep.py soundcloud [terms...]
  genre_vocab_sweep.py intent     [terms...]
  genre_vocab_sweep.py all
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

DEFAULT_TERMS = [
    "dubstep", "deep dubstep", "deep dub", "140", "140 dubstep", "uk dubstep",
    "riddim", "tearout", "wonky", "wonky 140", "dark 140", "dub techno",
    "dub reggae", "future bass", "drum and bass",
]
INTENT_TERMS = [
    "dubstep", "deep dubstep", "deep dub", "140 dubstep", "140 bass", "riddim",
    "tearout dubstep", "wonky bass", "uk dubstep", "dark 140",
]


class Blocked(Exception):
    """Raised when a control fails. THIS IS A BLOCK, NOT AN ABSENCE."""


def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


# --------------------------------------------------------------- SoundCloud

def sc_client_id():
    """Scrape a fresh client_id. It ROTATES -- never hardcode one."""
    html = fetch("https://soundcloud.com/search?q=dubstep")
    m = re.search(r"window\.__sc_hydration\s*=\s*(\[.*?\]);", html, re.S)
    if not m:
        raise Blocked("no __sc_hydration on the search page")
    for blk in json.loads(m.group(1)):
        if blk.get("hydratable") == "apiClient":
            return blk["data"]["id"]
    raise Blocked("no apiClient block in hydration")


def sc_total(cid, kind, q):
    url = (f"https://api-v2.soundcloud.com/search/{kind}"
           f"?q={urllib.parse.quote(q)}&client_id={cid}&limit=1")
    return json.loads(fetch(url)).get("total_results")


def sweep_soundcloud(terms):
    cid = sc_client_id()
    print(f"client_id: {cid}\n")

    print("CONTROLS")
    big = sc_total(cid, "tracks", "remix")
    nonsense = sc_total(cid, "tracks", "qxzjvbwmp")
    print(f"  remix      {big:>12,}   (must be > 100,000)")
    print(f"  qxzjvbwmp  {nonsense:>12,}   (must be < 1,000)")
    if (big or 0) < 100_000 or (nonsense or 0) > 1_000:
        raise Blocked("controls failed -- THIS IS A BLOCK, NOT AN ABSENCE")
    print("  VERDICT: PASS\n")

    print(f"{'term':<16}{'tracks':>14}{'playlists':>13}{'users':>10}")
    print("-" * 53)
    for t in terms:
        row = []
        for kind in ("tracks", "playlists", "users"):
            try:
                row.append(sc_total(cid, kind, t))
            except Exception:                                    # noqa: BLE001
                row.append(None)
            time.sleep(0.35)
        cells = "".join(f"{v:,}".rjust(w) if isinstance(v, int) else "ERR".rjust(w)
                        for v, w in zip(row, (14, 13, 10)))
        print(f"{t:<16}{cells}")


# ------------------------------------------------------------- Autocomplete

def google_suggest(term, gl="us"):
    url = ("https://suggestqueries.google.com/complete/search?client=firefox"
           f"&hl=en&gl={gl}&q={urllib.parse.quote(term)}")
    return json.loads(fetch(url))[1]


def youtube_suggest(term, gl="us"):
    url = ("https://suggestqueries-clients6.youtube.com/complete/search"
           f"?client=youtube&ds=yt&hl=en&gl={gl}&q={urllib.parse.quote(term)}")
    txt = fetch(url)
    start, end = txt.find("("), txt.rfind(")")
    return [s[0] for s in json.loads(txt[start + 1:end])[1]]


def sweep_intent(terms):
    for name, fn in (("GOOGLE", google_suggest), ("YOUTUBE", youtube_suggest)):
        print(f"\n{name} AUTOCOMPLETE")
        ctrl = fn("weather")
        print(f"  control 'weather': {len(ctrl)} results "
              f"{'PASS' if ctrl else '*** BLOCKED -- NOT AN ABSENCE ***'}")
        if not ctrl:
            raise Blocked(f"{name} control failed")
        print()
        for t in terms:
            try:
                out = fn(t)
            except Exception as e:                               # noqa: BLE001
                print(f"  {t:<18} ERROR {e}")
                continue
            print(f"  {t:<18} [{len(out):>2}] " +
                  (" · ".join(out[:8]) if out else "(none)"))
            time.sleep(0.4)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    args = sys.argv[2:]
    try:
        if cmd in ("soundcloud", "all"):
            sweep_soundcloud(args or DEFAULT_TERMS)
        if cmd in ("intent", "all"):
            sweep_intent(args or INTENT_TERMS)
        if cmd not in ("soundcloud", "intent", "all"):
            print(__doc__)
            return 2
    except Blocked as e:
        print(f"\n*** BLOCKED: {e}\n*** THIS IS A BLOCK, NOT AN ABSENCE.",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
