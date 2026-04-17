---
title: DATs — Data Operator Catalog
version: 1.0
last_updated: 2026-04-16
status: live
scope: Every DAT in TD 2025.32460. Tables, text, scripts, network.
dependencies: TD_LIBRARY_INDEX.md, TD_WORKFLOW_MIDI_OSC.md
---

# DATs — DATA OPERATORS CATALOG

DATs hold **text, tables, scripts, and network data**. They are how TD does Python, HTTP, WebSockets, OSC routing, config, and any non-numeric data.

**Core facts:**
- A DAT is either a **table** (rows × columns) or **text** (single document).
- DATs are cooked like other operators — on input/parameter change or explicit trigger.
- Table DATs are indexed with `op('table')[r, c]` or `[rowName, colName]`.

---

## Text / Script DATs

### Text DAT
Plain text document. Used to store Python scripts, GLSL code, config, anything textual.
- Params: File (optionally link to external file), Edit, Language Hint (Python, GLSL).
- Use: holds a Python function, GLSL fragment, JSON config.

### Script DAT
Runs arbitrary Python on input change or trigger.

### Execute DAT
Python callbacks tied to global TD events:
- `onStart(op)`, `onFrameStart(frame)`, `onPlayStateChange`, etc.
- Use: initialization, per-frame logic (prefer CHOPs for perf), state transitions.

### CHOP Execute DAT
Python callback when specified CHOP channels change.
- Callbacks: `onValueChange(channel, sampleIndex, val, prev)`, `onOnToOff`, `onOffToOn`, etc.
- Use: trigger actions on CHOP value cross events (threshold, pulse, change).

### DAT Execute DAT
Python callback when a DAT changes.
- Callbacks: `onTableChange`, `onRowChange`, `onCellChange`, `onSizeChange`.

### OP Execute DAT
Python callback on operator-level events.
- Callbacks: `onCreate`, `onDestroy`, `onFlagChange`, `onWireChange`, etc.
- Use: track network structural changes.

### Parameter Execute DAT
Python callback when a parameter value changes.
- Use: react to user edits.

### Panel Execute DAT
Callbacks on UI panel events (clicks, rolls, keys in a panel).

### Keyboard Execute DAT
Global keyboard callback.

### MIDI Event DAT
MIDI events as table rows — alternative to MIDI In CHOP for event-style MIDI handling.

### MIDI In DAT / MIDI Out DAT
Stream MIDI as table data.

---

## Table DATs

### Table DAT
A 2D table of strings.
- Params: Rows, Cols, cells via inline editor.
- Use: static lookup tables, configuration, scene lists.

### File In DAT
Loads a text file (CSV, JSON, TSV, plain text).
- Params: File, Format.

### File Out DAT
Writes a DAT to disk.

### Folder DAT
Lists directory contents as a table.
- Use: auto-discover media files in a folder.

### Monitors DAT
Connected monitors as a table (resolution, position).

### Info DAT
Operator metadata as table rows.
- Use: introspection — cook time, input count, type, path.

### Perform DAT
Perf metrics as a table.

### System DAT
System info (OS, user, paths).

### Evaluate DAT
Evaluates Python expressions per cell.
- Use: compute table contents dynamically from other DATs.

### Reorder DAT / Sort DAT / Select DAT
Table manipulation.

### Merge DAT
Concatenates tables.

### Switch DAT
Switches between DAT inputs.

### Rename DAT
Rename rows or columns.

### Header DAT
Manage header rows / columns.

### Convert DAT
Converts between formats (JSON ↔ table, XML ↔ table, CSV ↔ table).

### Substitute DAT
Find/replace in cells.

---

## Data Format Bridges

### CHOP to DAT
Exports CHOP channels to a table.

### DAT to CHOP
Converts a table to CHOP channels.

### SOP to DAT
Exports SOP attributes to a table.

### TOP to DAT
Exports TOP pixel data to a table.

