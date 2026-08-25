---
name: wobar-wander-writer
description: "Write new wander fragments (Mode B lore — the terminal's `wander`/`lore` path). Use this skill whenever Nick says 'write a wander fragment', 'new wander entry', 'add to the wander pool', 'add a lore fragment', 'wander line', or asks to grow the LORE array in the terminal. Not for the Passages (Mode A, Nick-authored narrative void poems) and not for journal/glimpse copy (MID register) — this skill is Mode B only: short belief-mirror fragments, generatable brand copy. Runs the locked writing process from reference/WOBAR_COPY.md against the live LORE pool in the wobar-landing-page repo to draft and kill-test candidates, then runs a mandatory one-round-minimum workshop/back-and-forth on Nick's pick before appending anything — a first 'I like it' is never treated as a lock."
---

# WOBAR Wander Fragment Writer

Draft new Mode B wander fragments — the short belief-mirror lines a Wanderer stumbles on via the terminal's `wander`/`lore` command. Generative, unlike the Passages (Mode A, Nick's personal verse — never generate that).

**Two files this skill lives between:**

| File | Role |
|------|------|
| `reference/WOBAR_COPY.md` — Mode B section + "Writing process (locked 2026-08-24)" | The instrument. Defines what a wander fragment is, what kills it, and the authoring process. Read it live — don't work from memory, it can be amended. |
| `/Users/nicholasrabow/Desktop/wobar/wobar-landing-page/components/terminal/content.ts` — `LORE` array | The live pool (separate git repo from this vault). Comments above each block already tag it to a belief or doctrine point — that grouping is the coverage map. |

---

## Step 1 — Establish the target belief (ask this first, before anything else)

- **If Nick named a belief, doctrine point, or theme already, use it and skip to Step 2.**
- If not, ask him directly which belief or doctrine point this fragment is for — don't assume and don't silently pick one.
- If he has no preference, **check coverage before proposing one.** Read `LORE` in `content.ts` at the path above — the belief/doctrine-point comment above each block is the existing coverage map, not just a list of lines. Cross-reference against the 8 beliefs in `reference/WOBAR_BRAND.md` §Belief System (recount live — this drifts as fragments get added). As of 2026-08-24 the thinnest is **transformation as well as entertainment** (1 fragment, vs. 2–4 for the rest) — the Writing process step 4 exists to stop new fragments crowding the easy beliefs. Propose the thinnest, let Nick redirect.
- Once a belief is set, state it in plain words before drafting anything (process step 1). This sentence never ships — it's scaffolding.

## Step 2 — Read the writing process live

Read `reference/WOBAR_COPY.md`, the Mode B subsection (rules 1–6) and the **Writing process** block directly beneath it. This is canonical — do not paraphrase from a prior session's memory. (If Step 1 didn't already require it, also read `LORE` in `content.ts` now, so drafts don't collide with or repeat an existing line for this belief.)

## Step 3 — Draft

Follow `WOBAR_COPY.md`'s process exactly:
1. Bend the belief into a paradox, not a statement of it (step 2). Strip test: could this be filed as doctrine with "it means" put back in front? If yes, keep bending.
2. Second-person or impersonal only (Mode B rule 2) — "you," "the void," "the drop," never "i."
3. One breath to a few lines, lowercase, no title (Mode B rules 5–6). A blank `''` element in the array is a valid beat/pause, matching existing lines like the drop entry.
4. Draft 3–5 candidates per pass, not one — the recognition test below eliminates most of them.

## Step 4 — Kill and test

Run every candidate through, in order, and cut anything that fails:
- **Narrative kill** — inhabits a form and speaks as it (a tree, a season)? That's Mode A. Cut.
- **Doctrine kill** — names the belief system directly, or instructs ("you should," "come to me")? §8 ban. Cut.
- **Clever kill** — payoff is wordplay, not recognition? That's LIGHT register. Cut.
- **Fortune-cookie kill** — read cold, out loud. Sounds wise rather than true? Law 0. Cut.
- **Recognition test** — read with zero context. A stranger should think *that's me* in one pass. Needs a second read or an explanation? Not done — revise or cut.

Show your work: for each surviving candidate, name the belief it renders and note that it passed the four kills. Don't just hand over a bare list of lines.

## Step 5 — Present, don't auto-ship

Present the surviving candidates to Nick with their belief tag. This is a draft pass, not a commit — Nick picks, edits, or rejects.

## Step 6 — Workshop the pick (mandatory before it ships)

**A first "I like A" is a starting point, not a lock.** Passing the four kills means a line is *not disqualified* — it doesn't mean it's the sharpest version of itself. This step is a real back-and-forth, not a rubber stamp: don't append on the first yes.

1. Nick names a favorite (or edits one himself). Take it seriously, then push on it once: name the specific thing that could still be tighter — a weak word, a beat that's doing no work, a version of the same paradox with less friction — and offer 1–2 alternates that are direct variations of *this* line (not a fresh batch from Step 3). Ground the push in a concrete standard, not a vibe: which kill is it closest to failing, or does it beat the recognition test as *strongly* as it could.
2. Nick responds — picks a variant, edits again, or says the original was right and defends why. Either answer is a legitimate outcome; the point is that the line got pressure-tested once, not that it has to change.
3. Repeat only if Nick keeps revising. Don't manufacture more rounds once he's settled — one real round of friction is the floor, not a fixed count.
4. **The round ends on an explicit lock signal** — "lock it," "ship it," "that's the one," "add it," or equivalent. Until you hear one, treat the line as still in workshop and do not write to `content.ts`.

## Step 7 — Append (only after lock)

1. Append the locked line to the correct belief-tagged block in `LORE` in `content.ts` (or start a new tagged block if it renders a belief with no existing group). Match the existing array-of-string-arrays format exactly, including `''` for pause beats.
2. Note that `wobar-landing-page` is a **separate git repo** from this vault — this skill edits the file but does not commit; that's Nick's call, same as any other code change.
3. Do not touch anything else in `content.ts` (Passages, the intro sequence, etc.) — scope is the `LORE` array only.
4. Confirm back to Nick with the exact line as written into the array and its belief tag, so there's a clean record of what actually shipped versus what was drafted.

---

## Source of Truth

The vault copy at `skills/wobar-wander-writer/SKILL.md` is canonical. After editing it, copy to `~/.claude/skills/wobar-wander-writer/SKILL.md` so the installed skill stays in sync.
