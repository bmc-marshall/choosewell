# Method: scored criteria (0–3, 1–3 or stars) with knock-outs

Use to rank a list of organisations, places or segments on a few criteria (typically 3–5) where judgement matters and the aim is a prioritised list, not a pass/fail filter. It is the default for **Who** (partner screening) and for **Where** when candidates are few.

## Steps

1. **Knock-outs first.** Apply agreed exclusion conditions (e.g. disqualifying safety record, sanctions, serious unresolved ethics findings, existing exclusive arrangements, out of scope). Excluded items are listed with the reason, not scored.
2. **Criteria with written levels.** For each criterion: the question, an example of what to look for, and a definition of every score level (`steps/05-criteria.md`). Without anchors, two scorers' "2" means different things.
3. **Score with evidence and confidence.** Each score has 1–3 evidence bullets, a source, and a confidence level (high / medium / low). Unknown → confidence low, score left blank or marked "X", next step "find out more". **Don't dock points for missing information**: it mixes "weak" and "unknown" and buries promising-but-obscure candidates.
4. **Aggregate.** Weighted sum. **Recommend swing weights** (`steps/05-criteria.md`), agreed before scoring; the group may choose equal weights instead (simplest; fine for 3–4 criteria in a screen), and the method-transparency note should say which and why. With equal weights, a simple total works (e.g. three criteria × 0–3 = /9). Stars: show 1–3 stars per criterion; if a total is used to select, say so. Keep **cost** out of the benefit score where value is to be compared with cost; show value against cost instead. For UK public business cases, see the compliance caution in `rulebooks/green-book.md` §5a.
5. **Rank and tier.** Sort by total, then by the most important criterion, then by judgement with the reason recorded. Tier with stated cut-offs (e.g. front-runners, worth exploring, others, needs further research, excluded). Cut-offs can be judgement, but show the reasoning ("a natural break between 8 and 7").
6. **Segment view.** If candidates fall into types (e.g. premixers vs ingredient suppliers vs flavour houses; corporates vs SMEs), tag every row with its type and show rankings within each type as well as overall, so a strong small player isn't buried under large ones.
7. **Check.** Spread per criterion (does it separate candidates?), consistency (similar candidates scored similarly?), dominance (any candidate beaten on every criterion?), sensitivity (would a one-point change on a low-confidence score change the tier? how far would a weight have to move to change the top few? `scripts/appraise.py sensitivity`).
8. **Prioritise follow-up** by value of information: outreach goes first to candidates whose unknowns could move them into the top tier (`steps/08-test.md` §8.3).
9. **Before committing** to a partner or supplier (a harder-to-reverse step), run adverse consequences on the top two or three and a short pre-mortem on the leader.

## Variants

- **Four-level desirability** (undesirable / suboptimal / desirable / optimal) across a few dimensions (e.g. competition, product fit, market size) for evaluating segments: show as a dot path per option.
- **Stars grid** (1–3 stars per criterion for 5–8 options, e.g. locations on convenience, buyer concentration, cost): recommend a selection; where two options win on different criteria, recommend both with the reason for each ("A for lower operating costs; B for existing client presence") so the decision-maker chooses the priority.

## Outputs

- **Methodology slide**: (1) research sources, (2) criteria scored out of N with their questions, (3) qualitative factors considered alongside (values/ethics, commercial skills, timelines).
- **Ranked summary table**: type tag, name, key facts (HQ, revenue, segments), total, per-criterion scores; tier separators; note on knock-outs and unknowns.
- **Pros/cons of the top tier**: one line each.
- **Others / needs further research**: same table, scores "?" where unknown, in priority order, with what would change their priority.
- **One-page profile per candidate** (`presenting/slide-patterns.md`): facts box, type and badges (e.g. on an approved list), scores, evidence by criterion plus "other" (reputation, notable facts), nice-to-haves, next steps; highlights and sources in the notes.
- **Excluded list** with reasons.

## Checklist
- [quick] Knock-outs applied before scoring; excluded list with reasons
- [quick] Missing information → low confidence and 'best case if resolved', not docked points
- [quick] Ranked table with tiers and stated cut-offs; ties broken by stated rule
- [standard][who,where] Segment/type view as well as overall ranking
- [standard] Value-for-cost frontier if cost matters
- [standard][who,where] One-page profiles for the top tier (consistent fields; sources in notes)
