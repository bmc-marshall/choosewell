# Method: quantified decision tree (probability-weighted payoffs)

Use when the answer hinges on a few uncertain events you can put rough numbers on, and especially when the choice comes in stages: test or pilot first, phase an investment, wait for news, try one site before another. It tells you which option is worth most on average, what to do at each later decision, how risky each option is, what extra information is worth, and what it's worth to keep options open.

This is not the same as the **decision tree** for matching options to situations (`methods/decision-tree.md`). That one is a set of yes/no questions that picks a model for each case. This one puts probabilities and values on the branches and does arithmetic.

| | |
|---|---|
| Good for | Go/no-go and invest/wait choices; pilots and test markets; phased R&D or programmes; bid or don't bid; settle or litigate; whether to commission a study; which risky approach to try first |
| Not good for | Many uncertain inputs with no clear events (use a cash-flow model with ranges, §11); futures nobody can put probabilities on (scenarios and regret, `steps/08-test.md` §8.4); consequences that can't share a common unit (scored criteria, or §10) |
| Often follows | A scored or red/amber/green long list: the tree is run on the two or three options left |
| Script | `scripts/uncertainty.py` (`tree`, `voi`, `bayes`); `--help` on each. Starter models in `assets/examples/`: staged programme, pilot value, which risky step first, learn then decide, tree flip, risk attitude |

## 1. The three ingredients

1. **Options**: what you can choose now and at each later point. Always include doing nothing, and at every later decision, stopping. Add flexible versions (pilot, phase, wait) where the future is uncertain.
2. **Uncertain events and their probabilities**: only the few that could change the choice. Each event's outcomes must be mutually exclusive and cover everything that can happen, so its probabilities add to 1.
3. **Values**: what each complete path through the tree is worth, usually as a present value in money. Say which discount rate and time horizon you used.

## 2. Drawing the tree

| Symbol | Means | Rule |
|---|---|---|
| Square | A decision | You choose the branch |
| Circle | A chance event | Branches carry probabilities that add to 1 |
| End point | A result | The payoff of the whole path, or what's left to receive from that point |

- **Left to right is time.** Put each decision where it's actually taken, after whatever has been learned by then. The same decision ("launch?") can appear several times, once for each thing you might have learned first, and the probabilities after it differ each time.
- **Probabilities are conditional** on everything to their left: after a good pilot, the chance of national success is the chance *given* a good pilot.
- **Enter each amount once, where it happens.** A pilot's cost goes on the pilot branch. Don't also take it off the end values: that counts it twice. **Check what the user's figures include**: a campaign's "extra profit" or a settlement's "net" value may already allow for costs. Ask, and state the assumption.
- **Include the cost of waiting** wherever a branch delays the main decision (a pilot, a study, a trial date): lost sales, a competitor moving first, a lapsing offer. If nobody knows it, find the break-even delay cost.
- **Leave out money already spent.** It's the same whichever option you choose, so it can't change the answer.
- **Keep inputs separate from the tree.** List every number once in an inputs table, with its source and a low and high value, and have the tree refer to it. In the JSON, an input can carry these directly: `"p_ok": {"value": 0.6, "low": 0.4, "high": 0.8, "source": "..."}`. They go into the Excel export, and `--tornado auto` uses the ranges.
- **Risks nobody has numbers for yet** (a competitor might launch): put them in with a clearly labelled placeholder probability and report the break-even ("this changes the answer only if a launch is more than 40% likely"), rather than leaving them out or waiting.
- **Keep it readable.** If a probability needs its own reasoning (will a court find the contract enforceable, given which witnesses appear and how the evidence lands?), work it out in a small side tree and carry one summary probability into the main tree. If an end value needs a cash-flow model, build the model separately and link its result in. A tree nobody can follow is a tree nobody will trust.

## 3. Folding back (working out the answer)

Work from right to left:
- At a **chance point**, take the expected value: each branch's value times its probability, added up.
- At a **decision point**, take the best branch and mark the others as rejected.

The number you end with at the left is the expected value of the best strategy. The marked branches give the **strategy**: not a single choice but a plan ("run the pilot; roll out if it goes well; stop if it doesn't").

**Worked example (invented).** A national roll-out of a new service would be worth £900k if it succeeds and lose £400k if it fails. On past experience of similar launches, the team puts the chance of success at 40%. A regional pilot costs £40k. Looking back at comparable pilots, 80% of eventual successes had good pilots, and so did 30% of eventual failures.

| Option | Calculation | Expected value |
|---|---|---|
| Roll out now | 0.4 × 900 − 0.6 × 400 | £120k |
| Don't roll out | | £0 |
| Pilot first, then decide | (see §7 for how the pilot probabilities are found) 0.5 × 432 + 0.5 × 0 − 40 | £176k |

