---
title: The Web Home — the Terminal You Wander
version: 0.1
last_updated: 2026-07-04
status: live — spec; the web home's form (a terminal/early-RPG world). Builds on the existing wobar-landing-page (Next 16 / Neon / Sanity / Three.js / jose / Twilio).
scope: The web home = the Ether made visible, built as a terminal you type into and wander. A wayfinder guide (not a guru) opens paths to Passages, music, and lore. Wanderers can leave offerings; Nick curates them in.
dependencies: [[reference/WOBAR_WORLD]], [[working/MIRROR_THRESHOLD_SPEC]], [[reference/WOBAR_OBSCURA]]
---

# THE WEB HOME — THE TERMINAL YOU WANDER

The web home is the **Ether made visible** (WOBAR_WORLD §7). Its form is a
**terminal** — text on black — that you explore by typing. **Wandering is the
verb of the world (§2); here it is the literal interaction.** The terminal renders
the void as an *interface* without ever depicting the sacred center (§8): text is
figurative, the mirror is approached, never shown.

Aesthetic: early-2000s dark terminal / early-RPG. Nostalgic, committed, memorable
(the Pit Viper / Moonglade lesson: commit to one era). Wobar-ized — desaturated
phosphor (bone/purple on off-black), grain, the two-broken-circles mark, a
generative canvas at the void's edge. Not green-hacker cliché; an **oracle
terminal that points inward.**

---

## THE DAEMON — the guide: a wayfinder, not a guru (the load-bearing rail)

**The guide is named `the daemon`** (locked 2026-07-04). Two meanings stacked: a
*daemon* (Unix) = a background process quietly running the system — terminal-native,
and literally something Nick *wrote* (the builder-self pulled into the lore); a
*daimon* (Greek) = a personal guiding spirit, and Socrates' daimonion was famous
for only ever saying *no* — it never told him what to do, it only warned him off.
A guide that guides *by deflection* is being exactly what a daemon has always
been. The anti-guru rail is encoded in the name.

`the daemon` is a presence in the terminal that helps you *use and explore* the
world — **never guides you through it.**

- **Teaches HOW, never WHAT/WHY.** "Type `passages` to read the written body." /
  "Type `listen`." / "Type `look` to see what's here." Pure wayfinding.
- **Never answers a real question.** Meaning, the self, advice, the future,
  interpretation, "what does the void mean," "who am I" — all deflected, in-voice,
  pointing back at the Wanderer: *"That's not mine to answer. Wander and see."* /
  *"The mirror answers that — not me. Keep going."*
- **Never reveals the cosmology or the Mirror (§8).** No lore-dump, no explaining
  the void, no depicting the center.
- **Empower, never instruct (§6.4, §8 — the sharpest edge).** The guide opens
  doors; it never walks you through them and never tells you what's behind them.

This is the single rule that decides whether the terminal elevates the world or
collapses it into a cult. A "wise Wobar that answers you" is the most
world-destroying thing we could build. The guide is a librarian of the dark, not
a sage.

---

## THE WORLD — paths the guide opens

A small, coherent **hub with paths** — not an infinite MUD (scope control). The
guide reveals these; you type to travel:

| Command | Leads to | Notes |
|---|---|---|
| `help` / `?` | how to move | the guide explains the mechanics only |
| `look` | what's here | reveals available paths in the current space |
| `passages` | the written body | list / read a **Passage** (per-EP void poems) |
| `listen` / `music` | songs / releases | play or link out; new drops surface here |
| `wander` / `lore` | lore fragments | void poems + world text, *found* by wandering |
| `mirror` | the door | the SMS crossing is *discovered* here — approach the mirror, receive the keyword; you never see it |
| `offer` / `leave` | contribute | leave an offering in the world (see below) |

The center (the Mirror) is the place you **approach but never reach**. Reaching
for it reflects your *own* inputs back — never Wobar's wisdom. Keep it empty.

**The terminal is the whole home (locked 2026-07-04 — full rebuild of
wobar-landing-page).** No simple front; everyone lands in the terminal. So the
*surface* must be frictionless — the first screen makes the paths obvious and
`listen` is reachable in ~2 keystrokes; a casual gets the music without realizing
they're "playing" anything. The *depth* stays optional (Moonglade rule): the
project stands without deep wandering; the Passages and lore reward the curious.
**Low door, deep room.**

---

## OFFERINGS — the contribution mechanic

Wanderers who explore can **leave something in the world.** They submit; it goes
to Nick; Nick decides if it's woven in.

- **In-world framing:** an *offering* left in the dark — a Wanderer's own writing,
  reflection, or fragment. On-brand because it points back at *them* (§5), not up
  at Nick. Not "fan mail"; a mark they leave on the world.
- **Flow:** `offer` → they write → stored `pending` → surfaces in Nick's review
  queue (`/admin`) → Nick accepts/declines → accepted offerings become *findable*
  by other Wanderers (a space of offerings, or woven into `lore`).
