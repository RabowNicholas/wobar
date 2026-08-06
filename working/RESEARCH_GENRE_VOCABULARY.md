---
title: Research — Genre Vocabulary Across Surfaces
version: 1.0
created: 2026-08-06
last_updated: 2026-08-06
status: raw research — unreviewed
scope: What the lane's genre words are worth on each surface. Measures three different things that are routinely conflated — what platforms PERMIT, what people LABEL, and what people SEARCH — and finds they disagree. Source of the retrieval/read split now governing [[reference/WOBAR_COPY]] and [[working/WOBAR_UPLOAD_SPEC]].
dependencies: [[reference/WOBAR_SONIC]], [[reference/WOBAR_COPY]], [[working/WOBAR_UPLOAD_SPEC]]
---

# RESEARCH — GENRE VOCABULARY ACROSS SURFACES

Commissioned 2026-08-06 off a live r/realdubstep thread (`redd.it/1vh8srz`, 54
comments) arguing about *dub* vs *deep dub* vs *dubstep*. The thread is a stigma
argument wearing a taxonomy costume, and it raised the question this file
answers: **what are these words actually worth, per surface.**

---

## §0 — THE DISTINCTION THE WHOLE FILE RESTS ON

"Search analytics" is three questions, not one. They are routinely collapsed, and
**they disagree with each other on every term measured here.**

| Layer | Question | Decides |
|---|---|---|
| **Institutional** | what does the platform's taxonomy *permit*? | a hard constraint — what you can pick at upload |
| **Supply-side** | how many people *label* things with it? | where the word is crowded or empty |
| **Demand-side** | how many people *search* it? | whether anyone is looking for you |

Beatport's `140 / Deep Dubstep / Grime` — the example that started this — is
**institutional only**. It says nothing about whether anybody searches the phrase.
As it turns out, almost nobody does.

---

## §1 — INSTITUTIONAL: what the platforms permit

**Method:** direct browser load, 2026-08-06 (Beatport is Cloudflare-blocked to
scripts; the browser passes). Sub-genre facet counts read from the live filter UI.

### Beatport carries TWO separate top-level genres

| Genre | ID | Sub-genres offered |
|---|---|---|
| **Dubstep** | 18 | Melodic Dubstep (1,795) · Midtempo (1,778) |
| **140 / Deep Dubstep / Grime** | 95 | **Grime (2,878) — and nothing else** |

Three findings, and the second is the one that matters:

1. **A release must choose one.** The choice is made once, inside a distributor UI,
   and it decides which chart the record competes on. ✅ verified
2. **"Deep Dubstep" is not a selectable category anywhere on Beatport.** It exists
   only inside a genre *title*. You cannot tag a track with it — you can only land
   in a bucket whose name happens to contain it. **The platform named the hedge and
   never implemented it.** ✅ verified
3. **Riddim and tearout — the two largest American styles — have no category at
   all**, under either genre. ✅ verified

⚠ `count: 10000` on Beatport's track listings is a **result cap, not a corpus
size.** Recorded because it looks exactly like a measurement. Same trap as iTunes
(below).

### Elsewhere

- **Bandcamp accepts `deep-dubstep`** as a discover tag — `/tag/deep-dubstep`
  resolves 200 to `/discover/deep-dubstep`. ✅ verified
- **The two marketplaces disagree** about whether the term exists as a category.

### ❌ Dead method, recorded so it isn't retried

**iTunes/Apple Search API `resultCount` is useless as a corpus measure.** It is
capped by the `limit` parameter and saturates: at `limit=200`, `dubstep` returned
188 and `deep dubstep` returned 200. The bigger term returned the smaller number.
**A saturated cap reads exactly like a real count** — same error class as the
scraped zero in [[working/RESEARCH_STORYTELLING]] §9.

---

## §2 — SUPPLY-SIDE: SoundCloud corpus

**Method:** `api-v2.soundcloud.com/search/{tracks,playlists,users}` → `total_results`.
Harness: `scripts/genre_vocab_sweep.py`. 2026-08-06.

**Controls passed in the same pass** — `remix` = 5,904,373 tracks (must be huge),
`qxzjvbwmp` = 0 (must be ~0). Per the standing rule, these numbers are real and not
rate-limit artifacts.

