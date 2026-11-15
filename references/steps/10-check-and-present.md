# Step 10: Check and present

Check the work before anyone else sees it, then present it as a clear argument rather than a data dump.

| | |
|---|---|
| Skip if | Never |
| You'll end up with | A checked write-up or deck someone else can follow and verify, and an offer to format it with slidewell |
| Next | Done; the workbook is the record |

## 10.1 Check before anything is delivered

AI-drafted analysis can contain errors that read as confidently as facts. No instruction removes that risk; what reduces it is checking claims before they reach the user and keeping uncertainty visible.

1. **Coverage**: `scripts/appraise.py audit` lists drafted ratings without evidence or source, overrides without reasons, and unsourced, unchecked or undated claims. Fix or label every item.
2. **Numbers**: every number in the output comes from the workbook or the scripts, never typed from memory. Re-derive totals, averages, counts and percentages and compare with the text.
3. **Key sources**: for the claims that drive the result (the top options, any knock-out, any deal-breaker), re-open the source and confirm it says what the claims log says. Never cite a source you haven't read.
4. **Currency**: guidance, regulation, leaders, prices and political positions change; re-check anything volatile and write "as of [date]".
5. **Consistency**: the same fact has the same value everywhere (workbook, profiles, slides, notes).
6. **Labels**: drafted content is still marked; inferences and estimates are labelled.
7. **Confidence profile**: if the recommendation rests on low-confidence ratings, the headline says so.
8. **Independent review** for consequential or hard-to-reverse decisions: someone (or a separate agent, given only the outputs, the sources and this list) who didn't produce the work checks that key claims match sources, numbers re-compute, no conclusion is stronger than the evidence, uncertainty is visible, and nothing obvious is missing. Record what changed.

A correctly flagged gap is good work; an unsupported confident claim is a defect. Say so on the "how we worked" slide, so the incentive is visible.

## 10.2 Keep uncertainty visible in the outputs

Confidence beside ratings (not buried in notes); ranges rather than single figures for uncertain costs, times and benefits; provisional flags; "best case if it resolves well" for screened lists; switching values and "the recommendation holds unless…" in the main story; open questions with owners; sources on every profile and evidence slide.

## 10.3 Present

1. Follow `presenting/writing.md` for every word the user sees.
2. Draft the storyline for the type of choice (`presenting/storylines.md`), with each slide's pattern (`presenting/slide-patterns.md`), and agree it before writing slide content.
3. Write the slide-by-slide content, including a "how we worked" section (`presenting/sources-of-methods.md`).
4. Offer to format it: *"Want me to turn this into a deck with slidewell?"* Hand-off details are in `presenting/storylines.md` §5. Don't build slides automatically, and don't copy the look of any source deck.

## Checklist
- [quick] Every number re-derived (from the workbook, the scripts or a fresh calculation) and matches the text
- [quick] Every fact in the output sourced, dated where it can change, and labelled if drafted or estimated
- [standard] Workbook audit run (`appraise.py audit`); unsourced or unlabelled items fixed or labelled
- [standard] Sources re-opened for the top options, knock-outs and deal-breakers
- [standard] Guidance and volatile facts checked as current, with "as of" dates
- [full] Independent review by someone who didn't produce the work
- [quick] Uncertainty visible: confidence, ranges, provisional flags, switching values, open questions
- [quick] If presenting: storyline agreed (one-sentence answer, headline sequence, pattern per slide)
- [quick] "How we worked" section included
- [quick] If presenting: format for the deck chosen (slidewell or another)
