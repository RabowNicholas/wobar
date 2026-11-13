// Runs inside a soundcloud.com tab. Reads SoundCloud's public web-app data (user search, profile, tracks, web links).
// Approved by the artist 2026-11-11. ~1 request per 1.5 s. Saves raw candidates; matching is done locally in python.
// Usage: window.NAMES = [[labelId, "Label Name"], ...]; then paste this file.
window.scrun = {i: 0, n: NAMES.length, done: false, err: null};
(async () => {
  const base = 'https://api-v2.soundcloud.com';
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const q = async p => { await sleep(1500); const r = await fetch(base + p + (p.includes('?') ? '&' : '?') + 'client_id=' + SCID);
    if (r.status === 403 || r.status === 429) throw new Error('blocked ' + r.status); return r.status === 200 ? r.json() : {status: r.status}; };
  const norm = s => (s || '').toLowerCase().replace(/[^a-z0-9]/g, '').replace(/(records|recordings|music|llc|inc|label)/g, '');
  const out = {}; let part = 0;
  for (const [lid, name] of NAMES) {
    const s = await q('/search/users?q=' + encodeURIComponent(name) + '&limit=8');
    const users = (s.collection || []).map(u => ({id: u.id, permalink: u.permalink, username: u.username, followers: u.followers_count,
      verified: u.verified, desc: u.description, track_count: u.track_count, city: u.city, country: u.country_code}));
    // candidates: name-similar accounts, best followed first, max 3
    const n0 = norm(name);
    const cands = users.filter(u => { const a = norm(u.username), b = norm(u.permalink); return a && (a.includes(n0) || n0.includes(a) || b.includes(n0)); })
      .sort((a, b) => b.followers - a.followers).slice(0, 3);
    for (const c of cands) {
      const t = await q(`/users/${c.id}/tracks?limit=80`);
      c.titles = (t.collection || []).map(x => x.title);
      const w = await q(`/users/soundcloud:users:${c.id}/web-profiles`);
      c.links = Array.isArray(w) ? w.map(x => [x.title || x.network, x.url]) : [];
    }
    out[lid] = {name, users: users.map(u => ({id: u.id, permalink: u.permalink, username: u.username, followers: u.followers})), cands};
    scrun.i++;
    window.SCOUT = out;
  }
  // one download per run: SoundCloud's site gets one automatic download before Chrome asks
  const b = new Blob([JSON.stringify(out)], {type: 'application/json'}); const a = document.createElement('a');
  a.href = URL.createObjectURL(b); a.download = 'lf_sc_' + (window.SCTAG || 'run') + '.json'; document.body.appendChild(a); a.click(); a.remove();
  scrun.done = true;
})().catch(e => { scrun.err = String(e); });
'started ' + NAMES.length;
