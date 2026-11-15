# Method: activity and responsibility mapping, with diagnosis

Use to work out what a new or changing function should do in a crowded landscape: who does what today, where there are gaps, duplication or unclear accountability, and therefore which activities the function should own, support, hand over or stop. It is the front half of the **What** type of choice, feeding impact × availability (`methods/matrix.md`).

> **Supporting, not core.** Use it to inform scope, structure or partner choices. For a standalone activity analysis, flag to the user that Choosewell handles this lightly (see `choices/what.md`).

## Phase 1: Map

1. **Define the value chain**: the end-to-end stages of the work (e.g. strategy & leadership → engagement → marketing → sales → finance & commercial → service delivery, plus back-office and policy). Start from a recognised process framework (e.g. APQC's Process Classification Framework) and adapt in workshops.
2. **List activities** under each stage at a consistent level of detail (a verb + object: "qualify international leads", "negotiate contracts with buyers and subcontractors"). Expect the list to grow as engagement surfaces new activities.
3. **List organisations** in the landscape.
4. **Plot the as-is responsibility matrix** (activities × organisations) using four codes:
   - **A**: Accountable (ultimately answerable for completion)
   - **AD**: Accountable and Delivers
   - **D**: Delivers (does the work)
   - **S**: Supports (supporting or consultative role)
   Summarise counts per organisation per code as a heatmap with callouts ("accountability typically sits with government"; "one body delivers most existing work").

## Phase 2: Diagnose and redesign

For each activity, classify the issue and the action:

| # | Issue | Action |
|---|---|---|
| 1 | No issue / desirable duplication | Document and signpost for users |
| 2 | Under-investment in a key activity | Add stakeholders |
| 3 | Undesirable duplication of effort | Clarify and redistribute workload |
| 4 | Lack of clear accountability | Confirm ownership |
| 5 | Gap / no activity | Establish a new remit |
| 6 | Unnecessary activity | Stop |

**Suggested classification from the codes** (the group confirms; `scripts/appraise.py diagnose` applies these):
- No organisation involved → 5 (gap)
- Two or more A or AD codes → 4 (unclear accountability)
- A with no D or AD → possibly 2 (under-investment); check
- Delivered (D) but nobody accountable (no A or AD) → 4 (unclear accountability)
- Two or more D codes → 1 or 3: judgement (is the duplication useful, e.g. regional coverage, or wasteful?)
- Activity not serving any agreed objective → 6 (stop): judgement
- Otherwise → 1 (no issue)

Then draw the **to-be**: for each activity, the new code per organisation, including the new function.

## Narrowing to the activities that matter

Show a waterfall: initial mapping → new activities identified → excluded internal set-up activities → excluded firmly out of scope → excluded where the new function would only support → activities in focus (split new vs existing). Counts depend entirely on the case; what matters is that every exclusion has a stated rule.

## Then prioritise

Score the activities in focus with impact × availability (`methods/matrix.md`), group into cumulative scenarios, and recommend a phased approach per scenario, with implications for existing organisations (what each gains, loses or must hand over).

## Outputs

- **Methodology**: two-phase process (mapping; prioritisation) and aims.
- **Value chain** with activity groups; later the same with focus areas highlighted.
- **Responsibility heatmap** (counts by organisation × code) with summary callouts.
- **Issue-type table**: issue, example as-is pattern, action, example to-be pattern.
- **Narrowing waterfall**.
- **Activity list by value-chain stage with scenario markers**; then with priority scores.

## Checklist
- [quick] Value chain and activity list (verb + object)
- [quick] As-is A / AD / D / S matrix with counts per organisation
- [quick] Issue type and action per activity (suggested, then confirmed)
- [standard] Narrowing waterfall with a rule for every exclusion
- [standard] To-be responsibilities and implications for existing organisations
