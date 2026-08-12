---
name: wobar-ig-review
description: "Fortnightly Instagram review for WOBAR — captures post-level Insights from Chrome into the WOBAR IG Post Log spreadsheet, then writes a dated report to working/ig_reports/. Use this skill whenever Nick says 'ig review', 'instagram review', 'run the ig cycle', 'social review', 'insights review', 'what's working on instagram', or asks to log/refresh Instagram post data or produce the fortnightly social report."
---

# WOBAR IG Review

Fortnightly cycle: **capture → refresh → report.** Runs on Instagram Insights via Chrome, writes to the Google Sheet and to a dated markdown report in the vault.

**Core principle: the report exists to change what gets posted, and it must be as willing to say stop as to say more.** [[working/WOBAR_SOCIAL_PLAN]] §0 fixes Instagram to genuine surplus — *post more* is not an available recommendation, so the only lever is yield. A cycle that produces observations and no decision was a wasted hour. A report that only ever adds is not reading anything.

**Second principle: never manufacture a verdict.** At this account's volume most two-post comparisons are noise. The honest and most common output is *"logged, no conclusion yet."* §7 of the social plan turns its own failure-mode test on this review: a recurring analytics ritual is close to the archetype of comfortable work. What keeps it legitimate is that it changes behaviour, can say stop, and never runs ahead of the music.

---

## Files

| File | Role |
|---|---|
| **Google Sheet — "WOBAR — IG Post Log"** | Two tabs, owned by `contact.wobar@gmail.com`. **`Untitled`** = the raw log, one row per post — this is the only tab you write data into. **`REPORT`** = live formulas that recompute the whole computed half from the raw log; **it needs no maintenance and must not be hand-edited** except the ACCOUNT block (B12:B19). Added 2026-08-12. |
| **`working/IG_NEXT.md`** | ⭐ **The deliverable. Overwritten every run.** One screen: MAKE / STOP / WATCH / NOT YET, plus standing mechanics and whether the last change worked. Nick opens this at the desk when deciding what to post — **it is the only artifact he should need.** Added 2026-08-12 after the first run: the report tab *"still reads as raw data. I skim it but it doesn't really help."* A dashboard reports state; it does not decide. |
| `working/ig_reports/YYYY-MM-DD.md` | The dated record. One per run. Git-tracked and greppable — the accumulated series is what makes calibration possible. **Not the deliverable.** |
| `working/WOBAR_SOCIAL_PLAN.md` | **Read §0, §1, §5 before every run.** Owns the priority rule, the two jobs, and what counts as working. |
| `working/RESEARCH_IG_PLATFORM_GUIDANCE.md` | Instagram's own T1 guidance. §1 is why the three metrics are shares / comments / follows. |

---

## The window — offset, not trimmed

**Score the 14-day window that ended 7 days ago. List the last 7 days as provisional.**

```
  ────────┼──────────────┬─────────────┐
   older  │  21d → 7d    │  7d → now   │ today
          │   SCORED     │ PROVISIONAL │
          │  (mature)    │ (not compared)
```

**Why offset rather than trimmed.** A reel keeps accumulating for days, so a fresh post scored against a two-week-old one looks like a failure for being young. But simply excluding the newest posts means that on the next run they are 14–21 days old, outside a naive "last 14 days" window, and **never get scored at all.** Offsetting the window scores every post exactly once, at comparable maturity, with no gaps.

Provisional posts still appear in the report with their numbers. They do not vote.

⚠ **7 days is a working assumption, not a measurement.** It gets tested by step 3 — refreshing posts under 21 days old shows how much a post moves between captures. After 2–3 cycles, set the cutoff from that data and record the change here.

---

## Procedure

### 1. Orient
Read `WOBAR_SOCIAL_PLAN` §0/§1/§5. Read the previous report in `working/ig_reports/` — it names the one change that was made, which is what this run is testing.

### 2. Capture account level
Open `https://www.instagram.com/accounts/insights/?timeframe=30`.

Record: **followers · views · viewers · interactions · accounts engaged · profile activity (visits, external link taps)** and the follower/non-follower splits.

⚠ **Account-level Insights is a rolling 90-day window and nothing survives it.** Presets are 7/14/30 days, previous month, 90 days; `?timeframe=N` in the URL works. Uncaptured account-level data does not become old, it becomes nonexistent. **Audience demographics and follower gained/lost are not on web** — mobile only. Skip them rather than stall.

