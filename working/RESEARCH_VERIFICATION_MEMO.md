---
title: Research — Adversarial Verification Memo
version: 1.0
created: 2026-07-26
status: live — SUPERSEDES the confident conclusions in RESEARCH_IG_COMPS, RESEARCH_SOUNDCLOUD_COMPS and RESEARCH_IG_CONVERSION
scope: 13-agent adversarial verification of every load-bearing claim from the 2026-07-26 research session. Researchers were instructed to REFUTE. Two adversarial critics audited all findings and caught fabricated data in two sub-reports.
dependencies: [[working/RESEARCH_IG_COMPS]], [[working/RESEARCH_SOUNDCLOUD_COMPS]], [[working/RESEARCH_IG_CONVERSION]], [[working/RESEARCH_LABEL_MAP]], [[working/WOBAR_PLACEMENT_PLAN]]
---

> **READ THIS BEFORE ACTING ON ANY OTHER RESEARCH FILE FROM 2026-07-26.**
> 9 of 10 claims returned UNSUPPORTED. Two sub-reports contained fabricated item-level data.
> Run: wf_98fcbeed-183 · 13 agents · 962K tokens · 426 tool calls.

# VERIFICATION MEMO — Growth Strategy Claims C1–C10
**Post-adversarial-audit final positions. Two source reports were found to contain fabricated item-level data; verdicts adjusted accordingly.**

---

## 1. VERDICT TABLE

| ID | Claim (one line) | FINAL VERDICT | CONFIDENCE |
|---|---|---|---|
| C1 | Spotify monthly listeners scale with number/tier of label releases (dose-response) | **UNSUPPORTED** | Medium |
| C2 | Label releases *cause* listener growth (vs. labels signing artists already growing) | **UNSUPPORTED** | Medium |
| C3 | Long-form (mixes/sets) outperforms individual tracks on SoundCloud, age-controlled | **UNSUPPORTED** (was REFUTED — downgraded; underlying dataset contaminated) | **Low — do not use until re-run** |
| C4 | A named, numbered, recurring mix series is a viable growth mechanic | **UNSUPPORTED** | Low-Medium |
| C5 | Direct DJ promo / dubplate sends is a working discovery lever with meaningful response rates | **UNSUPPORTED** | Medium-High |
| C6 | Demo submission to open-door labels has non-trivial acceptance for unknowns | **UNSUPPORTED** | Medium |
| C7 | SoundCloud is the primary discovery *and* A&R surface, and typically larger than Instagram | **PARTIAL** | Medium |
| C8 | Instagram followers do **not** predict Spotify monthly listeners (decoupled) | **UNSUPPORTED** (was REFUTED — downgraded) | Low |
| C9 | Uncleared flips can't reach DSPs; SoundCloud is viable home with manageable takedown risk | **PARTIAL** — Part 1 CONFIRMED, Part 2 reframed, Part 3 UNSUPPORTED | Part 1: High. Part 3: Low |
| C10 | Seven named labels are currently open to unsolicited demos with stated requirements | **PARTIAL** — openness confirmed 7/7, requirements wrong on 2 | Medium (perishable) |

**Note on "UNSUPPORTED":** it means *no credible published evidence exists either way*. It does not mean "false." Nine of ten claims land here, which is itself the headline finding: almost nothing in this domain has been measured by anyone.

---

## 2. WHAT SURVIVED

Six findings withstood adversarial verification. These are safe to build on.

