// SoundCloud handle crawler (step 2). Runs inside a soundcloud.com tab (Claude in Chrome), logged-in session, read only.
// Reads only rendered public pages: people search -> exact-name profiles -> sidebar web links, bio, track titles, followers.
// Records only Instagram / TikTok / YouTube / X links (no emails or other contact data).
// Usage: window.__names = [...]; window.__start = 0; then paste this file. Progress: window.__sc.
// Results stay in window.__sc.out (and localStorage 'acf_sc' as a backup); Claude reads them out in chunks.
(() => {
  const MAXC = 2;
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const norm = s => s.normalize('NFKD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '');
  const go = p => { history.pushState({}, '', p); dispatchEvent(new PopStateEvent('popstate')); };
  async function until(fn, ms = 7000) { const t0 = Date.now(); while (Date.now() - t0 < ms) { const v = fn(); if (v) return v; await sleep(200); } return null; }
  const clean = h => { try { let u = new URL(h); if (u.hostname.endsWith('gate.sc')) u = new URL(u.searchParams.get('url')); return (u.hostname.replace(/^www\./, '') + u.pathname).replace(/\/$/, ''); } catch (e) { return null; } };
  const SOC = /^(instagram\.com|tiktok\.com|youtube\.com|youtu\.be|twitter\.com|x\.com)\//;
  // SoundCloud always loads an invisible reCAPTCHA anchor frame; only a visible challenge or block text counts
  const visible = f => { const r = f.getBoundingClientRect(); return r.width > 50 && r.height > 50 && getComputedStyle(f).visibility !== 'hidden'; };
  const blocked = () => /are you a robot|too many requests|rate limit|verify you are human/i.test(document.body.innerText.slice(0, 3000)) ||
    [...document.querySelectorAll('iframe[src*="captcha"], iframe[src*="bframe"]')].some(visible);
  const num = s => { const m = (s || '').replace(/,/g, '').match(/([\d.]+)\s*([KM])?/); return m ? Math.round(+m[1] * ({ K: 1e3, M: 1e6 }[m[2]] || 1)) : null; };
  const S = window.__sc = { i: window.__start || 0, n: window.__names.length, out: [], stop: false, err: null, t0: Date.now() };
  const backup = () => { try { localStorage.setItem('acf_sc', JSON.stringify(S.out)); } catch (e) {} };
  (async () => {
    for (; S.i < S.n && !S.stop; S.i++) {
      const name = window.__names[S.i];
      const q = name.replace(/\s*\([A-Z]{2,3}\)\s*$/, '').trim();
      const rec = { name, q, cands: [], others: [] };
      try {
        document.querySelectorAll('.searchList__item').forEach(li => li.setAttribute('data-acf', 'old'));
        go('/search/people?q=' + encodeURIComponent(q));
        const fresh = () => [...document.querySelectorAll('.searchList__item')].filter(li => !li.hasAttribute('data-acf') && li.querySelector('a[href]'));
        const st = await until(() => {
          if (!document.title.includes(q)) return null;
          if (fresh().length) return 'ok';
          if (/no results|sorry! we didn't find/i.test(document.querySelector('.l-main, main, body')?.innerText || '')) return 'none';
          return null;
        }, 8000);
        if (blocked()) { S.err = 'blocked at ' + name; S.stop = true; break; }
        rec.search = st || 'timeout';
        await sleep(400);
        const items = fresh().map(li => {
          const a = li.querySelector('a[href]'); const txt = li.innerText.split('\n').map(s => s.trim()).filter(Boolean);
          const f = txt.find(t => /followers?$/.test(t));
          return { path: a.getAttribute('href'), nm: txt[0], followers: num(f) };
        });
        const exact = items.filter(x => norm(x.nm) === norm(q)).sort((a, b) => (b.followers || 0) - (a.followers || 0));
        rec.others = items.filter(x => !exact.includes(x)).slice(0, 3).map(x => [x.nm, x.path, x.followers]);
        for (const c of exact.slice(0, MAXC)) {
          const oldH = document.querySelector('.profileHeaderInfo__userName'); if (oldH) oldH.setAttribute('data-acf', 'old');
          go(c.path);
          const ok = await until(() => { const h = document.querySelector('.profileHeaderInfo__userName'); return h && !h.hasAttribute('data-acf') && location.pathname === c.path ? h : null; }, 8000);
          if (blocked()) { S.err = 'blocked at ' + name; S.stop = true; break; }
          await until(() => document.querySelector('.web-profiles a') || document.querySelectorAll('.soundTitle__title').length, 2500);
          await sleep(500);
          const links = [...new Set([...document.querySelectorAll('.web-profiles a')].map(a => clean(a.href)).filter(h => h && SOC.test(h)))];
          const bio = document.querySelector('.truncatedUserDescription')?.innerText || '';
          const bioHandles = [...new Set((bio.match(/(?:instagram\.com|tiktok\.com)\/@?[\w.]+|(?:ig|insta|instagram|tiktok|tt)\s*[:\-]?\s*@[\w.]+/gi) || []))];
          const stats = [...document.querySelectorAll('.infoStats__stat')].map(s => s.innerText.replace(/\n/g, ' '));
          const titles = [...new Set([...document.querySelectorAll('.soundTitle__title span')].map(s => s.innerText.trim()))].slice(0, 12);
          rec.cands.push({ path: c.path, nm: c.nm, followers: c.followers, loaded: !!ok, verified: !!document.querySelector('.profileHeaderInfo .verifiedBadge, .profileHeaderInfo [class*="verified"]'), links, bioHandles, stats, titles });
        }
      } catch (e) { rec.error = String(e); }
      S.out.push(rec); if (S.out.length % 10 === 0) backup();
      await sleep(600);
    }
    backup(); S.done = true;
  })();
})();
