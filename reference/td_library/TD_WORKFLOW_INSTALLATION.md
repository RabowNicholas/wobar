---
title: Interactive Installation Workflow
version: 1.0
last_updated: 2026-04-16
status: live
scope: Building long-running interactive installations — Kiosk Mode, crashAutoSave, watchdog scripts, sensor input, unattended operation.
dependencies: TD_LIBRARY_INDEX.md, TD_APPLE_SILICON.md, TD_WORKFLOW_LIVE_VJ.md, TD_OPERATORS_CHOP.md
---

# INTERACTIVE INSTALLATION WORKFLOW

Art installations that run unattended for hours/days, react to visitors, and recover from crashes without human intervention. Higher bar than live performance: the user won't be there to fix it.

---

## Installation vs Performance

| Factor | Live performance | Installation |
|--------|------------------|--------------|
| Attended | Yes | No |
| Runtime | 1–2 hrs | 8 hrs to months |
| Input | Performer (MIDI, OSC) | Audience (sensor, touch) |
| Failure mode | Performer troubleshoots | Must self-recover |
| Iteration | Per-gig tuning | Set-and-forget |

**Installation requires more engineering per visual result. Budget accordingly.**

---

## Reliability Layers

### Layer 1 — crashAutoSave
TD Preferences → Auto Save → crashAutoSave every N minutes. If TD dies, reopening recovers the last autosaved state.
- Set to every 2–5 minutes.
- Write to external SSD, not to the internal boot drive (thermal throttle risk on long runs).

### Layer 2 — Watchdog script (external)
Separate process monitors TD. If TD crashes or hangs, the watchdog restarts it.

On Mac: launchd agent + shell script checks every 30 seconds that TD is alive.
```bash
#!/bin/bash
if ! pgrep -x "TouchDesigner" > /dev/null; then
    open /path/to/project.toe
fi
```

### Layer 3 — Kiosk Mode
TD's Kiosk Mode (Preferences) launches project fullscreen on boot, disables editor UI. Designed for installations.
- Set Mac to auto-login.
- TD project in Login Items.
- Project opens in Perform Mode on launch.

### Layer 4 — Hardware watchdog (PowerPlug)
USB-controllable power outlet. External process monitors the install's health; if soft recovery fails, cycles power to the Mac.
- Last resort; use only if installation can't be attended.

---

## crashAutoSave Setup

### Configure
Preferences → Save → crashAutoSave:
- **Enable** = On.
- **Interval** = 5 minutes.
- **Save to Path** = external SSD path.
- **Max files** = 10.

### On crash
TD writes `<project>_crashautosave.N.toe`. Opening the latest one recovers state at the last autosave (within 5 minutes).

### Combined with launch script
```
open /ExternalSSD/project_crashautosave.latest.toe
```
- Shell script picks the most recent autosave by mtime.
- Watchdog uses this on restart.

---

## Kiosk Mode Details

### Preferences → Kiosk Mode
- **Kiosk Mode** = On.
- When enabled: project opens in Perform Mode automatically, no editor UI.
- Escape exits. You can remap the exit key or disable exit entirely for public installations.

### Disable exit entirely
Preferences → Kiosk Mode → Password field. With a password set, Escape prompts for it. Visitors can't exit.

### Auto-launch on boot (Mac)
1. System Settings → Users → Login Items → Add TouchDesigner.app.
2. System Settings → Users → Automatic Login = On.
3. Boot Mac → auto-login → TD opens → loads last project → Kiosk Mode → Perform Mode.

### Disable system updates
macOS can install updates overnight and reboot. This will break a long-running install.
- System Settings → Software Update → Disable auto-updates.
- Or use Focus mode to suppress all prompts.

---

## Sensor Input — Mac-Compatible Options

### Orbbec Astra / Femto (recommended for Mac)
- USB depth camera.
- M1-compatible via Orbbec SDK.
- Exposes depth image, color image, body tracking via TD plugin.

### MediaPipe GPU plugin
- Extracts body pose / hand landmarks / face mesh from any webcam.
- M1 native.
- Use: webcam → MediaPipe → skeleton positions as CHOP channels → drives visuals.

### Kinect Azure — NOT on Mac
Requires Windows / Linux + Kinect Azure SDK. On Mac, don't rely.

### RealSense — Unsupported on M1
Intel RealSense SDK is x86-only. Not usable on M1 without emulation (and even then unstable).

### LeapMotion (hand tracking)
- Small USB hand tracker.
- Historical: works via Leap SDK on Mac.
- Confirm with latest Ultraleap SDK before committing.

### Capacitive touch / hardware triggers
- Arduino / Teensy board reads touch sensors / buttons.
- Sends OSC or serial to TD.
- Cheap, reliable.
- Serial DAT in TD reads the data stream.

### Proximity / ultrasonic
- HC-SR04 ultrasonic sensor on Arduino → distance value → TD.
- Detects approach/retreat of visitor.

### IR break-beam
- IR transmitter + receiver across a doorway.
- Beam broken = trigger.
- Used for entry detection.

---

## Long-Running Cook Health

### Memory leaks
TD shouldn't leak, but:
- Python scripts that accumulate state across days can.
- Check periodically in debug: Python Textport memory usage.
- Kill-restart at scheduled intervals if memory grows.

### Thermal throttling
- Mac running for days gets hot.
- Install should have ventilation / sit in AC.
- Spec the Mac for the installation (Studio often more stable than MBP for long-term due to cooling).

