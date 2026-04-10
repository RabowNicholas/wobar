# WOBAR WEBSITE — PRODUCT REQUIREMENTS DOCUMENT
Version 2.0 | March 2026 | Status: Ready for Development

---

## PLACEHOLDER CONVENTION

Claude Code should use these tags anywhere a manual asset, decision, or copy item is required before that element can be built or finalized. Do not invent values — leave the tag and move on.

| Tag | Use for |
|-----|---------|
| `[PLACEHOLDER_COPY: description]` | Copy that must be written and brand-tested before use |
| `[PLACEHOLDER_ASSET: filename, dimensions, format]` | Image, audio, or file that Nick must provide |
| `[PLACEHOLDER_URL: description]` | URL not yet confirmed (domain, streaming links, etc.) |
| `[PLACEHOLDER_CONFIG: description]` | Environment variable or config value not yet set |

Where a placeholder is used in a visual element, render a clearly labeled empty container styled to spec (correct dimensions, black background, purple border at 30% opacity, placeholder label in small monospace text centered). Do not use lorem ipsum. Do not guess.

---

## 1. OVERVIEW

### Purpose
A single-page scroll experience that functions as a portal — not a site about portals. The visitor enters, descends through the music, and returns changed. The 5-Act Portal Framework maps directly to the page architecture. Seekers recognize the structure. Everyone else just knows it felt different.

### Primary Audiences
- **Fans** arriving via QR code or bio link (primary — mobile first)
- **Bookers and talent buyers** arriving via direct URL or referral (secondary — served via /epk)

### Primary Action
Stream the music. Everything else is secondary.

### Secondary Actions
- Give phone number (SMS list via Twilio)
- Check tour dates
- Book a show (routed via /epk)

---

## 2. TECHNICAL STACK

| Layer | Choice | Rationale |
|-------|--------|-----------|
| Framework | Next.js 14 (App Router) | SE background, full control, Vercel deploy |
| Styling | Tailwind CSS | Utility-first, consistent design tokens |
| Animation | Framer Motion + GSAP ScrollTrigger | Scroll-driven journey, section entry |
| Canvas | Three.js | Particle field hero |
| Audio | Web Audio API | Custom player — EPK and featured track |
| CMS | Sanity (free tier) | Phone-updatable, webhook → Vercel redeploy |
| SMS Capture | Twilio | Phone list, opt-in confirmation text |
| Tour Dates | Bandsintown REST API | Auto-sync, custom-styled |
| Hosting | Vercel | Next.js native, webhook-triggered deploys |
| Domain | `[PLACEHOLDER_URL: custom domain — confirm before going live. Use Vercel preview URL during build]` | TBD |

---

## 3. ROUTES

| Route | Purpose | Audience |
|-------|---------|----------|
| / | Full scroll journey | Fans |
| /epk | Electronic press kit | Bookers, talent buyers, press |

No other routes. Navigation on the main page is ambient — not the organizing principle.

---

## 4. VISUAL IDENTITY

