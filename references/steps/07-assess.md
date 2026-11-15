# Step 7: Assess the options

Apply the method. If a group scores, how the session runs matters as much as the criteria.

| | |
|---|---|
| Skip if | Scores are already agreed |
| You'll end up with | Suggested and agreed scores for every option, with reasons for any judgement calls (workbook Ratings and Decisions log tabs) |
| Next | Step 8 |

## 7.1 Apply the method

Follow the method file. Apply knock-outs first and list the options removed. Methods that don't score are assessed differently: a matching decision tree is walked through with real past cases (does it pick the model actually used, and if not, why?); a quantified tree is worked out (`scripts/uncertainty.py tree`); pros and cons are reviewed by the group against the deciding criterion. Combine scores with the rules agreed in Step 5 (`scripts/appraise.py rollup` for success-factor ratings or weighted scores).

For private scoring, `scripts/appraise.py init --scorers` adds a Scores by person tab; `appraise.py spread --suggest` then shows the spread for each option and criterion, flags wide disagreements, and writes the median as the suggested score for the group to discuss.

## 7.2 Running a group scoring session

Group judgement suffers from noise (different people, or the same person on different days, rating the same evidence differently) and anchoring (the first or most senior voice sets the answer). This session design follows the "decision hygiene" research in Kahneman, Sibony and Sunstein's *Noise* (2021):

1. **Before**: agree criteria, score definitions and combining rules; circulate an evidence pack per option. Consider showing the skill's drafted ratings only after people have scored, so the draft doesn't anchor them.
2. **Private first**: each person scores alone, one criterion at a time across all options (not option by option; that's what keeps scoring consistent).
3. **Reveal the spread and discuss** differences on the evidence, not on seniority. Compare with how similar options performed elsewhere where that's known.
4. **Score again.** The agreed score comes from the second round.
5. **Delay the overall judgement** until every criterion has been reviewed.
6. **Calibrate** if possible by scoring one or two well-understood options first.

Wide disagreement between scorers is a signal: the score definition is unclear or the evidence thin. Fix the definition or log an open question rather than averaging it away.

## 7.3 What the arguments are usually about

Prepare for these; they're the commonest challenges in real reviews:
- **Inconsistency** ("why is A green when B is amber?"): pre-empt with the consistency check (Step 8.1).
- **Formal evidence vs opinion**: a published plan or legal view overturns a judgement; record which a score rests on.
- **The wrong criterion**: move the issue to where it belongs rather than counting it twice.
- **Precedent** ("X already does this, so how can it be red?"): test ratings against real examples.
- **Mitigations**: record the score with and without the mitigation.
- **Unknowns**: turn them into open questions, not ambers.

## 7.4 Overrides and the decisions log

The method produces a **suggested** score; the group sets the **agreed** one. Record both.

| Override | Needs |
|---|---|
| One step (e.g. amber to green) | A sentence of reasoning |
| Two steps (red to green) | Evidence: a document, legal view or precedent |
| Repeatedly in one direction | A change to the rules or weights, made openly |

Keep a decisions log (date, decision, agreed by, evidence, what it replaced). It's the audit trail for anyone reviewing the work or joining later. Show the number of overrides on the "how we worked" slide: a handful is healthy; dozens means the rules don't reflect what the group values.

## Checklist
- [quick] Knock-outs applied; removed options listed with reasons
- [standard][scores,group] Group scored privately first, one criterion at a time; spread revealed; discussed; re-scored
- [quick][scores] Agreed score recorded beside the suggested one, with a reason for any override
- [standard][scores,group] Wide disagreements treated as unclear definitions or thin evidence, not averaged
- [quick] Decisions log kept
