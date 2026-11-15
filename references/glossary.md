# Glossary: one vocabulary across the skill, guide, checklist and outputs

Use the plain term in everything a person reads. Where a technical term is useful (for looking things up, or because the rulebook uses it), give it once in brackets on first use and then use the plain term. File names follow the plain terms.

| Plain term (use this) | Technical or alternative term | Meaning | Where it lives |
|---|---|---|---|
| Type of choice | Archetype | The kind of decision: scope, what, where, structure, structure by situation, who, design choices, or whether/when/how much | `choices/` |
| Whether, when or how much | Go/no-go decision | A single launch, settle, bid, invest-or-wait or spend-level decision | `choices/whether.md` |
| Method | Mechanism, appraisal technique | How options are assessed: threshold filter, scored criteria, red/amber/green against success factors, matrix, decision tree, pros and cons, responsibility mapping | `methods/` |
| Rulebook | Method base, appraisal guidance | The guidance that governs the appraisal: Green Book, US federal, or the general method | `rulebooks/` |
| Step | Stage | One of the ten steps of an appraisal | `steps/` |
| Tree 1, 2, 3 | | What are you deciding? / What rules and how much rigour? / How will you assess the options? | SKILL.md; the guide |
| Depth | Proportionality level | Quick, standard or full | `steps/02-rules-and-rigour.md` |
| Defensible | Audit-ready | Must withstand scrutiny: pass/fail tests, decisions log, sources for everything | `steps/02-rules-and-rigour.md` |
| Business as usual | BAU, status quo, counterfactual | What happens if nothing changes; the benchmark | `steps/03-long-list.md` |
| Long list / short list | | All reasonable options / the few compared in detail | Steps 3 and 8 |
| Knock-out | Must, gate, exclusion criterion | A condition that excludes an option before any scoring | `steps/05-criteria.md` §5.1 |
| Deal-breaker | Critical indicator | A statement that, if answered "no", fails a whole success factor | `steps/05-criteria.md` §5.1 |
| Success factor | Critical success factor (CSF) | A test every acceptable option must pass | `methods/rag-success-factors.md` |
| Statement | Indicator, sub-question | A short yes/no test under a criterion or success factor, worded so "yes" is good | `steps/05-criteria.md` §5.2 |
| Score definitions | Anchors, level descriptors | What earns each score on a criterion | `steps/05-criteria.md` §5.2 |
| Swing weighting | | Weights set by how much the worst-to-best difference on each criterion matters | `steps/05-criteria.md` §5.3 |
| Suggested / agreed score | Calculated / final rating | What the rules give / what the group decides | `steps/07-assess.md` §7.4 |
| Override | | Agreeing a score different from the suggested one, with a reason | `steps/07-assess.md` §7.4 |
| Marginal option | | One whose overall result changes if an uncertain score moves one step | `steps/08-test.md` §8.2 |
| Switching value | | How far a score, weight or estimate must move to change the top choice | `steps/08-test.md` §8.2 |
| Dominated option | | One that another option equals or beats on every criterion | `steps/08-test.md` §8.1 |
| Value for money view | Efficient frontier | Options where nothing else is both cheaper and better | `steps/08-test.md`; `scripts/appraise.py sensitivity` |
| Value of information | EVPI (expected value of perfect information) | How much it's worth knowing something before deciding | `steps/08-test.md` §8.3 |
| Regret | | How much worse an option does than the best option in the same scenario | `steps/08-test.md` §8.4 |
| Good enough everywhere | Satisficing | Meets an agreed minimum in all (or most) scenarios | `steps/08-test.md` §8.4 |
| Break-even probability | Probability switching value | The likelihood at which two options have equal expected value | `steps/08-test.md` §8.4 |
| Expected value | Expected monetary value (EMV) | The probability-weighted average result: each outcome times its probability, added up | `methods/quantified-tree.md` §3 |
| Quantified decision tree | Decision tree with payoffs | Decisions and uncertain events in time order, with probabilities and values, worked back to the best strategy | `methods/quantified-tree.md` |
| Folding back | Rolling back | Working a tree from right to left: averages at chance points, best branch at decisions | `methods/quantified-tree.md` §3 |
| Strategy | Contingency plan, policy | What to do now and at each later decision, depending on what's happened | `methods/quantified-tree.md` §3 |
| Risk profile | Outcome distribution | Every possible result of an option with its probability | `methods/quantified-tree.md` §3 |
| Break-even value | Switching value, indifference point | The value of an input at which the best option changes | `methods/quantified-tree.md` §6 |
| Prior / updated probability | Prior / posterior | The probability before and after new information | `methods/quantified-tree.md` §7 |
| Track record (of a test) | Likelihood, sensitivity and specificity | How often a test gives each result when the truth is one way or the other | `methods/quantified-tree.md` §7 |
| Tree flip | Bayes' rule | Turning a test's track record and the prior into updated probabilities | `methods/quantified-tree.md` §7 |
| Value of a test or study | EVSI (expected value of sample information) | How much better the decision is, on average, with the test's result than without it | `methods/quantified-tree.md` §7 |
| Risk tolerance | R in exponential utility | The size of 50–50 gamble (win R, lose R/2) someone would just accept | `methods/quantified-tree.md` §9 |
| Certainty equivalent | | The sure amount someone would accept instead of a risky option | `methods/quantified-tree.md` §9 |
| Easy extras | (often called quick wins) | Low-impact items that are easy to do now; not to be confused with priorities | `methods/matrix.md` |
| Gate | Pass/fail criterion | A criterion every option must pass; failing it removes the option before scoring | `steps/05-criteria.md` §5.1 |
| Keeping options open | Option value, real options | The value of being able to defer, stage, pilot, expand, switch or exit | `steps/09-decide.md` §9.1 |
| Route with triggers | Adaptive pathway | A planned sequence of options with agreed switch points | `steps/09-decide.md` §9.2 |
| Pre-mortem | | Imagining a decision has failed to find the likely reasons in advance | `steps/09-decide.md` §9.3 |
| Claims log | Claim ledger, evidence register | One row per fact: type, source, date, confidence, checked | `steps/06-evidence.md` §6.2 |
| Drafted | | Content the skill suggested that the group hasn't yet confirmed | `steps/06-evidence.md` §6.3 |
| Weighted analysis | Multi-criteria decision analysis (MCDA) | Formal weighted scoring | `rulebooks/green-book.md` §5a |
| Costed comparison | Cost-benefit / cost-effectiveness analysis, NPV | Comparing options in money terms | Rulebooks |
| Storyline | | The argument: which points, in what order | `presenting/storylines.md` |
| Slide pattern | | The standard layout for making one point | `presenting/slide-patterns.md` |
| Workbook | Appraisal spreadsheet | The single source of truth for the appraisal | `scripts/appraise.py init` |
