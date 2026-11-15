# Method: threshold filter (sequential pass/fail funnel)

Use when there are many candidates (more than about 12), each criterion has a measurable proxy, and the goal is to cut quickly to a shortlist for deeper work. Common for **Where** (countries, states, regions, cities) and for first-pass screening of large lists.

## Steps

1. **Pre-exclusions.** Remove candidates for reasons outside the criteria, each with a stated reason (existing market, pending contract, competitor exclusivity, policy). Show them as a footnote.
2. **Criteria → measures → thresholds.** For each criterion, the measure and the requirement, e.g.:

   | Criterion (why it matters) | Measure | Requirement |
   |---|---|---|
   | Market size (large enough to prioritise entry) | Potential users; users in the main target segment; number of sites | ≥ X; ≥ Y; ≥ Z (**at least one of these**) |
   | Budget (can afford to buy) | Funding per user | ≥ $N |
   | Accessibility (big enough to recover acquisition cost) | Users per average site | ≥ M |
   | Political support | Evidence of support in statements, voting, sponsorship | Evidence of support |

   OR-conditions ("at least one of these") and qualitative tests are fine; define them.
3. **Set thresholds from the data.** Look at the distribution before fixing thresholds, and anchor them to something real (break-even size, budget needed, a natural break). Avoid thresholds that sit in a dense cluster, where a small change flips many candidates.
4. **Order the filters.** AND-filters give the same final set in any order, but the order tells the story: put the most fundamental first (market size), then budget, then the harder-to-measure tests. Order also matters for effort: apply cheap, decisive filters before ones requiring research.
5. **Sensitivity.** For each threshold, show how many candidates pass if it is loosened or tightened by a sensible step (e.g. ±10–20%, or to the next natural break). Flag near-misses (candidates that fail only one filter, with how far they miss it) and consider showing one as a "removed from shortlist" profile to explain where the line fell.
6. **Shortlist → deep dive.** Survivors get profiles (one page per place, or one page per theme per place) and, often, a scored grid.

`scripts/appraise.py thresholds` runs the funnel and the sensitivity from a CSV.

## Outputs

- **Criteria table**: criterion (with the reason it matters), measure, requirement.
- **Funnel**: selection steps with the count remaining after each (e.g. 47 → 16 → 13 → 10 → 5), plus the shortlist named.
- **Map or grid** of all candidates coloured shortlisted / longlisted / removed, with a legend.
- **Sensitivity table**: threshold, base count, count if loosened, count if tightened, near-misses.
- **Profiles** for the shortlist (and any instructive near-miss).

## Cautions

- Thresholds create cliffs: a candidate just below the line may be better overall than one just above. Near-miss reporting is the guard.
- Criteria that trade off against each other (bigger regions get less funding per user) shouldn't both be filters: filtering on each removes the options that are strong overall. Filter on the one that's a true requirement, and score the rest.
- Unknown values ("unclear", blank) are not fails. Treat them as provisional passes, flag them, and list them as open questions. `appraise.py thresholds` does this and lists near-misses (options failing only one step).
- Set thresholds from the user's objectives and data, not from an example, and say where each came from.
- Proxy quality: say how well each measure captures the criterion.
- Date the data; political and funding positions move.

## Checklist
- [quick] Pre-exclusions with reasons; criteria → measure → requirement table
- [quick] Thresholds set from the data distribution and anchored to something real
- [standard] Threshold sensitivity (± a sensible step) and near-misses reported
- [quick] Funnel counts and map/grid of candidates by status
