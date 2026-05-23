---
title: Tool Stack Research — Phase 1 Verification
date: 2026-05-06
scope: Verify factual claims from AI-generated music marketing doc before building tool stack recommendations
status: phase 1 complete
---

# Phase 1 — Verification Findings

## Summary
Most tool pricing claims held up directionally but several had material errors that change the budget math. The biggest single break: **Buffer Essentials is $6/mo per channel, NOT $12/mo for 2 channels** — so a 3-channel setup is $18/mo, not the $12 the doc implied. The MailerLite free tier dropped to 500 subs in Sept 2025, and Hypeddit's price ladder skipped a tier ($9.99/$19.99/$100, not "$10/$20"). Load-bearing stats split: the Buffer 11.4M TikTok post study is real and broadly accurate (with one nuance — they recommend 2-5/week, not 3-5), the Instagram Reels 70-75 day lifespan is sourced (Measure Studio), and the SubmitHub $50/45-credit math holds. But the "30-60% download gate conversion" claim is **unsupported** — no primary source surfaces, and what data exists suggests ~25% is "acceptable," 61% is exceptional. Specific claims: SoundCloud 100% royalties confirmed (Nov 2025, requires Artist Pro), Of The Trees wipe confirmed (Jan 2026), Bass Coast 2026 dates **wrong** (closes Jan 10, 2026 — not a 7-day October window for music), and INZO "Overthinker" is at ~100M streams (doc's 52M is stale by years).

## Priority 1 — Tool Pricing

### 1. MailerLite
- **Claim**: Free tier 500 subs + 12,000 emails/mo; paid $10/mo at 500 subs with unlimited emails.
- **Verdict**: Confirmed (with timing caveat)
- **Actual**: Free = 500 subs + 12,000 emails/mo (was 1,000 subs until Sept 23, 2025). Growing Business plan starts at $10/mo.
- **Source**: https://www.mailerlite.com/pricing ; https://emailoctopus.com/blog/mailerlite-pricing-update
- **Notes**: 500-sub cap is recent — anyone citing older docs may still say 1,000.

### 2. Hypeddit
- **Claim**: Basic $10/mo, Pro $20/mo.
- **Verdict**: Partial / mislabeled tiers
- **Actual**: Pro $9.99/mo, Premium $19.99/mo, Elite $100/mo. Free tier exists with branding.
- **Source**: https://hypeddit.com/pricing
- **Notes**: Doc's "Basic" is what Hypeddit calls "Pro." Pricing is correct, naming is off. Yearly billing = 16% off.

### 3. SubmitHub
- **Claim**: $1–3 per credit; $50 campaign = 45 credits.
- **Verdict**: Partial
- **Actual**: 10 credits = $10 ($1 each), 100 credits = $80 ($0.80 each). $50 buys roughly 50-60 credits at bulk pricing, not 45. "Premium credits cost ~$1-3 per submission" is a function of curators charging multiple credits, not credit price itself.
- **Source**: https://www.musicpulse.app/blog/is-submithub-still-worth-it-in-2026-an-honest-review ; https://www.chartlex.com/blog/streaming/submithub-review-2026
- **Notes**: The $1-3 range conflates credit cost with per-submission cost. A single submission can cost 1-3 credits depending on curator tier.

### 4. Groover
- **Claim**: €2 / ~$2.18 per submission.
- **Verdict**: Confirmed for standard curators
- **Actual**: 2 Grooviz (~€2) for most curators, 4+ Grooviz for top curators. Bulk packs from €46 with up to 24% off.
- **Source**: https://groover.co/en/lp/pricing/ ; https://www.chartlex.com/blog/streaming/groover-review-2026
- **Notes**: Doc omits that "top curators" cost 2x+. Real average spend per submission is higher than €2.

### 5. Viberate for Artists
- **Claim**: $39/year.
- **Verdict**: Wrong
- **Actual**: Viberate for Artists = $2.99/mo (~$35.88/year). Higher tiers exist: Premium $19.90/mo, Unlimited $39.90/mo (both billed annually).
- **Source**: https://www.viberate.com/pricing/
- **Notes**: Doc may have confused "$39/year" with the Unlimited tier's monthly price. Actual entry price is much cheaper than claimed.

