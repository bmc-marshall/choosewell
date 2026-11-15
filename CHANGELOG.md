# Changelog

Dates are when a version was released. Guidance summaries (Green Book, US federal) are checked at each release; the "as of" date is in each rulebook file.

## 1.0.0 (2026-11-10)

First public release.
- Three questions (what are you deciding; what rules and how much rigour; how will you assess) and ten steps, each with its own reference file, safeguards and checklist.
- Assessment methods: threshold filter, scored criteria with swing weights, red/amber/green against success factors, impact × availability and Eisenhower matrices, decision tree for matching, quantified decision tree, pros and cons, responsibility mapping.
- Rulebooks: UK Green Book (2026 edition), US federal (OMB A-94/A-4, GAO), and a general method for everyone else.
- Scripts: appraisal workbook and roll-ups (`appraise.py`); quantified trees, value of information and Bayes updating (`uncertainty.py`); tailored checklists (`checklist.py`); consistency checks; tests.
- Offline guide in Word, rebuilt from `scripts/build_guide.js`.
- Activity prioritisation and naming are supported lightly and flagged to users as such.

Before release, the skill was run on 13 realistic requests (operating model for a business case, partner screening, regional expansion with data, contracting model per deal, pilot before launch, settle or go to trial, campaign spend, activity prioritisation, naming, a US federal analysis of alternatives, a quick vendor choice, an out-of-scope request, and a group joining part-way). Fixes from that testing:
- New type of choice for go/no-go, timing and how-much decisions (`choices/whether.md`), with checks for common shapes (pilots, disputes, bids, spend levels, waiting).
- Answers lead with the recommendation; outputs scale with depth; a user's deadline can set the depth; worked examples are flagged as patterns, not answers.
- `appraise.py rollup`: fixed wrong ratings when setup/ongoing phases are used; unrated options show as "not rated", not amber; blank scores are left out, not counted as zero; pass/fail gates; text weights tolerated; dominance and one-point flips for scored criteria; best case if unknowns resolve well; formulas read as values.
- `appraise.py`: private scoring (`init --scorers`, `spread`), method tabs (`init --methods`), CSV import (`init --scores`), a `matrix` command, threshold filters that treat unknowns as provisional and list near-misses, top-k stability and random-weight tests, an audit that handles blank ratings and missing tabs.
- `uncertainty.py`: fixed the risk-tolerance comparison; break-evens by bisection; tornado on the lead over the runner-up; risk profiles for every option; tie warnings; chance of a loss above a threshold; inputs with ranges and sources; zero-probability outcomes ignored.
- `checklist.py`: reads the workbook's fields exactly; items apply only to the methods chosen; paper layout with owner, date and notes columns.
- A second round of three re-tests fixed: a crash in the risk-tolerance check when one option is a sure thing; a broken table; quick-depth checks that needed a workbook; criteria for software and service choices; country-dependent prices; threshold near-misses ranked by how close they are, and the filter's status handed to the workbook; warnings for criteria that move together or trade off, and for two-criterion rankings.
- US federal rulebook: GAO-20-195G Appendix XI (superseding GAO-16-22), A-11 Capital Programming Guide, discount-rate choice for system replacements, a GAO crosswalk.

---

## Before 1.0: building the skill (reconstructed)

The rounds below happened in conversation before Choosewell was on GitHub, so they have no commits or tags. They're numbered retroactively, in the order they happened as best it can be reconstructed; dates are approximate (early November 2026). Each round came from the author's own options appraisals and teaching materials, generalised and anonymised.

## 0.6.0: Ready to share

- Two licences: MIT for the scripts, CC BY 4.0 for the written method and guide, with a notice crediting HM Treasury, OMB and GAO material.
- `requirements.txt`, a consistency check that the skill files, guide and checklists agree, automated tests, and a GitHub workflow to run them.
- Changelog and contributing guide; worked examples confirmed as invented or anonymised composites.

## 0.5.0: Renamed Choosewell

- Renamed from the working name "choicewell" to **Choosewell**; the offline "crib sheet" became `choosewell-guide.docx`, the guide.

## 0.4.0: Uncertainty and the value of information

- Built from the author's decision-analysis teaching materials (lecture deck, assignments, spreadsheet models and a case study).
- Quantified decision trees with probability-weighted payoffs, option value, value of information (EVPI, EVSI), Bayesian updating, sensitivity and break-evens, risk tolerance and certainty equivalents.
- New script `uncertainty.py` and method file `methods/quantified-tree.md`.

## 0.3.0: Three questions, ten steps

- Restructured around three questions (what are you deciding; what rules and how much rigour; how will you assess) and ten steps (frame, rules and rigour, long list, choose method, criteria, evidence, assess, test, decide, check and present). Each step has its own file, says when it can be skipped, carries its safeguards and ends with a checklist.
- Files regrouped as `choices/`, `methods/`, `rulebooks/`, `topics/` and `presenting/`, with a glossary of plain terms; five general modules folded into the steps.
- Hand-off to Slidewell to build the deck, offered rather than automatic.
- Lighter areas (activity prioritisation and naming) flagged to users, in the skill, the reference files and the guide.

## 0.2.0: More methods and decision types

- Drawn from the author's other options-evaluation decks: threshold filters, scored criteria, red/amber/green against critical success factors, impact × availability and Eisenhower matrices, decision trees for matching, pros and cons, responsibility mapping.
- Types of choice: scope, what, where, structure (overall or case by case), who, and smaller design choices.
- Rulebooks for the UK Green Book and US federal approaches, and a general method; topics on comparators, legal and regulatory questions, and engagement.
- First scripts (`appraise.py` for the workbook and roll-ups, `checklist.py`) and the offline guide in Word.

## 0.1.0: First draft

- Started from one real operating-model appraisal based on HM Treasury's Green Book: the general process, design principles, a long list of options rolled up into categories, criteria and sub-questions, red/amber/green ratings and the working-group conversations behind them, and legal considerations.
