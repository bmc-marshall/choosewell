# Method: decision tree (matching options to situations)

*Not to be confused with the quantified decision tree (`methods/quantified-tree.md`), which puts probabilities and values on the branches.*

Use when the right option depends on conditions specific to each situation, and those conditions become known over time: which contracting model fits a particular deal, which delivery route suits a particular project, which funding method suits a particular client. The question is "which option fits these conditions?", not "which option is best in general?". Tree 3 calls this a **match**.

## 1. Building a tree

1. **Define the options** with the same fact sheet for each (§2), ordered by a meaningful dimension (resource required, risk), including an out-of-scope or do-nothing option.
2. **Find the distinguishing questions**: the fewest yes/no questions that separate the options' fundamental differences (e.g. "Are industry partners needed?" → "Are suppliers known at signature?" → "Will we contract with suppliers?").
3. **Order the questions by when the answer becomes available**, not by importance. Early questions are usually answered by the other party's needs; later ones by your own appetite and processes. That makes the tree usable in real time and shows what can be ruled in or out at each milestone.
4. **Red lines**: conditions that, if met and unchangeable, force a branch ("the client must contract with government directly"; "we lack time to procure fairly"). Options that are red lines for your organisation are dropped at the start.
5. **If no red line decides it**, the choice is a judgement: list **push factors** (driven by you: management cost, in-life resource, governance burden, influence over reputation, financial upside) and **pull factors** (driven by the other party: procurement simplicity, risk to them, depth of partnership, timescale, control over partners) for each remaining option, and decide with the people who hold the appetite. Rate each factor low, medium or high, and write down what each level means for that factor ("in-life resource: low = under one person, high = a dedicated team") so ratings can be compared.
6. **Sub-questions** under each main question ("Why does the client want a government-to-government deal? Is there a market? Is it one-off or enduring?").
7. **Allow transitions**: options can change over time (supplier-pending becomes supplier-stated as partners are found). Say which transitions are expected, and show them as a route with triggers (`steps/09-decide.md` §9.2).
8. **Back-test the tree** on real past cases: answer its questions for each, and check it picks the model that was actually used, or that it should have been. Where it doesn't, fix the questions or record why the past choice was wrong. It's the cheapest and most convincing check.
9. **Separate drivers from consequences**: considerations that influence the choice go in the tree; those that follow from it (governance route, clearance, resourcing) go on the fact sheets.

The benchmark for a matching tree is the current way of choosing (usually case by case): say what the tree improves on it. Worked examples elsewhere in the skill show the shape of a tree, not the questions to use: build the questions from the user's own options and cases.

## 2. Fact sheet per option (same fields for each)

- Diagram of relationships at signature (political and commercial)
- Headline indicators: staff required, minimum set-up time, risk (in bid and in life), each with its basis
- Purpose of the relationship; your commitments; form of the arrangements
- Liability (yours, suppliers'); suppliers; procurement process; revenue flows
- Risks in bid and in life; clearance required; lessons from precedents
- Variants (e.g. a "pass-through" version of a model) with the legal points to check

## 3. Governance

Governance should match the chosen option: lower-risk options get a lighter route; high-risk, high-investment ones go through the full business-case process. Show the pathway as gateways, each with a template and a decision, and say at which gateway the option is confirmed.

## 4. Adding numbers (optional)

**Always offer this, once the tree's questions and red lines are agreed**, in a line such as:

> *This tree picks a model by asking yes/no questions; it doesn't need any numbers. If you can put rough odds on how often each situation comes up, or on what each model is likely to be worth, I can add those to show the expected value and risk of each route and what's worth finding out first. Want me to?*

If the user says no, carry on: the tree works without numbers. If yes, proceed as below.

When the branches can carry rough probabilities and values (how likely is each client need, what is each model worth to us?), turn the tree into a quantified one: `methods/quantified-tree.md`. That covers folding back to expected values, the value of flexibility, value of information and risk attitude, with `scripts/uncertainty.py tree` to do the arithmetic.

## 5. Outputs

- **Options comparison table**: model, examples, suppliers, procurement, who wins work, liability, your role, ordered by resource.
- **The tree**: questions on the left in the order they're answered, options on the right, yes/no paths, red lines marked, a "further considerations" box, a key.
- **Staged versions** showing what's decided by each milestone.
- **Push and pull table** for the judgement call.
- **Fact sheet per option**.
- **Cross-cutting risks** that apply whatever the option.

## Checklist
- [quick] Options described with the same fact sheet each
- [quick] Distinguishing questions ordered by when the answer becomes available
- [quick] Red lines identified; options that are your red lines dropped at the start
- [quick] User offered the option of adding probabilities and values (§4)
- [standard] Push and pull factors set out for the judgement call, with written definitions for each rating
- [standard] Tree back-tested on real past cases
- [standard] Expected transitions shown as a route with triggers
- [full] Tree quantified where estimates exist (`methods/quantified-tree.md`)
