# Step 8: Test the result

Check the answer is consistent, and ask how easily it could change. A recommendation that flips if one uncertain score moves a point is very different from one that holds whatever you assume.

| | |
|---|---|
| Skip if | Never; at quick depth, just ask what single change would alter the top choice |
| You'll end up with | A tested result, flagged marginal options, and a prioritised list of open questions |
| Next | Step 9; or back to Step 6 if an open question could change the answer and is cheap to settle |

`scripts/appraise.py` runs most of these: `rollup` (consistency, spread, double counting, marginal options), `sensitivity` (dominance, value for money, switching values, weight ranges, tornado), `payoff` (expected value, value of information, regret, break-even probability), `thresholds` (threshold sensitivity). For quantified trees, `scripts/uncertainty.py tree` gives break-evens, two-way tables, tornadoes and risk profiles.

## 8.1 Consistency checks

- **Consistency**: similar options scored similarly, or the difference explained.
- **Spread**: each criterion separated the options. One that gave 12 of 13 options the same rating either lacks evidence (open question) or should be redefined. The same goes for matrix axes.
- **Double counting**: the same issue under two criteria.
- **Dominance**: an option that another equals or beats on every criterion can usually be dropped, unless it's much cheaper or it's business as usual. (Most informative when no single option leads on everything.)
- **Benchmark**: business as usual is still in the comparison.
- **Drivers vs consequences**: considerations that drive the choice are in the scores; implications of choosing (governance, procurement route, delivery risks) belong in Step 9's risks, not the scores.

## 8.2 What would change the answer (sensitivity)

- **Score flips**: move each contested or unknown score one step each way; if the overall result changes, the option is **marginal** and deserves the group's time.
- **Switching values**: how far a score or weight must move before the top choice changes. If the leader is 0.37 ahead and a criterion's weight is 37%, its score would have to fall by 0.37 ÷ 0.37 = 1 point. The Green Book requires switching values for any preferred option; they tell decision-makers what the recommendation depends on.
- **Weight ranges**: the range of each weight over which the top option stays top. With only two or three criteria, say plainly that the ranking mostly reflects the weights.
- **Tornado**: move each input to a plausible low and high value and rank inputs by how much they swing the result.
- **Threshold sensitivity**: for filters, recount survivors with each threshold 10–20% looser and tighter, and report near-misses.
- **Choosing several, not one** (two or three regions, a top tier): test whether the **top group** holds, not just the leader (`appraise.py sensitivity --top-k 3`).
- **Random weights** (optional): draw thousands of weight sets and report how often each option comes first (`appraise.py sensitivity --random 10000`). It shows how much the ranking depends on the weighting at all.
- **Non-scoring methods**: back-test a matching decision tree on past cases; for a quantified tree, use break-evens and the tornado (`methods/quantified-tree.md` §6).
- **Monte Carlo** (optional, for quantified models): sample inputs from ranges (ideally calibrated 90% ranges, which most people set too narrow until trained) and report how often each option comes out best.

## 8.3 Which open questions to chase (value of information)

Information is worth gathering only if it could change the choice, and it's worth at most what a wrong choice would cost. Rank open questions:

| Could the answer change the choice? | Cost of being wrong | Cost to find out | Action |
|---|---|---|---|
| Yes | High | Low–medium | Chase first |
| Yes | Low | Any | Chase if cheap |
| No | Any | Any | Park, recorded |

"Could it change the choice?" is answered by the marginal flags and the "best case if it resolves well" scores. With rough probabilities and payoffs, the most it's worth paying is the **expected value of perfect information**: the average result if you always knew the future in advance, minus the expected value of the best choice now (e.g. 8.4 − 6.0 = 2.4; spend well below that). For a specific study or test with a known track record, work out what it's actually worth (EVSI) with `scripts/uncertainty.py voi`; the method, with a worked example, is in `methods/quantified-tree.md` §7. Beware the "measurement inversion" (Hubbard): effort tends to go into easy, well-measured variables that don't change the decision.

## 8.4 When the future is uncertain: scenarios and regret

Where people can describe plausible futures but can't sensibly assign probabilities:
- Describe two or three coherent **scenarios** and score or value each option under each.
- **Regret** of an option in a scenario = the best result any option achieves in that scenario minus this option's result. Prefer the option whose largest regret is smallest (minimax regret, from decision theory).
- **Good enough everywhere** (satisficing): the share of scenarios in which an option meets an agreed minimum.
- **Break-even probability**: with two scenarios, the likelihood at which two options have equal expected value ("A beats B only if support continues with more than 55% probability"). Often the clearest way to frame a board's real disagreement.
- Describe each option's **failure conditions** and prefer those whose failure is least plausible or easiest to spot.

## Checklist
- [quick][scores] Consistency across similar options checked
- [standard][scores] Spread checked: each criterion separates the options
- [standard][scores] Double counting and dominated options checked
- [quick][scores] Score flips tested; marginal options flagged
- [standard][weights] Switching values and weight ranges for the preferred option
- [standard][quantified-tree] Break-even values for the key inputs of the tree
- [standard] Open questions ranked by whether they could change the choice, cost of being wrong, and cost to find out
- [full] Scenarios with regret and good-enough-everywhere tests where the future is deeply uncertain
