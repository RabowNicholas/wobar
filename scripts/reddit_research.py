#!/usr/bin/env python3
"""Reddit research harness for the WOBAR vault. Built 2026-08-03.

WHY THIS EXISTS -- the hard-won facts, so they are never rediscovered:

  1. WebSearch CANNOT reach Reddit. `site:reddit.com` returns nothing usable.
     A research round burned 200 search calls and opened ZERO threads.
  2. WebFetch is blocked at reddit.com.
  3. Reddit's .json endpoints are blocked (they serve an HTML shell).
  4. Plain old.reddit.com HTML over curl WORKS. That is the only path.
  5. Reddit rate-limits hard. Without throttling you get empty responses that
     look exactly like zero results.

  #5 caused a false finding to enter a research doc ("track endings are
  severely under-discussed") built entirely on rate-limit noise. Hence:

  *** A ZERO IS NOT AN ABSENCE UNTIL A CONTROL QUERY PASSES IN THE SAME PASS. ***

  This tool raises Blocked rather than returning an empty result, and prints
  "THIS IS A BLOCK, NOT AN ABSENCE". Do not defeat that behaviour.

  For absence testing, run a known-common control term in the same subreddit
  first; if the control fails, the whole sub's results are inconclusive.
  See working/RESEARCH_STORYTELLING.md sections 0 and 9.

Usage:
  reddit_research.py search <subreddit> "<query>" [--sort top|relevance|new] [--time all|year|month]
  reddit_research.py searchall "<query>"
  reddit_research.py thread <url> [--limit N]
  reddit_research.py verify <url>

Counts are page-1 only: 25 means ">=25 / saturated", not "exactly 25".
Reddit search also matches loosely, so a count is a coarse relative signal,
never a corpus measurement.
"""
import sys, re, html, json, time, urllib.parse, subprocess

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")


RATE_FILE = "/tmp/.reddit_tool_last_req"


def _throttle(min_gap=6.0):
    """Global cross-process throttle. Reddit blocks hard under concurrent load."""
    try:
        with open(RATE_FILE) as f:
            last = float(f.read().strip())
    except Exception:
        last = 0.0
    wait = min_gap - (time.time() - last)
    if wait > 0:
        time.sleep(wait)
    try:
        with open(RATE_FILE, "w") as f:
            f.write(str(time.time()))
    except Exception:
        pass


class Blocked(Exception):
    pass


def get(url, tries=5):
    """Returns page text. Raises Blocked if we never got a real page.

    CRITICAL: an empty/short response means RATE LIMITED, not 'no results'.
    Never let a caller treat a block as an absence finding.
    """
    for i in range(tries):
        _throttle()
        p = subprocess.run(
            ["curl", "-s", "-L", "-A", UA, "--max-time", "40",
             "-H", "Accept-Language: en-US,en;q=0.9", url],
            capture_output=True, text=True)
        t = p.stdout
        # A real old.reddit page is always large and has these markers.
        if len(t) > 15000 and ("search-result" in t or 'class="thing' in t
                               or "sitetable" in t):
            return t
        time.sleep(8 * (i + 1))  # 8,16,24,32s backoff
    raise Blocked(f"BLOCKED after {tries} tries (len={len(t)}) url={url}")


