// Instagram profile reader (step 2b). Runs inside an instagram.com tab in Nick's logged-in Chrome. READ ONLY:
// no follows, likes, DMs, comments. Reads the rendered profile header: follower / post counts, account category,
// external bio link targets (Linktree etc., used to find TikTok). Never records emails or bio text.
// Usage: window.__ig_list = [[name, handle], ...]; paste (resumes from localStorage 'acf_ig'). Progress: window.__ig.
// Stops on any sign of a block ("try again later", challenge, login wall). Paced ~10 s per profile.
(() => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const go = p => { history.pushState({}, '', p); dispatchEvent(new PopStateEvent('popstate')); };
  async function until(fn, ms = 9000) { const t0 = Date.now(); while (Date.now() - t0 < ms) { const v = fn(); if (v) return v; await sleep(250); } return null; }
  const dec = h => { try { let u = new URL(h); if (u.hostname === 'l.instagram.com') u = new URL(u.searchParams.get('u')); return (u.hostname.replace(/^www\./, '') + u.pathname).replace(/\/$/, ''); } catch (e) { return null; } };
  const num = s => { const m = (s || '').replace(/,/g, '').match(/([\d.]+)\s*([KM])?/i); return m ? Math.round(+m[1] * ({ K: 1e3, M: 1e6 }[(m[2] || '').toUpperCase()] || 1)) : null; };
  const blocked = () => /try again later|suspicious activity|confirm it's you|help us confirm|log in to continue|we restrict certain activity/i.test(document.body.innerText.slice(0, 4000)) || /\/challenge\/|\/accounts\/login/.test(location.pathname);
  // resumable: Instagram sometimes hard-reloads the page; every record is saved, re-pasting skips done handles
  let prev = []; try { prev = JSON.parse(localStorage.getItem('acf_ig') || '[]'); } catch (e) {}
  if (window.__ig_list) localStorage.setItem('acf_ig_list', JSON.stringify(window.__ig_list));
  else window.__ig_list = JSON.parse(localStorage.getItem('acf_ig_list') || '[]');
  const done = new Set(prev.map(r => r.handle));
  window.__ig_list = window.__ig_list.filter(([n, h]) => !done.has(h));
  const S = window.__ig = { i: 0, n: window.__ig_list.length, out: prev, stop: false, err: null, t0: Date.now() };
  const backup = () => { try { localStorage.setItem('acf_ig', JSON.stringify(S.out)); } catch (e) {} };
  (async () => {
    for (; S.i < S.n && !S.stop; S.i++) {
      const [name, handle] = window.__ig_list[S.i];
      const rec = { name, handle };
      try {
        document.querySelectorAll('header').forEach(h => h.setAttribute('data-acf', 'old'));
        go('/' + handle + '/');
        const st = await until(() => {
          if (blocked()) return 'blocked';
          if (/sorry, this page isn't available|profile isn't available/i.test(document.querySelector('main')?.innerText || '')) return 'missing';
          const h = [...document.querySelectorAll('header')].find(h => !h.hasAttribute('data-acf') && /followers/i.test(h.innerText));
          return h ? 'ok' : null;
        });
        if (st === 'blocked' || blocked()) { S.err = 'blocked at ' + handle; S.stop = true; break; }
        rec.status = st || 'timeout';
        if (st === 'ok') {
          await sleep(600);
          const h = [...document.querySelectorAll('header')].find(h => !h.hasAttribute('data-acf'));
          const lines = h.innerText.split('\n').map(s => s.trim()).filter(Boolean);
          rec.followers = num(lines.find(l => /followers$/i.test(l)));
          rec.posts = num(lines.find(l => /posts?$/i.test(l)));
          rec.verified = !!h.querySelector('svg[aria-label="Verified"]');
          rec.links = [...new Set([...h.querySelectorAll('a[href]')].map(a => dec(a.href)).filter(x => x && !/^(instagram\.com|threads\.(com|net))/.test(x)))];
          rec.tt = (h.innerText.match(/tiktok\.com\/@?([\w.]+)/i) || [])[1] || null;
          rec.private = /this account is private/i.test(document.querySelector('main')?.innerText || '');
        }
      } catch (e) { rec.error = String(e); }
      S.out.push(rec); backup();
      await sleep(7000 + Math.random() * 4000);
    }
    backup(); S.done = true;
  })();
})();
