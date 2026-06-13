---
title: Skills (source of truth)
version: 1.1
last_updated: 2026-06-12
status: live
scope: Canonical, git-tracked versions of WOBAR-specific Claude skills. This folder is the source; `~/.claude/skills/` on each machine is a local copy.
---

# SKILLS

Git-tracked skill definitions for WOBAR work. This folder is the source of truth — `~/.claude/skills/` on any given machine is a synced copy.

## Why this folder exists

Claude's skill runtime loads from `~/.claude/skills/` (a read-only system path in some sandboxed environments). Keeping the authoritative copy here means:
- Changes are versioned and reviewable.
- Multiple machines stay in sync.
- The skill's logic lives alongside the vault files it reads, so updates to vault structure and skill behavior land in the same commit.

## Current skills

### `wobar-td-coach/`
TouchDesigner coaching skill. Two modes (BUILD / DEBUG), brand-locked to the 5-Act Portal Framework. Reads `reference/WOBAR_TD_REFERENCE.md` for brand work and `reference/td_library/` for general TD technique.

### `wobar-close-out/`
Session close-out ritual. Rewrites touched loop entries in `working/WOBAR_ACTIVE.md` (LOOP/STATUS/LAST/NEXT, house density), asks open/closed per loop, moves closed loops to `working/WOBAR_CLOSED.md`, adds the dense session-log row, bumps frontmatter dates, appends to `working/TD_BUILD_LOG.md` when a TD build happened. Added 2026-06-12.

### `wobar-promote/`
Correction-tracker → rule promotion pipeline with mandatory verification ("promoted = verified landed" — exists because a 2026-06-10 audit found 14 phantom promotions). MODE A promotes count≥2 tracker entries into `reference/WOBAR_TD_AGENT_RULES.md` with write→grep→mark discipline; MODE B audits existing promotion marks for orphans and contradictions. Added 2026-06-12.

### `wobar-brand-check/`
On-brand check against `reference/WOBAR_EMOTIONAL_REGISTER.md`. Establishes act/cusp target (with Vilos cross-brand guard), grabs eyes on the piece (TWOZERO screenshot or render), evaluates six register elements + always-on fundamentals (palette desat, never-pure-white, mirror lens, figurative-cheese test, audio reactivity), reports scored verdict with CRITICAL/MINOR misses + one concrete move per miss. Advisory only — never auto-fixes. Added 2026-06-12.

**Bundled references** live under `~/.claude/skills/wobar-td-coach/references/` on disk — that file (`WOBAR_TD_REFERENCE.md`) is a copy of the vault's brand TD reference and isn't tracked here. Don't duplicate it; sync manually when the brand reference changes materially.

## Install / sync pattern

When this folder changes:
1. Copy the updated `SKILL.md` from `skills/<skill-name>/SKILL.md` to `~/.claude/skills/<skill-name>/SKILL.md` on each machine that runs Claude.
2. Leave `references/` subfolders on disk alone unless the bundled reference itself changed.
3. Restart Claude Code session so the skill picks up the new description/behavior.

## Adding a new skill

1. Create `skills/<skill-name>/SKILL.md` with proper frontmatter (`name`, `description`).
2. Commit.
3. Copy to `~/.claude/skills/<skill-name>/SKILL.md` on machines that should have it.

## Not tracked here

- Non-WOBAR skills (fsc-copy-generator, ig-carousel, etc.) live in their own projects or in `~/.claude/skills/` only.
- Anthropic-shipped skills (pptx, docx, pdf, xlsx, schedule, etc.) — these are managed by the Claude runtime, not by me.
