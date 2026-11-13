# Calibration, 2026-11-11 (draft, awaiting artist sign-off)

Data: Beatport snapshot read 2026-11-11 19:32 UTC. 140 / Deep Dubstep / Grime Top 100 and Dubstep Top 100.
Universe: 18,709 releases, 2,597 labels, 17,394 artists, 2024-11-11 to 2026-11-11, both genres.

## Facts found
- Beatport flags both accepted genres as not included in Hype. Both Hype 100 pages are empty. Hype points moved: chart proof 30 -> 40, roster 20 -> 30.
- Label pages carry no bio text on Beatport (empty for all 118 labels read). Owners must come from SoundCloud bios or label sites.
- Beatport label track lists carry no publish_date or is_hype; release date = new_release_date.
- Distributors (Create Music Group, DistroKid, UnitedMasters) excluded as not labels.

## Calibration result (Beatport-side gates only)
| Label | Known as | Result | Why |
|---|---|---|---|
| Wubaholics | good | pass, 80 | |
| SubCarbon | good | pass, 90 | |
| DUPLOC | good | pass via roster path (RSI 75) | no current chart track |
| Infernal Sounds | good | pass via roster path (RSI 60), borderline | no current chart track |
| Locus Sound | good | FAIL | 2 releases in 6 months; RSI 36 |
| Odyzey | good | FAIL genre 3/12 | last 12 mostly Trap / Future Bass |
| Trippy Bee | good | FAIL genre 6/12 | 4 of last 12 Trap / Future Bass |
| Outertone | bad | fail | 0/12 genre |
| Space Yacht | bad | fail | genre and activity |
| Create Music Group, DistroKid | bad | excluded | distributors |

## Proposed changes
1. Activity: 3 releases in 6 months -> 2. (Locus)
2. RSI scene ties: peer-label artists add 8 for 3-4, 14 for 5+. No-chart threshold 60 -> 40. (Locus 42; candidates 19 -> 64)
3. No-chart labels qualify by RSI, not by the 50-point score (the score is built on chart proof).
