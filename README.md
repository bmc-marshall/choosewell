# Choosewell

**Options appraisal with Claude: shortlist, score and test options for organisational decisions, and produce recommendations that stand up to scrutiny.**

Choosewell guides a person or a working group through a structured choice. It covers what's in scope, where to work, how to organise (overall or case by case), who to work with, and smaller design choices such as team set-up, funding or hosting. It recommends a method for the situation, explains each methodological choice in plain language, keeps the group's judgement in charge, checks its own work, and produces the analysis and storyline behind a recommendation.

It was built from real options appraisals (operating models, partner screening, geographic prioritisation, contracting models) and from decision-analysis practice, generalised and anonymised.

## Methods included

- **Screening:** threshold filters, knock-outs, RAG (red/amber/green) ratings against critical success factors
- **Scoring:** scored criteria with written score definitions, swing weighting, pros and cons with option labels, impact × availability and Eisenhower matrices
- **Matching:** decision trees that pick the right model for each situation, with red lines and push/pull factors
- **Testing:** sensitivity analysis, switching values, dominance, tornado charts, random-weight tests, top-k stability, value-for-money frontier
- **Uncertainty:** quantified decision trees and expected value, risk profiles, value of information (EVPI, EVSI), Bayesian updating, option value, real options, risk tolerance and certainty equivalents, scenarios and minimax regret
- **Judgement and bias:** private scoring before discussion, claims log, pre-mortems, adverse-consequence analysis, decision-quality check, reference-class forecasting
- **Rulebooks:** compatible with the UK Green Book (five-case model, critical success factors, MCDA guidance) and US federal approaches (OMB Circular A-94, GAO analysis of alternatives), plus a general method for everyone else

> Not legal, financial or regulatory advice. Choosewell identifies where advice is needed and drafts the questions to ask.

## What it does

![Tree 1 in the offline guide](docs/images/guide-tree1.png)

It works through **three questions** and **ten steps**:

- **Tree 1: What are you deciding?** Scope → what → where → structure (overall or by situation) → who → design choices. Start at the top; stop at the first question you can't yet answer. Single go/no-go, timing or how-much decisions (launch, pilot, settle, bid, spend) have their own route.
- **Tree 2: What rules, and how much rigour?** UK central government → the Green Book; US federal → OMB and GAO guidance; everyone else → a general method drawing on both. Reversibility and stakes set the depth (quick, standard or full).
- **Tree 3: How will you assess the options?** Threshold filter, scored criteria with swing weights, red/amber/green against success factors, pros and cons, impact × availability or Eisenhower matrices, a decision tree for matching options to situations, and a **quantified decision tree** when a few uncertain events or staged choices drive the result.
- **Steps 1–10**: frame, rules and rigour, long list, choose a method, criteria, evidence, assess, test, decide, check and present. Each step says when you can skip it, and carries its own safeguards: a claims log for every fact, drafted content flagged until the group agrees it, independent scoring before discussion, sensitivity and break-even tests, a pre-mortem, an audit, and independent review for big decisions.

![A quantified decision tree from the guide](docs/images/quantified-tree-example.png)

**What you get**
- A working spreadsheet: options, criteria, ratings, claims, open questions and a decisions log.
- Results with checks: consistency, dominance, switching values, tornado charts, value of information, risk profiles.
- A storyline and slide-by-slide content, with an offer to format it using the slidewell skill if you have it.
- A checklist tailored to your choices (Word or Markdown).
- An offline guide in Word, so a group can run the whole method on paper.

**Where it's light.** Activity prioritisation and naming are included as inputs to the other choices, not as standalone tools; the skill tells users this. The default roll-up rules for red/amber/green ratings were calibrated on one working group's ratings, and the skill invites each group to agree its own before scoring.

## Install

**Claude apps (claude.ai, desktop):** download `choosewell.skill` from the latest release and upload it in your skills settings. Start a new conversation afterwards.

**Claude Code:** copy this folder to `~/.claude/skills/choosewell` (or your project's `.claude/skills/`).

The scripts need Python 3.9+ with the packages in `requirements.txt`; Claude installs them when needed.

## Try it

You don't need to name the skill. Ask the way you normally would:

- "We're setting up a new unit and need to decide its operating model and legal form for a business case. There'll be a working group of eight."
- "Here's data on 15 regions. We can expand into two or three next year. Which should we pick?"
- "Is a £60k pilot worth running before a national launch? Success is worth about £2m, failure loses £800k, and maybe a 35% chance it takes off."
- "We've scored six options on five criteria. The top one feels close. How robust is it?"
- "We'll run this on paper in the meeting. Can I have a checklist and the guide?"

![A step page from the offline guide](docs/images/guide-step5.png)

## What's inside

```
choosewell/
├── SKILL.md                    entry point: the three trees, the ten steps, explaining choices, hand-off
├── references/
│   ├── steps/                  01-frame … 10-check-and-present (one file per step, each with a checklist)
│   ├── choices/                scope, what, where, structure, structure-by-situation, who, design-choices, whether
│   ├── methods/                threshold-filter, scored-criteria, rag-success-factors, matrix, decision-tree,
│   │                           quantified-tree, pros-and-cons, responsibility-mapping
│   ├── rulebooks/              green-book (2026 edition), us-federal, general-method
│   ├── topics/                 comparators, legal-regulatory, engagement
│   ├── presenting/             writing, storylines (incl. slidewell hand-off), slide-patterns, sources-of-methods
│   └── glossary.md             plain terms used throughout, with technical equivalents
├── assets/
│   ├── choosewell-guide.docx   the offline guide
│   ├── guide/                  diagram sources (.mmd) and images for the guide
│   └── examples/               starter models: staged programme, pilot value, which risky step first,
│                               learn then decide, tree flip, risk attitude
├── scripts/
│   ├── appraise.py             workbook, roll-ups, checks, sensitivity, payoff tables, audit
│   ├── uncertainty.py          quantified decision trees, value of information, Bayes updating
│   ├── checklist.py            tailored checklist built from the files' Checklist sections
│   ├── check_consistency.py    checks the skill, guide and checklists agree
│   └── build_guide.js          rebuilds the offline guide (npm install docx)
└── tests/                      unit tests for the scripts
```

## Quality

- `python3 scripts/check_consistency.py` checks that every file reference resolves, every step and method appears in the guide and checklist, and every checklist item is tagged with a depth.
- `python3 -m unittest discover -s tests` checks the scripts' arithmetic against worked answers (expected values, break-evens, value of information, certainty equivalents, roll-ups).
- Both run on every push (`.github/workflows/test.yml`).
- The skill was tested on 13 realistic requests across every type of choice, including one it should decline; what that found and fixed is in `CHANGELOG.md`.

## Keeping it current

The UK and US rulebooks summarise official guidance as of November 2026. Each file says when it was last checked, and the skill tells Claude to check for later changes before relying on them. See `CHANGELOG.md` for what's changed.

## Contributing

Corrections, new worked examples and translations of the guide are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md): in particular, no client or confidential material.

## Licence and credits

Copyright (c) 2026 Benjamin Marshall.

- Code (`scripts/`, `tests/`): [MIT](LICENSE).
- Written method, guide and examples: [CC BY 4.0](LICENSE-docs.md).
- Contains public sector information licensed under the Open Government Licence v3.0 (HM Treasury Green Book and supplementary guidance). See [NOTICE.md](NOTICE.md) for this and other credits.
- Choosewell is not endorsed by HM Treasury, OMB, GAO or any organisation whose methods it describes.