### 6. Feature.fm
- **Claim**: $8–19/mo.
- **Verdict**: Partial / outdated
- **Actual**: Artist Plan $9.99/mo annual or $14.99/mo monthly; Pro Plan $24.99/mo annual or $34.99/mo monthly. Free tier exists.
- **Source**: https://feature.fm/pricing/artist
- **Notes**: Doc's range understates the Pro tier ($24.99-34.99). Entry-level claim ($8-19) is close but slightly low.

### 7. Bandzoogle
- **Claim**: $8.29/mo basic, up to $17/mo with music features.
- **Verdict**: Partial / outdated
- **Actual**: EPK $6.95/mo, Merch Table Lite $6.95/mo, Lite $11/mo ($111/yr), Standard and Pro tiers higher, Merch Table Pro $24.95/mo. Two months free if billed annually.
- **Source**: https://bandzoogle.com/pricing ; https://bandzoogle.com/help/articles/363-bandzoogle-pricing
- **Notes**: $8.29 figure doesn't match current tier. Closest is $6.95 (EPK) or $11 (Lite, the "starting band" plan).

### 8. Buffer Essentials
- **Claim**: $12/mo for 2 channels.
- **Verdict**: Wrong
- **Actual**: Essentials is $6/mo per channel (monthly billing), $5/mo per channel (annual). Buffer's pricing is PER-CHANNEL, not bundled.
- **Source**: https://buffer.com/pricing ; https://checkthat.ai/brands/buffer/pricing
- **Notes**: This breaks the budget math. 3 channels (IG + TikTok + Twitter) = $18/mo, not $12. 5 channels = $30/mo. For Wobar across IG, TikTok, SoundCloud (no native Buffer support — likely Twitter/X instead), YouTube — could be $24-30/mo.

## Priority 2 — Load-bearing Stats

### 1. Download gate conversion 30-60%
- **Verdict**: Unsupported
- **Actual**: No primary source surfaces this range. Industry references suggest ~25% is "acceptable," 61% is cited as exceptional on Hypeddit. The 30-60% range appears to be an AI hallucination or aggregation of best-case anecdotes.
- **Source**: https://promusicianhub.com/give-your-music/ (mentions 25% acceptable); Hypeddit blog mentions 61% as outlier
- **Notes**: This is a major weak link in the doc — the entire "Hypeddit ROI" argument rests on a number with no source.

### 2. SubmitHub $50/45 credits → 7-10 adds, 3-5K streams
- **Verdict**: Confirmed (corroborated by multiple case studies)
- **Actual**: One published case study ("Midnight Parade") hit 8 adds, 3,900 streams, 540 saves in 7 days on a $50 spend. Other reports cite 4 placements averaging 800-1,500 streams from a $50 spend (25 submissions at 15% acceptance).
- **Source**: https://www.musicpulse.app/blog/is-submithub-still-worth-it-in-2026-an-honest-review ; https://www.hypebot.com/hypebot/2022/03/what-spending-100-on-playlist-submissions-will-get-you-case-study.html
- **Notes**: 7-10 adds is the upper end. 4-8 adds is more realistic median.

### 3. SubmitHub acceptance rate 5-20%
- **Verdict**: Confirmed
- **Actual**: Platform-wide premium ~5-8% to 18% depending on source; standard ~5%; across genres 15-20% accepted; pop/hip-hop competitive <10%.
- **Source**: https://www.chartlex.com/blog/streaming/submithub-review-2026 ; https://www.musicpulse.app/blog/is-submithub-still-worth-it-in-2026-an-honest-review
- **Notes**: Wide range reflects genre/quality variance. Bass music likely falls in the higher end given less saturation.

### 4. Groover acceptance rate 10-20%
- **Verdict**: Confirmed
- **Actual**: Groover's own 2025 data: ~15-20% average acceptance. User reports: 10-20% typical. 25-35% indicates strong genre fit.
- **Source**: https://www.chartlex.com/blog/streaming/groover-review-2026 ; https://www.musicpulse.app/blog/groover-review-2026-is-the-guaranteed-feedback-model-worth-the-price
- **Notes**: Claim is accurate.