Pilot first is best: roll out if the pilot goes well, stop if it doesn't.

**What expected value means.** It's the average result if you could make this kind of decision many times. Any single decision will land on one branch. The pilot strategy above never actually produces £176k: it produces −£440k, −£40k or +£860k. Expected value is still the right basis for most decisions, because organisations make many of them and the good and bad luck evens out. The exception is when one bad outcome would be too much to bear (§9).

**Always show the risk profile beside the expected value**: every possible result with its probability, the chance of a loss, and the worst case.

| Pilot-first strategy | Probability |
|---|---|
| +£860k (pilot good, roll-out succeeds) | 32% |
| −£40k (pilot poor, stop) | 50% |
| −£440k (pilot good, roll-out fails) | 18% |

So there's a 68% chance of losing something, mostly the cost of the pilot. Compare roll-out-now: a 60% chance of losing £400k.

## 4. Where the probabilities come from

- **Start from how similar cases turned out** (the outside view): past launches, bids, trials, wells. Then adjust for what's unusual about this one, and say why. Most good probabilities blend records and judgement.
- **Break hard questions down.** "Will we win?" may really be "Is the contract enforceable?" and then "If so, was it breached?". Estimate the parts and multiply along the branches.
- **Ask several people independently**, then average and record the spread (Step 7.2). Where people won't give a number, offer a comparison instead: "Would you rather win £1,000 if this happens, or if a spinner with a 30% red slice lands on red?". Adjust the slice until they can't choose; that slice is their probability.
- **If the user gives only central estimates**, use placeholder ranges and label them: ±0.1 for probabilities (kept between 0 and 1) and ±25% for amounts. Say the tornado's ranking depends on them, and ask for real ranges for the top few inputs.
- **Record a range for each probability** (low, central, high). Sensitivity analysis (§6) shows whether the precision matters. Usually it doesn't.
- **Keep linked probabilities consistent.** The probabilities after a test depend on the prior and on the test's track record (§7). Change those inputs and recompute, rather than nudging the after-test numbers by hand.
- **Be careful with rare disasters.** Very small probabilities are hard to estimate. Show the size of the downside separately, and find the probability at which it would change the decision.

## 5. Reading the result

Report, in this order:
1. **The recommended strategy** in words, including what to do at each later decision.
2. **Its expected value**, and how much better it is than the next best option.
3. **The risk profile**: chance of a loss, worst case, and how likely the worst case is.
4. **What would change it**: break-even values (§6).
5. **What's left out**: effects that aren't in the numbers (§10).

## 6. What would change the answer

- **One input at a time.** Vary each uncertain input across its range and show which option is best at each value. The **break-even** is the value at which the best option changes. In the roll-out example, the pilot stays worthwhile unless it costs more than £96k. Break-evens are often more useful than the expected value itself: "launch at full scale only if you believe the chance of a superior product is above 45%" gives decision-makers something they can argue about.
- **Two inputs together**: a grid showing the best option for each pair of values. Use it when two inputs move together or interact.
- **Tornado**: move each input from its low to its high value and rank the inputs by how much they move the **lead of the best option over the runner-up**, and whether the best option changes. Spend effort on the top few. (Measuring the gap matters: when the best option is a sure thing, like a settlement offer, inputs that only affect the risky option still decide the choice.)
- **Risk tolerance**: if §9 applies, find the risk tolerance at which the choice flips.

`scripts/uncertainty.py tree model.json --sweep name=low:high --tornado auto --at "Decision name" --loss-threshold 100` does all of these: break-evens to four figures, risk profiles of every option, the chance of losing more than an amount that matters (often more useful than the chance of any loss, which counts a small pilot fee), and warnings when options tie. With `--at`, values are from that decision onwards; if several decisions share a name, use `--at "Name#2"`. Report the results in Step 8.2's terms: "The recommendation holds unless…".

## 7. What information is worth

Information has value only if some result could change what you'd do.

**Perfect information (EVPI).** Imagine someone could tell you the outcome before you decide. Work out the expected value if you always chose the best option for each outcome, and subtract the expected value of the best choice now. In the example: with perfect foresight you'd roll out only when it will succeed, 0.4 × 900 = £360k, minus £120k now = **£240k**. No pilot, study or consultant can be worth more than this. If a proposed study costs more, stop considering it.

