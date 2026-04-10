# TWOZERO + Claude Code Setup Guide

Full install guide for connecting TWOZERO (AI-powered TD node builder) to Claude Code with the WOBAR vault context. Follow in order. Each step has a verification check.

---

## Prerequisites

- **TouchDesigner 2025.32280+** — check version: Help > About TouchDesigner
- **Claude Code installed** — verify: run `claude --version` in terminal
- **WOBAR vault repo cloned** — should already be at your local path for the `wobar/` repo

If your TD version is older than 2025.32280, update first. TWOZERO won't load on older builds.

---

## Part 1 — Install TWOZERO Plugin

### Step 1: Download the plugin
Download `twozero.tox` from:
```
https://www.404zero.com/pisang/twozero.tox
```

### Step 2: Install in TouchDesigner
1. Open TouchDesigner
2. Drag `twozero.tox` into your project network
3. Select **Install** when prompted
4. The twozero component should appear in your network

### Step 3: Enable MCP
1. Open the twozero component parameters
2. Find the MCP toggle and enable it
3. Default port: **40404**
4. Leave port as default unless you have a conflict

### Step 4: Verify MCP is running
Open a browser or terminal and hit:
```bash
curl http://localhost:40404/mcp
```
If you get a response (even an error message about method), the server is live. If connection refused, MCP isn't enabled or TD isn't running.

---

## Part 2 — Connect Claude Code

### Step 5: Register TWOZERO as an MCP server
In terminal:
```bash
claude mcp add --transport http --scope user twozero_td http://localhost:40404/mcp
```

### Step 6: Verify registration
```bash
claude mcp list
```
You should see `twozero_td` listed with the localhost URL.

---

## Part 3 — Launch Claude Code with WOBAR Context

### Step 7: Navigate to the vault repo
```bash
cd /path/to/your/local/wobar/repo
```
This is the directory that contains `CLAUDE.md`, `WOBAR_CONTEXT.md`, and the `reference/` and `working/` folders. It's the git repo root.

**This is where you always launch Claude Code from for WOBAR TD work.**

### Step 8: Launch Claude Code
```bash
claude
```
Claude Code reads `CLAUDE.md` on startup. It will orient from the vault and have TWOZERO tools available.

### Step 9: Verify TWOZERO connection
First message to Claude Code:
```
Show me what you can see in my TD project.
```
If TWOZERO is connected and TD is running, Claude Code should describe your current project state — what containers exist, what operators are visible, etc.

If it can't connect, check:
- Is TouchDesigner running?
- Is the twozero component in your project?
- Is MCP enabled in the twozero parameters?
- Is port 40404 free? (`lsof -i :40404`)

---

## Part 4 — Test Build (Proof of System)

This test validates the full pipeline: Claude Code reads vault rules → uses TWOZERO to build a network → follows WOBAR conventions.

### Step 10: Open a fresh TD project
File > New to start clean. Drag twozero.tox in and enable MCP if it's not persistent.

### Step 11: Run the test prompt
Paste this into Claude Code:
```
Build me a simple Act 1 circle breathing visual. 
Output target: 1920x1080. Starting from blank network. 
Use the WOBAR conventions from the reference files.
```

### What to check in the result:

**Naming:**
- [ ] Operators use lowercase_with_underscores
- [ ] Control CHOPs prefixed with `ctrl_`
- [ ] Null TOPs prefixed with `null_`
- [ ] Chain capped with a Null TOP

**Architecture:**
- [ ] Circle TOP present with radius ~0.45, softness 0.25-0.4
- [ ] Composite TOP (Multiply or Inside) for masking
- [ ] LFO CHOP or sub-bass analysis driving breath rhythm (60-80 BPM range)
- [ ] Control values in Constant CHOPs, not hardcoded

**Color:**
- [ ] HSV Adjust TOP with satmult ~0.15
- [ ] Level TOP with blacklevel 0.08, gamma 0.75, contrast 1.3-1.35
- [ ] Purple palette (deep purple, not generic)

**Act 1 constraints:**
- [ ] Warm purple glow present
- [ ] No sharp geometric forms
- [ ] No aggressive motion
- [ ] No cool colors dominating

### Step 12: Log the result
Whether it passes or fails, this is your first build log entry. In Claude Code:
```
Log this build session to working/TD_BUILD_LOG.md.
What you got right, what I had to correct.
```

---

## Part 5 — Ongoing Workflow

**Every TD session:**
1. Open TouchDesigner with twozero plugin active
2. `cd` into the wobar repo
3. Run `claude`
4. Work — build, iterate, debug
5. Close out: Claude Code updates WOBAR_ACTIVE.md + TD_BUILD_LOG.md

**Periodically (every 5-10 sessions):**
1. Open Cowork (here)
2. Review TD_BUILD_LOG.md together
3. Promote repeated corrections to WOBAR_TD_AGENT_RULES.md
4. The system gets smarter

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| "Can't connect to MCP" | Verify TD is running + twozero MCP is enabled + port 40404 open |
| Claude Code doesn't read vault files | Make sure you launched from the repo root (where CLAUDE.md lives) |
| TWOZERO builds but ignores WOBAR conventions | Check that Claude Code actually read WOBAR_TD_AGENT_RULES.md — ask it "what naming convention should you use?" |
| Port conflict on 40404 | Change port in twozero settings, then re-register: `claude mcp remove twozero_td` then `claude mcp add` with new port |
| TWOZERO tools not appearing | Run `claude mcp list` to verify registration. Try `claude mcp remove twozero_td` and re-add |
| Build looks generic / wrong act | Claude Code may not have read the framework file — explicitly say which act and tell it to read WOBAR_FRAMEWORK.md |

---

## Quick Reference

| What | Where |
|------|-------|
| TWOZERO download | https://www.404zero.com/pisang/twozero.tox |
| MCP endpoint | http://localhost:40404/mcp |
| Register MCP | `claude mcp add --transport http --scope user twozero_td http://localhost:40404/mcp` |
| Verify MCP | `claude mcp list` |
| Launch directory | wobar repo root (where CLAUDE.md lives) |
| Agent rules | reference/WOBAR_TD_AGENT_RULES.md |
| TD reference | reference/WOBAR_TD_REFERENCE.md |
| Build log | working/TD_BUILD_LOG.md |
