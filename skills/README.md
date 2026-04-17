---
title: Skills (source of truth)
version: 1.0
last_updated: 2026-04-16
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