**S1 — Uncleared flips cannot be distributed to Spotify/Apple. Settled.**
Best source: [Spotify for Artists, "Know Your Copyrights"](https://artists.spotify.com/blog/know-your-copyrights) — distribution of a remix requires permission from *both* the master owner and the composition owner. Corroborated independently by [DistroKid](https://support.distrokid.com/hc/en-us/articles/360013648633-Uploading-DJ-Mixes-or-Remixes-to-DistroKid) and FUGA. The compulsory mechanical licence covers *covers only* and explicitly excludes remixes — there is no statutory workaround. The May 2026 Spotify/UMG remix agreement is a paid Premium AI feature, opt-in per artist, not a distribution path (URL independently verified by the auditor). **Consequence: a flip programme contributes exactly zero to Spotify monthly listeners.**

**S2 — Copyright strikes on SoundCloud are account-level and terminal. Separate the accounts.**
Best source: [SoundCloud, "How do copyright strikes work"](https://help.soundcloud.com/hc/en-us/articles/4402644695451-How-do-copyright-strikes-work) — strike 1 no effect, strike 2 downloads suspended, >2 active strikes = permanent account termination; strikes expire 12 months from issue. Separately confirmed: content-ID blocks carry *no* strike. This is a mechanism, not a rate estimate, so it survives the total absence of base-rate data. Originals and 55 followers currently sit on the same handle as uncleared major-label flips. That is an uninsured, uncapped, unrecoverable exposure. **This is the highest value-per-effort action in the entire body of work.**

**S3 — Unofficial remixes are permanently non-monetisable on SoundCloud.**
Best source: [SoundCloud, "Start Monetizing with SoundCloud for Artists"](https://help.soundcloud.com/hc/en-us/articles/4406233941787-Start-Monetizing-with-SoundCloud-for-Artists) — "Unofficial covers and remixes, mashups, DJ sets… are not monetizable." Widely-circulated 2016–17 coverage claiming otherwise is obsolete; the Dubset/MixBANK clearance pipe that underpinned it was absorbed by Pex in 2020 and no longer serves producers. Any revenue assumption attached to a flip cadence is dead.

**S4 — Two widely-circulating statistical clusters are fabricated. Kill them on sight.**
(a) The DropTrack cluster — "87% of labels accept demos," "0.2% major acceptance," "1 in 50 at indies," "Warner reports 34% of new signings come from direct online submissions." Fetched and audited: zero citations, zero named sources, AI-templated, sells its own submission product. The Warner figure does not exist in any Warner filing, release, or trade publication.
(b) The onestowatch cluster — "r=0.82, Billboard Pro 2025 validation study" and an "MBW independent audit of 400 indie artists." Neither study exists. Both cited on a machine-generated page with no outbound links.
These dominate search results on exactly these questions. Anyone researching this will hit them first and mistake them for data.

**S5 — Label demo intake in this scene runs through email inboxes and third-party portals, and labels request *private* links.**
Best source: [jadudala.com/pages/contact](https://jadudala.com/pages/contact) — "Please send private links to jadudala@gmail.com." The load-bearing distinction: a private SoundCloud link is unlisted and invisible to SoundCloud's discovery system, and the label treats it as interchangeable with Dropbox. **SoundCloud functions as file hosting in the A&R workflow, not as a discovery surface.** This is the single sharpest piece of reasoning in the whole body of research and it survived audit intact.

**S6 — Seven demo doors were open as of 2026-07-26/27, verified by live browser load.**
Jadu Dala, Wubaholics, Local Void, Gravitas, SubCarbon, Deep Dark & Dangerous, Trippy Bee. All seven loaded; none closed, seasonal, or gated. Best source: the live portals themselves. Corrections that must travel with this finding:
- Gravitas's only stated content rule is *"Please only send us unreleased music."* "Finished + mastered" does not appear on the label's current demo page. Gravitas also has a **second, undisclosed LabelRadar door** that accepts Dubstep.
- Jadu Dala's self-published door is **email**, not the LabelRadar portal.
- Local Void's Google Form makes **TikTok and X account fields required**.
- SubCarbon publishes an explicit channel restriction: **submissions@subcarbon.be, never SoundCloud DMs**.
- The three LabelRadar doors are **credit-metered ($1/refill) and judge a 20-second clip you select**, not a full track. That clip choice is a real creative decision.
- **This finding has a shelf life.** A sibling report found Wormhole's portal *closed*. Re-check before acting.

---

## 3. WHAT DIDN'T

**C3 — long-form vs. tracks on SoundCloud. Verdict inflated; data partly fabricated.**
The headline "in 13 of 13 artists the top item is a short track, never a mix" is **empirically false** — the pivotal artist's top three items are all mixes, and his #1 is a 60-minute mix at ~49,200 plays. Four items cited in the paragraph designed to neutralise that counter-example **do not exist in his catalogue**. At least four rows of the ceiling table are wrong by factors of 4–19x, and one contradicts the same report's own table three bullets later. Worse, the 13/13 statistic is *statistically vacuous even if true*: long-form is ~8% of items, so under a null of no format effect P(all 13 tops are short) ≈ 0.33 — exactly what chance produces.
**Honest position:** the report's own declared load-bearing test — artist-fixed-effects regression — returned coefficient −0.102, t = −1.56, 95% CI spanning 0.59x to 1.06x. **That interval includes parity.** There is no evidence long-form outperforms; the point estimate is negative; nothing is proven either way. The matched-pair result (74/200 wins) is directionally consistent but pseudo-replicated from only 46 long-form items. The *mechanism* arguments are independent of the bad data and stand: SoundCloud counts one play per listen regardless of duration, DiscoRank has no duration term, and mixes are barred from distribution and Mastering.
**Additionally:** on verified data, the artist the original observation came from *supports* the claim outright. The curated-unreleased-ID-mixtape hypothesis buried in that report's counter-evidence may be the real finding. **Re-run required before any of C3 is used.**

**C4 — self-run mix series. Verdict survives; a key evidence bullet is fabricated.**
"0 of 4 comps grew via a self-run mix series" is wrong on 3 of 4 artists: one has 4 long-form uploads not 1; another has 2 mixes not 0, one of which is his **#2 item overall**, beating 43 of his 45 uploads; a third has 1 mix not 0. A named top track was understated ~19x and does not exist in the catalogue. Two reports pulled the same public API and produced mutually incompatible counts for the same artists.
**What actually survives, and it is genuinely good:** consecutive episodes of a single label-run series on one fixed host audience ranged from 1,403 to 65,550 plays — a 47x spread determined entirely by *who the guest was*. **A series is a mirror of the audience you already have, not a machine for making one.** Also note an outcome substitution running through the whole report: the claim is about *audience growth*, and every measurement taken was *plays*. Follower delta was never measured by anyone.

**C8 — Instagram/Spotify decoupling. Refutation collapses under its own counter-evidence.**
The report refuted the claim on a self-computed n=9 convenience sample selected by the claimant, then dismantled its own verdict in the counter-evidence section and left the verdict standing. Partial correlation controlling for SoundCloud followers drops r from 0.938 to 0.591, **not significant**; IG and SC followers correlate at r=0.974. In the researcher's own words: *"Instagram adds no independent predictive signal beyond any other artist-size proxy."* Within the relevant narrow band, monthly listeners span 18x on a 2.3x spread in Instagram followers.
The "artist is on-trend" finding is circular — the test point was added to the sample, the model refit, then declared on-trend. Prediction band is ÷6.5 to ×6.5, meaning **anything from 8 to 325 monthly listeners would have been "on trend."** It could not have failed. R² moved 0.68→0.84 from adding one observation; the estimate is unstable to a single point.
The one peer-reviewed source measures **Facebook and Twitter, not Instagram**, with **PRS publishing royalties, not monthly listeners**, on a **UK publisher roster, 2016–2018**. Its elasticity of 0.367 means doubling followers yields +29% royalties — arguably evidence *for* substantial decoupling. The paper explicitly flags reverse causality.
**Honest position: untested.** Across the full size range, both metrics track artist scale — which is a different and much weaker proposition than the claim. Within a narrow band, the observed data is *consistent with* decoupling. **Do not accept the sentence "there is no streaming problem, there is a follower problem" — that is an interventional claim derived from a cross-sectional correlation the same report showed was a scale artifact.**

**C9 Part 3 — "manageable takedown risk." Direct internal contradiction.**
Key evidence says "at one flip per month that is a real but low-probability path." Counter-evidence says "nobody has published the base rate… no study, trade report, or first-party disclosure measures it." Both cannot be true. You cannot derive a probability from a strike ladder with no report rate and no denominator. **Say the mechanics (confirmed); drop the probability (unmeasured).** Related: the report correctly diagnosed survivorship bias in its own API enumeration — only surviving tracks are returned, numerator with no denominator — and then, one section later, recommended selecting flip targets by "the profile the comps demonstrate survives." That is selecting on survivors immediately after saying you can't.
Also overstated: "three flips returned 251/252/11 plays vs. originals 197/130/102, therefore flips aren't working" was called the strongest finding in the assessment. It is n=3 vs. n=3, uncontrolled for age, timing, and promo effort — and the report's own dates invert its reading, since the 11-play flip is the *oldest* of the three. At 55 followers no channel has the statistical power to detect a 4x multiplier.

**C1 — asymmetric statistical standards.**
The corrected comp-set inversions are real and genuinely fatal to dose-response: the artist with the most labels (6) sits *below* one with three, and the artist holding the highest-tier stack sits at less than half another's off a single relationship. Keep those. But three correlations were computed from the same n=9 and held to three different evidentiary standards, all resolving in the researcher's preferred direction — label count dismissed at rho=0.551 (p≈0.12), label *tier* waved away at rho=0.730 (p≈0.026, nominally significant), Instagram treated as decisive at rho=0.833. Correlation-difference tests at n=9 have no power. "Instagram out-predicts label count" is not supported by these numbers.
Two specific items must be struck: the "EDM is only 27.5% major-label" argument is a non-sequitur (every label in the claim is an indie, and the same source shows indies *dominate* EDM); and "cat# JADU278 means 278+ releases" is an unsupported inference — catalogue numbers start at arbitrary offsets and skip. The "observed dose ≈ 93 listeners" line is n=1 with no counterfactual and is the report's most quotable sentence. Do not quote it.

**C2 — the only original data in the report is false.**
Its central disconfirming test — "artist X (no known label) beats artist Y (six labels)" — rests on label attributions that a sibling researcher had *already falsified with Tier 1 sources*. Both named artists are verifiably Wakaan-affiliated (confirmed on Wakaan's own storefront by the auditor). The claim "5 of the top 11 SoundCloud accounts are unaffiliated, including #1" is wrong on at least 2 of 5, and silently omits the set's #2 account. The source `https://open.spotify.com/` is tagged "Tier 1 — direct platform observation" while the same entry admits the data was "as supplied in the brief" — that is inherited (and wrong) data laundered as first-party observation.
Also struck: the aggregate time-series argument ("signings rose 2014→2021 while first-time top-10 artists fell 2001→2022") is ecological correlation offered as causal evidence, in a report whose entire thesis is that ecological correlation cannot establish causation. Different windows, confounded by streaming-era chart mechanics. And an unsourced quantitative claim — "indie interest at ~10,000 monthly listeners, major interest near 50,000" — has no entry in the source list at all.
**What survives from C2, and it is the whole legitimate value:** no difference-in-differences, synthetic control, matched-cohort, or event study on label signing exists anywhere in the literature. The closest peer-reviewed paper explicitly declines to claim causation, flagging that majors "may be disproportionately likely to sign higher quality artists."

**C5 — the poster-child refutation is an argument from absence.**
"The claim's own poster child refutes it" over-claims. A short Q&A that does not mention promo sends is not a denial — he wasn't asked. Downgrade to "does not support." The report itself concedes DJ support genuinely preceded and plausibly caused the label deal.
The report's #1 actionable recommendation is a non-sequitur: "6 of 15 comps carry these label affiliations, therefore the on-ramp is the LabelRadar portal." **Affiliation does not tell you intake channel.** Nothing establishes those artists entered via a portal rather than a DM, a friend, or a scene relationship — which is exactly the relationship-first mechanism the same report documents everywhere else.
**What survives, and it's the best single argument across all ten claims:** [Inflyte's own FAQ](https://inflyteapp.com/faq) — *"Inflyte does not provide mailing lists, you are required to import your own."* The industry-standard promo rail is structurally closed to anyone without pre-existing DJ relationships. That is a mechanism, not a correlation, and it is circular in exactly the way the claim needs it not to be.

**C6 — the one real first-party number is misread, in the direction of the conclusion.**
"We have to reject 99% of the demos **for our main labels**" was converted to a flat "~1% acceptance rate" and used to build an expected-value calculation. On the fetched page, that line sits in a passage about **sublabel placement** — the label's stated outlet for the rejected 99%. Group-wide acceptance is higher than 1% and unpublished. Also: "NOBODY HAS PUBLISHED" appears four times in caps. A universal negative is unfalsifiable by search and cannot carry high confidence. Correct form: *not found on any first-party surface, help centre, parent-company editorial, or trade outlet searched.*

**C7 — uncited load-bearing assertions and a threshold that is a hole in the data.**
Two facts used to support the A&R conclusion and repeated as advice — a specific label's demo email, and another label's portal being closed with a paid Patreon as the only alternate route — **have no source in the report's source list at all.** Strip or cite.
"Two artists have no measurable SoundCloud at all" was promoted from *absence of data* to *a direct counterexample*. "Not in my table" ≠ "does not exist"; nobody checked.
"Ordering inverts below ~10K followers" is an artifact of a sampling gap — the comp set has **zero observations between 3,020 and 11,152 followers**. Correct statement: SC>IG holds at ≥11.1K, IG>SC at ≤3.0K, **untested in between** — which is precisely where the interesting question lives.

**C10 — one inference contradicted by the batch's own roster data.**
The claim that a label "isn't currently sourcing dubstep" because its portal checkbox list omits Dubstep is inference stacked on a UI artifact. That label's roster is bass artists. Portal genre tags are set once at onboarding and rarely maintained; the same list includes Trap and Future Bass. **Roster beats checkbox — cut this.** Also, "fabricated" is the wrong word for the Gravitas requirement language; the supportable statement is "not stated on the label's current demo page." And Local Void's required TikTok/X fields are Google Forms short-answer fields — fillable, not a hard gate. The useful read is that the label screens on multi-platform presence.

---

## 4. WHAT NOBODY KNOWS

**This section is the most important in the memo. These are not gaps in the research — they are gaps in the world. No amount of further searching will close them.**

1. **The causal effect of a label signing on an artist's streams.** Zero difference-in-differences, synthetic control, matched-cohort, or event studies exist. Chartmetric, Soundcharts, Songstats and Luminate all hold the raw panel data. None has published. The closest peer-reviewed work explicitly declines to claim causation.

2. **Label acceptance rates for unsolicited demos.** LabelRadar has ~500,000 tracks submitted, 1,000+ labels, and $300K ARR selling submission credits — maximum commercial incentive to publish a flattering conversion number — and has never published a signings figure anywhere. Its parent's own editorial cites five named success tracks as its entire evidence of efficacy. No label in this genre has published received-vs-signed counts.

3. **Response rates for direct DJ promo.** Every promo platform publishes vanity denominators (30M promos delivered, 125,000 tastemakers) and withholds every numerator. All three major platforms track per-campaign open/download/play and show it to paying senders. None publishes it in aggregate, and none segments by sender size.

4. **The base rate for uncleared-flip takedowns.** No published figure exists for: content-ID block rate at upload, manual-report rate per flip, per-artist annual strike rate, or termination rate. SoundCloud's transparency page carries no copyright statistics at all. Every survival observation is a numerator with an unobservable denominator — deleted tracks are invisible to any API pull.

5. **Where bass/140 A&Rs actually source signings.** No survey, no label-disclosed sourcing breakdown, no trade journalism quantifying it. The general-industry survey that two reports lean on is n=125, February 2024, and not genre-scoped — a single point of failure carrying two conclusions, unflagged in both.

6. **Whether long-form drives follower conversion.** Every measurement taken anywhere was *plays*. The claims are about *audience growth*. Follower delta from a mix, a series, or a flip has never been measured by anyone on any tier.

7. **Instagram followers vs. Spotify monthly listeners for emerging electronic artists.** No Tier 1 or Tier 2 source tests this. Spotify's official Fan Study contains no cross-platform social data. Meta has published nothing.

8. **Whether SoundCloud's Amplify eligibility is genuinely capped at 10 minutes.** This is the entire mechanistic backbone of the C4 refutation and **the auditor could not verify it** — the help domain 403s automated fetch and search budget was exhausted. **Verify in a browser before relying on it.**

9. **Unresolved hard conflict between two reports.** One states a specific comp artist has no measurable SoundCloud presence; another computes a partial correlation across n=9 that explicitly includes that artist and requires log-transformed SoundCloud values for all nine. You cannot log a missing value. Either the first report's flagship counterexample is false, **or** the second's degrees of freedom are misstated. Both use their version as load-bearing. Unresolved.

---

## 5. STRATEGY IMPLICATIONS

Derived **only** from S1–S6. Everything else is too weak to carry a recommendation.

### Act on these now

**A. Split the SoundCloud accounts. Today.**
Uncleared major-label flips currently share a handle with the originals and the entire follower base. Strikes are account-level, termination is permanent, there is no appeal ladder and no export. Three undisputed manual reports in a rolling 12 months destroys everything. Put flips on a separate handle; keep the main handle clean. This costs one afternoon and is derived from confirmed mechanics, not from any contested rate estimate. **It is the only recommendation in this memo that survived every objection from every reviewer.**

**B. Stop counting flips toward Spotify growth.**
S1 is settled on multi-source Tier 1. Uncleared flips cannot reach Spotify or Apple, there is no compulsory-licence workaround, and the 2026 Spotify/UMG remix product is not a distribution path. Whatever the flip programme is for, it is not for monthly listeners. Monthly-listener growth has to come entirely from originals.

**C. Budget flips as pure marketing spend with zero revenue, forever.**
S3 is unambiguous. Unofficial remixes are permanently non-monetisable on SoundCloud. Delete any revenue assumption from the plan.

**D. Replace "self-release after rejection" with a hard calendar date.**
The exit condition in the current plan almost never fires — silence is the modal outcome, and rejection is rarely delivered. Submit, log the date, self-release on day 60 regardless of what came back. Use one-to-many exposure rather than serial rounds. Hold at most two tracks, not four to six: label policies commonly require unreleased *and* unpublished (explicitly including no prior free download), so every held track is also withheld from the one channel currently producing measurable reach.

**E. Correct the demo doors before submitting.**
Re-check all seven portals first — one label in the wider set was found *closed* by a different researcher, proving state flips. Then: email the label that publishes an email door rather than routing through its portal; do not withhold tracks from Gravitas waiting on a mastering bar the label never set, and use its second LabelRadar door; email-only for SubCarbon, never a SoundCloud DM; create TikTok and X accounts before touching Local Void's form; and budget for LabelRadar credits plus the fact that every submission is judged on a 20-second clip you choose. **That clip selection is a real creative decision, not an afterthought.** Treat every submission as a lottery ticket with genuinely unknown odds.

### Where the evidence does not support a recommendation — say so, don't invent one

**F. Whether to make long-form at all: UNDETERMINED. Do not act on C3 or C4 as written.**
Both contain fabricated item-level rows. The one honest quantitative result — an artist-fixed-effects regression whose confidence interval includes parity — supports neither "mixes work" nor "mixes don't." The verified evidence that *does* stand is narrower and more useful: **series plays track the guest's pre-existing audience, not the series** (47x spread across consecutive episodes of one series on one host audience). That argues against a self-run series at a 55-follower base — not because long-form underperforms, but because *any* self-published upload into 55 followers reaches 55 people. It says nothing about whether a mix outperforms a track once an audience exists. Re-run both analyses on a published, reproducible dataset before deciding.

**G. "Short-form flips are the lever": NOT ESTABLISHED. Reject this recommendation.**
All five reports independently converged on it, which is a warning sign, not corroboration. It is derived from the same n=9-to-15 cross-sectional comp set those same reports declare non-identifying, and specifically from looking only at each artist's *top* item — textbook selection on the dependent variable. The direct test of it (three flips vs. three originals) is n=3 vs. n=3 with inverted dates and no power. **No report earned this conclusion.** Flips may well be worth making; nothing here tells you they are the growth lever.

**H. "Grow Instagram and Spotify will follow": NOT SUPPORTED. Reject.**
This is an interventional claim built on a cross-sectional rank correlation among nine survivors that the same report showed is a scale artifact — Instagram adds no predictive signal beyond any other size proxy, and the peer-reviewed source explicitly flags reverse causality. The prediction band is wide enough that no observed value could have contradicted it.

**I. The conversion-funnel finding is real as an observation, unexplained as a diagnosis.**
116,070 views and 9,148 accounts reached over 90 days producing 706 profile visits and 20 external link taps is a measured fact, and 20 taps from 9,148 reached is objectively poor. But no report established *why*, and no evidence in this body of work identifies which intervention would move it. Treat it as the best-identified open question, not as a solved problem with a known fix.

**J. Do not compose the four plans without checking the intersection.**
Taken together, the recommendations produce a deadlock nobody flagged: labels require unreleased *and* unpublished material (so originals are embargoed while under submission); flips belong on a burner account (so they leave the main handle); and the main handle must stay credible as submission infrastructure. **Composed literally, the primary channel has nothing left to post.** Whatever plan gets built must resolve this explicitly — most likely by capping held tracks at two, as in (D), so there is always something releasable.

---

**Bottom line.** Ten claims examined. One is genuinely settled (flips cannot reach DSPs). Two more rest on confirmed platform *mechanics* rather than measured *rates* (account-level strikes, non-monetisability) and are safe to act on. Everything else is unmeasured — not disproven, unmeasured. Two reports contained fabricated data and must be re-run. The reflexive strategic prescription that emerged from all five reports simultaneously has not been earned by any of them. **The correct posture is: fix the account-separation exposure, stop attributing Spotify growth to flips, submit on a calendar rather than on hope, and treat every remaining question as genuinely open.**