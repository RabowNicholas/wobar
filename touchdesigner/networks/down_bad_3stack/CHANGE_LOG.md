# CHANGE LOG — down_bad_3stack

Music video composite for the Down Bad remix (Dreamville / J Cole). Three identical synchronized copies of the source music video stacked vertically into a 9:16 portrait frame (720×1280, IG/TK catalog standard).

Act register: Act 4 Phase 1 (Physical Discharge — heavy halftime, 808s, body-feel). Full J Cole vocals preserved (source is the music video).

TD location: `/project1`

---

## v001 — In progress (2026-05-23)

**Composition:** 3 identical cells of the source music video stacked vertically with no gaps. Each cell ~720×427. Read as: same scene repeated, rhythmic visual tripling.

**Architecture target:**
```
movie_in (moviefileinTOP, 1280×720 source — Dreamville Down Bad ft JID, Bas, J Cole)
  ↓ (3 selectTOPs — efficient, share the same texture, no copy cost)
  ├─ sel_top
  ├─ sel_mid
  ├─ sel_bot
  ↓ (layoutTOP, 1 column × 3 rows, 720×1280 output)
  layout_stack
  ↓
  null_out
  ↓
  moviefileout (added later when render-ready)
```

**Notes:**
- Source aspect 16:9 (1280×720), target cell aspect ~16:9.5 (720×427) — close enough to avoid visible letterboxing or significant cropping; layoutTOP fit mode handles the small delta.
- Synchronized identical for v001. Possible v002+ variants: staggered start times (echo cascade), per-cell color grade variation, per-cell crop offset.

**Build status:** workspace folder created, CHANGE_LOG drafted. TD build pending.