| Term | Tracks | Playlists | Users |
|---|---:|---:|---:|
| dubstep | 2,585,351 | 877,139 | 17,036 |
| riddim | 603,364 | 128,078 | 3,218 |
| drum and bass | 475,535 | 182,260 | 3,516 |
| 140 | 342,693 | 36,037 | 12,182 |
| future bass | 225,996 | 54,275 | 564 |
| dub techno | 82,208 | 15,749 | 173 |
| wonky | 46,801 | 11,303 | 932 |
| tearout | 38,064 | 5,921 | 54 |
| deep dub | 27,179 | 8,198 | 127 |
| **deep dubstep** | **21,318** | 4,204 | 43 |
| dub reggae | 19,476 | 15,028 | 177 |
| uk dubstep | 3,864 | 1,221 | 62 |
| 140 dubstep | 3,616 | 1,220 | 10 |
| dark 140 | 1,538 | 146 | 238 |
| **wonky 140** | **17** | 43 | 16 |

⚠ **What the number is:** SoundCloud matches loosely across title, description and
tags, so this is *how many items mention the phrase*, not *how many are tagged it*.
A coarse supply proxy — but a real corpus count, not a page-1 estimate.

⚠ **Large counts are estimates and they wobble. Small counts are stable.** Found on
a re-run minutes later in the same session: the `remix` control moved **5,904,373 →
6,993,479 (+18%)**, while `dubstep` moved 2,585,351 → 2,585,441 (+0.003%) and
`wonky 140` returned **17** both times. So SoundCloud appears to estimate totals
above some threshold and count them exactly below it.
**Consequence for reading this table: treat the top rows as order-of-magnitude only,
and the bottom rows as real.** Which is convenient, because every decision in §5
turns on the bottom rows.

**`wonky 140` returns 17 tracks.** That is the vault's lead descriptor, on the
platform [[working/WOBAR_GROWTH_PLAN]] names as the priority surface.

---

## §3 — DEMAND-SIDE: Google Trends

**Method:** Trends' own `explore` → `widgetdata` endpoints, called same-origin from
inside a `trends.google.com` page (the API is Cloudflare-blocked to scripts and
token-gated to outside callers). 5-year window, 2026-08-06.

### Worldwide, on one scale

| Term | 5y avg | Last 12mo |
|---|---:|---:|
| riddim | 41.8 | 46.7 |
| dubstep | 33.7 | 44.5 |
| deep dub | 1.3 | 3.1 |
| **deep dubstep** | **0.1** | **0.4** |
| 140 dubstep | 0.0 | 0.1 |

⚠ **Those zeros mean "under half a percent of peak," not "zero searches."** Trends
normalises to the largest series. Reported this way only because the comparison to
`dubstep` is the point.

### Rescaled against low-volume anchors, so the small terms resolve

| Term | 5y avg |
|---|---:|
| melodic dubstep | 17.3 |
| riddim dubstep | 14.9 |
| **uk dubstep** | **13.5** |
| **deep dubstep** | **4.5** |
| tearout dubstep | 0.9 |

**The reversal is the finding: `uk dubstep` is searched ~3× more than `deep
dubstep`.** The r/realdubstep thread dismissed "UK dubstep" as well-meant and
obsolete, and endorsed "deep dubstep" as the workable US compromise. **The scene's
preferred replacement is the less-searched of the two.**

### Geography — and what it could NOT establish

| Term | Regional breakdown |
|---|---|
| dubstep | Cuba 100 · New Zealand 65 · **United States 61** · Canada 54 · Estonia 53 · **United Kingdom 41** · Australia 41 |
| uk dubstep | **United Kingdom 100 — nothing else above threshold** |
| **deep dubstep** | **empty — insufficient data for any country** |

🔴 **The US/UK thesis is UNTESTED, not confirmed.** `dubstep` and `uk dubstep`
returned regional data in the same pass, so the control held and `deep dubstep`'s
emptiness is genuinely below-threshold rather than a block. But that cuts both
ways: **if "deep dubstep" were a high-volume American term we would see US:100, and
we cannot see it, because the term is too small to geolocate at all.**

**The r/realdubstep thread remains the only evidence that it is an American word,
and that is one room with one allegiance.** Do not let this file be cited as
confirmation.

### ❌ Second dead method

**Google autocomplete's `gl` (geo) parameter does not meaningfully differentiate.**
US and GB returned near-identical suggestions across all ten terms. YouTube's showed
minor variation, Google's essentially none. **A null result here is a method
artifact and must never be read as "no regional difference."**

---

## §4 — INTENT: who is typing these words

**Method:** Google + YouTube autocomplete (public, unauthenticated, reflects real
query logs). Control term `weather` passed on every pass. 2026-08-06.

**This was not the question asked, and it is the most useful thing in the sweep.**

