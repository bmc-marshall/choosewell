# Storylines, the workbook, and the slidewell hand-off

## 1. The workbook (source of truth)

`scripts/appraise.py init --choice <type of choice> --methods <method,...> --out appraisal.xlsx` creates it (add `--scorers` for private scoring, `--scores file.csv` to import existing scores). Standard tabs:

| Tab | Columns |
|---|---|
| Frame | one row per field: decision, decision_maker, decision_date, in_scope, out_of_scope, what_happens_next, type_of_choice, methods, rulebook, depth, steps_skipped (step numbers only), assumptions. Fill the existing rows; don't add duplicates |
| Principles | type (process/outcome), principle, issue addressed, implication |
| Options | id, name, family, source, description, BAU flag, knock-out (y/n), knock-out reason |
| Criteria | id, name, question, dimension (standard/local), weight (a number; blank or text counts as 1 until agreed), scale (rag or score), max_score, level definitions, stage (gate = pass/fail, main = scored) |
| Indicators | criterion id, indicator id, statement (✓ = favourable), deal-breaker (y/n) |
| Ratings | option id, criterion or indicator id, phase (setup/ongoing), suggested, agreed, override reason, evidence, source, confidence, drafted (y/n) |
| Claims | claim id, option, claim, type (fact/claim/inference/estimate), source, date (or 'undated'), confidence, checked, used in |
| Open questions | id, question, option, criterion, owner, channel, due, would change |
| Decisions log | date, decision, agreed by, evidence, replaces |
| Results | (written by `rollup`): criterion ratings, overall, rank/tier, marginal flag, checks |

Method tabs added by `--methods`: decision-tree (Tree questions, Red lines, Push-pull, Fact sheets, Back-test), quantified-tree (Tree inputs), matrix (Activities), pros-and-cons (Pros and cons); `--scorers` adds Scores by person (then `appraise.py spread`). Not every type of choice uses every tab: a threshold filter uses Options + a data table + Results. Type weights rather than calculating them in formulas, or open and save the workbook in Excel before running the scripts so calculated values are stored.

Where the environment offers a shared spreadsheet artifact, use it so the group can edit; keep the same tabs.

## 2. Storyline format

Draft the storyline in the conversation before writing slide content. Use the same structure slidewell expects, so the hand-off is direct:

```
GOVERNING MESSAGE
<one sentence: the answer, recommendation, or request>

OPENING (SCQA)
S: <undisputed context>   C: <what's changed / the problem>
Q: <the question this deck answers>   A: <the governing message>

STORYLINE
Section 1: <section name as a claim or clear label>
  1. <headline>  | proves via: <pattern from slide-patterns.md + evidence> | job: present / discuss / decide
  2. …
Section 2: …
Appendix: <profiles, indicator matrices, comparators, evidence base>

BUILDING BLOCKS: e.g. exec summary, assessment criteria, long list → short list, options matrix (labelled RAG), recommendation, risks, decisions needed
ASSUMPTIONS / GAPS: drafted ratings awaiting group review; open questions; unverified data
```

Headlines are full-sentence claims ("Four options remain viable after assessment against seven critical success factors"), not labels ("Options assessment").

## 3. Default storylines by type of choice

**How storylines and slide patterns relate.** A storyline is the argument: which points to make, in what order, to reach the recommendation. A slide pattern (`presenting/slide-patterns.md`) is the building block for one point: what the slide contains and how it's arranged. Each line of a storyline names the pattern that carries it. The guide shows each default storyline as a table of slide, message and pattern.

Adapt; drop what the user doesn't need.

**Scope**: Why scope matters now → the facets and where the line sits → rationale and what's still under discussion → what would change it.

**Where**: Exec summary → the question and approach → criteria → funnel or grid → shortlist (map) → regulatory comparison → place profiles (appendix if many) → recommendation and next steps.

**What**: Exec summary → method (map, then prioritise) → value chain → who does what today → issues and actions → narrowing → scoring logic → matrix and priorities → scenarios and roadmap → implications for existing organisations.

**Structure**: Exec summary → purpose and method → principles → three-layer framing and scope → long list → criteria and roll-up rules → short list (summary matrix) → drop-out tracker → preferred option and rationale vs alternatives (with residual risks) → legal considerations → sub-choices (team, funding, name) → next steps. Appendix: indicator matrices per CSF, comparators, key differences between forms, evidence base.

**Structure by situation**: Definition and scope → assumptions and principles → models compared → the decision tree (and staged versions) → push/pull factors → model fact sheets → cross-cutting risks → legal and procurement → governance pathway → recommendations and asks.

**Who**: Exec summary (results, approach, observations) → long list by source → methodology → top tier (ranked table, pros/cons) → others → needs further research → excluded → profiles.

**Design choices**: one slide per choice (option cards or pros/cons) feeding an "answer on a page".

**Add to any storyline, as depth requires**: a "How we worked" slide (methods used in plain language, the frameworks and guidance they come from, and which choices were our own judgement; see `presenting/writing.md` §5); a robustness section (switching values or tornado; scenarios/regret where used); "what we still need to know" (information-value table); and, for hard-to-reverse choices, the pathway and triggers. Sensitivity detail can live in the appendix, but the headline ("the recommendation holds unless…") belongs in the main story.

## 4. Slide content

After the storyline is agreed, write the content per slide: headline, body content (table cells, bullets, ratings, labels), footnotes, sources for the notes, and the pattern name. Mark drafted content **[Drafted - for group review]**. Keep numbers traceable to the workbook.

## 5. Hand-off to slidewell

Offer it; don't do it automatically: *"The content is ready. Want me to build it as a deck with slidewell?"*

If yes and slidewell is available:
- Give slidewell the storyline above as its storyline proposal (deck type: **options appraisal**, or a mix), and the slide content and workbook as its material.
- Point to the pattern names so slidewell can choose matching layouts (e.g. "labelled RAG matrix", "criteria tick table", "pros/cons per option", "funnel", "profile template").
- Let slidewell run its own intake (audience, read vs presented, length, brand), theme and QA. Choosewell doesn't impose a look; source decks are structural references only.

If slidewell isn't available, offer the environment's own slide capability, a .pptx via any available presentation skill, or the content as a document.
