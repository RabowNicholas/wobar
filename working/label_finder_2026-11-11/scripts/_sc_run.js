window.SCTAG='main'; window.NAMES=[[56129, "A Records"], [68768, "Reinelex Records"], [80849, "19K"], [82292, "DirtySnatcha Records"], [97630, "Cimmerian Records"], [98363, "LDH Records"], [104173, "Station Underground"], [108075, "Sound in Picture"], [126144, "Lumasi Music"], [131208, "ZOT Records"], [166303, "Arctic Empire"], [168391, "Buku"], [175901, "Left Coast Records"], [378148, "Emengy Bass"], [7505, "Tru Thoughts"], [11966, "Amorphous Music"], [13396, "Wheel & Deal Records"], [14081, "Never Say Die Records"], [14690, "Deep Medi Musik"], [23236, "Kannibalen Records"], [23412, "Monstercat"], [24198, "Artikal Music UK"], [24539, "Gravitas Recordings"], [52116, "Full Flex Audio"], [55847, "1985 Music"], [56364, "Crucast"], [58064, "Bassweight Records"], [67064, "Discovery Project (Insomniac Records)"], [68956, "Ophelia"], [73191, "Manuka"], [73587, "Gud Vibrations"], [74173, "Overview Music"], [74919, "Incurzion Audio"], [77607, "Interval Audio"], [84691, "Grottingham"], [89126, "WiddFam"], [90307, "Morii Records"], [90858, "PullUp Recordings"], [91551, "DPMO"], [92872, "Lost In Dreams"], [96746, "Rude Service"], [98503, "MONTA"], [103220, "Neoluminum"], [104949, "Gemini Gemini"], [106994, "HypnoVizion Records Inc."], [107385, "Aspire Higher"], [110914, "Bad Medic Records"], [112736, "Sounds Of Mayhem"], [116122, "Boom Records LLC"], [117522, "cd91x"], [121985, "VOLPEVERSE"], [125074, "Mersiv Sound Music"], [126568, "oury"], [126959, "Continua MGMT"], [127779, "SHINE LIGHT RECORDS"], [127927, "Field Trip Records"], [127988, "Beat Intelligence Network"], [129522, "GRiZ LLC"], [130914, "ANTAGONIST"], [131258, "Port Zero"], [147320, "Artist Influence"], [149795, "Good Dub."], [18130, "UKF"], [43229, "Deep Dark & Dangerous"], [65158, "Bassrush Records"], [68217, "Wormhole Music Group"], [69987, "Deadbeats"], [72037, "Jadu Dala"], [110315, "Wakaan"], [78866, "Cyclops Recordings"], [78868, "Drama Club Recordings"], [90526, "Subsidia"], [105054, "Circus Electric"], [109502, "Wubaholics"], [113575, "Good Society"], [115076, "Memory Palace"], [126878, "Circus Records"], [129124, "Local Void"], [373903, "Disciple"], [40841, "SubCarbon Records"], [47581, "DUPLOC"], [68422, "Locus Sound"], [73029, "Infernal Sounds"], [90781, "Odyzey Music"], [150059, "Trippy Bee Records"]];
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
