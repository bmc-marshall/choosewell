# Type of choice: Whether, when or how much ("Should we do this, now, and at what scale?")

Use for a single go/no-go, timing or amount decision rather than a choice between organisational designs: launch or not, pilot first or not, settle or go to trial, bid or don't bid, invest now or wait, how much to spend, whether to commission a study. These sit outside the Tree 1 ladder because they don't depend on scope, structure or partners being settled first.

## Default method

| Situation | Recommend |
|---|---|
| The consequences can be put in money (or one common unit) and a few uncertain events drive them | **Quantified decision tree** (`methods/quantified-tree.md`) on its own. No criteria or weights: skip Step 5 |
| Same, but there's a single uncertainty with a few outcomes and no later decisions | A **payoff table** (`scripts/appraise.py payoff`): expected value, regret, break-even probability |
| The question is whether a study, test or pilot is worth its cost | **Value of information** (`scripts/uncertainty.py voi`), or the tree if waiting for the result costs something |
| Important consequences can't be put in money | The tree for the money, plus §10 of the method file for the rest; or scored criteria if money is a minor part |
| Many continuous uncertainties (growth, prices, usage) | **Cash-flow model with ranges** (`methods/quantified-tree.md` §11) |

## Keep it proportionate

Most of these questions can be answered in the reply: the recommendation first, then a short table of options with expected value, chance of a loss and worst case, the break-evens that matter, and what isn't in the numbers. Offer the workbook, the live Excel tree, a checklist or a storyline rather than building them unasked. Use the full ten steps only when the decision is large, contested or will be scrutinised.

## Before building the numbers

- **Check what the user's figures include.** Ask whether a payoff is before or after the cost of the action (a campaign's "extra profit", a settlement's "net" value). The answer can flip the result, so state the assumption in the first line.
- **Ask for missing probabilities, but don't wait for them.** Use a clearly labelled placeholder, then show the break-even: "this only matters if a competitor launch is more than 40% likely".
- **Ask where the organisation is and how big it is.** Rules, prices and offers often vary by country, and the stakes relative to the organisation's size decide whether risk attitude matters (`methods/quantified-tree.md` §9).

## Checks for common decision shapes

| Shape | Easy to miss |
|---|---|
| **Launch, with or without a pilot** | The cost of delay (a competitor moves, a season is missed); whether the pilot's track record is known; whether a good pilot changes the scale of launch, not just the go/no-go |
| **Settle or go to trial** | Where the case is heard (ask first: it decides the costs rule); who pays legal costs (each side, or loser pays); time to judgment and discounting; whether damages can actually be collected; appeals; whether the offer lapses once proceedings start; the reputational effect either way. The **walk-away point** for negotiation is the certainty equivalent of going to trial: settle for anything better |
| **Bid or don't bid** | Chance of winning (from past win rates); the cost of bidding; capacity tied up; the value of a relationship if you lose; what you'd do with the capacity instead |
| **How much to spend** | Diminishing returns at higher spend; a staged option (spend some, top up if early results are strong); competitor response; whether the payoffs already net off the spend |
| **Invest now or wait** | What's learned by waiting, against what's lost; whether the opportunity stays open; prices that may move |
| **Commission a study** | Whether any result would change the decision (if not, it's worth nothing); its cost against its value (`methods/quantified-tree.md` §7) |

## Outputs

A one-line recommendation with its strategy ("pilot; launch if it goes well; stop if not"); an options table (expected value, chance of a loss or of a loss above an agreed size, worst case); a risk profile for the top two; the break-evens that matter; value of information for any study; what's not in the numbers. Optional: the tree diagram, the live Excel tree, a one-page storyline.

## Worked example (invented)

A team weighed a national roll-out against a regional pilot first (the example in `methods/quantified-tree.md` §3 and §7). The tree gave pilot-first an expected value of £176k against £120k for rolling out now. The pilot was worth up to £96k, against its £40k cost. The team added the cost of a three-month delay: the pilot stayed best unless that delay cost more than £56k, which became the question for the commercial director.

## Checklist
- [quick] Confirmed whether the user's payoffs already include the cost of each option
- [quick] Recommendation in the first line, with the strategy for later decisions
- [quick] Options table with expected value, chance of a (large) loss and worst case
- [standard] Break-evens for the inputs nobody is sure of, and for any unquantified risk
- [standard] Cost of delay or waiting considered
- [standard] The shape-specific checks above covered (costs rule, collectability, win rate, diminishing returns, as relevant)
- [standard] Risk attitude considered if the worst case is more than about a quarter of the organisation's risk tolerance (`methods/quantified-tree.md` §9); otherwise say why expected value is enough
