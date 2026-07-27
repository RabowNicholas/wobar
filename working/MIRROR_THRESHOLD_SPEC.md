---
title: Mirror Threshold — Build Spec
version: 0.2 (+ §0 acquisition model, door copy locked, unreleased-music format 2026-07-27)
last_updated: 2026-07-27
status: live — build spec; stack-agnostic core + Twilio specifics. Integration layer TBD once app stack confirmed.
scope: The technical build for the Mirror Threshold — the SMS door from the seen world into the Ether. Twilio SMS backbone, hosted inside Nick's existing app. Grounds on WOBAR_WORLD §7 (the door, the Ether, glimpses, void poems).
dependencies: [[reference/WOBAR_WORLD]], [[reference/WOBAR_COPY]]
---

# MIRROR THRESHOLD — BUILD SPEC

The door: a Wanderer texts **MIRROR** → sets an intention (**seeing**) → crosses
into **the Ether**, where **glimpses** arrive (no schedule) and real two-way
dialogue happens. Twilio SMS. Automate only the door; everything past it is human.

---

## §0 — ACQUISITION MODEL (added 2026-07-27)

**The funnel inverted.** This spec was written when the plan was IG/TikTok → SMS: a **volume** funnel where huge top-of-funnel offsets brutal conversion. That funnel is measured and broken — 90 days of Instagram produced 9,148 non-followers reached, 706 profile visits, and **20 external link taps.**

The channel mix is now SoundCloud-first + Reddit ([[working/WOBAR_GROWTH_PLAN]]), and the acquisition model changes shape with it:

> **The door lives quietly in existing copy. People searching find it. Everyone else is invited personally.**

**Volume is not the goal. ~40 right people is.** At 40, two-way is real, the promise is keepable, and the list functions as a taste-bar instrument. Relationship-based acquisition at **2–3 a week reaches that in a season** — no reach required, and it self-selects for people who actually reply.

### Texture vs mechanism — do not confuse these
- **Passive placement is the texture.** It makes the door real and lets the rare searcher find it. At current scale it converts near zero on its own. That is expected, not failure.
- **Personal invitation is the mechanism.** Reddit relationships and the Flow State residency do the actual work.

Judging passive placement by subscriber count will produce the wrong conclusion. **Log how each subscriber arrived** — `invited` vs `found` — one field, and it's the only way to ever answer this.

### Sources, ranked
| Source | Volume | Conversion | Note |
|---|---|---|---|
| **Reddit** | low | **highest** | After a real exchange, the invitation is natural rather than a pitch. Stated currency there is already feedback + production help |
| **Live sets (Flow State residency)** | medium | **high** | The highest-intent moment that exists — people who just had the experience. Monthly, recurring, underweighted since the local goal was parked |
| **SoundCloud descriptions** | medium | low–medium | 11+ permanent free surfaces; compounds with the catalogue |
| **DJ plays / VA credits** | low | medium | Someone chasing an ID is already looking |
| **Instagram** | high | **~zero (measured)** | Leave it as credibility. Do not build on it |

### The door is the phone number
**The parked Terminal Rebuild does not block this.** The Mirror was specced as the `mirror` path inside the terminal, but SMS needs no web page — `text MIRROR to [number]` works from a track description, a DM, a stage, or an end-card. The number *is* the door.

### Door copy — LOCKED 2026-07-27

Hard constraint: **plain, never reaching.** A mystical invitation breaks **Law 0** and *explains* what **WORLD §8** says may be shown but never explained. State a fact and stop. `text MIRROR to …` is dual-valid by construction — the outsider reads an SMS keyword, the insider reads the Mirror.

**Minimal** — end-cards, artwork, bio, anywhere without room:
> text MIRROR to 801-XXX-XXXX

**Track / YouTube description** — one line, factual, bottom of the fold:
> unreleased music goes out here first — text MIRROR to 801-XXX-XXXX

