---
title: Research plan — brand psychology for music projects
version: 1.0
created: 2026-08-04
last_updated: 2026-08-04
status: ready to run — blocked on WebSearch budget
scope: The unrun research round for the brand-psychology sibling series. Briefs are written to be pasted straight into subagents. Not findings — a plan.
dependencies: [[working/WOBAR_GIVEBACK_NICHE]], [[working/RESEARCH_STORYTELLING]]
---

# RESEARCH PLAN — BRAND PSYCHOLOGY FOR MUSIC PROJECTS

**Why this exists as a doc rather than a completed round:** the session's WebSearch budget (200 calls) was exhausted by the storytelling round's failed Reddit agents before this could run. WebFetch still works, so *retrieval* is possible and *discovery* is not — and the part of this round that most needs discovery is the evidence war. Running it half would produce a one-sided map that looks complete. Parked deliberately.

**To run it:** raise `CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION`, or start a fresh session. The six briefs below are ready to paste.

---

## §1 — WHAT THIS ROUND IS FOR

The **second branch** of give-back ([[working/WOBAR_GIVEBACK_NICHE]] is the first). A sibling, not a child — it shares the audience, not the thesis.

**The sibling's spine, in Nick's words:**

> Brand is what ties together every release, every show, every set — **a way to have intention behind every action.** It's really easy to get lost on the marketing side of music.

**Planned series:** brand archetypes · brand voice · visual identity — online, live and physical.

### Three decisions already locked

1. **Posture: curator, not judge.** Surface the evidence war; take no side. *"I don't want to lock myself into one door — I want to talk about what everyone else is already talking about and put it in a format that is digestible on social media."*
   **The failure mode is mush**, and it conflicts with the standing need for strong opinions stated as fact. **Resolution: strong opinions on individual claims, no allegiance to a camp.** *"This specific idea is weak, here's why"* travels. *"I'm an Ehrenberg-Bass guy"* recruits enemies and boxes you in.
2. **No teardowns yet.** Landscape and method only. Actual artist teardowns are a later conversation.
3. **Credential posture: analysis, not testimony.** Never *"look what I did, it worked."* Authority is borrowed from an established body of knowledge, the way a critic's is — which also resolves the objection that rung 6 of the scale ladder was untellable. **Teardowns are demonstration of someone else's work, so they satisfy the show-don't-explain constraint without claiming a result.**

---

## §2 — SOURCE STRATEGY — INVERTED FROM THE LAST ROUND

The storytelling round was Reddit-primary because craft discourse lives there. **This round is not.** Brand theory lives in academic work, practitioner books and design press.

| Layer | Source | Weight |
|---|---|---|
| Theory and evidence | Academic papers, practitioner books, institute publications | **primary** |
| Applied practice | Published brand guidelines, design case studies | primary where obtainable |
| Music application | Artist output itself, interviews, label/agency writeups | primary |
| Reception | Reddit — what musicians find credible vs cringe | **secondary only** |

**Reddit access:** use `scripts/reddit_research.py`. WebSearch cannot reach Reddit; that script's docstring holds the full explanation.

---

## §3 — THE METHOD RULES, EARNED THE HARD WAY

Non-negotiable. The last round produced a confident, well-written, entirely false finding.

1. **A zero is not an absence until a control passes in the same pass.** See [[working/RESEARCH_STORYTELLING]] §9.
2. **Every substantive claim carries a source URL that was actually loaded.**
3. **Tag every source:** ACADEMIC / PRACTITIONER-BOOK / DESIGN-PRESS / MARKETING-BLOG / VENDOR / PRIMARY. **Marketing blogs recycle each other — five blogs agreeing is one source, not five.** This matters more here than in any previous round, because this topic is the most commercially polluted the vault has researched.
4. **Distinguish what a researcher claims from what their followers claim on their behalf.** Constantly violated in the Sharp-vs-positioning debate.
5. **Flag folklore.** Colour psychology and "logos must be simple" are widely repeated and poorly supported. Mark them rather than passing them on.
6. **Separate FOUND from MY READ**, every time.
7. **Never invent** a quote, statistic, author, date, channel or follower count.

---

## §4 — THE SIX BRIEFS

### 1. Brand archetypes — canon and evidence base
Jung → Mark & Pearson, *The Hero and the Outlaw* (2001), the 12-archetype system. Get the **actual 12 with real definitions**, not a blog's paraphrase. Who teaches it now and how. **Then the critical part: how well supported is any of it?** Hunt academic critique, replication problems, and marketing scientists who consider it unfalsifiable or decorative — find the *strongest* critique, not the mildest. Then: is there a defensible weaker version (archetypes as a generative tool rather than a predictive model), and who argues it? Finally, any application to artists or bands.
**Deliver:** the 12 as defined · who teaches it · strongest critiques quoted · what survives · music applications · a confidence assessment separating solid from pop-psych.