def clean(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()


def search(sub, query, sort="top", tspan="all"):
    q = urllib.parse.quote(query)
    if sub:
        url = (f"https://old.reddit.com/r/{sub}/search?q={q}&restrict_sr=on"
               f"&sort={sort}&t={tspan}")
    else:
        url = f"https://old.reddit.com/search?q={q}&sort={sort}&t={tspan}"
    try:
        t = get(url)
    except Blocked as e:
        print(f"QUERY: {query!r}  SUB: {sub or 'ALL'}")
        print(f"*** {e}")
        print("*** THIS IS A BLOCK, NOT AN ABSENCE. Do NOT record this query as "
              "'found nothing'. Wait and retry, or report it as a fetch failure.")
        return
    blocks = re.findall(r'<div class="[^"]*search-result-link[^"]*".*?(?=<div class="[^"]*search-result-link|<footer)', t, re.S)
    out = []
    for b in blocks:
        m_t = re.search(r'class="search-title[^"]*"[^>]*>(.*?)</a>', b, re.S)
        m_u = re.search(r'href="(https://old\.reddit\.com/r/[^"]+/comments/[^"]+)"', b)
        if not m_u:
            m_u = re.search(r'href="(/r/[^"]+/comments/[^"]+)"', b)
        m_s = re.search(r'class="search-score">([^<]*)</span>', b)
        m_c = re.search(r'class="search-comments[^"]*"[^>]*>([^<]*)<', b)
        m_d = re.search(r'datetime="([^"]+)"', b)
        m_sub = re.search(r'class="search-subreddit-link[^"]*"[^>]*>([^<]*)<', b)
        if not m_t:
            continue
        u = m_u.group(1) if m_u else ""
        if u.startswith("/"):
            u = "https://old.reddit.com" + u
        out.append({
            "title": clean(m_t.group(1)),
            "url": u.split("?")[0],
            "score": clean(m_s.group(1)) if m_s else "",
            "comments": clean(m_c.group(1)) if m_c else "",
            "date": m_d.group(1)[:10] if m_d else "",
            "subreddit": clean(m_sub.group(1)) if m_sub else (f"r/{sub}" if sub else ""),
        })
    print(f"QUERY: {query!r}  SUB: {sub or 'ALL'}  SORT: {sort}  TIME: {tspan}")
    print(f"RESULTS: {len(out)}")
    if not out:
        print("NO RESULTS -- record this as an absence finding with the exact query above.")
        if len(t) < 5000:
            print(f"(short response, possible block; first 200 chars: {t[:200]!r})")
    for r in out:
        print(json.dumps(r, ensure_ascii=False))


def thread(url, limit=40):
    url = url.split("?")[0].rstrip("/")
    url = url.replace("www.reddit.com", "old.reddit.com").replace("//reddit.com", "//old.reddit.com")
    if not url.startswith("http"):
        url = "https://old.reddit.com" + url
    try:
        t = get(url)
    except Blocked as e:
        print(f"*** {e}")
        print("*** BLOCK, not absence. Retry later or log as fetch failure.")
        return
    m_title = re.search(r'<a class="title[^"]*"[^>]*>(.*?)</a>', t, re.S)
    m_score = re.search(r'class="score unvoted"[^>]*>([^<]*)<', t)
    m_date = re.search(r'datetime="([^"]+)"', t)
    print(f"URL: {url}")
    print(f"TITLE: {clean(m_title.group(1)) if m_title else 'UNKNOWN'}")
    print(f"SCORE: {clean(m_score.group(1)) if m_score else 'UNKNOWN'}")
    print(f"DATE: {m_date.group(1)[:10] if m_date else 'UNKNOWN'}")
    body = re.search(r'<div class="expando"[^>]*>(.*?)</div>\s*</div>', t, re.S)
    if body:
        b = clean(body.group(1))
        if b:
            print(f"\nPOST BODY:\n{b[:2500]}")
    print("\n--- COMMENTS ---")
    entries = re.findall(
        r'<div class="entry unvoted">(.*?)</div>\s*</div>\s*</div>', t, re.S)
    n = 0
    for e in entries:
        au = re.search(r'class="author[^"]*"[^>]*>([^<]+)<', e)
        sc = re.search(r'class="score unvoted"[^>]*>([^<]*)<', e)
        md = re.search(r'<div class="md">(.*?)</div>', e, re.S)
        if not md:
            continue
        txt = clean(md.group(1))
        if len(txt) < 40:
            continue
        n += 1
        if n > limit:
            break
        print(f"\n[{n}] u/{au.group(1) if au else '?'} | {clean(sc.group(1)) if sc else 'no score'}")
        print(txt[:1800])
    if n == 0:
        print("NO COMMENTS PARSED (thread may be empty, removed, or layout changed).")


def verify(url):
    u = url.split("?")[0].replace("www.reddit.com", "old.reddit.com")
    try:
        t = get(u)
    except Blocked as e:
        print(json.dumps({"url": url, "resolves": None, "error": str(e)}))
        return
    exists = len(t) > 20000 and "comments" in t
    m_title = re.search(r'<a class="title[^"]*"[^>]*>(.*?)</a>', t, re.S)
    m_score = re.search(r'class="score unvoted"[^>]*>([^<]*)<', t)
    print(json.dumps({
        "url": url,
        "resolves": bool(exists),
        "title": clean(m_title.group(1)) if m_title else None,
        "score": clean(m_score.group(1)) if m_score else None,
        "bytes": len(t),
    }, ensure_ascii=False))


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        sys.exit(1)
    cmd = a[0]
    def opt(name, default):
        return a[a.index(name) + 1] if name in a else default
    if cmd == "search":
        search(a[1], a[2], opt("--sort", "top"), opt("--time", "all"))
    elif cmd == "searchall":
        search(None, a[1], opt("--sort", "top"), opt("--time", "all"))
    elif cmd == "thread":
        thread(a[1], int(opt("--limit", "40")))
    elif cmd == "verify":
        verify(a[1])
    else:
        print(__doc__)