**Personal invitation** — Reddit, DMs. First person, Nick's voice, *not* world-voice:
> i send unreleased stuff to a small list before it's out anywhere — and i actually read the replies. want in? text MIRROR to 801-XXX-XXXX

That last one is the one that matters: plain, names the value, and names the two-way part — the actual differentiator.

**Rejected:** *"cross the threshold"* · *"enter the Ether"* (both explain) · *"exclusive content"* · anything with *"join"* (marketing register). All three reach.

### Placement
SoundCloud track descriptions (bottom line) · SoundCloud bio (minimal — folds into the bio rewrite already owed) · YouTube descriptions (per [[reference/WOBAR_YOUTUBE]] fold + CTA order) · visualizer end-cards · live-set close · **Reddit and DMs use the personal version.**

### What lives in the channel
Content model is owned by **WORLD §7** (journal glimpses · release glimpses · open questions · void poems). Two amendments from the 2026-07-27 session:

1. **Add a fifth format — unreleased music sent for reaction.** Not "release glimpses" (finished work). A dub nobody has, sent for a response. **This is the one thing SMS does that SoundCloud and Reddit structurally cannot**, and it's the format with the clearest fan value — something they want to receive, not something Nick wants to send.
2. **The bare release announcement does not belong here.** *"New track out now"* is redundant — a Spotify follow does it free. *"Here's the track, here's what it came out of, tell me what you think"* is not redundant at all. Same release, different artifact. **The test for any format: does it create a reply?**

**Also flagged, not yet designed** (Nick, 2026-07-27): show announcements · merch · **letting the list vote on releases / be part of the project.** Later, if the channel is working.

**Do not lean on the "98% SMS open rate" figure.** It is ubiquitous and essentially unsourced — the same shape as the fabricated demo-acceptance statistics caught in [[working/RESEARCH_VERIFICATION_MEMO]]. The *mechanism* is enough and isn't in dispute: 1:1 arrival, no feed competition, a reply path.

### Two tensions to resolve before scale
- **"No forced cadence" has a floor.** Right in spirit — a fought naturalness reads as fake. But *no schedule* and *no contact for four months* are different things; a cold list reads the eventual message as spam from someone they forgot opting into.
- **The scale ceiling is acknowledged but unplanned.** WORLD §7 says accept that 1:1 evolves "when the numbers force it." At 40 it's real; at 400 it's a part-time job; at 4,000 it's impossible and the promise breaks. Know roughly where it changes shape so it's a decision, not a collapse.

### Blocking
**10DLC registration** — days-to-weeks of carrier approval, nothing sends until it clears, and every line of copy above is unusable without a number. **This is the first action and it is mostly waiting.**

---

## Design decisions (locked defaults — override as needed)
1. **Intentions:** stored, treated as sacred. Pinned to the Wanderer's thread.
   Inform how Nick *sees* them; never used for marketing/segmentation.
2. **First glimpse:** the crossing reply carries a tiny taste; the first full
   glimpse arrives on Nick's next natural send. No instant automated drip.
3. **Early music:** delivered as a link (unlisted SoundCloud / hosted file) inside
   a glimpse.
4. **Number:** local 10DLC long code (reads personal, cheapest).
5. **Automation boundary:** only the two door auto-replies + STOP/HELP are
   automated. No drips, no scheduled sequences. "Pure feel" = human sends.

---

## The two surfaces

**The door (automated):** keyword → intention prompt → crossed. Two auto-replies.
**The room (human):** glimpses out (broadcast), replies in (1:1 inbox). No bot.

---

## User flow (the Crossing)

```
1. Door copy in existing content (see §0 — LOCKED): "text MIRROR to <number>"
   [prior draft "The mirror goes inward. Text MIRROR to..." REJECTED 2026-07-27 —
    it explains, which WORLD §8 forbids, and it reaches, which breaks Law 0]
2. User texts MIRROR
   → auto-reply #1 (threshold + intention prompt + compliance footer)
   → contact.state = PENDING_INTENTION
3. User replies (free text = their intention)
   → store intention; contact.state = CROSSED
   → auto-reply #2 (crossed + tiny glimpse)
4. Thereafter: glimpses arrive on Nick's cadence; user can reply anytime;
   Nick reads + responds by hand.
```

