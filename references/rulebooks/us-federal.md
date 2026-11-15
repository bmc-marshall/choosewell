# US federal guidance (Green Book equivalents)

The US has no single equivalent of the UK Green Book. The closest pieces are OMB circulars on benefit-cost analysis and GAO's best practices for analyses of alternatives. Use this module for US federal work, and as optional good practice for US state, local and non-profit work (non-federal bodies are encouraged, not required, to follow OMB guidance).

**Currency check.** US guidance has changed repeatedly since 2023. The position below was checked in November 2026: always verify the current versions on whitehouse.gov (OMB) and gao.gov before relying on them, and tell the user if anything has moved.

## 1. What applies to what

| Decision | Guidance | Status (as of Nov 2026) |
|---|---|---|
| Federal programmes and projects with benefits/costs over 3+ years (start, renew, expand); lease vs purchase; asset sales | **OMB Circular A-94** (benefit-cost analysis of federal programs) | The **1992 version** was reinstated by OMB memo M-25-23 (April 2025), rescinding the 2023 revision. Appendix C (Treasury-based discount rates) is updated annually: the March 2026 update gives e.g. 10-year real 1.6%, 30-year real 2.0% |
| Federal regulations | **OMB Circular A-4** (regulatory analysis) under Executive Order 12866 | The **2003 version** applies again (the 2023 revision was repealed in 2025). EO 14192 adds regulatory cost-offset requirements; EO 14215 extends review to independent agencies |
| Capital acquisitions, major systems, basing and similar choices | **GAO analysis of alternatives (AOA) best practices**: Appendix XI of GAO's *Cost Estimating and Assessment Guide* (GAO-20-195G, 2020) | Current; supersedes the earlier lists in GAO-15-37 and GAO-16-22; used by GAO to audit agency decisions |
| Capital assets, including major IT investments | **OMB Circular A-11** and its *Capital Programming Guide* (business case, alternatives analysis, life-cycle cost); for IT, the agency CIO's review under FITARA, and OMB shared-services policy (look for an existing government-wide or shared solution) | Updated most years: check the current A-11 and any IT or shared-services memos before relying on them |

## 2. A-94 essentials (1992 version)

- **Alternatives to consider**: different scales of programme, different methods of provision, and different degrees of government involvement. For capital assets: do nothing, direct purchase, upgrading or sharing existing property, leasing or contracting for services. (This is close to the Green Book options framework: scope, delivery, funding.)
- **Decision criterion**: net present value of benefits minus costs, measured by willingness to pay; incremental costs and benefits only (ignore sunk costs, exclude transfers); no employment multipliers.
- **Discount rate**: 7% real for the base case of public investment analysis, with sensitivity to other rates; Treasury rates (Appendix C) for cost-effectiveness, lease-purchase, and internal cost-saving investments. Adjust for risk through certainty-equivalents, not by changing the discount rate.
- **Cost-effectiveness analysis** when benefits are the same across alternatives or impractical to monetise: choose the lowest present-value cost for a given level of benefit.
- **Uncertainty**: describe sources, use expected values and probability distributions where possible, note known biases (e.g. historical cost growth), and run sensitivity analysis on key assumptions including the discount rate (how: `methods/quantified-tree.md`).
- **Lease vs purchase**: decide first whether to acquire the asset's services, then compare the discounted life-cycle cost of leasing with buying.

## 3. GAO analysis of alternatives best practices

GAO assesses AOAs against four characteristics: **comprehensive, well-documented, unbiased and credible**, using 22 best practices across five phases:

1. **Initialise**: define the mission need and functional requirements *without presupposing a solution*; set the study plan, ground rules, timeframe and who conducts the analysis.
2. **Identify alternatives**: a sufficient, diverse and viable set, including a **baseline (status quo)** alternative; describe each.
3. **Analyse**: compare costs (life-cycle cost estimates), benefits/effectiveness tied to the mission need, and risks (with mitigations), using a consistent, quantitative process; include sensitivity analysis.
4. **Document and review**: one document recording every step; independent review.
5. **Select**: compare alternatives against criteria agreed in advance and select the one that best meets the mission need, with the rationale.

For the full numbered list, see Appendix XI of GAO-20-195G (also published on gaoinnovations.gov). When an AOA must stand up to GAO review, build a crosswalk: each of the 22 practices, where the analysis meets it, and the evidence. Map them to the four characteristics GAO scores against (comprehensive, well-documented, unbiased, credible).

## 4. How choosewell maps onto US practice

| Choosewell step | US equivalent |
|---|---|
| Frame (decision, principles) | Mission need and functional requirements, solution-neutral (GAO 1) |
| Long list with BAU | Diverse, viable alternatives including baseline / do nothing (GAO 2; A-94) |
| Criteria and level definitions | Selection criteria and weights agreed before analysis (GAO 1, 5) |
| RAG / scored screening | No formal US equivalent of the Green Book CSF filter. Use red/amber/green against must-have requirements (or knock-outs) to narrow the long list, then **scored effectiveness criteria with swing weights plus a separate life-cycle cost** for the short list: that's what GAO expects to see quantified. Document the screen as part of the AOA |
| Short-list analysis | NPV (A-94) or cost-effectiveness; life-cycle costs (GAO 3) |
| Sensitivity, switching values | Required sensitivity analysis (A-94; GAO 3) |
| Decisions log, evidence base | Single AOA document; independent review (GAO 4) |

**Practical defaults for US federal users:** frame solution-neutrally; always include the status quo; agree criteria and weights before analysis (swing weighting is a good fit); use the 7% real base rate plus sensitivity for public-investment NPV where benefits are monetised and differ between alternatives, or Appendix C rates for cost-effectiveness (the usual case for replacing a system or capability with similar benefits: compare life-cycle costs at the Appendix C rate for the matching term, with sensitivity); record everything in one document and plan for independent review. For US non-federal users: use the same structure as good practice and say it is voluntary.

## Checklist
- [quick] Current OMB guidance checked (A-94 1992 version reinstated 2025; A-4 2003 version for rules; Appendix C rates for the year)
- [quick] Mission need and functional requirements defined without a preferred solution
- [quick] Alternatives vary scale, method of provision and degree of government involvement; status quo baseline included
- [standard] Selection criteria and weights agreed before analysis
- [full] Life-cycle cost estimates; NPV at 7% real base case with sensitivity (or Appendix C rates for CEA / lease-purchase)
- [full] Risk via expected values / certainty-equivalents, not discount-rate adjustment
- [standard] Single AOA document; independent review
- [standard] Crosswalk to GAO's 22 AOA practices (Appendix XI, GAO-20-195G) if GAO review is likely
- [standard] For capital assets and IT: A-11 Capital Programming Guide requirements, and existing shared or government-wide solutions, checked