| Query | Autocompletes to | Intent |
|---|---|---|
| `dubstep` | meaning · music · songs · artists · dance · bpm · gun | **listener** |
| `deep dubstep` | sample pack · sample pack free · serum presets · presets · labels · mix | **producer** |
| `140 dubstep` | sample pack · drum pattern · serum presets · labels · tutorial | **producer** |
| `tearout dubstep` | sample pack · serum presets · bpm · tutorial · reddit | **producer** |
| `uk dubstep` | sample pack · serum presets · labels · djs · *uk vs us dubstep* | **producer** |

On YouTube the same split holds and sharpens: `deep dubstep` → *mix · tutorial ·
sound design · ableton · serum 2*.

> **The qualifier words are searched by people MAKING the music. The bare word is
> searched by people LISTENING to it.**

Two collisions found in the same data:

- **`deep dub` does not resolve to this genre.** It competes with dub reggae, dub
  techno, and literally Dubai (`deep dubai pool`). Google's own second suggestion
  for it is `deep dubstep` — i.e. the engine treats it as a probable mistype.
- **`dark 140` belongs to hip-hop type beats** — *dark trap 140 bpm*, *dark type
  beat 140 bpm*, *dark beat 140 bpm*. It retrieves the wrong thing rather than
  nothing.
- **`wonky bass` collapses into an unrelated disco/house record** (*wonky bassline
  disco banger*) and TroyBoi. It does **not** surface the 2008 UK wonky/purple
  scene the word historically names.

---

## §5 — THE SYNTHESIS

Three layers, one pattern. **The vocabulary splits into words that are FOUND and
words that are PRECISE, and they barely overlap.**

| | Found | Precise |
|---|---|---|
| Words | dubstep · 140 · riddim | dark wonky 140 · deep dubstep |
| SC corpus | 2.6M · 343K · 603K | 17 · 1,538 · 21K |
| Search demand | real | at or below threshold |
| Who searches | **listeners** | **producers** |

**This maps onto a split already in the vault, which is why it is decision-relevant
rather than trivia:** [[working/WOBAR_ROADMAP]] §1's twelve-month goal is
**listeners**, while [[working/WOBAR_SOCIAL_PLAN]]'s target audience is **producers
and DJs at 2K–20K.** Both vocabularies are needed. Until now nothing said which word
served which goal.

**The sharpest consequence:** `wonky 140` at 17 tracks is not an unclaimed lane — it
is a phrase nobody uses. Nick's own recorded correction applies directly
([[working/RESEARCH_STORYTELLING]] §6.5): *saturation is the target; thin means
nobody cares; an unoccupied niche is usually uninteresting.*

**It does not follow that the phrase should be dropped.** It works as a *descriptor*
in prose read by a human A&R, where it does no retrieval work. It cannot be the word
anyone finds the project by — and the EPK was asking it to be both.

---

## §6 — WHAT THIS DOES NOT SUPPORT

Recorded so the file cannot be over-read later.

- **Adopting `uk dubstep`.** It is the most interesting number here — ~3× the demand
  of `deep dubstep` on ⅕ the supply, a genuine gap. **It is also inaccurate**, and
  adopting a word because it is underserved rather than because it is true is the
  DDD room-fit error running in reverse. Observation, not a lever.
- **"Use `dubstep` and you will be found."** This sweep measured corpus size and
  search volume. **It did not measure discovery** — whether a genre field or tag
  actually drives plays on any platform. The supported claim is only the negative
  one: *do not spend a retrieval field on a string nobody types.*
- **Reopening the education frame.** §4's producer-intent finding looks like it
  argues against the null result in [[working/WOBAR_CLOSED]]. It does not quite:
  that null was measured on **brand and strategy education for small artists**,
  while this demand is for **sound design and sample packs** — different product,
  different competition, genuinely untested. Flagged as a distinction, **not** a
  proposal.
- **n and provenance.** Every number here is first-party and dated 2026-08-06.
  SoundCloud's `client_id` rotates; the harness re-scrapes it per run.

---

## §7 — REPEATING THIS

`scripts/genre_vocab_sweep.py` — SoundCloud corpus + autocomplete intent, with
controls built in. Refuses to report numbers if a control fails.

**Google Trends cannot be scripted** — Cloudflare blocks the endpoint and the
widget tokens are session-bound. It must be run from inside a `trends.google.com`
page in a browser. The working call sequence is documented in §3's method note:
`explore` → read `widgets[].token` → `widgetdata/multiline` (timeseries) or
`widgetdata/comparedgeo` (regions), stripping the `)]}'` prefix. **Trends rate-limits
hard at ~4 calls; a 429 is a block, not an absence.**
