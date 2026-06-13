---
name: wobar-brand-check
description: "Brand-alignment check for WOBAR pieces against the 5-Act Portal Framework emotional register. Use this skill whenever Nick asks 'is this on brand', 'brand check', 'on-brand check', 'does this fit Act N', 'register check', 'brand review', 'does this feel like the cusp', or any request for aesthetic judgment of a WOBAR visual, track artwork, or copy against an act or cusp. Trigger on mid-session gut-checks during TouchDesigner builds and on formal pre-release reviews. The check is EMOTIONAL alignment with the act the track lives in — not implementation nitpicking. Reads reference/WOBAR_EMOTIONAL_REGISTER.md as the primary instrument."
---

# WOBAR Brand Check

Run a rigorous, consistent on-brand check of a WOBAR piece against the act or cusp its track lives in. The canonical instrument is `reference/WOBAR_EMOTIONAL_REGISTER.md` (locked v1.0) — built exactly for this purpose. The question is never "does it use the right palette or primitive" — it is **does the piece emotionally align with the act this track lives in?** Implementation details live in the TD docs; the brand check happens at the emotional layer.

This check is advisory. Report findings and stop. Nick decides what to act on. Never auto-fix.

---

## Step 1 — Establish the Register Target

Identify which act or cusp the track lives in. If Nick stated it, use it. If not, ask in his act language: "Which register is this — Act 2, Act 3/4 cusp, early Act 4?" Music dictates the act — BPM, energy arc, what the song asks the listener's body to do. Most tracks live on a cusp.

**Cross-brand guard:** this skill is WOBAR-only. Nick also runs Vilos (`/Users/nicholasrabow/Desktop/vilos/vilos/`), a different brand with different rules. If there is any chance the piece is for Vilos, ask before checking. Never evaluate a Vilos piece against the WOBAR register.

**Never conflate Act 3 and Act 4.** Act 3 is psychological pressure ("sit with this") — oppressive, held. Act 4 is cathartic discharge ("move") — driving, propulsive. If the stated act and what you see disagree on this axis, say so explicitly.

## Step 2 — Get Eyes on the Piece

- **TouchDesigner visualizer, TD running:** capture the live output with the TWOZERO MCP. Load the tool schema first via ToolSearch (`select:mcp__twozero__td_get_screenshot`), then capture. If TWOZERO is unavailable, ask Nick for a screenshot or render path.
- **Rendered video or image:** read the file Nick points to. For video, ask for representative frames if you cannot sample it directly — at minimum intro, biggest drop, outro.
- **Non-visual output (copy, artwork direction):** work from the artifact text directly.

One frame is rarely enough for a visualizer — movement quality is half the register. If you only have a still, say which findings are motion-dependent and unverifiable from a still (especially audio reactivity and propulsion).

## Step 3 — Load the Register

Read the target act's entry in `reference/WOBAR_EMOTIONAL_REGISTER.md`. For a cusp, read the cusp entry AND both adjacent acts — the cusp's "what lives only here" is usually the load-bearing element. Do not check from memory; the doc is locked and canonical.

## Step 4 — Evaluate

Check the piece against the act entry's six elements:

1. **Felt sense** — does the piece produce this body state?
2. **Posture** — does it put the listener in this relationship to the music?
3. **Implicit ask** — does the piece make the act's ask (safe / follow / sit / move / feel) feel inevitable?
4. **Quality of movement** — does the motion character match (sub-perceptual / hypnotic / held tension / driving / slow deliberate)?
5. **What breaks it** — walk the act's break list item by item. Any hit is a critical finding.
6. **On-brand check question** — the entry's final test, answered honestly.

Then apply the **always-on fundamentals** (from `reference/WOBAR_BRAND.md`), regardless of act:

- **Palette discipline** — desaturated psychedelic range (muted = 30–40% desat from full neon); never pure white (bone/ash are the ceiling); never neon/glowstick/candy. Psychedelic ceremony, not rave.
- **Mirror/encounter lens** — the piece should read as mirror and encounter, not generic journey-to-elsewhere. Could it ship as any bass artist's visual? If yes, that is a finding.
- **Figurative-cheese test** — recognizable figurative objects plus literal destruction read as cheesy stock FX. Abstraction is the WOBAR lane; recognizability is the cheese vector. (Calibration: a full Act 4 piece was killed 2026-06-10 for statue→goat→chunk-grid cheese.)
- **Audio reactivity (visualizers only)** — load-bearing, not decoration. A visually strong piece with no reactivity wired is "still water" and fails Act 4 outright ("the body cannot discharge in still water"); in Act 2 the form must breathe WITH the sound.
- **Texture** — matte, grainy, organic; glow as bioluminescence not LED. Metallics only in the mirror register.

**Calibration precedents** (settled judgment — apply, do not relitigate):
- Blue/teal for Act 2 DESCENSION is a brand-approved departure when desaturated.
- Chromatic aberration is on-brand only in the nostalgic/analog register — muted and small (1–3px), not saturated and large.

If one or two register elements miss, identify which and present them as decisions for Nick — fix or accept deliberately. If three or more miss, say plainly that the piece likely belongs to a different act, and name which.

## Step 5 — Report

Use the established review register. Format:

1. **Verdict** — score out of 10, anchored to the act or cusp. Example: "8/10 cusp 4→5."
2. **What lands** — specific strengths tied to register elements. "Black pupil + crushed darks carry the heavy register," not "looks good."
3. **Misses** — numbered list, each tagged with severity:
   - **CRITICAL** — violates a what-breaks-it criterion or an always-on fundamental (e.g. "still water — no audio reactivity wired, violates 'the body cannot discharge in still water'"; "pure-white edge color violates never-pure-white").
   - **MINOR** — register drift that weakens but does not break (e.g. "no forward propulsion," "CA at 8px may be too aggressive for the nostalgic register," "no 'discharge' visual moment," "palette not verified against the WOBAR ramp").
4. **One concrete move per miss** — a specific, actionable change, not a direction. "Add a slow continuous palette hue cycle for forward propulsion," not "make it more dynamic."

Be specific at the granularity of the exemplar reviews: name the missing register element, the violated criterion, or the exact parameter in question. Vague findings ("could be more dynamic") are below the bar.

Then stop. Do not implement fixes, do not modify the network, do not edit the artifact — even for critical misses. Nick deferred five documented misses on down_bad_3stack as "not a big deal"; deferral is his call to make.

## Pre-Release Checks

If this check is gating a release (not a mid-session gut-check), also point Nick at `working/WOBAR_RELEASE_STANDARD.md` — its Gate 2 (Brand) is the formal release version of this check, plus technical and craft gates. Do not duplicate its checklist here; run the register check above and note that the full release standard applies separately.

---

## Source of Truth

The vault copy at `skills/wobar-brand-check/SKILL.md` is canonical. After editing it, copy to `~/.claude/skills/wobar-brand-check/SKILL.md` so the installed skill stays in sync.
