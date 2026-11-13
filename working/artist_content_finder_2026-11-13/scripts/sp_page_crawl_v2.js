// Spotify page crawler. Runs inside an open.spotify.com tab (Claude in Chrome).
// Reads only the rendered public pages: search -> exact-name artists -> artist page text.
// v2: fixes stale-results bug in v1 (about 2,000 false 'not found'). Usage: window.__names = [...]; window.__start = 0; then paste this file. Progress: window.__sp2.
// Output: window.__sp2.out, downloaded as acf_sp_<n>.json every CHUNK names (then moved by collect.py).
(() => {
  const CHUNK = 200, MAXC = 3;
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const norm = s => s.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim();
  const go = p => { history.pushState({}, '', p); dispatchEvent(new PopStateEvent('popstate')); };
  async function until(fn, ms = 7000) { const t0 = Date.now(); while (Date.now() - t0 < ms) { const v = fn(); if (v) return v; await sleep(200); } return null; }
  const save = (obj, name) => { (window.__saved = window.__saved || []).push([name, obj]); const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([JSON.stringify(obj)], { type: 'application/json' })); a.download = name; a.click(); };
  const S = window.__sp2 = { i: window.__start || 0, n: window.__names.length, out: [], stop: false, err: null, part: 0, t0: Date.now() };
  (async () => {
    for (; S.i < S.n && !S.stop; S.i++) {
      const name = window.__names[S.i];
      const rec = { name, cands: [] };
      try {
        const q = name.replace(/\s*\([A-Z]{2,3}\)\s*$/, '').trim();
        rec.q = q;
        let state = null;
        for (let tries = 0; tries < 3 && !state; tries++) {
          // mark old result links so a stale page is never read as the new search
          document.querySelectorAll('main a[href^="/artist/"]').forEach(a => a.setAttribute('data-acf', 'old'));
          go('/search/' + encodeURIComponent(q) + '/artists');
          const fresh = () => [...document.querySelectorAll('main a[href^="/artist/"]')].filter(a => !a.hasAttribute('data-acf'));
          state = await until(() => {
            const t = document.querySelector('main')?.innerText || '';
            if (/no results found/i.test(t) && document.title.includes(q)) return 'none';
            if (document.title.includes(q) && fresh().some(a => norm(a.textContent.trim()) === norm(q))) return 'ok';
            return null;
          }, 6000);
          if (!state && document.title.includes(q) && fresh().length >= 3) state = 'nomatch';
          if (!state) { go('/'); await sleep(1500); }
        }
        rec.search = state || 'timeout';
        if (state === null && /something went wrong|too many requests/i.test(document.querySelector('main')?.innerText || '')) { S.err = 'error page at ' + name; S.stop = true; break; }
        await sleep(500);
        const seen = new Set();
        const hits = state !== 'ok' ? [] : [...document.querySelectorAll('main a[href^="/artist/"]')].filter(a => !a.hasAttribute('data-acf'))
          .map(a => ({ id: a.getAttribute('href').split('/')[2], nm: a.textContent.trim() }))
          .filter(x => norm(x.nm) === norm(q) && !seen.has(x.id) && seen.add(x.id)).slice(0, MAXC);
        rec.nhits = hits.length;
        for (const h of hits) {
          const oldH = document.querySelector('main h1'); if (oldH) oldH.setAttribute('data-acf', 'old');
          go('/artist/' + h.id);
          const fresh = () => { const x = document.querySelector('main h1'); return x && !x.hasAttribute('data-acf') && norm(x.innerText) === norm(h.nm) ? x : null; };
          const ok = await until(fresh, 8000);
          if (ok) await until(() => /monthly listeners/.test(document.querySelector('main')?.innerText || ''), 1500);
          await sleep(250);
          const t = document.querySelector('main')?.innerText || '';
          if (/something went wrong|too many requests/i.test(t)) { S.err = 'error page at ' + name; S.stop = true; break; }
          const m = t.match(/([\d,]+) monthly listeners/);
          const main = document.querySelector('main');
          const rows = [...main.querySelectorAll('[data-testid="tracklist-row"]')].slice(0, 10).map(r => r.innerText.split('\n').filter(Boolean).slice(0, 5).join(' | '));
          const rels = [...new Set([...main.querySelectorAll('a[href^="/album/"]')].map(a => a.textContent.trim()).filter(Boolean))].slice(0, 20);
          const fans = [...new Set([...main.querySelectorAll('a[href^="/artist/"]')].filter(a => !a.getAttribute('href').includes(h.id)).map(a => a.getAttribute('href').split('/')[2] + '|' + a.textContent.trim()))].slice(0, 12);
          const tour = (t.match(/upcoming concerts \((\d+)\)/) || [])[1];
          rec.cands.push({ id: h.id, loaded: !!ok, ml: m ? +m[1].replace(/,/g, '') : null, rows, rels, fans, tour: tour ? +tour : 0 });
        }
      } catch (e) { rec.error = String(e); }
      S.out.push(rec);
      if (S.out.length >= CHUNK || S.i === S.n - 1) { save(S.out, `acf_sp2_${String(S.part).padStart(2, '0')}_${S.i}.json`); S.part++; S.out = []; }
    }
    if (S.out.length) { save(S.out, `acf_sp2_${String(S.part).padStart(2, '0')}_${S.i}_stop.json`); S.out = []; }
    S.done = true;
  })();
  return 'started at ' + S.i + ' of ' + S.n;
})();
