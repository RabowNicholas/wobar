---
title: Release Plan Exercise — shareable prompt
version: 1.0
created: 2026-07-26
status: live — hand this to another artist
scope: A single self-contained prompt an independent artist pastes into an AI. Runs a guided exercise from "I'm frustrated with social media" to a concrete release plan built on their own numbers. Genre-agnostic.
---

# HOW TO USE THIS

Send them the block below. They paste it into Claude (or any capable AI with web access) and answer the questions as they come. It takes about an hour. It ends with a release plan.

Tell them two things up front:
1. **It will ask questions before it gives answers.** That's the point — the plans that fail are the ones written before anyone measured anything.
2. **It's built to disagree with them.** If it only agrees, it's broken.

---

# THE PROMPT — copy everything below

```
I'm an independent musician and I want to work out a release plan that actually
fits me. I'm going to be honest with you: I'm frustrated with marketing my music
on social media. It feels like shouting into a void, or like an echo chamber of
other producers, and I don't know if I'm bad at it or if it's the wrong thing to
be spending my time on.

I don't want a content strategy. I want to find out what actually moves the needle
for someone in my position, and end up with a release plan I'll actually follow.

HOW I WANT YOU TO WORK

- Ask me questions ONE OR TWO AT A TIME and wait for my answer. Do not send me a
  questionnaire. I will disengage.
- Do not be agreeable. If my assumptions are wrong, say so directly. If something
  I'm proud of isn't working, tell me. I can handle it and I need it.
- Do not reassure me that social media doesn't matter, and do not tell me to post
  more or post better. Neither of us knows yet. We're going to find out from MY
  numbers.
- Use the web. Verify things. When you can't verify something, say "nobody has
  published this" instead of guessing — that's a useful answer, not a failure.
- Tag every claim you make: [SOLID] = verified with a real source. [OBSERVED] =
  it's in my actual data but uncontrolled. [GUESS] = your reasoning, unproven.
  I want to know which is which.

RUN IT IN THIS ORDER. Don't skip ahead to advice.

STAGE 1 — WHERE I ACTUALLY AM
Ask me for links to every place my music and I exist: streaming, socials, wherever
I upload, mailing list. Then look them up and build me a table: followers on each,
how much I've posted or released, and how the last 6-10 things performed.

Then compute my funnel — how many people get reached, how many look at my profile,
how many actually follow or click through. Give me the numbers with no
interpretation yet.

STAGE 2 — WHAT I ACTUALLY WANT
Before any strategy, ask me this and push me for a specific picture, not a category:
"If it's 12 months from now and this went well, what specifically happened?"

Then challenge my answer. Tell me what it implies, what it demotes, and where it
conflicts with how I currently spend my time. If my answer changes halfway through
this conversation, that's normal — the second answer is usually the real one.

Also ask whether the different parts of what I'm doing are pointed at the same
goal, or three different ones. Be blunt if they're not.

STAGE 3 — WHAT LANE I'M ACTUALLY IN
Don't use my stated influences — I'll describe myself aspirationally. Ask me for
evidence of what I actually make and play: my last DJ set or live setlist, my last
10 finished tracks, or my most-played artists this year.

Break it down by proportion. Tell me where my center of mass actually is, who
shows up most, and whether that matches how I describe myself. If it doesn't,
tell me which one is real.

STAGE 4 — WHO MY REAL PEERS ARE
This part matters and it's easy to get wrong.

Build a comparison set from LABEL ROSTERS — pick 4-6 labels that release artists
in my lane, including small ones, and take the artists from their recent releases.
Do NOT build the list by searching for "artists like me," because search only
surfaces people who already have press and management, and you'll end up comparing
me to a group where everyone is succeeding and conclude I'm uniquely broken.

When you need their social handles, don't web-search for them. Go to each label's
own account and look at who that label FOLLOWS. Labels follow their artists whether
or not those artists have any press. Log the ones you can't find rather than
quietly dropping them.

STAGE 5 — WHERE THE AUDIENCE ACTUALLY IS
For each peer, put their numbers on EVERY platform side by side, including
streaming. Add me to the table.

Then compare per-follower, not raw — raw comparisons against people with 50x my
audience tell me nothing. Tell me which platform my gap is actually on. It may not
be the one I've been worrying about.

STAGE 6 — DOES ANY OF IT CONVERT
Two questions:
(a) Do peers with similar social followings have wildly different streaming numbers?
    If yes, social size doesn't drive listeners in my lane and growing it isn't the
    lever for that goal. Say so plainly.
(b) Whatever door I want — a label, an agent, a playlist, a support slot — find
    people who recently got through it and how big they were at the time. Their
    current follower count is an upper bound on what they had then. Tell me whether
    those doors are gated on audience size or on taste.

STAGE 7 — ARGUE AGAINST YOURSELF
Before you write me a plan, take your main conclusions and try to REFUTE them.
Search independently. Rate each: CONFIRMED (a platform's own docs, or two solid
independent studies) / PARTIAL / UNSUPPORTED (nobody has measured this) / REFUTED.

Treat agency blogs, SEO listicles and Reddit as hypotheses only, never as evidence.
If you find a statistic you can't trace to a real named study, flag it — there is a
lot of fabricated data circulating on exactly these questions.

Then tell me which of your conclusions didn't survive.

STAGE 8 — THE RELEASE PLAN
Now write it. Keep it short enough that I'll actually follow it. Include:

- The goal, and the 2-3 numbers I track (with today's values as the baseline)
- What I make, how often, and where each thing goes — be specific about which
  platform gets what, and why
- The release cadence, and what I hold back if holding anything back serves a
  purpose
- What I'm deliberately NOT doing, listed explicitly so it stops nagging at me
- What this plan does NOT know — the honest unknowns
- Tag every recommendation with its confidence

Then check the recommendations against each other. Plans built from separate
findings often deadlock when you combine them — if two parts of your advice cancel
out, tell me before I find out the hard way.

LAST THING
If at any point I show you something from my own world that contradicts what you
found — a link, a screenshot, an artist who obviously does the opposite of what you
said — actually look at it and update. My first-hand knowledge of my scene is
usually better evidence than a broad search, especially where nobody has published
real data. Don't defend your earlier position out of consistency.

Start with Stage 1.
```

---

# NOTES FOR WHOEVER SENDS THIS

**On the frustration.** The prompt deliberately refuses to resolve the social-media question up front in either direction. Telling a frustrated artist "social media doesn't matter" is as useless as telling them to post more — both skip the measurement. The honest answer is usually "here's what your own funnel says," and that lands very differently than an opinion.

**The most important instruction in there** is Stage 4's handle-resolution trick. Building a peer set from search results silently selects for artists with press and management, which makes every comparison say "everyone is doing better than you." Sampling from label rosters, and resolving handles from the label's own following list, is what surfaces the peers who are also struggling — which is the comparison that's actually informative.

**Expect the goal to change in Stage 2.** It usually does, once someone says the aspirational version out loud and hears what it implies. The revised answer is the one to plan against.

**The plan should feel smaller than expected.** If it comes back as a content calendar and a growth strategy, the exercise failed. A good outcome is usually a short list, most of it about making and sending music, with an explicit "stop doing this" section.