**Imperfect information (EVSI).** Real tests are fallible, so you need their track record: how often the test gives each result when the truth is one way or the other. Turn that around ("tree flip", using Bayes' rule) to get what you need for the tree: the chance of each test result, and the probability of the truth after each result.

| Step | Pilot goes well | Pilot goes poorly |
|---|---|---|
| 1. Prior × track record ("joint"): would succeed | 0.4 × 0.8 = 0.32 | 0.4 × 0.2 = 0.08 |
| …would fail | 0.6 × 0.3 = 0.18 | 0.6 × 0.7 = 0.42 |
| 2. Chance of this result (add the column) | 0.50 | 0.50 |
| 3. Chance of success after this result (joint ÷ column total) | 0.32 ÷ 0.50 = 0.64 | 0.08 ÷ 0.50 = 0.16 |
| 4. Best action and its value | Roll out: 0.64 × 900 − 0.36 × 400 = £432k | Stop: £0 |

Expected value with the pilot (before its cost) = 0.5 × 432 + 0.5 × 0 = £216k. **EVSI** = 216 − 120 = **£96k**: the most worth paying for the pilot. At £40k it's a good buy.

Rules of thumb:
- **Buy information when its cost is below its EVSI.** EVPI is the ceiling; a real test recovers only part of it.
- **If every result leads to the same action, the test is worth nothing**, however interesting it is.
- **Mind the base rate.** When the thing you're testing for is rare, even a good test leaves a lot of doubt. With a 5% prior, a test that catches 90% of true cases and wrongly flags 10% of the rest gives P(true | flagged) = 0.045 ÷ (0.045 + 0.095) = 0.32. Two flags out of three are false.
- **Several signals combine** if they're independent once the truth is known: multiply the track records along with the prior. `uncertainty.py bayes` does this.
- **Chase the information that could change the choice**, not the easiest to collect (Step 8.3).

`scripts/uncertainty.py voi` takes a payoff table, the priors and each test's track record, and reports EVPI, EVSI, the decision rule after each result, and whether the test is worth its cost. It assumes every option is still open, at the same value, once the result is in. If waiting costs something or an option can lapse (a settlement offer withdrawn once proceedings start), build the full tree instead.

## 8. Keeping options open, staging and sequencing

**Option value** = expected value with the flexibility − expected value without it. Build both versions of the tree and subtract. Kinds of flexibility:
- **Stop at a stage gate.** Each phase of a phased programme is an option to carry on or stop. A project can be worth starting even when committing to all of it isn't, because you'll only pay for the later, expensive stages if the early ones succeed.
- **Test before committing**: pilots, trials, surveys, studies (§7).
- **Wait.** Delay costs something (a competitor may take the opportunity, a window may close), but you may learn or prices may move. Put both in the tree.
- **Start small and expand, or switch later.**
- **Learn from one choice before the next.** When outcomes are related (neighbouring sites, similar markets), trying one first tells you about the other. The tree shows the value: "do A; if it works do B; if not, stop" against "do both now".

**Which risky step first?** When you must clear several pass/fail hurdles and any failure sends you to a fallback:
- If a failure costs only what you've spent so far, start with the hurdle whose **cost divided by its chance of failing** is lowest: cheap and likely to fail goes first. Example: hurdle A costs £100k and fails 20% of the time (100 ÷ 0.2 = 500); B costs £300k and fails 40% of the time (300 ÷ 0.4 = 750). A first: expected cost £860k against £880k for B first, with a fallback costing £1m.
- If a late failure costs more (less time left, so the fallback has to be rushed), the step **most likely to fail** may belong first even if it costs more. With the same hurdles, but a fallback costing £1.5m when the failure is found late, B first is now cheaper (£940k against £1,020k).
- Running hurdles **in parallel** saves time but means paying for both even when one fails. Put all three orders in the tree.

For the common shapes (launch with a pilot, settle or go to trial, bid or not, how much to spend, invest now or wait), `choices/whether.md` lists what's easy to miss.

Carry the result into Step 9: what the preferred option keeps open (§9.1) and the route with triggers (§9.2).

## 9. Attitude to risk

Expected value is right when the stakes are modest for the organisation and the decision is one of many. Decision analysts report that risk attitude changes the answer in only a minority of business decisions. Bring it in when a bad outcome would be large relative to the organisation's budget or reserves, or when decision-makers are clearly uneasy about an option that wins on expected value.

**The simple version.** Show the risk profile and the chance of a loss, and agree a maximum acceptable loss in advance. Treat that as a knock-out (`steps/05-criteria.md` §5.1).

**The fuller version: risk tolerance and certainty equivalents.** Exponential utility needs one number, the **risk tolerance** (R), in money. To find it, ask: "Would you accept a 50–50 chance of gaining R or losing half of R?" The largest R people would accept is roughly their risk tolerance. As starting points for that conversation, Ronald Howard found that large companies' risk tolerances ran at roughly 6% of annual sales, a little over a year's net income, or about a sixth of equity. These are guides from large firms, not facts: prefer the net-income or equity guide where those are known (sales says little about margins), and for small organisations, charities and public bodies, ask the 50–50 question directly. Always show the result across a range of risk tolerances. The **certainty equivalent** of an option is the sure amount you'd take instead of it:

- utility of a result x: U = 1 − e^(−x/R)
- expected utility: the probability-weighted average of U over the option's results
- certainty equivalent: CE = −R × ln(1 − expected utility)
- **risk premium** = expected value − certainty equivalent: what the risk costs you

Example: a 50–50 chance of +£3m or −£1m has an expected value of £1m. With R = £2m, U(3) = 0.777 and U(−1) = −0.649, so the expected utility is 0.064 and CE = −2 × ln(0.936) ≈ £0.13m. The gamble is still better than nothing, but it's worth about £0.13m to this decision-maker, not £1m.

Report the risk tolerance at which the choice flips (the script finds it in either direction, or says there isn't one): "the bolder option is better if you'd accept a 50–50 gamble of winning £4.4m or losing £2.2m". (`uncertainty.py tree --risk-tolerance R` does this, and reports certainty equivalents for every option.)

## 10. Things money doesn't capture

- **Put them on a common scale, carefully.** Express each consequence relative to a reference ("the cost of one unnecessary check = 1; wrongly barring someone = 50") and test those ratios hard. They're judgements, and they often drive the answer.
- **Or back-solve.** Leave the effect out, then ask how big it would have to be to change the choice: "the new approach wins only if the reputational benefit is worth more than £X". Decision-makers can usually say whether it's that big, even when they can't put a figure on it.
- **Name what's left out** in the write-up (brand, relationships, precedent, future contracts), and say which way each would push.

## 11. Many uncertain inputs: cash-flow models with ranges

When the uncertainty lies in many continuous inputs (growth rates, usage, prices, staffing) rather than a few events, a tree gets bushy fast. Instead:
1. Build a period-by-period cost or cash-flow model for each option over the same horizon, with the same discount rate.
2. Give every uncertain input a low, central and high value, each with its source.
3. Run one input at a time and draw a **tornado** of the difference between options. Then find the **break-even** of the top driver ("the pay-as-you-go platform is cheaper unless usage grows faster than 7% a quarter").
4. Run combined scenarios (everything low, everything high, and the combinations that hurt each option most).
5. Optionally, run a Monte Carlo simulation: sample all inputs from their ranges and report how often each option comes out best.

Include one-off switching costs, and the value of flexibility: capacity you pay for as you use it against capacity you commit to in advance. If one or two events dominate after this, put them in a tree with the model's results at the end points.

## 12. Outputs

- **The tree**, pruned to the branches that matter, with rejected options marked.
- **Inputs table**: each number with its source, range and owner.
- **Strategy statement**: what to do now and at each later decision.
- **Risk profile chart** for the top two or three options.
- **Break-even table or chart**, and a **tornado**.
- **Value of information table**: EVPI, then EVSI against cost for each study considered.
- **Option value line**: what the flexible version is worth over the rigid one.
- **What's not in the numbers**, and which way it pushes.

`uncertainty.py tree model.json --xlsx tree.xlsx` writes a live Excel version (named inputs, formulas throughout) for a group to explore, or to use with Excel's Goal Seek and Data Table.

## 13. Pitfalls

- Treating the expected value as a forecast of what will happen.
- Counting a cost twice, or counting money already spent.
- Probabilities at a chance point that don't add to 1, or after-test probabilities that aren't consistent with the prior and the test's track record.
- A "bushy mess": detail that belongs in a side calculation.
- No do-nothing option, or no way to stop at later decisions.
- Precise-looking outputs from rough inputs. Round, and lead with break-evens.
- Leaving out everything that isn't money, without saying so.

## Checklist
- [quick] Options include doing nothing, and stopping at each later decision
- [quick] Tree drawn in time order, with decisions placed after what's learned by then
- [quick] Each probability sourced (records, judgement or both), with a low and high value; each chance point adds to 1
- [quick] Each amount entered once, where it occurs; money already spent left out
- [quick] Recommended strategy stated in words, with its expected value and risk profile (chance of a loss, worst case)
- [standard] Inputs kept separate from the tree, each with its source
- [standard] Break-even values for the key inputs, and a tornado
- [standard] Value of information worked out for each study or test considered (EVPI ceiling, EVSI against cost)
- [standard] Flexible versions (stage, pilot, wait, sequence) compared with rigid ones; option value stated
- [standard] Effects not in the numbers named, with the direction they push
- [full] Attitude to risk considered: maximum acceptable loss, or risk tolerance with certainty equivalents and the tolerance at which the choice flips
- [full] Linked probabilities derived consistently (tree flip) rather than set by hand