### 2. The evidence war
Map the central conflict, fairly, **without picking a winner.**
- **Pole 1 — positioning and personality:** differentiation, Jennifer Aaker's five brand-personality dimensions, Keller's brand equity, Kapferer. Claims and basis.
- **Pole 2 — Ehrenberg-Bass:** Byron Sharp, *How Brands Grow*. Get the **actual** claims, not the caricature: double jeopardy, mental and physical availability, **distinctiveness over differentiation**, light buyers over loyalists, the critique of segmentation.
- Where they genuinely conflict, and where they are talking past each other.
- **Counter-critiques of Ehrenberg-Bass** — required for fairness. Who pushes back, on what grounds (B2B, luxury, small and new brands, whether the laws hold outside FMCG).
- **Highest priority: does any of it apply to a very small or unknown brand?** The laws derive largely from large FMCG brands. If the honest answer is *"the research mostly doesn't cover this,"* that is a vital finding and must be stated.

### 3. Brand voice
Suspected the least-defined of the three series. Establish whether a usable body of practice exists or whether it is mostly vibes.
Definitions — **voice vs tone**, a real and commonly-collapsed distinction. Established frameworks with their actual components (NN/g's tone-of-voice dimensions and others). **Prioritise PRIMARY sources: find real published voice guidelines** (Mailchimp's content style guide is public) and record what they concretely contain — word lists, do/don't tables, register rules. Then: is there any evidence voice consistency does anything measurable, or is it pure craft convention? *"No measurement exists"* is a legitimate finding.
**Music application is the priority** — captions, bios, track descriptions, interviews, stage banter, merch, newsletters. Does anyone teach this for musicians at all? Plus **the faceless case**: how voice works with no visible person.

### 4. Visual identity
**Anchor on distinctive brand assets** — Ehrenberg-Bass / Jenni Romaniuk, the fame-and-uniqueness grid, asset-building rules. This is the most measurable part of brand theory; treat it as the spine.
Then the conventional design canon — identity systems vs logos, typography, consistency — separating established from folklore. **Colour psychology specifically: check whether "colour meanings" claims survive scrutiny.** Then music-specific practice across cover art, press photos, video language, stage visuals, merch, social grid. **The faceless case is high priority** — with no face, what carries identity? Masks, marks, symbols, colour, typography, recurring motifs. Finally the live/physical layer, and whether anyone treats stage design as brand identity rather than production.

### 5. Competitive content landscape
**Who already makes this content** — YouTube, TikTok/IG, newsletters, podcasts, courses teaching branding to musicians. Names, angles, audience size where visible. What angle dominates: tactics (playlists, ads, algorithms) versus psychology versus identity? **Is anyone teaching brand theory with rigour, or engaging the evidence debates at all?** Almost certainly not — confirm with evidence.
**Teardown format models** — who does teardowns well in music and in adjacent fields (design, marketing, startups), with structure described: length, pacing, visual approach. Reddit secondary: how musicians react to branding content, what earns respect and what gets mocked. Plus format intelligence on what makes short-form explainers travel.

### 6. Exemplar landscape — MAP ONLY, NO TEARDOWNS
⚠ **Scope limit, per Nick: breadth over depth. A long essay on one artist is a failed task.**
Candidates grouped by identity strategy: **anonymity** (Burial, Boards of Canada, Zhu, Malaa, SBTRKT) · **mask/persona** (Daft Punk, deadmau5, Marshmello, Rezz, Claptone) · **alias systems** (Eric Prydz, Aphex Twin, Four Tet) · **documentation-as-identity** (Fred again..) · **visual-system-led** (Bicep, Overmono, Floating Points) · **the client's own lane** (Of The Trees, G Jones, Tipper, CharlesTheFirst).
Per artist, **only**: strategy in 1–2 lines · the distinctive assets a viewer would recognise · roughly when it was established · **what documentation exists** to support a future teardown, and where it's thin.
Then: which are richest for teardown, ranked — weighing documentation, clarity of strategy, and whether the lesson transfers to a small artist. **Plus any brand that visibly failed or backfired** — abandoned personas, mocked lore, flopped rebrands. Those are more instructive than successes and far less covered. And: has anyone already published good analysis of these artists?

---

## §5 — WHAT THE ROUND MUST ANSWER

1. Which parts of the canon are solid enough to teach without being embarrassed later.
2. Whether brand voice is a real discipline or a convention with a vocabulary.
3. Whether anything in the evidence base speaks to **small and unknown** brands — the client's actual situation.
4. Whether anyone is already making this content well.
5. Whether the teardown format has a workable evidence base, or whether the documentation is too thin.

---

## §6 — OPEN, AND NOT ANSWERABLE BY RESEARCH

- **The series still has no format.** Same gap as the first branch. Research will not close it.
- **Whether these two branches share a name, a channel, or an audience funnel.** Decided as siblings; the packaging is undecided.
- **Whether "digestible on social media" and "the evidence is contested" survive in the same piece.** The honest version of a contested field is longer than the format usually allows. Unresolved, and it is a real design problem rather than a research question.
