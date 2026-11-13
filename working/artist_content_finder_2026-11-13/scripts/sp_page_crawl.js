// Spotify page crawler. Runs inside an open.spotify.com tab (Claude in Chrome).
// Reads only the rendered public pages: search -> exact-name artists -> artist page text.
// Usage: window.__names = [...]; window.__start = 0; then paste this file. Progress: window.__sp.
// Output: window.__sp.out, downloaded as acf_sp_<n>.json every CHUNK names (then moved by collect.py).
(() => {
  const CHUNK = 200, MAXC = 3;
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const norm = s => s.normalize('NFKD').replace(/[̀-ͯ]/g, '').toLowerCase().trim();
  const go = p => { history.pushState({}, '', p); dispatchEvent(new PopStateEvent('popstate')); };
  async function until(fn, ms = 7000) { const t0 = Date.now(); while (Date.now() - t0 < ms) { const v = fn(); if (v) return v; await sleep(200); } return null; }
  const save = (obj, name) => { (window.__saved = window.__saved || []).push([name, obj]); const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([JSON.stringify(obj)], { type: 'application/json' })); a.download = name; a.click(); };
  const S = window.__sp = { i: window.__start || 0, n: window.__names.length, out: [], stop: false, err: null, part: 0, t0: Date.now() };
  (async () => {
    for (; S.i < S.n && !S.stop; S.i++) {
      const name = window.__names[S.i];
      const rec = { name, cands: [] };
      try {
        go('/search/' + encodeURIComponent(name) + '/artists');
        await until(() => document.title.includes(name) && document.querySelector('main a[href^="/artist/"]'), 6000);
        await sleep(400);
        const seen = new Set();
        const hits = [...document.querySelectorAll('main a[href^="/artist/"]')]
          .map(a => ({ id: a.getAttribute('href').split('/')[2], nm: a.textContent.trim() }))
          .filter(x => norm(x.nm) === norm(name) && !seen.has(x.id) && seen.add(x.id)).slice(0, MAXC);
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
      if (S.out.length >= CHUNK || S.i === S.n - 1) { save(S.out, `acf_sp_${String(S.part).padStart(2, '0')}_${S.i}.json`); S.part++; S.out = []; }
    }
    if (S.out.length) { save(S.out, `acf_sp_${String(S.part).padStart(2, '0')}_${S.i}_stop.json`); S.out = []; }
    S.done = true;
  })();
  return 'started at ' + S.i + ' of ' + S.n;
})();