- **Curation is the point** (Nick's call: "given to me to see if they should be
  added in"). Moderation protects coherence and the tightrope.
- **Guardrail:** accepted offerings still obey the world — figurative, points-back,
  never guru. Nick's the filter.

---

## AI ARCHITECTURE — intent-routing, authored content

The guide *can* be AI (Nick's lane) — but built so it **cannot** answer real
questions. The safe shape:

- **Deterministic command core.** Exact commands (`help`, `look`, `passages`,
  `listen`, `mirror`, `offer`) are parsed directly — instant, free, no model.
- **AI as the natural-language front-end + deflector.** For fuzzy input ("i want
  to hear something new", "where do the poems live"), an LLM (Claude) classifies
  intent → routes to an allowed action, OR — if the input is a *real question* —
  returns an in-voice **deflection**. It never free-form answers, never generates
  lore.
- **All content is authored** (Sanity: Passages, poems, releases). The AI serves
  and routes; it never writes the world.
- **System-prompt rails (hard):** wayfinder role; navigate-or-deflect only; never
  answer/advise/diagnose/interpret; never reveal cosmology or the Mirror;
  empower-never-instruct; stay in the desaturated Sage-adjacent void voice;
  figurative only. Structured output: `{ action, target, line }`.
- **MVP = deterministic first.** Ship the command core + authored content. Layer
  the AI wayfinder/deflector second, behind the rails. (Authored is safe and
  finite; the LLM is a guarded enhancement, never the foundation.)

---

## DATA MODEL

**Sanity (authored content):**
- `passage` — per Portal EP: title, linked release/EP, the void poems, the seal
  (mark variant), slug.
- `loreFragment` (or reuse `poem`) — standalone void poems / world text found via
  `wander`.
- reuse `release` (music), `set`.
- (Optional) `space` / world-map config if the hub grows rooms.

**Neon (dynamic):**
```sql
create table offerings (
  id uuid primary key default gen_random_uuid(),
  body text not null,
  wanderer_phone text,            -- null if anonymous; set if crossed via the Mirror
  status text not null default 'pending' check (status in ('pending','accepted','declined')),
  created_at timestamptz not null default now(),
  reviewed_at timestamptz
);
-- optional: terminal_sessions / command_log for analytics + "where you've been"
```
Accepted offerings either promote into Sanity (a curated doc) or stay in Neon and
surface in the `lore` space.

---

## AESTHETIC + REUSE (against the existing repo)

- **Terminal UI:** monospaced, blinking cursor, off-black (`#0E0813`), desaturated
  phosphor (bone/wobar-purple), grain (`public/grain.svg`), the mark
  (`public/logo*.png`). An "ENTER" gate = the threshold.
- **Canvas at the void's edge:** reuse `PortalContainer` / `UnifiedCanvas` /
  `ActBackground` (Three.js + simplex-noise) — subtle, dark, felt, never depicting
  the center.
- **Reuse:** `lib/db` (Neon `sql`), Sanity pipeline (`lib/sanity`, schemas),
  `TextureOverlay`, `app/fonts`, `jose` auth for `/admin`.
- **Add:** the terminal route/component, the `passage` + `loreFragment` schemas,
  the `offerings` table + review UI in `/admin`, the AI wayfinder endpoint
  (`app/api/guide/route.ts`).

---

## DOCTRINE RAILS — the checklist for this surface
- Guide = wayfinder, not guru. Teaches HOW, never WHAT/WHY. Deflects real
  questions, in-voice (§6.4, §8).
- The Mirror is never shown; the center stays empty; you approach, never reach
  (§8).
- Content authored, never AI-generated. AI routes + deflects only.
- Figurative, sparse — no lore-dump/exposition (tightrope, §0.2).
- Offerings point back at the Wanderer; Nick curates (§5).
- Optional depth — the project stands without the terminal (Moonglade rule).

---

## BUILD ORDER
1. **Passages + lore in Sanity** — author the first `passage` + a few
   `loreFragment`s (needs content, non-blocking on code).
2. **Terminal shell** — the route/component, ENTER gate, command parser,
   deterministic paths (`help`/`look`/`passages`/`listen`/`lore`).
3. **`mirror` path** — discover the crossing inside the terminal; hand off the
   keyword (ties to MIRROR_THRESHOLD_SPEC).
4. **Offerings** — `offer` command + `offerings` table + review UI in `/admin`.
5. **AI wayfinder** — layer the intent-router + deflector behind the rails.

---

## RESOLVED (2026-07-04)
- **Offerings** = a Wanderer's own writing/reflection/fragment (points back at
  them).
- **Terminal = the whole home** — full rebuild of wobar-landing-page. Low door,
  deep room.
- **Guide MVP: deterministic-first, AI-second.** Yes.
- **The guide is named `the daemon`.**

## STILL OPEN
- Offering length/format limits (build-time).
- Name the world/terminal itself as a whole? (Parked.)
- WOBAR_WORLD reconciled: `the daemon` added to §9 lexicon; web-home form noted in
  §7.5.
