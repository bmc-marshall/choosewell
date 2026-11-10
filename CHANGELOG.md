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