### Non-Negotiables
- **Background:** Pure black (#000000) always. Not dark grey. Not navy. Black.
- **Primary accent:** Deep purple (#6B2E87). Used sparingly as signal — not background fill.
- **Secondary accent:** Muted cyan (#4A7B9D). Cold contrast. Use for depth, secondary elements.
- **Grain overlay:** Film grain SVG texture, fixed position, full page, low opacity (~0.04), pointer-events none. Applied as a CSS pseudo-element on the `body` or root layout. Runs on every route including /epk.
- **Motion:** Everything moves slowly or not at all. No bounce. No aggressive slide-ins. Animations breathe. Framer Motion `whileInView`: fade + 20px upward translate, 0.6s ease, `once: true`.
- **Interactions:** Restrained. Hover on release card: album art brightness +10%. Hover on CTA: text shifts white → purple, no border change. Submit fires logo pulse once. Nothing else.

### Typography
Source: Art Direction Playbook 2025 (locked). All fonts available on Adobe Fonts.

**Primary — Futura PT**
- `Futura PT Heavy` — wordmark, section headers, act labels, CTAs, all caps display text
- `Futura PT Book` — body copy, bio text, Transmission text, captions
- Letter-spacing: +50 to +100 tracking on all caps usage
- Never thin weight. Never italic.

**Secondary — Space Mono**
- All monospace contexts: tour date rows, contact details, EPK lists, code-like labels
- Regular weight only

**Rules:**
- Maximum 2 font families per page (Futura PT + Space Mono — already at limit)
- ALL CAPS for brand name, section headers, act labels, CTAs
- Title case for body copy only
- No serifs. No decorative fonts. No Inter. No system fonts.

### Logo
Broken double-ring SVG. Counter-rotation animation — two rings, opposite directions, different durations (outer: 18s, inner: 12s), CSS keyframes, no JS required. Persistent ambient presence through scroll as a small corner element (bottom-left, 32px, opacity 0.4).

### Particle Field (Hero Background)
- Three.js canvas layer, full viewport, z-index below content
- Particle color: deep purple (#6B2E87) and near-black (#1A0A24) only — no bright colors
- Motion: slow drift, scroll-reactive (particles pull gently toward center as user scrolls down)
- Density: sparse — atmosphere, not spectacle
- Performance: `requestAnimationFrame` with delta time, particle count capped at 120 mobile / 200 desktop
- Pause when tab not visible (`visibilitychange` event)

### Scroll Color Temperature
GSAP ScrollTrigger scrubs a CSS custom property `--warmth-color` tied to scroll position. Interpolated across five acts. Visitor does not see this consciously — they feel it.

| Act | Section | Color value | Hex |
|-----|---------|-------------|-----|
| 1 — Rift | Hero | Deep purple warmth | `#6B2E87` |
| 2 — Descension | Featured Track | Cooling purple | `#2D1445` |
| 3 — Encounter | Transmission | Near black, coldest | `#0D0010` |
| 4a — Release | Tour Dates | Slight warmth returning | `#1A0A2E` |
| 4b — Release | List Capture | Purple returning | `#3D1A5C` |
| 5 — Integration | About + Footer | Full purple return | `#6B2E87` |

Implementation: use GSAP ScrollTrigger with `scrub: true` to interpolate `--warmth-color` between these hex values as scroll position moves through each section. Apply `--warmth-color` as a glow or subtle background tint on section wrapper — not as a visible background fill. Opacity of the tint layer: 0.06 maximum.

### Section Transitions
No hard cuts. No visible dividers. No `hr` tags. No section borders. Each section fades into the next. One continuous surface.

---

## 5. MAIN PAGE — SECTION SPECIFICATIONS

### SECTION 01 — HERO (Act 1: Rift)
**Emotional register:** I am safe here. Something is beginning.

**Layout:** Full viewport height. Centered content. Particle field behind.

**Elements:**
- Broken double-ring logo — counter-rotating, centered, fades in at 0s delay
- WOBAR wordmark — Futura PT Heavy, white, ALL CAPS, letter-spacing 0.2em, fades in at 2s
- Sage voice line — single sentence, Futura PT Book, white 60% opacity, fades in at 3s
  `[PLACEHOLDER_COPY: Hero Sage voice line — must pass Portal Test, Body Test, and Earned Language Test from WOBAR_COPY before use. Example register: "The portal goes inward. Everything you need is already there." Do not use this example — write new copy.]`
- Single text CTA — `ENTER ↓` — Futura PT Heavy, purple (#6B2E87), letter-spacing 0.25em, fades in at 4s, smooth-scrolls to Section 02
- Scroll indicator — subtle animated chevron, bottom center, disappears on first scroll event

**Mobile:** Same layout. Particle field reduced (60 particles max). Logo scales to 80px. Wordmark at 28px.

**No video. No image. Particle field and grain only.**

---

### SECTION 02 — FEATURED TRACK (Act 2: Descension begins)
**Emotional register:** I'm being pulled somewhere. There's something I need to hear.

**Layout:** Full-width album art on mobile (square, edge-to-edge). Desktop: album art left (50vw), track info right.

**Elements:**
- Album art — `[PLACEHOLDER_ASSET: featured-track-cover.jpg, minimum 1000×1000px, square, full quality]`
- Act label — small, uppercase, Space Mono, purple, above track name. e.g. `ACT III — ENCOUNTER`
- Track name — Futura PT Heavy, white, large
- Custom audio player — Web Audio API
  - Play/pause button (custom SVG, no native browser chrome)
  - Waveform visualization on canvas — frequency bar style, reacts live to `AnalyserNode` data, purple bars on black
  - Progress bar — scrubable, purple fill on black track
  - Duration display — Space Mono, small, white 60% opacity
  - iOS unlock: create `AudioContext` on first user gesture (touchstart or click), store context ref, resume on play
- Stream CTAs below player:
  - `STREAM ON SPOTIFY →`
  - `SOUNDCLOUD →`
  - Both open new tab. Futura PT Heavy, white, letter-spacing 0.15em. Hover → purple.

**CMS fields:** `title`, `act_label`, `cover_art_url`, `audio_url`, `spotify_url`, `soundcloud_url`

**Placeholders if CMS not yet populated:**
- Audio: `[PLACEHOLDER_ASSET: featured-track.mp3, externally hosted URL required — do not embed in repo]`
- Spotify URL: `[PLACEHOLDER_URL: Spotify track or artist URL]`
- SoundCloud URL: `[PLACEHOLDER_URL: SoundCloud track URL]`

---

### SECTION 03 — TRANSMISSION (Act 3: Encounter)
**Emotional register:** Something confrontational. No relief. Eyes open.

**Layout:** Full viewport height. Text centered. Nothing else on screen.

**Elements:**
- Single Sage voice statement — 1–2 sentences maximum
  `[PLACEHOLDER_COPY: Transmission text — must pass Portal Test and Body Test. Must name a truth, not describe Wobar. Must have one physical or somatic anchor. Must be screenshot-worthy as standalone text.]`
- Futura PT Book, white, `clamp(24px, 4vw, 40px)`
- No background treatment beyond black + grain
- No CTA. No decoration. This section does not ask anything of the visitor.

**CMS fields:** `transmission_text`

---

### SECTION 04 — TOUR DATES (Act 4: Release begins)
**Emotional register:** Movement. Action. Where to find this live.

**Layout:** Left-aligned list. Monospace typography.

**Elements:**
- Section label: `DATES` — Futura PT Heavy, small, uppercase, letter-spacing 0.3em, purple
- Each event row (Space Mono):
  ```
  03.28 — FLOW STATE — SALT LAKE CITY          GET TICKETS →
  ```
  White. Date · Venue · City left-aligned. Ticket CTA right-aligned. Hover: row background tint (#6B2E87 at 8% opacity).
- Each ticket CTA opens Bandsintown or direct URL in new tab.

**Data source:** Bandsintown REST API — `GET /artists/[PLACEHOLDER_CONFIG: confirm Bandsintown artist slug — likely "wobar"]/events`
Cache: Next.js `revalidate: 21600` (6 hours)

**Empty state:**
```
NEXT DATE INCOMING.
GET THE SIGNAL WHEN IT DROPS. →
```
Arrow anchors to Section 05.

---

### SECTION 05 — LIST CAPTURE (Act 4: Release — commitment)
**Emotional register:** Join something. Not subscribe to something.

**Layout:** Centered. Minimal. One input. One button.

**Elements:**
- Headline: single line, Futura PT Heavy, white, ALL CAPS
  `[PLACEHOLDER_COPY: Capture headline — must feel like an invitation, not a form. Must pass brand writing tests.]`
- Sub-line: Futura PT Book, white 50% opacity, small
  `[PLACEHOLDER_COPY: Capture sub-line — example register: "Drop your number. Shows, drops, transmissions. Nothing else." Do not use this example — write tested copy.]`
- Input: phone number, E.164 client-side validation, placeholder `+1 (___) ___ ____`, Space Mono
- Submit button: `GET THE SIGNAL` — Futura PT Heavy, white text, transparent background, 1px purple border. Hover: purple background fill, white text.
- Submit flow:
  1. Client-side E.164 validation
  2. POST to `/api/subscribe`
  3. API route calls Twilio — sends opt-in SMS: `"You're in. Wobar drops and shows will find you here. Reply STOP to opt out."`
  4. Success: logo pulses once (CSS keyframe), form replaced inline with `YOU'RE IN.` — Futura PT Heavy, white
  5. No redirect. No page reload.
- Error state: inline, below input, Space Mono, small, `#FF4444`. "Something went wrong. Try again."

**CMS fields:** `capture_headline`, `capture_subline`

**Backend:** Twilio Programmable SMS. `/api/subscribe` is a Next.js serverless function (App Router route handler). Phone numbers stored in Twilio only — never written to Sanity or any client-accessible layer.

---

### SECTION 06 — MUSIC CATALOG (Act 4: Release — depth)
**Emotional register:** More. Go deeper.

**Layout:** Responsive grid. 2 columns mobile. 3 columns desktop. Gap: 8px.

**Elements per card:**
- Album art — square, full bleed within card
  `[PLACEHOLDER_ASSET: per release — cover art minimum 800×800px. Until populated, render placeholder container with dimensions preserved.]`
- Act label — Space Mono, small, uppercase, purple, overlaid bottom-left of art (semi-transparent black backing, 60% opacity)
- Track name — below art, Futura PT Heavy, white, 14px
- Hover: art brightness +10%, act label brightens to white
- Click: opens smart link URL in new tab

**Sort:** Reverse chronological. Latest release first. Featured track from Section 02 appears here — no exclusion.

**CMS fields per release:** `title`, `act_label`, `cover_art_url`, `smart_link_url`, `release_date`

---

### SECTION 07 — ABOUT (Act 5: Integration)
**Emotional register:** What does this mean. I understand now. I'm back.

**Layout:** Two-column desktop (text left, image right). Single column mobile (image above text).

**Elements:**
- Atmospheric still — `[PLACEHOLDER_ASSET: about-image.jpg, 1200×800px minimum, treated: crushed blacks, purple-shifted midtones, reduced saturation — treatment applied before upload. Source: FREQUENCY or SENSELESS footage still.]`
- Bio — Futura PT Book, white, 100 words maximum, third person. Must pass Earned Language Test.
  `[PLACEHOLDER_COPY: About bio — 100 words, third person, pulled from WOBAR_COPY medium bio template and shortened. Must pass Earned Language Test.]`
- Booking contact — `BOOKING: contact.wobar@gmail.com` — Space Mono, small, purple, mailto link
- Press photos — `PRESS PHOTOS →` — Futura PT Heavy, small, white, opens in new tab
  `[PLACEHOLDER_URL: Press photos folder — Dropbox or Google Drive link]`

**CMS fields:** `bio_text`, `booking_email`, `press_photos_url`, `about_image_url`

---

### SECTION 08 — FOOTER
**Layout:** Single row desktop. Stacked mobile.

**Elements:**
- Social icons: Instagram, TikTok, SoundCloud, YouTube — SVG icons, 20px, white, hover → purple
  `[PLACEHOLDER_URL: confirm all four social profile URLs]`
- Booking email: `contact.wobar@gmail.com` — Space Mono, small, mailto
- Copyright: `© {new Date().getFullYear()} WOBAR` — Space Mono, small, white 30% opacity

**No newsletter signup in footer. SMS capture in Section 05 is the only capture mechanism.**

---

## 6. /EPK ROUTE — SPECIFICATIONS

### Purpose
Serve bookers, talent buyers, and press. Same visual world — black, grain, purple, typography. Different emotional register: scannable, credible, complete. No scroll journey. No Act structure.

### Layout
Single page. Vertical scroll. Fixed nav within /epk: `BIO · MUSIC · SHOWS · PRESS · CONTACT` — Futura PT Heavy, small, letter-spacing 0.2em, white, hover → purple.

Mobile: fixed nav collapses to hamburger or scrolls horizontally at full width (no hamburger menu — inline horizontal scroll on mobile, all items visible).

---

### EPK HERO
- WOBAR wordmark — Futura PT Heavy, same treatment as main site
- Tagline: `Psychedelic bass. Salt Lake City.` — Futura PT Book, white 70% opacity, one line only
- No particle field — static black + grain only
- Logo counter-rotation animation present

---

### BIO
Three lengths, all visible, labeled (Futura PT Heavy label, Futura PT Book copy):
- `SHORT (50 WORDS)`
- `MEDIUM (100 WORDS)`
- `LONG (250 WORDS)`

`[PLACEHOLDER_COPY: All three bio lengths — short, medium, long. Must pass Earned Language Test. Pull from WOBAR_COPY bio templates.]`

Copy icon next to each — copies bio text to clipboard. Futura PT Heavy, small, white, hover → purple. No download.

**CMS fields:** `bio_short`, `bio_medium`, `bio_long`

---

### MUSIC
Same Web Audio API component as main site — reuse component.
3 tracks maximum. Each: album art (small, square), track name (Futura PT Heavy), act label (Space Mono, purple), play/pause, waveform, progress, duration.
Below player: `STREAM ALL →` — Futura PT Heavy → Spotify artist page.

`[PLACEHOLDER_ASSET: up to 3 EPK tracks — title, act label, cover art, hosted audio URL each]`

**CMS fields:** `epk_tracks[]` — array of `{title, act_label, cover_art_url, audio_url}`

---

### NOTABLE SHOWS
Space Mono list:
```
FLOW STATE RESIDENCY — SALT LAKE CITY — ONGOING
FREQUENCY — LAKE EFFECT, SALT LAKE CITY — 2026
```
`[PLACEHOLDER_COPY: confirm full notable shows list]`

**CMS fields:** `notable_shows[]` — array of `{name, city, date_or_period}`

---

### PRESS
- Press photo grid — 2–3 photos, each click-to-download full-res. Label: `DOWNLOAD HI-RES` — Futura PT Heavy, small.
  `[PLACEHOLDER_ASSET: 2–3 press photos — atmospheric, treated on-brand. Thumbnail + full-res download URL each.]`
- Press quotes — CMS-managed, pull quote format, attributed. Render section only if quotes exist.

**CMS fields:** `press_photos[]` — array of `{thumbnail_url, download_url}`, `press_quotes[]` — array of `{quote, attribution}`

---

### CONTACT
```
BOOKING
contact.wobar@gmail.com

MANAGEMENT
[PLACEHOLDER_COPY: management contact or remove section if TBD]
```
Both as mailto links. Space Mono. Clean.

**CMS fields:** `booking_email`, `mgmt_email`

---

## 7. CMS SCHEMA — SANITY

### Document Types

**`siteConfig`** (singleton)
```
transmission_text        string
capture_headline         string
capture_subline          string
booking_email            string
mgmt_email               string
press_photos_url         string
```

**`featuredTrack`** (singleton)
```
title                    string
act_label                string
cover_art                image (Sanity asset)
audio_url                string
spotify_url              string
soundcloud_url           string
```

**`release`** (array)
```
title                    string
act_label                string
cover_art                image (Sanity asset)
smart_link_url           string
release_date             date
order                    number
```

**`epkConfig`** (singleton)
```
bio_short                text
bio_medium               text
bio_long                 text
epk_tracks[]             {title, act_label, cover_art (image), audio_url}
notable_shows[]          {name, city, date_or_period}
press_photos[]           {thumbnail (image), download_url}
press_quotes[]           {quote, attribution}
```

**`aboutSection`** (singleton)
```
bio_text                 text (100 words max)
about_image              image (Sanity asset)
press_photos_url         string
```

### Deploy Trigger
Sanity webhook → Vercel deploy hook on every publish. ~30 second update cycle from phone to live site.

---

## 8. DATA FLOW

```
STATIC (in code, never changes)
  Brand colors, typography tokens, animation configs,
  particle field parameters, grain overlay

SANITY CMS (updated from phone)
  Transmission text, bio, capture copy,
  featured track, release catalog, EPK content,
  contacts, press photos, about image

BANDSINTOWN API (auto-sync)
  Tour dates — fetched server-side
  Revalidated every 6 hours (Next.js ISR)
  Manual Sanity override available

TWILIO (write-only from site)
  Phone number capture
  Opt-in confirmation SMS
  List lives in Twilio — never exposed client-side

VERCEL (hosting + serverless)
  /api/subscribe — Twilio POST handler
  /api/tour — Bandsintown fetch + cache
  Webhook-triggered redeploy from Sanity
```

---

## 9. PERFORMANCE REQUIREMENTS

- **Mobile-first.** Every component designed at 390px before 1440px.
- **Lighthouse target:** 90+ mobile performance.
- **Particle field:** Capped 120 mobile / 200 desktop. `requestAnimationFrame` with delta time. Paused on `visibilitychange`.
- **Images:** Sanity image CDN, automatic WebP, responsive `srcset`. No unoptimized images.
- **Audio:** MP3, externally hosted. Loaded on play only. No preload.
- **Reduced motion:** `prefers-reduced-motion: reduce` — disable particle animation, disable scroll color shift, logo counter-rotation at 50% speed.
- **Font loading:** `font-display: swap`. Latin subset only.

---

## 10. COPY REQUIREMENTS

All copy — hero line, Transmission, capture headline, capture subline, bio — must pass three brand writing tests before handoff.

**TEST 1 — THE PORTAL TEST:** Does this create a portal or describe Wobar?
**TEST 2 — THE BODY TEST:** Is at least one claim grounded in the physical?
**TEST 3 — THE EARNED LANGUAGE TEST:** Is every transformation claim backed by demonstrated practice?

Anti-vocabulary strictly enforced. See WOBAR_COPY for full list. Key prohibitions: good vibes, love and light, sacred journey, healing frequencies, conscious music, spiritual awakening as marketing promise.

All copy is currently open. Use `[PLACEHOLDER_COPY]` tags throughout until tested copy is provided.

---

## 11. IMPLEMENTATION SPECS FOR CLAUDE CODE

### Project Structure
```
/app
  layout.tsx                  # Root layout: grain overlay, font loading, global CSS
  page.tsx                    # Main scroll journey — imports all section components
  /epk
    page.tsx                  # EPK page
  /api
    /subscribe
      route.ts                # Twilio SMS handler
    /tour
      route.ts                # Bandsintown fetch + cache

/components
  /sections
    Hero.tsx
    FeaturedTrack.tsx
    Transmission.tsx
    TourDates.tsx
    ListCapture.tsx
    MusicCatalog.tsx
    About.tsx
    Footer.tsx
  /epk
    EpkHero.tsx
    EpkBio.tsx
    EpkMusic.tsx
    EpkShows.tsx
    EpkPress.tsx
    EpkContact.tsx
    EpkNav.tsx
  /shared
    LogoMark.tsx              # SVG logo with counter-rotation CSS animation
    GrainOverlay.tsx          # Fixed grain texture layer
    AudioPlayer.tsx           # Reused across main site and EPK
    Waveform.tsx              # Web Audio API canvas visualizer
    ScrollColorTemp.tsx       # GSAP ScrollTrigger warmth interpolation
    ParticleField.tsx         # Three.js canvas — hero only
    PlaceholderBlock.tsx      # Renders [PLACEHOLDER_*] containers visually

/lib
  /sanity
    client.ts
    queries.ts
  /bandsintown
    fetcher.ts
  /audio
    context.ts                # AudioContext singleton + iOS unlock utility

/hooks
  useAudio.ts
  useScrollProgress.ts
  useReducedMotion.ts

/styles
  tokens.css                  # CSS custom properties: colors, spacing, type scale
  grain.svg                   # Film grain texture asset

/public
  /fonts                      # Futura PT + Space Mono files (if self-hosting)
  logo.svg                    # Broken double-ring mark
```

### Design Tokens (tokens.css)
```css
:root {
  /* Colors */
  --color-black:       #000000;
  --color-purple:      #6B2E87;
  --color-purple-dark: #2D1445;
  --color-purple-deep: #1A0A2E;
  --color-purple-mid:  #3D1A5C;
  --color-near-black:  #0D0010;
  --color-void:        #1A0A24;
  --color-cyan:        #4A7B9D;
  --color-white:       #FFFFFF;

  /* Scroll warmth — scrubbed by GSAP */
  --warmth-color:      #6B2E87;

  /* Typography */
  --font-display:      'Futura PT', sans-serif;
  --font-mono:         'Space Mono', monospace;
  --tracking-wide:     0.15em;
  --tracking-wider:    0.2em;
  --tracking-widest:   0.3em;

  /* Animation */
  --duration-slow:     0.6s;
  --ease-portal:       cubic-bezier(0.16, 1, 0.3, 1);
}
```

### Key Component Notes

**LogoMark.tsx**
- Two concentric SVG rings as separate `<path>` elements
- Counter-rotation via CSS: outer ring `animation: spin 18s linear infinite`, inner ring `animation: spin-reverse 12s linear infinite`
- `@keyframes spin { to { transform: rotate(360deg); } }`
- `@keyframes spin-reverse { to { transform: rotate(-360deg); } }`
- Persistent ambient version (bottom-left corner): 32px, opacity 0.4, `position: fixed`, `z-index: 10`

**ParticleField.tsx**
- Client component (`'use client'`)
- Initialize Three.js in `useEffect` after mount
- Cleanup: dispose geometry, material, renderer on unmount
- Scroll reactivity: listen to `window.scrollY`, lerp particle attraction toward center
- Mobile detection: `window.innerWidth < 768` → cap at 120 particles
- `visibilitychange` → pause/resume `requestAnimationFrame`

**AudioPlayer.tsx + Waveform.tsx**
- iOS AudioContext unlock: on first user gesture, call `audioContext.resume()` if state is `'suspended'`
- `AudioContext` created as singleton — one instance per page
- Waveform: `AnalyserNode` feeding a `<canvas>` element, `requestAnimationFrame` loop drawing frequency bars
- Bar color: `--color-purple` (#6B2E87), gap: 2px, height: proportional to frequency magnitude
- Do not load audio on page load — initialize `AudioBufferSourceNode` only on play

**ScrollColorTemp.tsx**
- Client component with `useEffect`
- Register GSAP ScrollTrigger plugin
- Create a ScrollTrigger for each section transition using the color values from Section 4
- Update `document.documentElement.style.setProperty('--warmth-color', interpolatedHex)` on scroll
- Apply a `::before` pseudo-element on section wrappers using `--warmth-color` as a radial gradient at 6% opacity

**GrainOverlay**
- Implemented as a CSS pseudo-element on `body::after` in `globals.css`
- `background-image: url('/styles/grain.svg')`
- `position: fixed; inset: 0; opacity: 0.04; pointer-events: none; z-index: 9999`

**ListCapture — /api/subscribe**
```ts
// Expected request body: { phone: string } (E.164 format)
// Validate E.164 server-side before Twilio call
// Twilio call: messages.create({ to: phone, from: process.env.TWILIO_FROM_NUMBER, body: '...' })
// Return: { success: true } or { error: string }
// Never log or store the phone number — pass directly to Twilio
```

**Bandsintown — /api/tour**
```ts
// GET https://rest.bandsintown.com/artists/{ARTIST_SLUG}/events?app_id={APP_ID}
// Next.js: export const revalidate = 21600
// Return sorted array of { date, venue, city, ticket_url }
// If fetch fails, return empty array — do not throw, render empty state
```

### Environment Variables
```
# Sanity
NEXT_PUBLIC_SANITY_PROJECT_ID=     [PLACEHOLDER_CONFIG: Sanity project ID]
NEXT_PUBLIC_SANITY_DATASET=        production

# Twilio
TWILIO_ACCOUNT_SID=                [PLACEHOLDER_CONFIG: Twilio account SID]
TWILIO_AUTH_TOKEN=                 [PLACEHOLDER_CONFIG: Twilio auth token]
TWILIO_FROM_NUMBER=                [PLACEHOLDER_CONFIG: Twilio phone number in E.164 format]

# Bandsintown
BANDSINTOWN_APP_ID=                [PLACEHOLDER_CONFIG: Bandsintown app ID]
BANDSINTOWN_ARTIST_SLUG=           [PLACEHOLDER_CONFIG: confirm artist slug — likely "wobar"]
```

### Framer Motion Variant (standard entry animation)
```ts
export const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, ease: [0.16, 1, 0.3, 1] }
  }
}
// Usage: <motion.div variants={fadeUp} initial="hidden" whileInView="visible" viewport={{ once: true }}>
```

### Logo Pulse (submit success)
```css
@keyframes logo-pulse {
  0%   { transform: scale(1);    opacity: 1; }
  50%  { transform: scale(1.08); opacity: 0.7; }
  100% { transform: scale(1);    opacity: 1; }
}
.logo-pulse { animation: logo-pulse 0.6s var(--ease-portal) once; }
```

---

## 12. OPEN ITEMS BEFORE BUILD STARTS

| Item | Owner | Status |
|------|-------|--------|
| Domain confirmed | Nick | Open |
| Hero Sage line written and tested | Nick + Claude | Open |
| Transmission text written and tested | Nick + Claude | Open |
| Capture copy (headline + subline) written and tested | Nick + Claude | Open |
| About bio written and tested | Nick + Claude | Open |
| Atmospheric still selected and treated | Nick | Open |
| Press photos folder created | Nick | Open |
| Twilio account + phone number created | Nick | Open |
| Sanity project created + project ID confirmed | Nick / Dev | Open |
| Bandsintown artist slug confirmed | Nick | Open |
| Audio files hosted — URLs for featured track + EPK tracks | Nick | Open |
| Social profile URLs confirmed (all four platforms) | Nick | Open |
| Management contact confirmed or section removed | Nick | Open |
| Futura PT + Space Mono licensed / self-hosting confirmed | Nick | Open |

---

## 13. OUT OF SCOPE (THIS VERSION)

- Merch integration
- Blog or journal section
- Comment or community features
- Multiple language support
- Accessibility beyond WCAG AA basics
- Analytics beyond Vercel built-in