Copy below is placeholder — final passes through WOBAR_COPY (Sage/Magician,
empower-never-instruct, faceless).

- **Auto-reply #1 (threshold):**
  > You found the mirror. Before you cross — set your intention. Reply with what
  > you came here to find. What you bring is what the portal amplifies.
  > — Wobar · glimpses come when they come · Msg&data rates may apply · HELP for
  > help, STOP to leave
- **Auto-reply #2 (crossed):**
  > You're through. Nothing to do now — what's inside will find you. Walk your
  > own way.

---

## Data model (stack-agnostic)

**Wanderer (contact)**
| field | type | notes |
|---|---|---|
| id | uuid | |
| phone | string (E.164) | unique |
| state | enum | `PENDING_INTENTION` \| `CROSSED` \| `OPTED_OUT` |
| intention | text, nullable | the first reply after MIRROR |
| crossed_at | timestamp, nullable | |
| created_at | timestamp | |
| last_inbound_at | timestamp, nullable | drives inbox sorting |
| last_outbound_at | timestamp, nullable | |

**Message (log — needed for the inbox AND consent/compliance record)**
| field | type | notes |
|---|---|---|
| id | uuid | |
| wanderer_id | fk | |
| direction | enum | `in` \| `out` |
| body | text | |
| twilio_sid | string | dedupe / delivery status |
| created_at | timestamp | |

**Consent** is satisfiable from the Message log: the inbound `MIRROR` message +
timestamp is the express opt-in record. Keep it immutable.

---

## Inbound webhook — state machine

Twilio Messaging Service → POST to `<app>/webhooks/twilio/sms`. On each inbound:

```
body = trim(lower(inbound.Body)); from = inbound.From

if body in {stop, unsubscribe, cancel, end, quit}:
    mark OPTED_OUT; (Twilio Advanced Opt-Out can auto-ack) ; log ; return
if body in {help, info}:
    reply HELP text (program name, contact, STOP) ; log ; return

w = getOrCreateWanderer(from)

if body == "mirror" and w.state != CROSSED:
    w.state = PENDING_INTENTION ; log inbound (this is the consent record)
    send auto-reply #1 ; return

if w.state == PENDING_INTENTION:
    w.intention = inbound.Body ; w.state = CROSSED ; w.crossed_at = now
    log inbound ; send auto-reply #2 ; return

# w.state == CROSSED (or a stray message): normal two-way
log inbound ; surface in inbox ; NO automated reply   # Nick answers by hand
```

**Edge cases**
- `MIRROR` texted twice while PENDING → re-send prompt or ignore (idempotent).
- Already-CROSSED texts `MIRROR` → treated as a normal message (ritual not
  re-triggered).
- Whatever they reply after MIRROR *is* their intention, even "hi" — acceptable.
- Re-subscribe: an OPTED_OUT number texting `START`/`MIRROR` → reactivate (Twilio
  handles START; app flips state).

---

## Outbound — sending a glimpse (broadcast)

- Nick composes a glimpse in the app → app selects `state == CROSSED` (exclude
  OPTED_OUT) → sends via Twilio **Messaging Service** (not a bare number) → logs
  each `out` message.
- **Throughput:** 10DLC long code ≈ ~1 msg/sec (MPS scales with trust tier).
  Fine for hundreds; queue the send. At thousands, revisit number type / MPS.
- Personalization optional (name/token); keep it feeling human, not mail-merged.

## The room — two-way inbox (app UI)

- Conversation list sorted by `last_inbound_at`; each thread shows full history
  with the **intention pinned at top**.
- Reply box → outbound send + log. This is where the intimacy lives — no
  automation touches it.

---

## Twilio setup checklist

1. **A2P 10DLC registration FIRST** (days–weeks to clear carriers — the real
   lead-time gotcha). Register Brand (Nick's entity) + Campaign (use case:
   fan/community engagement).
