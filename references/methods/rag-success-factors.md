# Method: RAG against critical success factors (with indicators)

Use when options should be ruled out if they fail a test, the audience expects a defensible audit trail (public money, boards), and the criteria are broad enough to need several sub-questions each. The classic use is the Green Book long-list filter (`rulebooks/green-book.md`), but it works for any "which form / which option is viable" question.

## Contents
1. Structure
2. Indicator level
3. Indicators → criterion rating
4. Criteria → overall rating
5. Gate first: sequential filtering
6. Calibration notes from a real appraisal
7. Outputs

---

## 1. Structure

Options (columns) × criteria (CSFs), each criterion broken into 4–8 **indicators**: short statements worded so that a ✓ is always favourable ("Does not require new legislation", "Able to sign contracts with foreign governments"). Each criterion can be rated for **setup** and **ongoing** separately where timing matters.

## 2. Indicator level

| Mark | Meaning | Value | In the denominator? |
|---|---|---|---|
| ✓ | Favourable | +1 | Yes |
| – | Neutral / no different from others | 0 | Yes |
| ✗ | Unfavourable | −1 | Yes |
| ? | Unknown | none: logged as an open question with an owner | No |
| n/a | Doesn't apply to this option | none | No |

Before scoring, tag each indicator as a **differentiator** or a **deal-breaker** (a single unmitigated ✗ fails the criterion; e.g. "has the legal powers/remit", "can transact using the models required").

Why these choices:
- Ticks and crosses cancel symmetrically among differentiators. Asymmetry (crosses matter more) is handled by the deal-breaker tag; weighting crosses as well would double-count and make the arithmetic opaque.
- Neutral counts in the denominator, so an option that is mostly "no different" lands amber: it hasn't distinguished itself.
- Unknowns are excluded rather than treated as neutral, so ignorance doesn't masquerade as mediocrity.

## 3. Indicators → criterion rating (suggested)

Score = (ticks − crosses) ÷ applicable indicators, giving −1 to +1 whatever the number of indicators (this is what makes criteria with 13 indicators and criteria with 6 comparable).

- **Red** if any deal-breaker indicator has an unmitigated ✗.
- **Green** if score ≥ +0.4 (with 6 indicators: net +3, e.g. 3 ✓ and no ✗; with 13: net +6).
- **Amber** otherwise.
- **Provisional** flag if more than a third of indicators are "?". Show it (e.g. hatched or "A?"), don't convert it to amber.
- **Split ratings** (Green/Amber, Amber/Red) are allowed when the group is between two; they count half a step and must carry a note on what would resolve them.

Totals never produce red on their own: a pile of fixable weaknesses (costs, time) lowers a rating to amber; only a deal-breaker rules an option out. The group can still agree red by override with a reason (`steps/07-assess.md`).

## 4. Criteria → overall rating (suggested)

Score criteria G = +1, G/A = +0.5, A = 0, A/R = −0.5, R = −1.

- **Red overall** if any criterion is red. One red is enough: in the Green Book a CSF is a pass/fail test, and an option failing the objectives can't be value for money.
- **Green overall** if no reds and the average ≥ +0.5 (roughly: at least half the criteria green).
- **Amber overall** otherwise (meets the CSFs but less attractive; can be carried forward).

Criteria are equally weighted unless weights were agreed before scoring. If the group finds itself preferring an option with the same profile as one it rejected (e.g. 3 greens and 4 ambers each, one green overall, the other amber), that reveals an implicit weighting (often speed and cost): make it explicit and re-run rather than overriding silently.

Each overall rating carries a one-line rationale, because the roll-up is a suggestion, not a verdict.

## 5. Gate first: sequential filtering

Apply criteria in stages so the group's effort goes where it matters:
1. **Initial sift**: knock-outs (legal impossibility, policy prohibitions, out of scope), with reasons.
2. **Strategic fit gate**: options red on strategic fit stop here.
3. **Other criteria**: rate the survivors.
4. **Overall rating** and **short list** (respecting the composition rules where the Green Book applies: BAU always carried).

Show this as a **drop-out tracker** (`presenting/slide-patterns.md`): options down the side grouped by family, stages across the top, a line running until the stage where each option drops out (×), and the short list at the end.

## 6. Calibration notes from a real appraisal

These rules were tested against 91 criterion ratings from a working group's operating-model appraisal (13 options × 7 CSFs):
- Simple net balance of ticks and crosses matched the group's rating ~60% of the time; most misses were the sum calling red where the group said amber (mostly affordability and supplier capability: fixable issues).
- Reserving red for deal-breakers raised agreement to ~80%.
- One criterion was rated amber for 12 of 13 options regardless of indicators, because evidence was pending: amber was being used for "don't know yet". Hence the separate provisional flag.
- "Any red CSF → red overall" held for every option. "At least half green, no red → green" reproduced every overall rating but one, and that exception revealed an implicit weighting towards speed and affordability.
- One indicator appeared under two criteria (double counting).

Treat the thresholds (+0.4, +0.5) as defaults to adjust with the group, not constants (and say so in the method-transparency note).

## 6a. When RAG isn't enough

If the RAG filter leaves several ambers and no clear preferred way forward (often trade-offs over scope and solution), the next step is **swing-weighted MCDA** on the remaining long-list options (`rulebooks/green-book.md` §5a), followed (for UK public business cases) by cost-benefit or cost-effectiveness analysis on the short list. Outside UK central government, a swing-weighted score can also be used at short-list stage; say which rules apply.

Where uncertainty is high and the decision hard to reverse, add a flexibility indicator ("preserves future options / can transition later") under strategic fit or achievability, and consider staged or transition options (`steps/09-decide.md` §9.1).

## 7. Outputs

- **Criteria and sub-questions slide**: each CSF with its dimension (strategic, economic, commercial, financial, management, local), sub-questions, and which are standard vs local.
- **Roll-up rules slide**: the legend (Green = meets CSF, preferred way forward; Amber = meets CSF but less attractive, carry forward; Red = fails, drop) and the principles (equal weighting; one red → red; gradations within categories; any short-list cap).
- **Indicator matrix per CSF** (one slide each): indicators down the side, options across, ✓ / – / ✗ / ?, with the criterion rating as a coloured bar (with the letter) above each option, the CSF question as the headline, setup/ongoing marker, and key questions in the notes.
- **Summary matrix**: options (grouped by family) × CSFs, plus overall and "progress to short list". Then the same matrix filtered to the short list.
- **Drop-out tracker** (§5).
- **Rationale vs alternatives**: preferred option, why it beats each alternative or family, and the risks that remain despite choosing it.

## Checklist
- [quick] Indicators per criterion (4-8), deal-breakers tagged, setup vs ongoing where relevant
- [quick] Roll-up rules agreed: deal-breaker ✗ → red; score ≥ +0.4 → green; any red criterion → red overall; ≥ +0.5 average → green
- [standard] Provisional flag where > 1/3 indicators unknown
- [quick] Drop-out tracker and summary RAG matrix
- [standard] Rationale vs alternatives and risks that remain