### Disk fill
- Log files, autosaves, caches accumulate.
- Weekly / monthly cleanup job.
- If using Movie File Out for recording visitor footage, plan disk space carefully.

### Scheduled daily restart
- launchd: restart TD at 3am daily. Fresh state every day.
- Prevents subtle drift from days of runtime.

---

## Visitor Interaction Patterns

### Pattern 1 — Presence-based animation
```
Sensor detects presence → presence CHOP = 1 → triggers animation state
No presence > 30s → return to idle state
```

### Pattern 2 — Touch-reactive
```
Capacitive sensor → touch event → burst effect at sensor's mapped visual location
```

### Pattern 3 — Multi-person crowd response
```
Depth camera → count blobs in view → visitor_count CHOP
Visitor count drives crowd-dependent visual (more people = more particles)
```

### Pattern 4 — Path-based reveal
```
Visitor walks past → path tracked → visual "follows" them along the wall
Use Orbbec body tracking → CHOP → drives a Feedback TOP offset
```

### Pattern 5 — Collaborative state
```
Multiple visitors interact simultaneously
Each visitor is a tracked blob, each affects a region of the visual
State persists across visitors (visual accumulates)
```

---

## Idle vs Active States

### Idle state
- Minimal generative visual, low brightness, low reactivity.
- Gets attention without being chaotic.

### Active state
- Triggered by presence / interaction.
- Higher intensity, more color, more motion.

### Transition
- Crossfade 2–5 seconds between states.
- Don't pop — feels wrong for an installation.

### Fallback idle
- If sensor fails and no activity detected, stay in active state? Or fallback idle?
- Log the issue; don't make visitors notice.

---

## Sensor Failure Recovery

### Check sensor health
```python
# Execute DAT every 30s
sensor_data = op('sensor_in')[0]
if sensor_data is None or sensor_data.lastCookTime > 5:  # 5s since last data
    # mark sensor unhealthy, fall back to random / timed triggers
    op('fallback_enabled').par.value = 1
```

### Software redundancy
- Two sensors for the same purpose.
- If sensor A silent, use sensor B.

### Graceful degradation
- Full interactivity → sensor timing-based random → timer-based autonomous mode.
- Installation keeps running even with total sensor failure.

---

## Logging for Installations

### What to log
- Crash timestamps.
- Sensor dropouts.
- Visitor count per hour (useful retrospectively).
- Framerate over time (catch thermal throttle).

### How
```python
# Execute DAT on interval:
import datetime
log_entry = f"{datetime.datetime.now().isoformat()}, fps={project.cookRate}, visitors={op('visitor_count')[0]}"
with open('/ExternalSSD/install_log.txt', 'a') as f:
    f.write(log_entry + '\n')
```

### Review
Weekly pull of log files. Check for patterns — does it always crash at midnight? Framerate drops every 6 hours?

---

## Installation Pre-Launch Checklist

### 1 week before
- [ ] Hardware confirmed: Mac model, sensors, cables, power.
- [ ] Software version locked: TD build, OS version.
- [ ] Kiosk Mode + auto-login + crashAutoSave configured.
- [ ] Watchdog script installed and tested.
- [ ] Sensor wiring tested end-to-end.
- [ ] All dependencies installed (MediaPipe plugin, Orbbec SDK, etc.).

### 1 day before
- [ ] Full 24-hour test run. Note any issues.
- [ ] Backup of project to external drive.
- [ ] Spare hardware: Mac power brick, cables, sensor.
- [ ] Installation documentation: how to restart if needed.

### Day of
- [ ] Install hardware, position sensors.
- [ ] Boot → confirm auto-launch works.
- [ ] Watch for 30 minutes. Confirm framerate, reactivity.
- [ ] Step away. Check back in 2 hours.

### During run
- [ ] Daily check-in. Look at logs.
- [ ] Weekly: clean autosaves, review framerate logs.

---

## Common Installation Failures

### Mac goes to sleep
- Preferences → Energy Saver → Prevent sleep = On.
- Caffeine app as backup.

### macOS update reboots Mac
- Disable all auto-updates.

### Display goes off
- System Settings → Displays → Turn display off = Never.

### Sensor disconnects over USB
- Use powered USB hub.
- Long USB cables can drop — use active cables for > 3m.

### WiFi drops, breaks OSC
- Use ethernet, not WiFi.

### Projector overheats and dims
- Commercial projector with rated 24/7 operation.
- Gaming-grade or AV-rated, not consumer.

### Power outage wipes state
- UPS (uninterruptible power supply). 15-minute runtime is enough for a clean shutdown.

### Heavy visitor day crashes TD
- Stress-test with simulated high-input events.
- Pre-warm all ops, reserve headroom (run at 50% cook budget normally so spikes have room).

### Dust on sensor
- Regular clean schedule if install is long-running.
- Especially depth cameras — dust affects IR.

---

## Remote Monitoring

### Screen-view over VNC / Screen Sharing
- See what the installation is doing from anywhere.
- Mac has Screen Sharing built in.
- Configure with strong auth; port-forward carefully.

### Push notification on crash
- Watchdog script sends Slack/email on restart events.
- `curl` to a webhook → Nick sees the restart happened.

### Status dashboard
- Small web server in a DAT → reports state → external dashboard shows live health.
- For installations with support SLA.

---

## Reading This File

For the first installation: read sequentially. Critical sections: §Reliability Layers + §Kiosk Mode + §crashAutoSave. Sensor choices in §Sensor Input. §Installation Pre-Launch Checklist is the gate before going live. §Common Installation Failures is the debugging cheat sheet.
