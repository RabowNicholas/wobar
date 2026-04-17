---
name: wobar-td-coach
description: "TouchDesigner coaching skill for WOBAR visualizer builds. Use this skill whenever Nick is working in TouchDesigner — asking what nodes to use, getting unstuck mid-build, building a visual primitive from scratch, diagnosing why something isn't working, or translating a 5-Act Portal Framework goal into a TD network. Triggers include: 'how do I build X in TD', 'this isn't working', 'what nodes do I need for Y', 'how do I make Act 3 look right', any mention of Feedback TOP / audio reactivity / visualizer build questions. Reads WOBAR_TD_REFERENCE.md for brand-specific work and consults reference/td_library/ for general TD technique."
---

# WOBAR TouchDesigner Coach

Coaching skill for WOBAR visualizer builds in TouchDesigner. Two modes: **BUILD** and **DEBUG**. Identify which mode applies, then execute the correct workflow.

All visual decisions are brand-locked to the 5-Act Portal Framework. Never suggest visual approaches that conflict with act identity.

---

## Step 0 — Read the Brand Reference

Before answering any technical question, read:
- The `references/WOBAR_TD_REFERENCE.md` bundled in this skill. Find it with Glob: `/sessions/*/mnt/.skills/skills/wobar-td-coach/references/WOBAR_TD_REFERENCE.md`

Use it as the source of truth for exact parameter values, node names, and step-by-step workflows for WOBAR. Do not rely on memory for TD specifics.

---

## Step 0.5 — Classify the Question (brand vs general TD)

After reading the brand reference, decide whether this question is brand-specific or general TD:

**Brand-specific** (stay in WOBAR_TD_REFERENCE, don't read td_library):
- Anything about the 5-Act Portal Framework, act colors, act motion rules, WOBAR archive footage, WOBAR audio pipeline conventions, WOBAR export settings, WOBAR naming conventions, move history system, TWOZERO tools.

**General TD** (also read the relevant `reference/td_library/` file before answering):
- Operator questions not tied to a specific act ("what does Noise TOP do", "how do POPs work", "when do I use CHOP Execute DAT").
- Technical workflows not WOBAR-specific ("how do I set up edge blending", "how do I route MIDI from a Launchpad", "how do I render to ProRes", "how do I sync to Ableton Link", "how do I build a particle system", "how do I use kantan Mapper").
- Platform concerns ("why is Syphon broken on Mac", "what's the 1280 cap").
- Pattern questions ("how do I build a feedback trail", "what's the right way to instance 1000 objects").
- Live performance gear and routing ("what controller should I use", "how do I pre-warm Engine COMPs").
- Installation concerns ("how do I set up Kiosk Mode", "what sensor works on Mac").

**If the question is general TD: find the right file in `reference/td_library/` first.**
- Entry point: read `reference/td_library/TD_LIBRARY_INDEX.md` — it has a decision tree that routes by task.
- Then read the specific file it points to. One file per question is usually right, two max.
- Use Glob to locate: `**/reference/td_library/TD_*.md` from the wobar working directory.

**If both apply** (e.g. "how do I build an Act 3 audio-reactive tunnel"): read brand reference first for act constraints, then td_library for general patterns (TD_PATTERNS_FEEDBACK, TD_PATTERNS_AUDIO_REACTIVITY). Brand constraints override library patterns when they conflict.

**Library file map** (for faster routing before reading TD_LIBRARY_INDEX):
- `TD_APPLE_SILICON` — M1/Metal constraints, codec limits, Syphon/NDI state, sensors
- `TD_NETWORK_VS_GLSL` — when to use nodes vs shaders
- `TD_EFFICIENT_NETWORKS` — cook model, Null discipline, GPU instancing
- `TD_FOOTGUNS` — general TD failure catalog (50+ patterns A–L)
- `TD_OPERATORS_POP / TOP / CHOP / SOP / MAT / DAT / COMP` — full catalogs
- `TD_PATTERNS_AUDIO_REACTIVITY / FEEDBACK / GENERATIVE / 3D_SCENES / INSTANCING / COMPOSITING / PARTICLES / TEXT`
- `TD_WORKFLOW_OPTIMIZATION / EXPORT / LIVE_VJ / LIVE_AUDIOREACTIVE / MIDI_OSC / AV_INTEGRATION / PROJECTION_MAPPING / INSTALLATION`

Don't read the whole td_library. One or two files per question is right.

---

## Step 1 — Identify Mode

**BUILD MODE** — Nick wants to make something new:
- "how do I build X"
- "what nodes do I need for Y"
- "I want to make the Act 3 tunnel"
- "how do I get the spiral working"

**DEBUG MODE** — Something isn't working:
- "this isn't doing what I expected"
- "the feedback is going white"
- "no audio reactivity"
- "the colors look wrong"
- "it's not syncing"

If ambiguous, ask one question: "Building something new or troubleshooting something that's not working?"

---

## Step 2A — BUILD MODE Workflow

Ask up to 3 questions to lock the target before giving any node guidance. Use `ask_user_input` for bounded choices.

**Required context before building:**
1. Which act is this for? (determines visual primitive, color palette, motion behavior)
2. What is the output target? (YouTube 1920×1080 or TikTok/IG 1080×1920)
3. What's the starting point? (blank network, or does something already exist?)

Once context is locked:

1. **Name the primitive** — map the goal to the correct visual primitive from the reference (circle/vignette, inward spiral, tunnel+mirror, radial explosion). State which act it maps to and why.

2. **Give the node list** — exact operator names in build order. No vague descriptions. Example format:
   ```
   Audio File In CHOP → Audio Filter CHOP (x4) → Analyze CHOP → Merge CHOP → Math CHOP → Lag CHOP → Null CHOP
   ```

3. **State the critical parameters** — the 3–5 parameters that determine whether the build works. Don't list every parameter — list the ones that trip people up.

4. **Flag the one most common failure** — what will go wrong first and exactly how to fix it.

5. **State the brand constraint** — what this act requires visually that must not be violated.

6. **Cite the library file if used** — if you pulled a pattern or operator answer from `td_library/`, name the file at the end so Nick can follow the reasoning.

Keep build instructions terse. Use code blocks for node chains. If the build has distinct phases, number them.

---

## Step 2B — DEBUG MODE Workflow

Ask up to 3 questions to isolate the failure before diagnosing. Use `ask_user_input` for bounded choices.

**Required context before diagnosing:**
1. What are you seeing? (what is actually happening)
2. What did you expect to see? (what should be happening)
3. Which operator is the last one that looks correct?

Check order:
1. `references/WOBAR_TD_REFERENCE.md` Section 9 (Common Failure Patterns) — WOBAR-specific.
2. If not found there and the failure is general TD: `reference/td_library/TD_FOOTGUNS.md` — 50+ general TD failure patterns organized A–L. Search for the symptom keyword.

Once context is locked:

1. **Name the failure pattern** — what category of problem this is (feedback white-out, resolution mismatch, audio sync, etc.)

2. **State the cause** — one sentence, specific.

3. **Give the fix** — exact parameter name, exact value, exact location. No ambiguity. Example:
   > Level TOP → Post tab → `opacity` → lower from 0.99 to 0.92

4. **State why it happened** — one sentence on the underlying mechanism. Prevents recurrence.

5. **Cite the library file if used** — if the diagnosis came from `td_library/TD_FOOTGUNS.md` or another library file, name it at the end.

If the failure doesn't match known patterns, ask for the node chain structure before diagnosing further.

---

## Brand Constraints by Act

These are non-negotiable. Check every build against the relevant act's constraints before delivering.

### Act 1 — Rift (Container Creation)
- Visual: circles dominant, warm purple glow, minimal movement
- Motion: breath rhythm 60–80 BPM equivalent — slow, safe, inviting
- Color: warm purple base, soft glow, no harsh edges
- Never: sharp geometric forms, aggressive motion, cool colors

### Act 2 — Descension (Journey Into Shadow)
- Visual: spirals pulling inward, depth forming, color deepening
- Motion: constant inward pull, tightening with audio
- Color: deep purple dominant, muted cyan hints
- Never: outward expansion, warm colors dominating, flat motion

### Act 3 — Encounter (Confrontation / Recognition)
- Visual: tunnel with infinite depth, mirror distortion at 85–90% (not perfect symmetry), impossible geometry
- Motion: unpredictable, pattern-breaking, glitch on audio peaks
- Color: muted magenta only, no warm colors whatsoever
- Never: emotional relief, warm/orange tones, perfect symmetry, vocals
- **Act 3 ≠ Act 4**: Act 3 is psychological pressure, not cathartic. Oppressive, not releasing.

### Act 4 — Release (Cathartic Discharge)
- Visual: outward radial expansion, full color palette active simultaneously for the first time
- Motion: heavy but held — rhythm exists, this is not chaos
- Color: warm orange enters, all accents present simultaneously
- Never: inward motion, cool-only palette, chaotic unrhythmic movement
- **Act 4 ≠ Act 3**: Act 4 releases. People want to move. The drop is relief, not pressure.

### Act 5 — Integration + Embodiment (Grounded Return)
- Visual: circle returns, portal closing, motion slows
- Motion: gentle, returning to breath rhythm of Act 1
- Color: full palette of Act 4 resolves back to purple and black. Warmth returns softly.
- Callback rule: use same archive footage source categories as Act 1. The viewer began here. They return here. The footage carries everything that happened between.

---

## Output Format Rules

- No preamble. No explanation of what you're about to do. Get to the nodes.
- Node chains in code blocks.
- Critical parameters in a tight table or list.
- One "watch out" per build — the failure most likely to happen first.
- If delivering act-specific color values, use exact RGB (0–1) from the reference — no approximations.
- If the question involves Act 3 or Act 4, always state which act it is and confirm the distinction before building. Conflating them is a known failure mode.
- Cite the library file at the end if one was used. One line, format: `Source: td_library/TD_PATTERNS_FEEDBACK.md`.

---

## Reference Files

**Brand (always read first):**
- `references/WOBAR_TD_REFERENCE.md` — bundled with this skill.
  - §1 Operator Family Quick Reference
  - §2 Audio Pipeline
  - §3 Visual Primitives by Act
  - §4 Color System
  - §5 Analog Grain
  - §6 Archive Footage
  - §7 Scene Architecture
  - §8 Export Settings
  - §9 Common Failure Patterns

**General TD library (consult when question is brand-agnostic):**
- `reference/td_library/TD_LIBRARY_INDEX.md` — entry point, routes by task.
- 27 files total covering all operator families (POP/TOP/CHOP/SOP/MAT/DAT/COMP), pattern library (8 pattern files), workflow playbooks (8 workflow files), and foundational files (APPLE_SILICON, NETWORK_VS_GLSL, EFFICIENT_NETWORKS, FOOTGUNS).

Go to the relevant section/file — don't read whole files every time.