### 5. Pre-save w/ email opt-in converts 15-25%
- **Verdict**: Confirmed
- **Actual**: Pre-save conversion from email = 15-25%, vs 2-5% from social. Linkfire data: Spotify pre-save rate >30% from landing pages.
- **Source**: https://orphiq.com/resources/spotify-pre-save-setup ; https://www.linkfire.com/blog/decoding-pre-save-rates
- **Notes**: The 15-25% number refers specifically to email-channel conversion, which matches the claim.

### 6. Spotify save rate 8-10% is "the algorithmic threshold"
- **Verdict**: Partial / not officially confirmed
- **Actual**: There is no official Spotify-published threshold. Industry analysis cites: 4.5% as the floor for sustained algorithmic carry (May 2026 estimate), 5-8% as "healthy," 8%+ as a quality signal, and 20%+ as a Discover Weekly trigger.
- **Source**: https://www.chartlex.com/blog/streaming/spotify-save-rate-benchmarks-by-genre-2026 ; https://www.chartlex.com/blog/streaming/spotify-algorithmic-playlists-2026
- **Notes**: 8-10% is widely repeated but not a Spotify-stated number. It's a community benchmark, not a published threshold.

### 7. Buffer 2025 TikTok study: 11.4M posts, 150K accounts, 3-5/week optimal
- **Verdict**: Partial — numbers are slightly off
- **Actual**: Buffer analyzed "over 11 million TikTok uploads from over 150,000 accounts." Recommendation is **2-5 posts/week**, not 3-5. 2-5/week generates +17% views/post vs once weekly; 6-10/week = +29%; 11+/week brings biggest overall lift but with diminishing per-post returns.
- **Source**: https://buffer.com/resources/how-often-should-you-post-on-tiktok/ ; https://www.socialmediatoday.com/news/tiktok-post-frequency-improves-per-post-reach-report-buffer/802443/
- **Notes**: Doc's "11.4M" is just rounded language ("over 11 million"). 150K is correct. Optimal range is 2-5, not 3-5 — minor but real difference for biweekly release planning.

### 8. IG Reels 70-75 days vs TikTok ~35-day window
- **Verdict**: Confirmed
- **Actual**: TikTok ~35 days to reach 95% of total views, with ~72% on day one. Instagram Reels ~70-75 days to reach 95% of lifetime views.
- **Source**: https://www.measure.studio/post/tiktok-vs-instagram ; https://napolify.com/blogs/news/content-longevity-tiktok-instagram
- **Notes**: Source is Measure Studio analysis. Holds up.

### 9. SoundCloud #bassline tag tracks up 37% in last 2 years
- **Verdict**: Confirmed
- **Actual**: SoundCloud's Music Intelligence Report cites #bassline uploads up 37% over the last two years.
- **Source**: https://hmc.chartmetric.com/soundcloud-trends-2025-josh-baker-electronic/ ; https://www.musicweek.com/digital/read/soundcloud-s-music-intelligence-report-reveals-consumption-trends/091668
- **Notes**: Strong, sourced. Directly relevant for Wobar.

## Priority 3 — Specific Claims

### 1. SoundCloud eliminated distribution revenue share late 2025
- **Verdict**: Confirmed (with conditions)
- **Actual**: SoundCloud's All-in-One Artist Subscription launched October 30, 2025. The 20% distribution revenue share was eliminated at end of November 2025. Artists on **Artist Pro ($99/year, ~$8.25/mo)** keep 100% of royalties from 60+ DSPs including Spotify, Apple Music, TikTok, YouTube Music.
- **Source**: https://www.musicweek.com/digital/read/soundcloud-now-enables-artists-to-keep-100-of-distribution-royalties/092964 ; https://edm.com/industry/soundcloud-executives-discuss-all-in-one-artist-subscription/
- **Notes**: Wobar already has SoundCloud Pro — needs to confirm whether his existing tier is the "Artist Pro" tier that includes the 100% royalty change. There's a distinction between SoundCloud's various artist subscription tiers.