### Render Pick DAT
Picks from a Render TOP and exposes as table data — clicked-on object, hit point, etc.
- Use: interactive installations; click on 3D objects.

---

## Network / Web DATs

### Web Server DAT
Hosts an HTTP server inside TD.
- Params: Port, Callbacks for GET/POST.
- Use: remote control, webhook endpoints.

### WebClient DAT
HTTP client — GET / POST / etc.
- Use: poll APIs, post analytics.

### WebSocket DAT
WebSocket server/client.
- Use: real-time browser ↔ TD communication.

### TCP/IP DAT / UDP DAT
Low-level network.

### OSC In DAT / OSC Out DAT
OSC as DAT-formatted messages (parallels OSC In/Out CHOPs but produces/consumes string messages).
- Use: handling OSC address patterns beyond simple CC-like signals.

### Serial DAT
Serial port read/write.

### Touch In DAT / Touch Out DAT
TD-to-TD messaging.

### MQTT DAT
MQTT pub/sub.

### DMX In DAT / DMX Out DAT
DMX as DAT messages.

---

## Specialty DATs

### Null DAT
Passthrough / named endpoint.

### In DAT / Out DAT
COMP I/O.

### Clip DAT
Stores arbitrary binary clips.

### Error DAT
Collects errors/warnings from operators.
- Use: project health monitoring.

### Monitors / Info / Perform / System — see Table DATs.

### Performance DAT
Per-operator cook timing as a table.
- Use: profiling.

---

## Python Inside DATs

DATs are how you write Python in TD:

- **Module DAT mode:** a Text DAT can be imported as a module with `mod('text1')` or `mod.text1`.
- **Extension classes:** attach a Text DAT to a COMP's Extensions parameter — turns it into methods on that COMP.
- **Callbacks:** Execute DATs hold functions called by TD on events.
- **Parameter expressions:** any parameter's expression can reference Python directly; short snippets live inline, longer logic goes in a DAT.

### Extension pattern
```python
# Text DAT named "MyExt"
class MyExt:
    def __init__(self, ownerComp):
        self.ownerComp = ownerComp
    
    def DoThing(self):
        op('null1').par.Color1 = 0.5
```
On the COMP: Extensions page → set Extension1 to `mod('MyExt').MyExt(me)`. Now `op('myComp').ext.MyExt.DoThing()` works.

### Callback pattern
Execute DAT:
```python
def onFrameStart(frame):
    # per-frame logic — but prefer CHOPs for perf
    pass
```

---

## Canonical DAT Chains

### Config-driven scene switch
```
Table DAT (scene list) ──► DAT to CHOP ──► Switch TOP (index) ──► Out
```

### HTTP webhook trigger
```
Web Server DAT (POST handler) ──► Execute DAT (route to scene) ──► CHOP value changes
```

### Folder-watch media auto-load
```
Folder DAT (media directory) ──► DAT Execute DAT (onRowChange → reload Movie File In)
```

### Debug overlay
```
Info DAT (cook time) + Perform DAT ──► DAT to CHOP ──► Text TOP driven by CHOP values
```

### OSC address routing
```
OSC In DAT ──► DAT Execute (parse /address, route to op) ──► updates CHOP values
```

---

## DAT Performance Notes

- Table DATs are strings — numeric ops on them are expensive. Convert to CHOP once, work in CHOP domain.
- Execute DATs running expensive Python per frame are the most common perf regression in a TD project.
- Evaluate DAT with complex expressions per cell — heavy at large tables.
- Web Server DAT running on a hot path (frequent requests) — run logic in a separate thread via Script DAT or externalize.
- CHOP Execute DAT firing per frame of a fast CHOP: rate-limit with Trigger CHOP upstream.

---

## Reading This File

Grep by DAT name. Groups: Text/Script, Table, Format Bridges, Network, Specialty. For Python patterns, see "Python Inside DATs." For network/OSC/MIDI use, pair with `TD_WORKFLOW_MIDI_OSC.md`.
