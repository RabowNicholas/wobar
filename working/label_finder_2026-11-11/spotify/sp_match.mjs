// Phase 1: match Beatport tracks to Spotify. Phase 2 (arg "create"): build one private playlist per label.
import fs from 'fs';
import { spotifyFetch, loadSpotifyConfig } from '/Users/nicholasrabow/mcp-servers/spotify-mcp-server/build/utils.js';
const DIR = '/Users/nicholasrabow/Desktop/vaults/Vaults/wobar/wobar/working/label_finder_2026-11-11/spotify';
const IN = `${DIR}/label_tracks.json`, OUT = `${DIR}/label_matches.json`, PL = `${DIR}/label_playlists.json`;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const norm = (s) => (s || '').toLowerCase().normalize('NFKD').replace(/[̀-ͯ]/g, '').replace(/\(.*?\)|\[.*?\]|feat\..*|ft\..*/g, '').replace(/[^a-z0-9]/g, '');

async function call(endpoint, opts = {}) {
  // Raw fetch so Spotify's Retry-After is honoured. Long waits stop the run instead of hammering.
  try { await spotifyFetch('me'); } catch (e) {}  // token refresh
  const c = loadSpotifyConfig();
  let url = `https://api.spotify.com/v1/${endpoint}`;
  if (opts.query) url += '?' + new URLSearchParams(opts.query).toString();
  for (let i = 0; i < 5; i++) {
    const r = await fetch(url, { method: opts.method || 'GET', headers: { Authorization: `Bearer ${c.accessToken}`, ...(opts.body ? { 'Content-Type': 'application/json' } : {}) }, ...(opts.body ? { body: JSON.stringify(opts.body) } : {}) });
    if (r.status === 429) {
      const ra = Number(r.headers.get('retry-after') || 30);
      if (ra > 120) { console.log(`STOP: rate limited, Spotify asks to wait ${ra} s`); process.exit(2); }
      console.log('rate limited, waiting', ra + 2, 's'); await sleep((ra + 2) * 1000); continue;
    }
    if (r.status >= 500) { await sleep(10000); continue; }
    if (!r.ok) throw new Error(`${r.status} ${(await r.text()).slice(0, 200)}`);
    const t = await r.text(); return t ? JSON.parse(t) : undefined;
  }
  throw new Error('gave up after retries');
}

function pick(items, t) {
  const want = norm(t.title), arts = t.artists.map(norm);
  const mix = (t.mix || '').toLowerCase();
  const isRemix = mix.includes('remix') || mix.includes('vip') || mix.includes('flip') || mix.includes('bootleg');
  const mixWord = norm(mix.replace(/remix|mix|edit|extended|original/g, ''));
  let best = null, bestScore = 0;
  for (const it of items || []) {
    if (!it) continue;
    const name = it.name || '';
    if (!norm(name).startsWith(want) && norm(name) !== want) continue;
    const ia = it.artists.map((a) => norm(a.name));
    const overlap = arts.filter((a) => ia.includes(a)).length;
    if (!overlap) continue;
    const nl = name.toLowerCase();
    let s = overlap * 2;
    if (isRemix) { if (mixWord && norm(nl).includes(mixWord)) s += 5; else continue; }
    else if (/remix|vip|flip/.test(nl) && !/remix|vip|flip/.test(t.title.toLowerCase())) continue;
    if (/extended/.test(nl)) s -= 1;
    if (s > bestScore) { bestScore = s; best = it; }
  }
  return best;
}

async function match() {
  const labels = JSON.parse(fs.readFileSync(IN, 'utf8'));
  const done = fs.existsSync(OUT) ? JSON.parse(fs.readFileSync(OUT, 'utf8')) : {};
  for (const L of labels) {
    done[L.label] = done[L.label] || {};
    let hit = 0;
    for (const t of L.tracks) {
      const k = `${t.title}|${t.mix}|${t.artists.join(',')}`;
      if (!(k in done[L.label])) {
        const q = `track:${t.title.replace(/"/g, '')} artist:${t.artists[0].replace(/"/g, '')}`;
        let r = await call('search', { query: { q, type: 'track', limit: 10 } });
        let m = pick(r?.tracks?.items, t);
        if (!m) {
          await sleep(3000);
          r = await call('search', { query: { q: `${t.title} ${t.artists[0]}`, type: 'track', limit: 10 } });
          m = pick(r?.tracks?.items, t);
        }
        done[L.label][k] = m ? { id: m.id, name: m.name, artists: m.artists.map((a) => a.name).join(', '), date: t.date } : null;
        fs.writeFileSync(OUT, JSON.stringify(done));
        await sleep(3000);
      }
      if (done[L.label][k]) hit++;
    }
    console.log(`${L.label}: ${hit}/${L.tracks.length}`);
  }
}

async function create() {
  const labels = JSON.parse(fs.readFileSync(IN, 'utf8'));
  const done = JSON.parse(fs.readFileSync(OUT, 'utf8'));
  const made = fs.existsSync(PL) ? JSON.parse(fs.readFileSync(PL, 'utf8')) : {};
  for (const L of labels) {
    if (made[L.label]) continue;
    const lm = done[L.label] || {};
    if (L.tracks.some((t) => !(`${t.title}|${t.mix}|${t.artists.join(',')}` in lm))) { console.log(`${L.label}: not fully matched yet, skipped`); continue; }
    const ids = [];
    for (const t of L.tracks) {
      const m = done[L.label][`${t.title}|${t.mix}|${t.artists.join(',')}`];
      if (m && !ids.includes(m.id)) ids.push(m.id);
    }
    if (!ids.length) { console.log(`${L.label}: no matches, skipped`); continue; }
    const p = await call('me/playlists', { method: 'POST', body: {
      name: `Label study: ${L.label}`,
      description: `${L.label}, releases from 2025-11-11 to 2026-11-11, newest first. Built from Beatport catalogue. ${ids.length} of ${L.tracks.length} tracks found on Spotify.`,
      public: false } });
    for (let i = 0; i < ids.length; i += 100) {
      await call(`playlists/${p.id}/items`, { method: 'POST', body: { uris: ids.slice(i, i + 100).map((x) => `spotify:track:${x}`) } });
    }
    made[L.label] = { id: p.id, url: p.external_urls.spotify, tracks: ids.length, of: L.tracks.length };
    fs.writeFileSync(PL, JSON.stringify(made, null, 1));
    console.log(`${L.label}: ${ids.length}/${L.tracks.length} ${p.external_urls.spotify}`);
    await sleep(300);
  }
}

(process.argv[2] === 'create' ? create() : match()).catch((e) => { console.error('ERR', e.message.slice(0, 300)); process.exit(1); });
