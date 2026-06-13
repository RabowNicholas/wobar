---
name: wobar-promote
description: "Promotion pipeline for the WOBAR TD feedback loop — moves recurring corrections from the Correction Tracker in working/TD_BUILD_LOG.md into permanent rules in reference/WOBAR_TD_AGENT_RULES.md, with mandatory grep verification that each rule actually landed. Use this skill whenever Nick says 'promote', 'promote corrections', 'run promotion', 'promotion pass', 'audit promotions', 'verify promotions', after any td-save session that bumped tracker counts, or on any mention of the correction tracker, rule promotion, or the feedback-loop pipeline."
---

# WOBAR Promotion Pipeline

Move corrections that have recurred 2+ times from the Correction Tracker (`working/TD_BUILD_LOG.md`) into permanent rules (`reference/WOBAR_TD_AGENT_RULES.md`), and verify they landed.

**Core principle: promoted = verified landed.** A 2026-06-10 audit found 14 tracker entries marked "✅ PROMOTED" whose rule text had never been written into AGENT_RULES — promotion was marked on intent, never checked. Every TD session that trusted those marks was building without rules it believed existed. The verification step below is the entire reason this skill exists. Never mark a tracker entry promoted until a grep of AGENT_RULES confirms the rule text is physically in the file.

Two modes. Default is PROMOTE. Run AUDIT when Nick says "audit promotions" or "verify promotions", or when promotion marks are in doubt.

---

## Files

| File | Role |
|------|------|
| `working/TD_BUILD_LOG.md` | Correction Tracker — table `| Correction | Count | Promoted? |` under the `## Correction Tracker` heading. Count cells carry dated bumps (e.g. `2 (05-21, 06-10)`). Superseded entries are struck through with `SUPERSEDED →` pointers — never promote those. |
| `reference/WOBAR_TD_AGENT_RULES.md` | Where rules land. Operator-family groupings live under "Promoted Gotchas — by Operator Family". Topic sections exist for audio (Audio Pipeline Standard), feedback (Feedback Chain Rules), export (Export and Render), Python scripting (Python Scripting Rules), control architecture. |
| `working/TD_CLAUDE_DEBUG_LOG.md` | Sibling log (confirmed wrong advice + corrected patterns, read before TD actions). Not modified by this skill, but check it when drafting rule text — the debug log entry for the same failure often has the most precise corrected pattern. |

---

## MODE A — PROMOTE (default)

1. **Read the tracker.** Open `working/TD_BUILD_LOG.md`, locate the `## Correction Tracker` table. Read the Conventions paragraph above it — it is binding.

2. **Find candidates.** Entries where Count ≥ 2, Promoted? is `No`, and the entry is not struck through / marked `Superseded`. List them before writing anything.

3. **Draft each rule in AGENT_RULES house style.** Study neighboring rules first. The established phrasing is: bold lead stating the trap or rule, then the symptom, then the fix with exact parameter names and values, then provenance in parentheses (e.g. "(Recurred 04-16 + 05-23 → promoted.)"). Imperative, terse, no hedging. Carry over exact par names, error message text, and code snippets from the tracker entry verbatim — precision is the point.

4. **Place each rule in the correct section.** Prefer the most specific home:
   - Audio analysis/normalization/reactivity → Audio Pipeline Standard
   - feedbackTOP / loop wiring → Feedback Chain Rules
   - moviefileoutTOP / recording / codecs → Export and Render
   - `td_execute_python` / expression scoping → Python Scripting Rules
   - ctrl_master / custom pars → Control Architecture
   - Everything else → "Promoted Gotchas — by Operator Family", under the matching operator-family `###` subheading; create a new subheading if none fits.
   If a rule contradicts an existing rule, do not silently overwrite — flag the conflict to Nick and resolve explicitly (the newer, better-diagnosed pattern usually wins; mark the loser superseded).

5. **Write the rule into `reference/WOBAR_TD_AGENT_RULES.md`.** Then **VERIFY**: grep AGENT_RULES for a distinctive phrase from the rule just written (an exact par name, error string, or unique clause — not a generic word). Only after the grep returns the line do you proceed. If the grep misses, the write failed or landed wrong — fix it before touching the tracker.

6. **Mark the tracker — only after verification.** Update the entry's Promoted? cell to `✅ PROMOTED (verified YYYY-MM-DD)` using today's date. One entry at a time: write rule → grep → mark. Never batch-mark on the assumption that earlier writes succeeded.

7. **Report.** For each promotion: the correction, the rule's destination section, and the grep phrase that confirmed it. Plus a count of tracker entries updated. If `last_updated` frontmatter exists in either file, bump it.

---

## MODE B — AUDIT

1. **Collect all tracker entries marked PROMOTED** (any variant: `✅ PROMOTED`, with or without dates/notes).

2. **For each, grep `reference/WOBAR_TD_AGENT_RULES.md`** for a distinctive phrase from the correction (par name, error string, unique clause). Try 2–3 phrasings before declaring a miss — the landed rule may be reworded.

3. **Report three buckets:**
   - **Verified** — rule found; optionally upgrade the tracker cell to the `(verified YYYY-MM-DD)` form.
   - **Orphans** — marked promoted, rule missing from AGENT_RULES. Offer to land them now via the Mode A write → grep → mark loop.
   - **Contradictions** — a tracker entry and an AGENT_RULES rule give conflicting fixes for the same failure. Surface both texts to Nick; do not auto-resolve.

---

## Discipline

- Never mark promoted on intent. Write, grep, then mark — in that order, per entry.
- Never promote SUPERSEDED entries; promote the superseding canonical entry instead.
- Do not editorialize or generalize rule text — the tracker entry earned its specificity through real failures.
- Count threshold is 2. Count-1 entries stay in the tracker; do not promote early even if the lesson seems important (Nick can override explicitly).

---

## Source of truth

The vault copy at `skills/wobar-promote/SKILL.md` is canonical. After any edit, copy it to `~/.claude/skills/wobar-promote/SKILL.md` so the installed skill stays in sync.
