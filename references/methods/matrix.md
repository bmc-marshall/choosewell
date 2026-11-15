# Method: two-axis prioritisation matrix

Use to sequence many activities, initiatives or opportunities. Two variants:

- **Bottom-up: impact × availability** ("what we *can* do"): impact from stakeholder evidence, availability from the team's assessment of how feasible it is to do now.
- **Top-down: Eisenhower, urgency × importance** ("what we *must* do"): for mandated or deadline-driven work.

Often used after responsibility mapping (`methods/responsibility-mapping.md`) in the **What** type of choice.

> **Supporting, not core.** Choosewell uses these matrices to sequence work feeding a wider choice. For standalone prioritisation, flag that it handles this lightly (see `choices/what.md`).

## Impact × availability

**Impact (1–3)**, from evidence, ideally countable. Example rules (agree your own):
- Number of independent mentions in stakeholder feedback: 1 → 1; 2–3 → 2; 4+ → 3
- Strength of feedback in specific forums (e.g. 1 mention → 1; 2+ → 3)
- Inclusion in external research reports (count)
Average the metrics for the impact score. Metrics and factors are equally weighted unless the group agrees otherwise; swing weights (`steps/05-criteria.md` §5.3) are for choosing between options, not needed here.

**Availability (1–3)**, team assessment averaged across factors, each scored 1–3:
- **Difficulty** (1 = hard, 3 = easier)
- **Dependency** (1 = highly co-dependent, 3 = standalone)
- **Capacity** (1 = low availability, 3 = manageable)
- **Capability** (1 = specialist/external, 3 = internal)

**Grid.** Default **3×3**: band each average into low (<1.67), medium (1.67–2.33), high (>2.33). Option: **4×4** with bands at 1.5 / 2.0 / 2.5, where cells are labelled with a combined score (row band + column band) and boundary cells are shown hatched (judgement zone).

**Zones** (name them on the slide):
- High impact, high availability → **Principal priorities**
- High impact, low availability → **Longer-term roadmap** (invest in availability)
- Low impact, high availability → **Easy extras** (do them if they build momentum; don't mistake them for priorities)
- Low impact, low availability → **Hand over or deprioritise**
- Middle / boundary cells → judgement, recorded

**Before plotting, merge duplicates and exclude** with reasons: internal set-up tasks, items clearly out of scope, items where the organisation's role would only be supporting. Show the narrowing as a waterfall or funnel.

**Check spread.** Averages of a few 1–3 scores bunch in the middle, so most items can land in judgement cells. If that happens, use relative bands (split the items into equal-sized groups), the 4×4 grid, or sharper level definitions. `scripts/appraise.py matrix` places items, counts each zone and warns when this happens. If items bunch on one axis (e.g. nothing in the low-availability columns), the axis isn't discriminating: revisit the factor scoring or anchors before drawing conclusions.

**Scenarios and roadmap.** Group priorities into cumulative scenarios (Scenario 1; + Scenario 2; + Scenario 3) by value-chain area, and show which activities enter at each, then a phased roadmap.

## Eisenhower (urgency × importance)

Standard four quadrants:
- Urgent and important → **Do now**
- Important, not urgent → **Schedule** (plan and resource)
- Urgent, not important → **Delegate** (or handle with minimum effort)
- Neither → **Drop**

Define "urgent" (a deadline, legal/regulatory requirement, commitment already made, or rapidly closing window) and "important" (contribution to agreed objectives) in writing before sorting. Use it for mandated work, or alongside impact × availability to make sure "must do" items aren't deprioritised because they're hard.

## Outputs

- **Scoring logic slide**: the impact metrics and availability factors with their 1–3 definitions, and the grid with zones and cell scores.
- **Plotted matrix**: counts per cell, key priorities listed alongside, exclusion note.
- **Scenario overlay / roadmap**: activities by value-chain area with scenario or priority markers.

## Checklist
- [quick] Axis definitions with 1-3 levels (impact metrics; availability factors) or urgency/importance defined
- [quick] Exclusions before plotting (internal, out of scope, support-only)
- [standard] Grid size chosen (3×3 default); boundary cells resolved by recorded judgement
- [standard] Spread checked on each axis
- [standard] Scenarios / roadmap and implications for existing organisations
