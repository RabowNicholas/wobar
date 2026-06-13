---
name: wobar-close-out
description: "Session close-out ritual for the WOBAR vault. Use this skill whenever Nick signals the end of a WOBAR working session — 'close out', 'close-out', 'wrap up the session', 'session done', 'end of session', 'let's wrap', 'closing out', 'that's it for today', or any sign he is finishing WOBAR work. Rewrites touched loop entries in working/WOBAR_ACTIVE.md, asks open/closed per loop, moves closed loops to working/WOBAR_CLOSED.md, adds a dense session-log row, bumps frontmatter dates, and appends to working/TD_BUILD_LOG.md when a TouchDesigner build happened."
---

# WOBAR Session Close-Out

Run the close-out ritual that ends every WOBAR working session. The vault's working files ARE the cross-session memory — the next session (and the next Claude) knows only what gets written here. A thin close-out loses the harvest; a precise one makes the next session start at full speed.

All paths are relative to the vault root `/Users/nicholasrabow/Desktop/wobar/wobar/`.

## Workflow

### 1. Identify what this session touched

From the conversation, list: which open loops in `working/WOBAR_ACTIVE.md` were worked on, whether a TouchDesigner build or modification happened, and whether any new loop was born this session. Read the Open Loops section of WOBAR_ACTIVE.md to match against existing entries (the file is large — read in chunks or grep for `^LOOP:` to inventory loop names first).

### 2. Rewrite each touched loop entry

For every touched loop, rewrite its entry in place:

- **STATUS:** update the state plus a short dash-detail of where it stands now.
- **LAST:** replace entirely with `<today's date> — ` followed by a dated narrative of THIS session. House style is long, dense, single-paragraph prose with **bold key phrases** marking subsystems, decisions, and verdicts. Capture exact parameter values, file paths, network names, and Nick's verbatim verdicts — these are what the next session needs to resume without re-deriving. Do not summarize down to two lines; density is the point.
- **NEXT:** rewrite as concrete, numbered next actions — `(1) ... (2) ...` — specific enough to execute cold (exact files, exact commands, exact thresholds), not vague intentions.

Untouched loops stay byte-identical. Do not reflow, retitle, or "improve" entries the session didn't touch.

Entry shape (abbreviated):

```
LOOP: down_bad_3stack v002 — Act 4 Phase 1 visualizer for Down Bad remix
STATUS: in progress — pipeline wired; pending final tuning + canonical save + IG render.
LAST: 2026-05-26 (later) — Major session. **Video timing system:** moviefileinTOP re-wired
in `specify` playmode with index expression ... **Audio reactivity infrastructure:** new
`base_audio_react` baseCOMP publishing 8 normalized channels ... Nick: "I think its
looking really good" — visual passes his bar; 5 minor brand misses deferred.
NEXT: (1) Save canonical `.toe` checkpoint as v002. (2) Final IG-ready render via
Pipeline C (PNG → FFmpeg `-crf 18 -preset slow -tune grain`). (3) ...
```

### 3. Ask Nick: open or closed?

For each touched loop, ask whether it stays open or closes. Use AskUserQuestion if available (one question per loop, options: "Still open" / "Closed"); otherwise ask in plain text. Also ask whether any new loop should open from this session's work. Never decide closure unilaterally — pausing, shipping, and retiring are Nick's calls, and WOBAR_CLOSED.md entries record his reasoning.

If a new loop opens, add a full LOOP/STATUS/LAST/NEXT entry to Open Loops in the same format.

### 4. Move closed loops to WOBAR_CLOSED.md

For each closed loop, write an entry at the TOP of the loop list in `working/WOBAR_CLOSED.md` (most recent first, below the intro line). Closed entries use a different shape than active ones — they get a `##` header and a closure line:

```
## <Loop name> — <RESOLUTION TAG, e.g. SHIPPED / PAUSED / QUIET RETIREMENT>

**Closed:** <date> — <one-line resolution: Nick's call and why>.

**What it was:** ...
```

After the closure line, carry the loop's full substance forward as bolded narrative sections. Section names flex with the loop type — shipped builds use **What it is / Arc / Key learnings**, paused work uses **Context / Build progress / Why paused / Preserved artifacts / Notable learnings transferred** — match the register of existing entries. The goal: someone reading only CLOSED.md can understand what the loop was, why it ended, and what survives it (artifacts, transferable patterns, preserved plans).

Then delete the loop's entry from WOBAR_ACTIVE.md entirely, and bump `last_updated` in WOBAR_CLOSED.md's frontmatter to today.

### 5. Add a Session Log row

Add one row to the `## Session Log` table in WOBAR_ACTIVE.md, directly under the header row (newest first). Format: `| <date> | <summary> |` — the date cell may carry a qualifier when multiple sessions land on one day (e.g. `2026-06-10 (stress test)`).

The summary is ONE dense single-cell narrative paragraph with **bold key phrases**, matching the density of existing rows. It should carry: what the session set out to do, what was built/decided (with names and paths), the verdict (including kills and failures — those are harvest, not embarrassment), what was logged where (debug-log entries, tracker rows, promotions, new memories, new files born), and loop state changes ("No loop opened" / "X closed → CLOSED.md"). A row that takes 30 seconds to read and replaces re-reading the whole session is the bar. Two-line summaries lose the harvest — write the long row.

### 6. Bump WOBAR_ACTIVE.md frontmatter

Set both `last_updated:` and `last_session:` in the YAML frontmatter to today's date.

### 7. If a TD build happened: append to TD_BUILD_LOG.md

Add a new entry at the TOP of `working/TD_BUILD_LOG.md` (below the intro, newest first). Header: `## <date> (<qualifier if needed>) — <network/build name> — <one-phrase verdict>`. Body sections, matching existing entries:

- **What was built:** subsystem-by-subsystem, with op names, expressions, and parameter values.
- **First-pass-right:** what the agent got correct without correction — this validates existing rules.
- **Corrections against the agent:** what needed manual fixing, with counts and whether entries were logged to TD_CLAUDE_DEBUG_LOG. This feeds the promotion pipeline: corrections appearing 2+ times become rules in WOBAR_TD_AGENT_RULES.md, so undercounting here breaks the feedback loop.
- **WOBAR craft (Nick-reviewed):** the aesthetic/brand lessons — often the highest-value section.

Bump `last_updated` in TD_BUILD_LOG.md's frontmatter too. Skip this step entirely if no TD work happened.

### 8. Close with a summary

End with a short list of files touched: which loops were rewritten, which moved to CLOSED, the session-log row added, frontmatter bumps, and TD_BUILD_LOG entry if any. Terse — this is a receipt, not a recap.

## Notes

- Write in the vault's house voice: dense, specific, no filler. The vault files are professional prose regardless of conversational style.
- Preserve Obsidian conventions already in the files: `[[wikilinks]]`, frontmatter fields, `---` separators between loops.
- Source of truth for this skill is the vault copy at `skills/wobar-close-out/SKILL.md`. After editing it, copy to `~/.claude/skills/wobar-close-out/SKILL.md` so Claude Code picks up the change.
