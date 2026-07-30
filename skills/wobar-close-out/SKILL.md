---
name: wobar-close-out
description: "Session close-out for the WOBAR vault. Use this skill whenever Nick signals the end of a WOBAR working session — 'close out', 'close-out', 'wrap up the session', 'session done', 'end of session', 'let's wrap', 'closing out', 'that's it for today', or any sign he is finishing WOBAR work. Updates current context in working/WOBAR_ACTIVE.md, puts decisions in the governing docs that own them, retires dead threads to working/WOBAR_CLOSED.md, and appends to working/TD_BUILD_LOG.md when a TouchDesigner build happened."
---

# WOBAR Session Close-Out

All paths are relative to the vault root `/Users/nicholasrabow/Desktop/wobar/wobar/`.

## The principle — read this before touching anything

**The vault is context, not a project tracker.** It exists so a future session starts already understanding the state of the world and can answer Nick's questions well. **Nick tracks his own work and does not need his hand held.**

Set by Nick, 2026-07-30: *"we can track the changes but we dont need to track the actual work. i am doing that. i dont need my hand held. i more want the vault to contain the current context so that you can understand and help with my questions as they come up."*

The test for any line you are about to write:

| Write it | Don't |
|---|---|
| A decision, and why | A next action for Nick |
| A constraint, trap or blocker | Progress narration |
| A technical fact needed to resume (params, paths, expressions) | A recap of what happened this session |
| **What was tried and failed, and why** | A count of what hasn't been done yet |
| A genuinely open question | A task list dressed as a question |

**Git is the change log.** A real commit message replaces a session-log entry. `working/WOBAR_SESSION_LOG.md` is a frozen archive — **never append to it.**

**Repeating an undone task back at Nick is nagging, not context.** State it once, as a fact, in the place it belongs.

## Workflow

### 1. Update current context — only where the world changed

`working/WOBAR_ACTIVE.md` holds **POSITION** (the numbers and the rare assets), **THREADS** (one short section per live thread), and **STANDING TRAPS**.

Each thread carries **State** (one line: what it is, where it stands, what blocks it), the **decisions and technical facts** a future session needs to resume, and **Open** — genuine unknowns. Parked work gets a one-line `Parked` note with the reason, so it isn't lost.

Leave threads the session didn't touch byte-identical. Do not reflow or "improve" them.

### 2. Put the reasoning in the governing doc, not the tracker

A decision belongs in the file that owns it, at the point of decision — `WOBAR_ROADMAP`, `WOBAR_SOCIAL_PLAN`, `WOBAR_SURFACES`, `WOBAR_GROWTH_PLAN`, `reference/`. When a decision replaces an earlier one, **preserve the prior wording in a dated revision note** so the change is auditable rather than silent.

Per the Drift Rule in `WOBAR_CONTEXT`: every mutable fact has exactly one owning file. Everything else links to it.

**Corrections outrank additions.** If this session invalidated a claim, banner the doc that carries it and say what is void, what survives, and what error class it was. A vault that quietly keeps a dead finding is worse than a thin one.

### 3. Retire dead threads

Ask whether any thread should retire — never decide closure unilaterally. Retired threads move to the **top** of `working/WOBAR_CLOSED.md` with a `##` header, a resolution tag (SHIPPED / PAUSED / SUPERSEDED / RETIRED), a `**Closed:**` line carrying Nick's call and reasoning, then **full narrative**.

CLOSED.md is the one place to write at length. It is read rarely, and its job is to stop dead ideas being re-proposed and to preserve what outlives the thread — findings, artifacts, transferable method lessons, and what was never done.

Delete the thread from WOBAR_ACTIVE.md. Bump `last_updated` in CLOSED.md.

### 4. If a TD build happened — append to TD_BUILD_LOG.md

This one **is** a genuine feedback loop, not tracking: corrections appearing 2+ times get promoted to rules in `reference/WOBAR_TD_AGENT_RULES.md`, so undercounting breaks the mechanism.

New entry at the top, below the intro. Header `## <date> — <build name> — <one-phrase verdict>`. Sections: **What was built** (op names, expressions, parameter values) · **First-pass-right** (validates existing rules) · **Corrections against the agent** (with counts, and whether logged to TD_CLAUDE_DEBUG_LOG) · **WOBAR craft (Nick-reviewed)** — usually the highest-value section. Bump `last_updated`.

### 5. Bump frontmatter and close

Set `last_updated` in WOBAR_ACTIVE.md. Then give a terse receipt: files touched, threads retired, TD_BUILD_LOG entry if any. A receipt, not a recap — Nick was there.

## Notes

- House voice: dense, specific, no filler. Vault files are professional prose regardless of conversational style.
- Preserve Obsidian conventions — `[[wikilinks]]`, frontmatter, `---` separators.
- Source of truth is the vault copy at `skills/wobar-close-out/SKILL.md`. After editing, copy to `~/.claude/skills/wobar-close-out/SKILL.md`.
