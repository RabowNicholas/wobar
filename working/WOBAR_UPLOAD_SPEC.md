---
title: Wobar Upload Spec — release + post metadata
version: 1.1 (+ tags downgraded to hygiene — kill condition fired 2026-08-07)
created: 2026-08-06
last_updated: 2026-08-06
status: live — governing for retrieval fields
scope: What goes in the genre field, the tag fields and the distributor genre selector, per register. OWNS the retrieval layer. Does NOT own bio copy, pitch framing or the label swap table — those are the read layer and live in [[reference/WOBAR_COPY]].
dependencies: [[reference/WOBAR_COPY]], [[reference/WOBAR_SONIC]], [[working/RESEARCH_GENRE_VOCABULARY]]
---

# WOBAR UPLOAD SPEC

**Open this when uploading.** Same job as [[working/WOBAR_MASTER_CHECKLIST]] — the
procedure, not the reasoning. Reasoning is in
[[working/RESEARCH_GENRE_VOCABULARY]].

**Why this file exists:** the vault had a locked swap table for emails to labels and
**nothing at all for the field filled in on every single upload.** SoundCloud is the
priority surface ([[working/WOBAR_GROWTH_PLAN]]) and its genre field had no owner.

---

## §1 — THE THREE SLOTS

Genre words do three unrelated jobs. **Collapsing them is what put a flat comp list
in the EPK in 2026-07, and what put a 17-track phrase in a retrieval field.**

| Slot | Surfaces | Chosen by | Words |
|---|---|---|---|
| **Retrieval** | genre fields · tags · hashtags · distributor selector | **volume** | `dubstep` · `140` |
| **Positioning** | EPK lead · pitch · demo text · DM | **the recipient's register** | the swap table, [[reference/WOBAR_COPY]] |
| **Identity** | world-facing bio · wobar.music | **accuracy + world** | mechanism, no genre word |

**The rule:** where a genre word is **read**, accuracy and room-fit decide it. Where
a genre word is **searched**, reach decides it. **Never let the searched layer set
the read layer** — that inversion is the original 2026-07 failure.

**This file owns slot 1 only.**

---

## §2 — SOUNDCLOUD, PER REGISTER

Register definitions and weights: [[reference/WOBAR_SONIC]] six-register table.

| Register | Genre field | Tags |
|---|---|---|
| 1 deep/hypnotic · 2 hinge · 5 dub pivot | `Dubstep` | dubstep · 140 · deep dubstep |
| **3 dark/wonky 140** ← centre of mass | `Dubstep` | dubstep · 140 · bass |
| 4 rap flip | `Bass` | flip · bass · 140 |
| 6 psy-bass | `Bass` | bass · psychedelic bass · dubstep |

**`deep dubstep` earns its place in tags and nowhere else.** 21,318 SoundCloud
tracks, producer-intent in search, and a tag field is exactly where a
producer-facing word costs nothing. It is still barred from the read layer
([[reference/WOBAR_SONIC]] §Genre Positioning).

> ### ⚠ §4's kill condition FIRED, 2026-08-07 — tags are hygiene, not the lever
> This section was written assuming tags do the retrieval work. **Measured on
> Wobar's own catalogue, they don't — the two tracks that rank best in SoundCloud
> search carry no tags at all**, while the title carries the match. Genre-term
> queries (`dark wonky 140`, `deep dubstep 140`) return nothing of Wobar's in 50
> results.
>
> **What actually retrieves on SoundCloud is the TITLE.** The `Artist - Title
> (Wobar Flip)` convention is doing the work, unaided, and it is why the flips
> out-rank everything else. **Keep tags tidy; do not expect them to move anything.**
>
> **The genre field stays specified** — it costs nothing, it is one dropdown, and
> consistency across a catalogue is worth having whether or not it retrieves.
>
> **Method note, because it nearly cost a false rule:** the first read of this
> evidence produced a "competition density" finding built on raw play counts across
> tracks spanning 262 days of age. It died when release dates were pulled. See
> [[working/WOBAR_ACTIVE]] standing traps — *age-normalise before comparing.*

### 🔴 Barred from every retrieval field

| String | Why |
|---|---|
| **`wonky 140`** | **17 tracks on SoundCloud.** Not an unclaimed lane — a phrase nobody uses |
| **`dark 140`** | 1,538 tracks, **and it retrieves the wrong thing** — autocomplete gives *dark trap 140 bpm*, *dark type beat 140 bpm*. It belongs to hip-hop type beats |
| **`deep dub`** | Collides with dub reggae, dub techno and Dubai. Google treats it as a probable mistype of `deep dubstep` |

**Both of the first two survive as prose** in the EPK, where a human reads them and
they do no retrieval work. Barred here, kept there — that is the whole point of §1.

---

## §3 — BEATPORT / DISTRIBUTOR GENRE

**Select `140 / Deep Dubstep / Grime` (genre 95).**

Not because it describes the sound better — because it is where the lane's labels
and charts already sit throughout [[working/RESEARCH_LABEL_LANDSCAPE]], including
the six top-10 placements that corroborate the register table
([[reference/WOBAR_SONIC]]). The sibling genre, `Dubstep` (18), offers only Melodic
Dubstep and Midtempo as sub-genres and is not this lane.

**Recorded because it is a single irreversible choice per release, made inside a
distributor UI, that decides which chart the record competes on** — and nothing in
the vault said it. Beatport carries the two as *separate top-level genres*; there is
no parent to fall back to.

⚠ **Register 4 has no home here.** The rap-flip register is uncleared by
construction and cannot reach Beatport or any DSP ([[working/WOBAR_ACTIVE]] standing
traps). It is SoundCloud-native and this row does not apply to it.

⚠ **"Deep Dubstep" is not selectable on Beatport.** It appears only inside the genre
*title*. Do not go looking for it as a sub-genre or a tag — the platform named the
hedge and never implemented it.

---

## §4 — WHAT THIS SPEC DOES NOT CLAIM

The sweep behind it measured **corpus size and search volume. It did not measure
discovery** — whether a genre field or tag actually drives plays anywhere.

**The supported claim is the negative one: do not spend a retrieval field on a
string nobody types.** *"Use `dubstep` and you will be found"* is not supported and
should not be inferred from this file.

**Kill condition:** if a register's tags are ever measured against plays and the
ranking disagrees with §2, §2 loses. Nothing here outranks first-party evidence.

---

## §5 — OPEN

- **Artist- and label-name tags are untested — but already in use on YouTube.** The
  99-min set carries `of the trees`, `inzo`, `lsdream` in its tag field, alongside
  `melodic dubstep` (the highest-volume qualifier measured, 17.3 vs `deep dubstep`'s
  4.5). Nobody has checked whether adjacency tagging works on either platform; it is
  the most plausible untested retrieval mechanism left.
- **Register 4's genre field is unresolved and deliberately untouched.** dêtre splits
  his — `Dubstep` ×7 for the 140, `Hip-hop & Rap` ×6 for the flips. Wobar's flips are
  all filed `Dubstep` **and they are the best-performing tracks in the catalogue**,
  so there is no case for changing a working thing on one comp's practice. Recorded
  so the observation isn't lost, not as a pending change.
- **Apple Music and Spotify genre are not selectable** the way Beatport's is; they
  are assigned by distributor category and algorithm. Unverified what Wobar is
  currently filed as on either.
- **YouTube tags** are specified separately in [[reference/WOBAR_YOUTUBE]] and were
  brought into line 2026-08-06. They follow §1 and should not drift from §2.
