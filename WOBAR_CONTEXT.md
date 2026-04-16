---
title: Wobar Context Index
version: 1.0
last_updated: 2026-03-10
status: live
scope: Master index for all Wobar reference files. Read this first in every conversation.
dependencies: none
---

# WOBAR CONTEXT INDEX

This is the index file for the Wobar project reference system. Read this file first. Pull additional files only as needed for the task at hand.

## File Registry

### Project / Brand
| File | Location | Scope | Status |
|------|----------|-------|--------|
| [[working/WOBAR_ACTIVE]] | /working | Open project loops, current context, session history | live |
| [[working/WOBAR_CLOSED]] | /working | Completed project loops, archived from WOBAR_ACTIVE | live |
| [[reference/WOBAR_BRAND]] | /reference | Foundation, mission, archetypes, beliefs, positioning | locked |
| [[reference/WOBAR_FRAMEWORK]] | /reference | 5-Act Portal Framework, act definitions, percentages | locked |
| [[reference/WOBAR_COPY]] | /reference | Voice, lexicon, anti-vocabulary, writing tests | locked |
| [[reference/WOBAR_SONIC]] | /reference | Sonic identity, reference artists, genre positioning | locked |
| [[reference/WOBAR_CONTENT]] | /reference | Content system, release architecture, posting | locked |
| [[reference/WOBAR_ARCHIVE]] | /reference | Archive sourcing by act, portal depth, pipeline | locked |
| [[reference/WOBAR_CLAUDE]] | /reference | How to work with Nick | locked |
| [[reference/WOBAR_PATCH_SYSTEM]] | /reference | Serum 2 patch naming, 8-macro standard, versioning | locked |
| [[reference/WOBAR_OBSCURA]] | /reference | Obscura visual identity and reference system | locked |

### TouchDesigner — Entry Point
| File | Location | Scope | Status |
|------|----------|-------|--------|
| [[reference/WOBAR_TD_INDEX]] | /reference | **TD entry point** — decision tree for which TD docs to load per task | live |

### TouchDesigner — Core Rules & Conventions
| File | Location | Scope | Status |
|------|----------|-------|--------|
| [[reference/WOBAR_TD_AGENT_RULES]] | /reference | Build conventions: naming, architecture, act constraints, Python rules | live |
| [[reference/WOBAR_TD_REFERENCE]] | /reference | Full specs: audio pipeline, visual primitives, color system, export — load by section | locked |
| [[reference/WOBAR_MOVE_SYSTEM]] | /reference | Move history system spec — JSON schema, lifecycle, network→comp mapping | locked |

### TouchDesigner — TWOZERO MCP
| File | Location | Scope | Status |
|------|----------|-------|--------|
| [[reference/WOBAR_TWOZERO_GUIDE]] | /reference | Confirmed type strings, parameter names, limitations, known behaviors | live |
| [[reference/WOBAR_TWOZERO_MCP_CATALOG]] | /reference | Full parameter tables for all 35 TWOZERO tools — load by group, not full file | live |

### TouchDesigner — Snippet Libraries
| File | Location | Scope | Status |
|------|----------|-------|--------|
| [[reference/WOBAR_TD_EXPRESSION_COOKBOOK]] | /reference | Paste-ready expressions: CHOP access, audio-reactive mappings, time, footguns | live |
| [[reference/WOBAR_GLSL_PATTERNS]] | /reference | Act-specific GLSL shaders (10 total), utility functions, act color reference | live |
| [[touchdesigner/reference_networks/README]] | /touchdesigner | Structural examples — node chains + taste decisions per network type | live |

### TouchDesigner — Session Logs
| File | Location | Scope | Status |
|------|----------|-------|--------|
| [[working/TD_CLAUDE_DEBUG_LOG]] | /working | Confirmed wrong advice + corrected patterns — read before any TD action | live |
| [[working/TD_BUILD_LOG]] | /working | Session-by-session build log — correction tracker, patterns | live |
| touchdesigner/networks/[network]/CHANGE_LOG.md | /touchdesigner | Per-network change log — why changes were made | live |
| touchdesigner/networks/[network]/moves/ | /touchdesigner | Per-network move history — JSON files for granular undo | live |

## Current State
Brand 6.0 locked March 2026. All files reflect current version.
TWOZERO MCP integration added April 2026. TD agent rules established.
Move history system added April 2026. Three slash commands: /td-build, /td-undo, /td-save.
TD doc library expanded April 2026: MCP catalog, debug log, expression cookbook, GLSL patterns, reference networks, TD index all added.
WOBAR_PROJECT_INSTRUCTIONS.md is deprecated — CLAUDE.md is the authority.

## Notes
When a file status is in-flux, confirm current state with Nick before using as reference.
