---
title: Merch — on-demand, quality-first
version: 1.0
last_updated: 2026-08-14
status: live — decided, not yet built
scope: On-demand merch store — platform selection, blank selection, terminal integration. Decisions and the reasoning behind them, not a task tracker.
dependencies: [[working/WEB_HOME_SPEC]], [[working/WOBAR_ACTIVE]]
---

# MERCH — ON-DEMAND, QUALITY-FIRST

## THE DECISION

**Apliiq (fulfillment) + Shopify (storefront), locked 2026-08-14.** Weighed against Printful, Fourthwall, Printify — quality of blanks was named the deciding axis, ranked above cost, integration simplicity, and monthly fee. The platform with the best blank/embroidery quality won even though it costs the most in dependencies (a required Shopify layer) and money (Shopify's monthly fee, where every alternative here is free).

## WHY APLIIQ, AND WHAT LOST

**Printify — cut first.** It's an aggregator, not a single production facility: quality depends on which of many print partners fulfills a given order, and consistency would require manually vetting and pinning a specific provider per product. Opposite of a quality-first decision by construction.

**Printful — strongest runner-up, and the fallback if Apliiq underdelivers.** Direct REST API (no Shopify dependency needed), New Era caps confirmed in catalog, Champion + Independent Trading Co hoodies with embroidery, holographic die-cut stickers, no monthly fee, and multiple public working examples of Next.js + Printful + Stripe integrations exist — low engineering risk if the terminal integration is ever rebuilt native. Lost on: no confirmed in-house/domestic embroidery, narrower premium blank catalog than Apliiq's.

**Fourthwall — best integration story, lost on cap quality.** Purpose-built creator/musician commerce platform. Its Storefront API is designed exactly for "headless catalog + our own frontend + their hosted checkout" — the cleanest technical fit for the terminal, before the terminal-integration requirement was dropped (see below). Confirmed Bella+Canvas, Comfort Colors, Champion, Independent Trading Co embroidery. **No New Era caps found in its catalog** — its cap brands are Yupoong/Otto Cap/Valucap/Richardson/Flexfit, the budget-to-mid tier. Its sticker product is a kiss-cut sublimation *sheet*, not an individual die-cut sticker — a different product than the one wanted.

**Apliiq — won on quality.** Broadest premium blank range of the three finalists: Bella Canvas, Independent Trading Co, Comfort Colors, Next Level, Rabbit Skins, Richardson (caps — different lineage than New Era but well-regarded), plus Nike/Adidas licensed blanks. Strongest reputation signal found — 4.9 stars, reviewers specifically describing the garment feel as premium, not just "good for POD." **Embroidery is done in-house in the USA** — the one explicit domestic-quality claim none of the print-facility competitors made. Traded for: Shopify as a required middle layer (Apliiq is Shopify-native, not a standalone headless API), and 7–10 business day turnaround on embroidered/labeled orders — slower than Printful's on-demand embroidery.

## BLANKS LOCKED

- **Tee — Bella Canvas or Comfort Colors, DTG.** Undecided between the two; Comfort Colors is heavier/garment-dyed (fashion feel), Bella Canvas is the industry-standard ringspun premium. Resolve once designs exist and can be sampled on both.
- **Hoodie — Champion or Independent Trading Co, embroidery.** Same open call — Champion Reverse Weave is the heaviest/most structured, Independent Trading Co SS4500 a lighter premium fleece.
- **Cap — Richardson, embroidery.** New Era was the original quality bar (Nick named it directly) but isn't in Apliiq's catalog — Richardson is the accepted substitute, chosen knowingly on reputation, not discovered as a compromise later.
- **Sticker — die-cut holographic, platform tbc.** Not yet confirmed whether Apliiq carries an individual die-cut holographic sticker, vs. Fourthwall's kiss-cut sheet which doesn't match the brief. If Apliiq doesn't carry it, Printful's confirmed holographic die-cut sticker is the one cross-platform SKU — stickers don't touch the quality argument the way apparel and embroidery do, so sourcing that one item outside Apliiq isn't a doctrine break.

## PRODUCTION METHOD BY PRODUCT — DECIDED, NOT INCIDENTAL

**Tee = DTG. Hat and hoodie ("wear") = embroidery.** Nick's own framing: heavier garments get the premium/durable treatment, tees stay print. Stated preference, not a platform default — should hold regardless of which platform ends up fulfilling which SKU.

## TERMINAL INTEGRATION — RESOLVED SIMPLER THAN FIRST SCOPED

Original ask was a native in-terminal storefront (product list + checkout inside wobar.music's command interface, matching how `listen` is treated). **Dropped 2026-08-14, Nick's call: "the /shop command in the terminal can just launch a new page."** This removed the entire headless-integration question that had been driving the Printful-vs-Fourthwall API comparison. `shop` is now a one-line addition to the daemon's command table, same pattern as `listen` (which already opens Spotify/SoundCloud in a new tab) — it opens the Shopify store URL in a new tab. No cart logic, no webhook glue, no API key management inside the terminal codebase.

**Where it lives:** `components/terminal/daemon.ts`, alongside the existing command case statements — add `shop` to the matched-command table and to the `menu`/`help` listing, per [[working/WEB_HOME_SPEC]]'s command table format.

## COST TRADEOFF ACCEPTED

Shopify carries a monthly fee (~$25–39/mo depending on plan) — the one recurring cost in this plan, since Printful/Fourthwall/Printify all offer zero-monthly-fee storefronts. Accepted explicitly in exchange for Apliiq's blank/embroidery quality ceiling. Worth re-litigating only if Apliiq's actual finished product doesn't bear out the reputation once samples are in hand.

## OPEN

- **Apliiq's die-cut holographic sticker availability unconfirmed** — check the catalog directly; Printful holographic die-cut is the fallback for that one SKU only.
- **Bella Canvas vs Comfort Colors (tee) and Champion vs Independent Trading Co (hoodie) undecided** — resolve once designs exist and can be sampled on both.
- **Designs not yet created** — three needed: the mark for the DTG tee; the mark (or a bolded/embroidery-safe wordmark — Futura PT Heavy's fine strokes don't embroider cleanly at small sizes) for the embroidered hoodie + cap.
- **Shopify plan tier not chosen.**
- **Pricing/margins not set** for any SKU.
- **The `shop` daemon command not yet written** — trivial once the real Shopify store URL exists; can be stubbed with a placeholder URL before the store is live if wanted.
- **New Era was the stated quality bar and isn't in the final platform's catalog — Richardson is the substitute, decided on reputation research, not a hands-on comparison.** Worth Nick's own gut-check against a physical Richardson cap before treating this as settled.