### 2. Of The Trees wiped social Jan 2026 / Moonglade Park rollout
- **Verdict**: Confirmed (with detail correction)
- **Actual**: Of The Trees scrubbed his Instagram on Jan 9, 2026, leaving only a link to an interactive site for "Moonglade Park." A new single "Dolori" dropped Jan 16, 2026. Fans speculate this is the rollout for his long-awaited debut album.
- **Source**: https://edmidentity.com/2026/01/09/of-the-trees-wipes-instagram/ ; https://edm.com/news/of-the-trees-debut-album-rumors-cryptic-site-moonglade-park/
- **Notes**: Doc says "album rollout for Moonglade Park" — confirmed publicly as speculation, not yet announced as the album title. Still a valid reference for cryptic-rollout strategy.

### 3. Bass Coast applications open 7 days in early October (2025 = Oct 1-7)
- **Verdict**: Wrong for 2026 cycle
- **Actual**: The Oct 1-7 7-day window was for the **2024 festival cycle** (music applications). For the **2026 cycle**, applications **closed January 10, 2026** with notifications by Feb 10, 2026. Interactive Art submissions ran Oct 15, 2025 to Jan 10, 2026 (a 3-month window). The Oct 1-7, 2025 window applied to murals, not music.
- **Source**: https://basscoast.ca/pages/applications-2026 ; https://basscoast.ca/blogs/news/application-deadlines
- **Notes**: The "7-day October window" pattern was a 2024 quirk, not a recurring rule. Bass Coast 2026 dates: Jul 10-13, 2026. **2027 music application window has not been announced** — Wobar should follow Bass Coast socials / newsletter rather than count on an October opening.

### 4. INZO "Overthinker" 52M+ Spotify, Gold Record
- **Verdict**: Wrong on streams, confirmed on Gold
- **Actual**: "Overthinker" surpassed **50M Spotify streams** somewhere around 2022-2023; as of 2025 it has reportedly surpassed **100M streams**. RIAA Gold certification received July 16, 2025 (the doc's "Gold" claim is correct, though source describes it as for the album not single — needs clarification).
- **Source**: Facebook post celebrating 50M (older); recent stats showing 100M; RIAA Gold July 2025
- **Notes**: "52M" is years stale. Current number ~100M materially strengthens the case study Wobar might draw from.

## Discrepancies that affect the budget recommendation

- **Buffer is per-channel, not flat $12.** For Wobar's likely 3-4 channel setup, real cost is $18-30/mo, not $12. This eats meaningfully into the $50-200/mo budget. Consider Buffer Free (3 channels, limited scheduling) vs alternatives like Later, Metricool, or Publer that bundle channels.
- **Hypeddit's actual ladder is $9.99 / $19.99 / $100**, not $10/$20. The jump from Premium to Elite is steep — there is no $40-60 middle tier the doc implied.
- **Viberate for Artists is $2.99/mo, not $39/year.** This is a near-free add and should be reclassified as Tier 1 (essential) rather than Tier 2 (consider).
- **Bandzoogle entry is $11/mo for Lite, not $8.29.** Plus EPK-only is $6.95 if Wobar just wants a press kit. Pricing structure is more granular than doc claims.
- **MailerLite free tier dropped to 500 subs (Sept 2025).** Wobar will hit the cap faster than older guides suggest — paid tier ($10/mo) becomes necessary sooner.
- **Download gate conversion claim (30-60%) is unsupported.** Any tool prioritization that leans on "Hypeddit will convert at 40%" should be revised. Plan for 15-25% conversion as a more realistic baseline.
- **SubmitHub $50 = 50-60 credits, not 45.** Math is slightly more favorable than doc states.
- **Bass Coast application window claim is wrong** — the 7-day October pattern doesn't apply to 2026 and may not return. Don't bake "apply in October" into Wobar's timeline without confirming.
- **Buffer study optimum is 2-5/week, not 3-5/week.** Biweekly release cadence (16 tracks over 6 months = ~1 release every 11 days) suggests Wobar's post-frequency floor should be 2-3/week minimum to cluster around releases.
- **SoundCloud's 100% royalty change is real but tier-gated.** Wobar needs to verify he's on the right SoundCloud Pro tier ("Artist Pro" at ~$8.25/mo) to actually benefit.
