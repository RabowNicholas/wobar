---
title: Text & Typography Patterns
version: 1.0
last_updated: 2026-04-16
status: live
scope: Text rendering via Text TOP / Text SOP / Text POP (2025). Animated typography, title cards, lyric display.
dependencies: TD_LIBRARY_INDEX.md, TD_OPERATORS_TOP.md, TD_OPERATORS_POP.md
---

# TEXT AND TYPOGRAPHY PATTERNS

TD has three text paths, each suited to a different job:
- **Text TOP** — rasterized text as a texture. Fastest. Best for static labels, UI, captions.
- **Text SOP** — extruded 3D geometry from a font. Best for 3D titles, extruded logos.
- **Text POP** (new 2025) — text as point data. Best for animated typography, text-to-particles.

---

## Text TOP

Rasterizes a string into a texture.

### Key parameters
- **Text** — the string. Can be expression-driven for dynamic text.
- **Font** — system font. Known Mac issue: color emoji fonts fall back to outline (see `TD_FOOTGUNS.md`).
- **Size** — point size.
- **Alignment** — left / center / right, top / middle / bottom.
- **Border / Fill** — color and width.
- **Outline** — separate color and width.
- **Stroke Width** — thickness of outline.
- **Drop Shadow** — offset, color, softness.

### Dynamic text via expression
```python
# Text param:
f"{op('null_score')['score'][0]:.0f} pts"
```
Live-updating numeric display.

### Use cases
- Lyrics (driven from a Table DAT or Audio-synced timestamps).
- Frame counter / timestamp debug overlay.
- Static title cards.
- Simple UI labels.

---

## Text SOP

Extrudes text as 3D geometry.

### Key parameters
- **Text** — string.
- **Font** — font file or system font.
- **Size** — geometric size.
- **Depth** — extrusion depth (creates 3D).
- **Bevel** — edge bevel size and steps.
- **Resolution** — curve sampling density per glyph.

### Use cases
- 3D titles ("WOBAR" extruded, rotating, materialed).
- Exploded text (individual letters as separate geometry via Group SOP).
- Text on 3D surfaces.

### Pipeline
```
Text SOP ──► Extrude SOP (if more depth needed)
          ──► Subdivide / Bevel
          ──► Normal SOP
          ──► Material SOP (Phong / PBR MAT)
          ──► Geometry COMP ──► Render TOP
```

---

## Text POP (2025)

Generates point data from text — per-character, per-word, or per-path samples.

### Key parameters
- **Text** — string.
- **Font** — font.
- **Sampling Mode** — Characters / Words / Path Samples.
- **Density** — samples per glyph outline.

### Outputs
- @P — position of each point (along the glyph outline).
- @char — character index.
- @word — word index.
- @uv — UV within the glyph.

### Use cases
- Text disintegrating into particles.
- Points orbiting character outlines.
- Audio-reactive text (each character animated independently).
- Procedural typography visualization.

### Canonical pipeline
```
Text POP ("WOBAR", Sampling = Path, Density = 50)
  ──► 250 points along letter outlines
  ──► Noise POP (animate jitter)
  ──► Attribute POP (color based on @char index)
  ──► Geometry COMP instance (small glowing quad)
```

---

## Typography Patterns

### Pattern 1 — Glitch text
```
Text TOP ──► Displace TOP (displacement = noise)
         ──► Chromatic Aberration TOP
         ──► Level TOP
         ──► Out
```
- Noisy displacement gives RGB-split glitch.
- Strength driven by audio for reactive glitches on kicks.

### Pattern 2 — Particle text explosion
```
Text POP (sampled from text)
  ──► initial emit positions
  ──► Simulate POP (start with outward velocity on trigger)
  ──► Force POPs (drag, turbulence)
  ──► Lifespan POP
  ──► Geometry COMP instance
```
- Text assembled from particles, then on trigger explodes outward.

### Pattern 3 — Text as a mask
```
Text TOP (white on black) ──► used as alpha/mask for another layer
```
- Visual effect plays "inside" letter shapes.
- Composite with Matte TOP or Composite Inside mode.

### Pattern 4 — Kinetic typography (character-by-character animation)
```
For each character: separate Text TOP or Text SOP
Each character animated independently (position, rotation, scale, opacity)
Driven by Pattern CHOP with delay per index.
```

### Pattern 5 — Text flowing along a curve
```
Curve SOP (path) ──► sampled for positions
Text SOP for each character, positioned and oriented along the curve.
```
Or Text POP with Sampling = Characters, each character instanced at a curve sample.

### Pattern 6 — Text on 3D geometry surface
```
Text TOP rendered to texture
  ──► Mapped as Color Map on Phong MAT
  ──► Geometry COMP applies to surface
```

### Pattern 7 — Expanding/contracting text
Drive Text TOP's Size or Tracking parameter from audio or a CHOP.

### Pattern 8 — Type-on effect (revealing characters over time)
```
Text TOP's Text param = text_string[: int(reveal_count)]
reveal_count = absTime.seconds * 10  # characters per second
```
- Character-by-character reveal.

---

## Audio-Reactive Text

### Size pulse
```
Text TOP Size expression: 40 + op('null_audio_sub')['rms'][0] * 20
```

### Tracking shake
```
Text TOP Character Spacing expression driven by Noise CHOP with audio-scaled amplitude.
```

### Per-character jitter
```
Text POP ──► Attribute POP (per-character offset = noise(char_index + time))
         ──► Geometry COMP instance of that character's shape
```
- Each letter jitters independently.

### Color pulse
```
Text TOP + color driven by HSV Adjust → hue shift from audio high band.
```

---

## Font Handling

### System fonts on Mac
Text TOP's Font param lists installed fonts. Install custom fonts via Font Book; restart TD.

### Font files
Some Text ops accept a direct .ttf / .otf path — useful for fonts you don't want system-installed.

### Font atlas (for Text SOP / POP)
Pre-render a font atlas via a Text TOP, then sample per-character from known UV coordinates. Used in custom pipelines for color fonts / emoji on Mac.

---

## Reading Data into Text

### From Table DAT
```
Text TOP Text param = op('table_lyrics')[current_row, 'text']
Current row driven by timeline or audio-synced cue.
```

### From Web Server / API
```
WebClient DAT fetches JSON ──► Script DAT parses, updates Text TOP param
```

### From OSC
```
OSC In DAT ──► Execute DAT (on message, update Text TOP)
```

---

## Performance

- **Text TOP** is cheap for static strings. Frequent Text changes are mild re-cook cost.
- **Text SOP** with many letters + high Resolution + bevel is expensive per cook. Cache with File Out when geometry is finalized.
- **Text POP** with high Density samples is fine on M1 up to ~5k total points.
- **Per-character independent instancing** for long strings — scales linearly.

---

## Reading This File

Pick the text path (TOP / SOP / POP) based on the use case. Then jump to the matching pattern section. For animated / audio-reactive text, the Audio-Reactive Text section has the specific knobs.