Also get **current SoundCloud followers** — the report needs the IG:SC ratio (§1's inversion constraint).

### 3. Capture and refresh posts
Grid: `https://www.instagram.com/accounts/insights/content/?media_type=all&metric=views&sort_by=highest&timeframe=30&view_type=card`

Per-post detail: `https://www.instagram.com/insights/media/{media_id}/` — gives everything needed: views + follower split, viewers, interactions + follower split, likes, comments, saves, **shares**, accounts engaged, profile activity, **follows**.

**Capture every post in the scored window, and re-capture every post under 21 days old** — refreshing is what makes the maturation curve measurable. Stamp `captured_at` on every row touched.

**Known mechanics, learned 2026-08-12 — do not rediscover these:**
- Grid cards are **video elements and are not in the accessibility tree.** `find` returns nothing. Coordinate clicking only.
- Click the **small format icon at the card's top-right corner**, not the card centre. Centre clicks land on the video and are swallowed.
- Clicks only register **before the video thumbnails paint.** After a back-navigation, wait ~10s for the grid, then click — expect roughly half to miss and simply retry.
- **Better route when the grid fights back:** the profile grid at `instagram.com/wobar.exe/` has real `<a>` links per post. Walk that in order instead.
- `metric=` accepts `views · viewers · interactions · accounts_engaged · shares` only. **Comments and follows are not sortable** — they require the per-post page.
- `sort_by=recent` is invalid and silently reverts to `highest`. `view_type=list` likewise reverts to `card`.

**Take no action on the account.** Read only — never like, comment, follow, post or boost. Clicks land near the like button in the post modal; be deliberate about coordinates.

### 4. Compute
Rates are **per viewer**, never per view, and always in preference to raw counts — reach varies several-fold across posts, so raw shares measure distribution, not quality.

`share_rate = shares / viewers` · `comment_rate = comments / viewers` · `follow_rate = follows / viewers`

Bucket rollups use the **median, never the mean** — a single outlier post (2026-08-04 ran 331 shares against a field of 0–25) destroys an average.

**travels vs talks** = `share_rate ÷ comment_rate`. High = it travels to strangers by DM and recruits. Low = it starts conversation among people already there and deepens. **These are different jobs, not better and worse**, and averaging them into "engagement" destroys the distinction.

### 5. Write to the sheet — automatic, via the browser
**Drive's MCP tools are create/read only and cannot update a file. Write through Chrome instead.** Verified working 2026-08-12:

1. `navigate` to the Sheet URL, wait ~8s for it to load.
2. **Click the target cell first** (e.g. `A8` for the first empty row). ⚠ **The clipboard write fails with `NotAllowedError: Document is not focused` unless a click into the page precedes it.** This is the whole trick.
3. `javascript_tool`: build the rows as an array of arrays, `join("\t")` per row and `join("\n")` across rows, then `await navigator.clipboard.writeText(tsv)`.
4. `computer` → `key: "cmd+v"`. Sheets splits the TSV across columns and evaluates the formulas.
5. Screenshot to confirm, and scroll right to check the rate columns computed rather than landing as text.

**Never recreate the Sheet to add rows** — it mints a new URL every time and orphans the old file, which Drive tools cannot delete.

Include the rate formulas in each row so they self-maintain:

`age_days` `=IFERROR(B{r}-A{r})` · `share_rate` `=IFERROR(Q{r}/P{r})` · `comment_rate` `=IFERROR(R{r}/P{r})` · `follow_rate` `=IFERROR(S{r}/P{r})`

Never fill `why_guess`, `confidence` or `verdict`. **Those columns are Nick's** — the guess recorded before the outcome is known is what makes the log compound, and a filled-in guess from the assistant is worthless.

### 6. Update the ACCOUNT block, then write the judgment report

**The `REPORT` tab computes itself** the moment new rows land in the raw log — window boundaries, scored/provisional counts, thresholds, bucket medians, the sorted post table and the 2×2 quadrant per post. **Do not rebuild it.** The only cells to touch are the ACCOUNT block, `B12:B19` — followers, SoundCloud followers, views, viewers, non-follower share, profile visits, link taps — because account-level figures are not derivable from post rows.

Then write `working/ig_reports/YYYY-MM-DD.md` using the template below, **carrying only the judgment half**: verdict, the experiment register, calibration, THE ONE CHANGE, and any gap worth recording. Tables the `REPORT` tab already computes may be summarised for the record, but the sheet is their home.

**Division of labour:** the sheet answers *what happened*, always current, no run required. The markdown answers *what it means and what changes*, dated and immutable. Nick can open the sheet any day without waiting for a cycle.

### 7. Write `working/IG_NEXT.md` — the actual deliverable

**Overwrite it. It is always current, never a series.** Four blocks, and nothing else:

| Block | Rule |
|---|---|
| **MAKE** | One thing. The format with the best evidence behind it, named specifically enough to act on without interpretation. |
| **STOP** | One thing. If nothing has earned a stop, say *"nothing yet"* — never pad it. |
| **WATCH** | The single metric currently doing the discriminating, with the numbers that prove it. |
| **NOT YET** | What the data is *close* to saying and cannot say yet. This is what stops the file overclaiming. |

Plus **STANDING** (the hard mechanics worth re-reading at the moment of posting) and **LAST CHANGE** (what the previous cycle changed and whether it worked — calibration where he will actually see it).

**Rules for this file:**
- **Every line is an instruction, not a finding.** "Make another studio post" — not "studio posts perform well."
- **Numbers only where they earn the instruction.** No tables. If it needs skimming it has failed.
- **One screen. Sixty to a hundred words of body.**
- **It must be usable without opening the sheet or the report.** If it isn't, the wrong thing is in it.

### 8. Then talk it through
**The cycle ends in a conversation, not a document.** Bring the read, let Nick push back, agree the one change together — the dataset is small enough to hold entirely in a session, and the questions worth asking ("why did that post get 331 shares and 2 comments?") are ones no spreadsheet answers. Write `IG_NEXT.md` and the dated report as the *record of what was agreed*, not as a recommendation delivered cold.

---

## Report template

**Two rules govern this template. A section with nothing to say is OMITTED, not filled** — that is what stops the report becoming a ritual that generates content to justify itself. **And no verdict on any variable with fewer than 3 mature observations per level** — it says "not enough yet" and moves on.

⚠ **Count observations across every mature post in the log, not only those inside the scored window.** Amended 2026-08-12, first run: the bucket variable had n=2 inside the window and would have been gagged, while the full captured set held 5 music posts against 5 commentary posts with **total separation on shares** (331·25·19·16·10 against 3·0·0·0·0). A gate that suppresses that is protecting nothing. The window governs *which posts are compared*; the gate counts *how much evidence exists*. When a call rests partly on provisional rows, say so in the report and re-check it next cycle.

**The whole report fits on one screen. If it needs scrolling it has stopped being a rudder.**

```markdown
# IG REVIEW — YYYY-MM-DD
Scored window: YYYY-MM-DD → YYYY-MM-DD (14d, ending 7d ago) · N scored · N provisional

## Verdict
[One line. What changed, or that nothing did.]

## Account
Followers N (delta ±N) · IG:SC ratio N:N [direction since last run]
Views N · Viewers N · Interactions N · Accounts engaged N · Profile visits N · Link taps N

⚠ [Only if IG grew while SoundCloud did not — §1's inversion constraint. Growing IG against a flat
SoundCloud deepens the thing the credibility is meant to fix.]

## Scored posts
| date | bucket | topic | viewers | share% | comment% | follow% | %flwr | travels/talks |

## Bucket medians
Follows per 1,000 viewers, median: music N · meme N · give-back N

## The 2×2
Thresholds are relative to the trailing median, not fixed — there is no external benchmark
(RESEARCH_IG_PLATFORM_GUIDANCE §8) and won't be until a peer-tier comp set exists.

REPEAT (high reach, high follow rate): ...
TRAP (high reach, low follow rate): ...
PUSH HARDER (low reach, high follow rate): ...
CUT (low reach, low follow rate): ...

⚠ The 2x2 scores FOLLOW RATE ONLY, and that is a choice, not a truth. Corrected
2026-08-12: it called the GIF/front-camera posts a TRAP while they carried 3.14%
and 1.26% comment rates against 0.09-0.68% on the music posts — five to thirty
times, on a metric Instagram explicitly names. POSTS HAVE DIFFERENT JOBS: some
travel (shares, recruiting strangers), some talk (comments, identifying who to
approach), some convert (follows). One conversion axis cannot see the first two.
Read the quadrant beside the travels/talks column, never alone, and never let it
recommend cutting a post that is winning a job it does not measure.

## Experiments
| variable | hypothesis | mature posts | status |
[<3 posts → "not enough yet". No exceptions.]

## Calibration
[Old why_guess entries the data can now check. Was the read right?]

## THE ONE CHANGE
[Exactly one. Or: "No change — keep going." Allowed to say cut.]

## Provisional — not scored
[Last 7 days, numbers shown, explicitly not compared.]
```

---

## Standing rules

- **One change per cycle, maximum.** Five changes means next cycle can attribute nothing.
- **Never stop what is working in order to test.** The experiment budget is the marginal post.
- **Who outranks how many.** A rising follower count made of non-lane accounts is the CUTDWN failure in progress ([[working/WOBAR_SOCIAL_PLAN]] §3), not success, and rates alone cannot see the difference.
- **Never chart views or likes.** The highest-viewed post of 2026-08 returned 0 shares and 1 follow. A views line going up feels like progress and means nothing — it is the Insights trap rendered prettily. Instagram's own guidance lists neither as a metric to watch.
- **Music first, always** (§0). This review never generates a reason to post ahead of a release.
- **Two permanent taxes, priced in before judging a music post:** original audio forgoes Instagram's trending-audio ranking signal, and a sound-first product fights a sound-off platform.