2. Buy a **local long-code** number.
3. Create a **Messaging Service**; attach the number.
4. Point the Messaging Service **inbound webhook** at the app endpoint.
5. Enable **Advanced Opt-Out** (auto STOP/HELP/START handling) at the service.
6. Store Twilio auth in the app's secrets; verify webhook signatures
   (`X-Twilio-Signature`) so the endpoint can't be spoofed.

## Compliance (non-negotiable)
- Express consent = the inbound `MIRROR` (log + timestamp, immutable).
- Opt-in confirmation (#1) must contain: program name, message frequency,
  "Msg&data rates may apply," HELP + STOP. (Baked into the footer.)
- Honor STOP immediately; never send to OPTED_OUT.
- 10DLC registered to avoid carrier filtering/blocking.

---

## Cost (order-of-magnitude, a few hundred Wanderers)
- Number ~$1–2/mo · 10DLC brand ~$4 one-time + campaign ~$1.50–10/mo · SMS
  ~$0.008/msg. → **well under $50/mo.** Verify current Twilio rates at build time.

---

---

## Integration — Next.js (App Router) + Neon + Vercel

**Deps:** `twilio`, `@neondatabase/serverless`. **Env:** `DATABASE_URL`,
`TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_MESSAGING_SERVICE_SID`,
`APP_PUBLIC_URL` (e.g. `https://wobar.xyz`).

### Schema (Neon Postgres)
```sql
create type wanderer_state as enum ('pending_intention','crossed','opted_out');

create table wanderers (
  id uuid primary key default gen_random_uuid(),
  phone text unique not null,
  state wanderer_state not null default 'pending_intention',
  intention text,
  crossed_at timestamptz,
  created_at timestamptz not null default now(),
  last_inbound_at timestamptz,
  last_outbound_at timestamptz
);

create table messages (
  id uuid primary key default gen_random_uuid(),
  wanderer_id uuid not null references wanderers(id) on delete cascade,
  direction text not null check (direction in ('in','out')),
  body text not null,
  twilio_sid text,
  created_at timestamptz not null default now()
);
create index on messages (wanderer_id, created_at desc);
create index on wanderers (last_inbound_at desc);
```

### Inbound webhook — `app/api/webhooks/twilio/sms/route.ts`
```ts
import { NextRequest, NextResponse } from 'next/server';
import twilio from 'twilio';
import { neon } from '@neondatabase/serverless';

export const runtime = 'nodejs'; // twilio SDK needs node crypto

const sql = neon(process.env.DATABASE_URL!);
const STOP = new Set(['stop','unsubscribe','cancel','end','quit','stopall']);
const HELP = new Set(['help','info']);

const xml = (m?: string) =>
  new NextResponse(m ? `<Response><Message>${esc(m)}</Message></Response>`
                     : `<Response></Response>`,
                   { headers: { 'Content-Type': 'text/xml' } });
const esc = (s: string) =>
  s.replace(/[<>&'"]/g, c => ({'<':'&lt;','>':'&gt;','&':'&amp;',"'":'&apos;','"':'&quot;'}[c]!));

export async function POST(req: NextRequest) {
  const form = await req.formData();
  const p: Record<string,string> = {};
  form.forEach((v,k) => (p[k] = v.toString()));

  // verify it's really Twilio (URL must match what Twilio calls exactly)
  const ok = twilio.validateRequest(
    process.env.TWILIO_AUTH_TOKEN!,
    req.headers.get('x-twilio-signature') || '',
    `${process.env.APP_PUBLIC_URL}/api/webhooks/twilio/sms`,
    p,
  );
  if (!ok) return new NextResponse('bad signature', { status: 403 });

  const from = p.From;
  const raw = (p.Body ?? '').trim();
  const body = raw.toLowerCase();

  if (STOP.has(body)) { await sql`update wanderers set state='opted_out' where phone=${from}`; return xml(); }
  if (HELP.has(body)) return xml('Wobar — glimpses from the mirror. Reply STOP to leave. contact.wobar@gmail.com');

  const [w] = await sql`
    insert into wanderers (phone, last_inbound_at) values (${from}, now())
    on conflict (phone) do update set last_inbound_at = now()
    returning id, state` as { id: string; state: string }[];

  await sql`insert into messages (wanderer_id, direction, body, twilio_sid)
            values (${w.id}, 'in', ${raw}, ${p.MessageSid ?? null})`;

  if (body === 'mirror' && w.state !== 'crossed') {
    await sql`update wanderers set state='pending_intention' where id=${w.id}`;
    return xml(`You found the mirror. Before you cross — set your intention. Reply with what you came here to find. What you bring is what the portal amplifies.
— Wobar · glimpses come when they come · Msg&data rates may apply · HELP for help, STOP to leave`);
  }
  if (w.state === 'pending_intention') {
    await sql`update wanderers set intention=${raw}, state='crossed', crossed_at=now() where id=${w.id}`;
    return xml(`You're through. Nothing to do now — what's inside will find you. Walk your own way.`);
  }
  return xml(); // crossed → human handles the reply, no auto-response
}
```

### Broadcast a glimpse — server action
```ts
'use server';
import twilio from 'twilio';
import { neon } from '@neondatabase/serverless';

const sql = neon(process.env.DATABASE_URL!);
const client = twilio(process.env.TWILIO_ACCOUNT_SID!, process.env.TWILIO_AUTH_TOKEN!);

export async function sendGlimpse(body: string) {
  const rows = await sql`select id, phone from wanderers where state='crossed'` as {id:string;phone:string}[];
  // messages.create only ENQUEUES at Twilio (returns fast); Twilio then delivers
  // at the number's MPS (~1/s for 10DLC). So fire with bounded concurrency.
  const CONC = 10;
  for (let i = 0; i < rows.length; i += CONC) {
    await Promise.all(rows.slice(i, i+CONC).map(async w => {
      const m = await client.messages.create({
        to: w.phone, messagingServiceSid: process.env.TWILIO_MESSAGING_SERVICE_SID!, body,
      });
      await sql`insert into messages (wanderer_id, direction, body, twilio_sid)
                values (${w.id}, 'out', ${body}, ${m.sid})`;
      await sql`update wanderers set last_outbound_at=now() where id=${w.id}`;
    }));
  }
}
```

### Inbox — `app/ether/page.tsx` (sketch)
- Threads: `select * from wanderers where state!='opted_out' order by last_inbound_at desc nulls last`.
- Thread view: messages for a wanderer + **intention pinned at top**; a reply form
  → server action that `client.messages.create({ to, messagingServiceSid, body })`
  and logs the `out` row. No automation touches this path.

### Vercel gotchas
- **Runtime:** webhook must be `nodejs` (the `twilio` SDK). Neon's `neon()` HTTP
  driver runs fine on both.
- **Signature URL:** `validateRequest` checks the exact URL Twilio called. Point
  Twilio at the **production** domain and set `APP_PUBLIC_URL` to it. Preview
  deploys have different URLs → validation fails there (that's fine; test via
  Twilio CLI / ngrok locally).
- **Broadcast timeout:** a serial send over hundreds can exceed the function
  limit. `messages.create` returns fast (Twilio queues delivery), so bounded
  concurrency (above) handles hundreds in seconds. For thousands, move the
  broadcast to a queue (Upstash QStash / Vercel Cron) instead of a request.
- **Advanced Opt-Out:** if enabled on the Messaging Service, Twilio auto-answers
  STOP/HELP and may not forward them — the in-code STOP/HELP branch is a safety
  net; keep the DB opt-out state in sync either way.

---

## Open / TBD
- Final ritual copy through WOBAR_COPY.
- The first void poem (the taste in auto-reply #2, and the first full glimpse).
- Quiet-hours policy (pure-feel sends only; avoid overnight bulk).
- Inbox auth (it's your admin surface — gate it).
