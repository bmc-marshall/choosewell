#!/usr/bin/env python3
"""
appraise.py - helpers for choosewell appraisals.

Subcommands
  init        Create the appraisal workbook (.xlsx). --methods adds the tabs a method needs
              (decision-tree, quantified-tree, matrix, pros-and-cons); --scorers adds private scoring;
              --scores imports an options x criteria CSV.
  spread      Private scoring: the spread of individual scores per option x item, median as suggestion.
  rollup      Roll indicator marks up to criterion and overall ratings (RAG/CSF), or average criterion
              scores (scored criteria); gates, dominance, one-point flips; write a Results tab.
  matrix      Place activities on an impact x availability grid (3x3 or 4x4) and count each zone.
  thresholds  Run a sequential threshold filter from a CSV + JSON rules, with sensitivity.
  diagnose    Suggest issue types for an A/AD/D/S responsibility matrix (CSV).
  sensitivity Weighted-score ranking with dominance, weight and score switching values, tornado.
  payoff      Options x scenarios payoff table: expected value, EVPI, regret, satisficing.
  tree        Shortcut to `uncertainty.py tree` (quantified decision trees). For trees, value of
              information and Bayes updating use scripts/uncertainty.py directly.
  audit       Verification: drafted ratings without evidence/source, overrides without reasons,
              confidence profile, claim-ledger gaps (unsourced, unchecked, undated).

Run `python appraise.py <subcommand> --help` for options.

Conventions (see references/methods/rag-success-factors.md):
  Indicator marks: ✓ / Y / +1 = favourable; - / 0 = neutral; ✗ / X / N / -1 = unfavourable;
                   ? = unknown (excluded, logged); n/a = not applicable (excluded).
  Criterion score = (ticks - crosses) / applicable indicators  -> -1..+1
  Suggested criterion rating: Red if any deal-breaker indicator is ✗; Green if score >= --green
                   (default 0.4); else Amber. Provisional if > 1/3 of indicators unknown.
  Overall: Red if any criterion Red; Green if mean (G=1, G/A=.5, A=0, A/R=-.5, R=-1) >= --overall
           (default 0.5); else Amber. Weights from the Criteria tab if given (default equal).
All results are SUGGESTIONS for the working group; agreed ratings in the Ratings tab take precedence.
"""
import argparse, csv, json, sys, collections

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
except ImportError:  # pragma: no cover
    sys.exit("openpyxl is required: pip install openpyxl")

TABS = {
    "Frame": ["field", "value"],
    "Principles": ["type (process/outcome)", "principle", "issue addressed", "implication"],
    "Options": ["option_id", "name", "family", "source", "description", "is_bau (y/n)",
                "knock_out (y/n)", "knock_out_reason"],
    "Criteria": ["criterion_id", "name", "question", "dimension (standard/local)", "weight",
                 "scale (rag/score)", "max_score", "level_definitions", "stage (gate/main)"],
    "Indicators": ["criterion_id", "indicator_id", "statement (worded so ✓ = favourable)",
                   "deal_breaker (y/n)", "drafted (y/n)"],
    "Ratings": ["option_id", "item_id (indicator or criterion)", "phase (setup/ongoing/blank)",
                "suggested", "agreed", "override_reason", "evidence", "source",
                "confidence (H/M/L)", "drafted (y/n)"],
    "Claims": ["claim_id", "option_id", "claim (one fact, specific)", "type (fact/claim/inference/estimate)",
               "source (link, doc + page, or calculation)", "date of information", "confidence (H/M/L)",
               "checked (who/what, when)", "used in (rating/profile/slide)"],
    "Open questions": ["q_id", "question", "option_id", "item_id", "owner", "channel", "due",
                       "would_change"],
    "Decisions log": ["date", "decision", "agreed_by", "evidence", "replaces"],
}
FRAME_FIELDS = ["decision", "decision_maker", "decision_date", "in_scope", "out_of_scope",
                "what_happens_next", "type_of_choice", "methods", "rulebook", "depth", "steps_skipped", "assumptions"]

RAG_VAL = {"G": 1.0, "G/A": 0.5, "A/G": 0.5, "A": 0.0, "A/R": -0.5, "R/A": -0.5, "R": -1.0}


# ---------------------------------------------------------------- helpers
def mark_value(m):
    """Return +1/0/-1 for a mark, None for unknown, 'na' for not applicable."""
    if m is None:
        return None
    s = str(m).strip().lower()
    if s in ("", "?", "unknown", "tbc"):
        return None
    if s in ("n/a", "na"):
        return "na"
    if s in ("✓", "y", "yes", "+1", "1", "+", "tick", "pass"):
        return 1
    if s in ("✗", "x", "n", "no", "-1", "cross", "fail"):
        return -1
    if s in ("-", "–", "0", "neutral", "o"):
        return 0
    try:
        return max(-1, min(1, int(float(s))))
    except ValueError:
        return None


def rows(ws):
    hdr = [c.value for c in ws[1]]
    for r in ws.iter_rows(min_row=2, values_only=True):
        if any(v not in (None, "") for v in r):
            yield dict(zip(hdr, r))


def first(d, prefix):
    for k, v in d.items():
        if k and str(k).startswith(prefix):
            return v
    return None


def yes(v):
    return str(v or "").strip().lower() in ("y", "yes", "true", "1")


def band(score, green):
    return "G" if score >= green else "A"


def overall_from(ratings, weights, overall_thr):
    if any(r == "R" for r in ratings.values()):
        return "R", None
    tw = sum(weights.get(c, 1.0) for c in ratings) or 1.0
    mean = sum(RAG_VAL.get(r, 0.0) * weights.get(c, 1.0) for c, r in ratings.items()) / tw
    return ("G" if mean >= overall_thr else "A"), round(mean, 2)


# ---------------------------------------------------------------- init
METHOD_TABS = {
    "decision-tree": {"Tree questions": ["order", "question", "answered by (who/when)", "yes →", "no →", "notes"],
                      "Red lines": ["red_line", "forces (option or branch)", "whose red line", "source"],
                      "Push-pull": ["option_id", "factor", "push or pull", "rating (L/M/H)", "rating definition", "evidence"],
                      "Fact sheets": ["option_id", "field", "content", "source"],
                      "Back-test": ["past case", "answers to the questions", "model the tree picks", "model actually used", "match? / why not"]},
    "quantified-tree": {"Tree inputs": ["input", "central value", "low", "high", "unit", "source or basis", "owner"]},
    "matrix": {"Activities": ["activity_id", "activity", "excluded (reason)", "impact metric 1", "impact metric 2",
                              "impact metric 3", "availability: difficulty", "availability: dependency",
                              "availability: capacity", "availability: capability", "notes"]},
    "pros-and-cons": {"Pros and cons": ["option_id", "pro or con", "point", "evidence", "how much it matters (L/M/H)"]},
}
SCORER_TAB = ["scorer", "option_id", "item_id", "score", "reason"]


def cmd_init(a):
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    bold = Font(bold=True)
    tabs = dict(TABS)
    for m in [x.strip() for x in (a.methods or "").split(",") if x.strip()]:
        if m not in METHOD_TABS and m not in ("scored-criteria", "rag-success-factors", "threshold-filter",
                                             "responsibility-mapping"):
            raise SystemExit(f"Unknown method '{m}'")
        tabs.update(METHOD_TABS.get(m, {}))
    if a.scorers:
        tabs["Scores by person"] = SCORER_TAB
    for name, hdr in tabs.items():
        ws = wb.create_sheet(name)
        ws.append(hdr)
        for c in ws[1]:
            c.font = bold
            c.fill = PatternFill("solid", fgColor="DDDDDD")
            c.alignment = Alignment(wrap_text=True, vertical="top")
        for i, h in enumerate(hdr, 1):
            ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = max(14, min(40, len(h) + 4))
        ws.freeze_panes = "A2"
    fr = wb["Frame"]
    preset = {"type_of_choice": a.choice, "methods": a.methods or "", "rulebook": a.rulebook or "", "depth": a.depth or ""}
    for f in FRAME_FIELDS:
        fr.append([f, preset.get(f, "")])
    fr.append([])
    fr.append(["(steps_skipped: step numbers only, e.g. 3, 6. Put reasons in the Decisions log.)"])
    if a.scores:
        crits, w, opts = _read_scores(a.scores)
        for i, o in enumerate(opts, 1):
            wb["Options"].append([f"O{i}", o, "", "imported", "", "y" if any(t in o.lower() for t in ("business as usual", "bau", "do nothing", "status quo")) else "n", "n", ""])
        if a.rescale:   # 0-100 per criterion, worst = 0, best = 100
            for j in range(len(crits)):
                col = [v[j] for v in opts.values() if v[j] is not None]
                lo, hi = (min(col), max(col)) if col else (0, 1)
                for o in opts:
                    if opts[o][j] is not None:
                        opts[o][j] = round(100.0 * (opts[o][j] - lo) / (hi - lo), 2) if hi > lo else 100.0
        for j, c in enumerate(crits, 1):
            col = [v[j - 1] for v in opts.values() if v[j - 1] is not None]
            mx = 100 if a.rescale else (a.scale_max or (max(col) if col else 3))
            wb["Criteria"].append([f"C{j}", c, "", "", round(w[j - 1], 4), "score", mx,
                                   "rescaled 0-100 (worst to best on the table)" if a.rescale else "", "main"])
        col_s, drafted = ("suggested", "y") if a.drafted else ("agreed", "n")
        for i, (o, vals) in enumerate(opts.items(), 1):
            for j, v in enumerate(vals, 1):
                row = [f"O{i}", f"C{j}", "", v if col_s == "suggested" else "", v if col_s == "agreed" else "",
                       "", "", "", "", drafted]
                wb["Ratings"].append(row)
        n = len(opts)
        if a.excluded:
            for r in csv.DictReader(open(a.excluded, newline="", encoding="utf-8-sig")):
                k = list(r.keys())
                st = (r.get("status") or "").lower()
                if st in ("passed", "provisional") or r[k[0]] in opts:
                    continue
                n += 1
                wb["Options"].append([f"O{n}", r[k[0]], "", "screened out", "", "n", "y",
                                      r.get("reason") or (r[k[1]] if len(k) > 1 else "")])
        print(f"Imported {len(opts)} options x {len(crits)} criteria from {a.scores} "
              f"(weights normalised; scores entered as {'drafted suggestions' if a.drafted else 'agreed'}"
              f"{'; rescaled 0-100' if a.rescale else ''}). Add business as usual to the Options tab if it isn't there.")
    wb.save(a.out)
    print(f"Created {a.out} with tabs: {', '.join(tabs)}")


# ---------------------------------------------------------------- spread (private scoring first)
def cmd_spread(a):
    """Reads 'Scores by person'; shows the spread for each option x item and suggests the median."""
    import statistics
    wb, wv = load_values(a.workbook)
    if "Scores by person" not in wv.sheetnames:
        raise SystemExit("No 'Scores by person' tab: create one with init --scorers, or add it with columns " +
                         ", ".join(SCORER_TAB))
    by = collections.defaultdict(list)
    for r in rows(wv["Scores by person"]):
        try:
            by[(str(first(r, "option_id")), str(first(r, "item_id")))].append((r.get("scorer"), float(r.get("score"))))
        except (TypeError, ValueError):
            v = mark_value(r.get("score"))
            if isinstance(v, int):
                by[(str(first(r, "option_id")), str(first(r, "item_id")))].append((r.get("scorer"), float(v)))
    if "Spread" in wb.sheetnames:
        del wb["Spread"]
    ws = wb.create_sheet("Spread")
    ws.append(["option_id", "item_id", "n scorers", "min", "median", "max", "range", "discuss?", "scores"])
    disc = 0
    for (o, i), xs in sorted(by.items()):
        v = [x for _, x in xs]
        rng = max(v) - min(v)
        flag = "yes" if rng >= a.threshold else ""
        disc += bool(flag)
        ws.append([o, i, len(v), min(v), statistics.median(v), max(v), rng, flag,
                   "; ".join(f"{p}={x:g}" for p, x in xs)])
    filled = 0
    if a.suggest and "Ratings" in wb.sheetnames:
        rw = wb["Ratings"]
        hdr = [c.value for c in rw[1]]
        col = {h.split(" ")[0] if h else "": k for k, h in enumerate(hdr)}
        have = {}
        for row in rw.iter_rows(min_row=2):
            have[(str(row[col["option_id"]].value), str(row[col["item_id"]].value))] = row
        for (o, i), xs in by.items():
            med = statistics.median([x for _, x in xs])
            row = have.get((o, i))
            if row is None:
                rw.append([o, i, "", med] + [""] * (len(hdr) - 4))
                filled += 1
            elif row[col["suggested"]].value in (None, ""):
                row[col["suggested"]].value = med
                filled += 1
    wb.save(a.out or a.workbook)
    print(f"{len(by)} option x item cells scored; {disc} with a range of {a.threshold:g} or more to discuss first "
          f"(tab 'Spread').")
    if a.suggest:
        print(f"Median written as the suggested score for {filled} cell(s); the group still agrees each one.")


# ---------------------------------------------------------------- rollup
def load_values(path):
    """Workbook for writing, plus a copy with formulas replaced by their last calculated values."""
    wb = openpyxl.load_workbook(path)
    wv = openpyxl.load_workbook(path, data_only=True)
    has_formula = any(isinstance(c.value, str) and c.value.startswith("=")
                      for name in ("Options", "Criteria", "Ratings") if name in wb.sheetnames
                      for row in wb[name].iter_rows() for c in row)
    if has_formula and all(c.value is None for name in ("Criteria",) if name in wv.sheetnames
                           for row in wv[name].iter_rows(min_row=2) for c in row):
        print("NOTE: the workbook has formulas without saved results. Open and save it in Excel (or LibreOffice) "
              "so the calculated values are stored, then run this again.")
    return wb, wv


def cmd_rollup(a):
    wb, wv = load_values(a.workbook)
    for need in ("Options", "Criteria"):
        if need not in wv.sheetnames:
            raise SystemExit(f"The workbook has no '{need}' tab; rollup is for scored or red/amber/green methods.")
    options = {str(first(r, "option_id")): r for r in rows(wv["Options"]) if first(r, "option_id")}
    crit = {str(first(r, "criterion_id")): r for r in rows(wv["Criteria"]) if first(r, "criterion_id")}
    inds = collections.OrderedDict()
    for r in (rows(wv["Indicators"]) if "Indicators" in wv.sheetnames else []):
        if not first(r, "indicator_id"):
            continue
        inds[str(first(r, "indicator_id"))] = {
            "crit": str(first(r, "criterion_id")),
            "text": str(first(r, "statement") or ""),
            "db": yes(first(r, "deal_breaker")),
        }
    ratings = collections.defaultdict(dict)  # (opt, item, phase) -> row
    for r in (rows(wv["Ratings"]) if "Ratings" in wv.sheetnames else []):
        key = (str(first(r, "option_id")), str(first(r, "item_id")), str(first(r, "phase") or ""))
        ratings[key] = r

    def val(opt, item, phase=""):
        r = ratings.get((opt, item, phase)) or (ratings.get((opt, item, "")) if phase else None)
        if not r:
            return None, None
        ag, sg = first(r, "agreed"), first(r, "suggested")
        return (ag if ag not in (None, "") else sg), (str(first(r, "confidence") or "").upper()[:1])

    weights, wnotes = {}, []
    for c, r in crit.items():
        try:
            weights[c] = float(first(r, "weight") or 1)
        except (TypeError, ValueError):
            weights[c] = 1.0
            wnotes.append(c)
    gates = [c for c, r in crit.items() if str(first(r, "stage") or "").strip().lower().startswith("gate")]

    def phases_for(item_ids):
        """Phases used for these items (e.g. setup/ongoing); untagged ratings count in every phase."""
        ph = sorted({k[2] for k in ratings if k[1] in item_ids and k[2]})
        return ph or [""]
    live = [o for o, r in options.items() if not yes(first(r, "knock_out"))]
    knocked = [o for o in options if o not in live]
    out, notes = [], []

    has_inds = {d["crit"] for d in inds.values()}

    def is_rag(c, r):
        sc = str(first(r, "scale") or "").strip().lower()
        if sc:
            return sc.startswith("rag")
        return c in has_inds and not first(r, "max_score")   # blank scale: statements → rag; else scored
    rag_crit = [c for c, r in crit.items() if c not in gates and is_rag(c, r)]
    score_crit = [c for c in crit if c not in rag_crit and c not in gates]
    if wnotes:
        notes.append(f"WEIGHTS: non-numeric weight for {', '.join(wnotes)}; treated as 1 until agreed.")

    # --- gates (pass/fail criteria): any ✗ on the criterion or its statements fails the gate
    gate_fail = collections.defaultdict(list)
    for o in live:
        for c in gates:
            items = [c] + [i for i, d in inds.items() if d["crit"] == c]
            for i in items:
                for ph in phases_for([i]):
                    if mark_value(val(o, i, ph)[0]) == -1:
                        gate_fail[o].append(c if i == c else f"{c}/{i}")
    failed = [o for o in live if gate_fail.get(o)]
    live = [o for o in live if o not in failed]

    # --- RAG / indicator roll-up
    results = {}
    for o in live:
        crit_ratings, crit_info = {}, {}
        for c in rag_crit:
            c_inds = [i for i, d in inds.items() if d["crit"] == c]
            per_phase = []
            for ph in phases_for(c_inds):
                marks = [(i, mark_value(val(o, i, ph)[0])) for i in c_inds]
                if all(m is None for _, m in marks) and not c_inds:
                    continue
                appl = [m for _, m in marks if m not in (None, "na")]
                unk = sum(1 for _, m in marks if m is None)
                db_fail = [i for i, m in marks if m == -1 and inds[i]["db"]]
                score = (sum(appl) / len(appl)) if appl else 0.0
                sugg = "R" if db_fail else band(score, a.green)
                prov = c_inds and unk > len(c_inds) / 3
                per_phase.append((ph, sugg, round(score, 2), prov, db_fail,
                                  sum(1 for m in appl if m == 1), sum(1 for m in appl if m == -1),
                                  sum(1 for m in appl if m == 0), unk))
            # worst phase governs the suggestion; nothing rated yet -> "not rated"
            order = {"R": 0, "A": 1, "G": 2, "–": 3}
            per_phase = [p if (p[5] + p[6] + p[7]) or p[4] else (p[0], "–") + p[2:] for p in per_phase]
            if per_phase:
                worst = min(per_phase, key=lambda p: order[p[1]])
            else:
                worst = ("", "–", 0.0, True, [], 0, 0, 0, 0)
            agreed, _ = val(o, c)
            agreed = str(agreed).strip().upper() if agreed not in (None, "") else None
            final = agreed or worst[1]
            crit_ratings[c] = final
            crit_info[c] = {"suggested": worst[1], "agreed": agreed, "score": worst[2],
                            "provisional": bool(worst[3]), "deal_breakers": worst[4],
                            "ticks": worst[5], "crosses": worst[6], "neutral": worst[7],
                            "unknown": worst[8], "phase": worst[0]}
        rated = {c: r for c, r in crit_ratings.items() if r != "–"}
        if crit_ratings and not rated:
            ov, mean = "not rated", None
        else:
            ov, mean = overall_from(rated, weights, a.overall) if rated else (None, None)
            if rated and len(rated) < len(crit_ratings) and ov != "R":
                ov = f"{ov} (partial: {len(crit_ratings) - len(rated)} not rated)"
        # scored criteria
        scores, wsum, tot, unknown = {}, 0.0, 0.0, []
        for c in score_crit:
            v, conf = val(o, c)
            try:
                sc = float(v)
            except (TypeError, ValueError):
                sc = None
            scores[c] = (sc, conf)
            if sc is None:
                unknown.append(c)
            else:
                tot += sc * weights[c]
                wsum += weights[c]
        total = (tot / wsum) if wsum else None   # weighted average on the score scale; unknowns left out
        wall = sum(weights[c] for c in score_crit) or 1.0
        best_case = (tot + sum(float(first(crit[c], "max_score") or 3) * weights[c] for c in unknown)) / wall \
            if unknown else total
        maxs = max([float(first(crit[c], "max_score") or 3) for c in score_crit] or [3])
        results[o] = {"crit": crit_info, "final": crit_ratings, "overall": ov, "mean": mean,
                      "scores": scores, "total": total, "max": maxs, "unknown": unknown, "best_case": best_case}

    # --- sensitivity: flip unknown / low-confidence indicators one step
    def overall_with(o, override):
        cr = {}
        for c in rag_crit:
            ci = results[o]["crit"][c]
            if ci["agreed"]:
                cr[c] = ci["agreed"]; continue
            c_inds = [i for i, d in inds.items() if d["crit"] == c]
            worst = "G"
            for ph in phases_for(c_inds):
                marks = []
                for i in c_inds:
                    m = override.get((i, ph), mark_value(val(o, i, ph)[0]))
                    marks.append((i, m))
                appl = [m for _, m in marks if m not in (None, "na")]
                db = any(m == -1 and inds[i]["db"] for i, m in marks)
                if not appl and not db:
                    continue
                s_ = "R" if db else band(sum(appl) / len(appl), a.green)
                worst = min(worst, s_, key=lambda x: {"R": 0, "A": 1, "G": 2}[x])
            cr[c] = worst
        return overall_from(cr, weights, a.overall)[0] if cr else None

    marginal = collections.defaultdict(list)
    if rag_crit:
        for o in live:
            if str(results[o]["overall"]).startswith("not rated"):
                continue
            for i in inds:
                if inds[i]["crit"] not in rag_crit:
                    continue
                for ph in phases_for([i]):
                    v, conf = val(o, i, ph)
                    m = mark_value(v)
                    if m is None or conf == "L":
                        for alt in (1, -1):
                            if alt == m:
                                continue
                            if overall_with(o, {(i, ph): alt}) != str(results[o]["overall"]).split(" ")[0]:
                                marginal[o].append(f"{i}{'/' + ph if ph else ''}→{'✓' if alt == 1 else '✗'}")

    # --- checks
    spread = {}
    for c in rag_crit:
        cnt = collections.Counter(results[o]["final"][c] for o in live if results[o]["final"][c] != "–")
        spread[c] = cnt
        if cnt and max(cnt.values()) >= max(3, round(0.8 * len(live))):
            notes.append(f"SPREAD: criterion {c} gives the same rating to {max(cnt.values())} of "
                         f"{len(live)} options ({dict(cnt)}): is it separating options, or is evidence pending?")
    for c in score_crit:
        vals = [results[o]["scores"][c][0] for o in live if results[o]["scores"][c][0] is not None]
        if vals and len(set(vals)) == 1 and len(vals) > 2:
            notes.append(f"SPREAD: every scored option has {vals[0]} on {c}.")
    seen = collections.defaultdict(list)
    for i, d in inds.items():
        seen[d["text"].strip().lower()].append(f"{i} ({d['crit']})")
    for t, ids in seen.items():
        if t and len(ids) > 1:
            notes.append(f"DOUBLE COUNT: indicator '{t}' appears {len(ids)} times: {', '.join(ids)}")
    bau = [o for o, r in options.items() if yes(first(r, "is_bau"))]
    if not bau:
        notes.append("BENCHMARK: no option is flagged as BAU / do-nothing.")
    for o in bau:
        if o in knocked:
            notes.append(f"BENCHMARK: BAU option {o} was knocked out; keep it as the benchmark.")
    for o in live:
        for c, ci in results[o]["crit"].items():
            if ci["agreed"] and ci["agreed"] != ci["suggested"]:
                steps = abs(RAG_VAL.get(ci["agreed"], 0) - RAG_VAL.get(ci["suggested"], 0))
                if steps >= 2:
                    notes.append(f"OVERRIDE: {o}/{c} suggested {ci['suggested']} → agreed {ci['agreed']} "
                                 f"(two steps: needs evidence, not just preference).")
    # consistency: within a family, an indicator split ✓/✗ with no evidence recorded for one side
    fam = collections.defaultdict(list)
    for o in live:
        fam[str(first(options[o], "family") or "")].append(o)
    unexplained = []
    for f, os_ in fam.items():
        if len(os_) < 2:
            continue
        for i in inds:
            ms = {o: mark_value(val(o, i)[0]) for o in os_}
            if {m for m in ms.values() if m in (1, -1)} != {1, -1}:
                continue
            bare = [o for o, m in ms.items() if m in (1, -1)
                    and not first(ratings.get((o, i, ""), {}), "evidence")]
            if bare:
                unexplained.append(f"'{f}' {i}: ✓ {[o for o, m in ms.items() if m == 1]} vs "
                                   f"✗ {[o for o, m in ms.items() if m == -1]}")
    if unexplained:
        notes.append(f"CONSISTENCY: {len(unexplained)} indicator(s) split ✓/✗ within a family with no "
                     f"evidence recorded, e.g. " + "; ".join(unexplained[:3]) +
                     (" (full list in Results)" if len(unexplained) > 3 else ""))
    full_consistency = unexplained

    # --- scored criteria: ranking, dominance, one-step flips
    scored = [o for o in live if results[o]["total"] is not None]
    unscored = [o for o in live if o not in scored]
    ranked = (sorted(scored, key=lambda o: -results[o]["total"]) + unscored) if score_crit else live
    for o in scored:
        if results[o]["unknown"]:
            notes.append(f"INCOMPLETE: {o} has no score on {', '.join(results[o]['unknown'])}; its total uses the "
                         f"criteria it has (treat as provisional; unknowns are not counted as zero).")
    if score_crit and len(scored) > 1:
        sv = {o: [results[o]["scores"][c][0] for c in score_crit] for o in scored}
        for o2 in scored:
            for o1 in scored:
                if o1 == o2:
                    continue
                pairs = [(x, y) for x, y in zip(sv[o1], sv[o2]) if x is not None and y is not None]
                if pairs and all(x >= y for x, y in pairs) and any(x > y for x, y in pairs):
                    notes.append(f"DOMINATED: {o2} is matched or beaten by {o1} on every scored criterion, "
                                 f"so no weights can put it ahead of {o1}.")
                    break
        top = ranked[0]

        def leader(override):
            best, bv = None, None
            for o in scored:
                t, ws_ = 0.0, 0.0
                for c in score_crit:
                    v = override.get((o, c), results[o]["scores"][c][0])
                    if v is not None:
                        t += v * weights[c]; ws_ += weights[c]
                t = t / ws_ if ws_ else 0
                if bv is None or t > bv + 1e-12:
                    best, bv = o, t
            return best
        for o in scored:
            for c in score_crit:
                v = results[o]["scores"][c][0]
                if v is None:
                    continue
                mx = float(first(crit[c], "max_score") or 3)
                for alt in (v - 1, v + 1):
                    if 0 <= alt <= mx and leader({(o, c): alt}) != top:
                        marginal[o].append(f"{c}→{alt:g}")
        flips = sum(len(v) for v in marginal.values())
        if flips:
            notes.append(f"MARGINAL: {flips} single one-point score change(s) would change which option is top "
                         f"(listed per option in Results); confirm those scores first.")
    bau_unscored = [o for o in unscored if yes(first(options[o], "is_bau"))] if score_crit else []
    if bau_unscored:
        notes.append(f"BENCHMARK: business as usual ({', '.join(bau_unscored)}) has no scores; describe it in words "
                     f"as the benchmark rather than ranking it last.")
    if failed:
        notes.append("GATES: failed by " + "; ".join(f"{o} ({', '.join(gate_fail[o])})" for o in failed))

    # --- write Results
    if "Results" in wb.sheetnames:
        del wb["Results"]
    ws = wb.create_sheet("Results")
    hdr = ["option_id", "name", "family"]
    for c in rag_crit:
        hdr += [f"{c} suggested", f"{c} score", f"{c} agreed", f"{c} provisional"]
    hdr += ["overall (suggested from final criteria)", "mean"]
    for c in score_crit:
        hdr += [f"{c} score", f"{c} conf"]
    if score_crit:
        hdr += ["weighted average score", "scale max", "criteria not scored", "best case if unknowns resolve well"]
    hdr += ["marginal (flips that change overall)"]
    ws.append(hdr)
    for o in ranked:
        r = results[o]
        row = [o, first(options[o], "name"), first(options[o], "family")]
        for c in rag_crit:
            ci = r["crit"][c]
            row += [ci["suggested"], ci["score"], ci["agreed"] or "", "yes" if ci["provisional"] else ""]
        row += [r["overall"], r["mean"]]
        for c in score_crit:
            row += [r["scores"][c][0], r["scores"][c][1]]
        if score_crit:
            row += [round(r["total"], 3) if r["total"] is not None else "not scored", r["max"],
                    ", ".join(r["unknown"]), round(r["best_case"], 3) if r["best_case"] is not None else ""]
        row += ["; ".join(marginal.get(o, []))]
        ws.append(row)
    for o in knocked:
        ws.append([o, first(options[o], "name"), first(options[o], "family"), "KNOCKED OUT: " +
                   str(first(options[o], "knock_out_reason") or "")])
    for o in failed:
        ws.append([o, first(options[o], "name"), first(options[o], "family"), "FAILED GATE: " +
                   ", ".join(gate_fail[o])])
    ws.append([])
    ws.append(["CHECKS"])
    for n in notes or ["No issues flagged."]:
        ws.append([n])
    if full_consistency:
        ws.append([])
        ws.append(["UNEXPLAINED SPLITS WITHIN FAMILIES"])
        for u in full_consistency:
            ws.append([u])
    for c in ws[1]:
        c.font = Font(bold=True)
    wb.save(a.out or a.workbook)

    # --- console summary
    print(f"Options assessed: {len(live)}; knocked out: {len(knocked)}" +
          (f"; failed a gate: {len(failed)}" if failed else ""))
    for o in ranked:
        r = results[o]
        line = f"  {o:>4} {str(first(options[o], 'name'))[:32]:32}"
        if rag_crit:
            line += " " + " ".join(f"{c}:{r['final'][c]}" for c in rag_crit) + f" → {r['overall']} ({r['mean']})"
        if score_crit:
            line += (f"  score {r['total']:.2f}/{r['max']:g}" if r["total"] is not None else "  not scored") + \
                (f" (missing {len(r['unknown'])})" if r["unknown"] and r["total"] is not None else "")
        if marginal.get(o):
            line += "  MARGINAL"
        print(line)
    print("Checks:")
    for n in notes or ["  No issues flagged."]:
        print("  - " + n)
    if rag_crit and all(str(results[o]["overall"]).startswith("not rated") for o in live):
        print("Nothing has been rated yet: fill the Ratings tab (or let the group score) before reading any results.")
    print(f"Results written to {a.out or a.workbook} (tab 'Results'). All ratings are suggestions until agreed.")
    if a.json:
        json.dump({o: {k: v for k, v in results[o].items()} for o in results}, open(a.json, "w"),
                  default=str, indent=1)


# ---------------------------------------------------------------- thresholds
def cmd_thresholds(a):
    """rules JSON: {"exclude": {"CA": "existing market"},
                    "steps": [{"name": "Market size", "any": [{"col": "students", "op": ">=", "value": 500000}, ...]},
                              {"name": "Budget", "all": [{"col": "funding_per_student", "op": ">=", "value": 20000}]}],
                    "sensitivity": 0.1}"""
    data = list(csv.DictReader(open(a.csv, newline="", encoding="utf-8-sig")))
    rules = json.load(open(a.rules))
    key = a.key or list(data[0].keys())[0]
    ops = {">=": lambda x, y: x >= y, ">": lambda x, y: x > y, "<=": lambda x, y: x <= y,
           "<": lambda x, y: x < y, "==": lambda x, y: x == y, "in": lambda x, y: x in y}

    def num(v):
        try:
            return float(str(v).replace(",", "").replace("$", ""))
        except ValueError:
            return str(v).strip()

    UNKNOWN = ("", "?", "unknown", "unclear", "tbc", "n/a", "na")

    def test(row, cond, scale=1.0):
        raw = str(row.get(cond["col"], "")).strip().lower()
        if raw in UNKNOWN:
            return "unknown"
        x = num(row.get(cond["col"], ""))
        y = cond["value"]
        if isinstance(y, (int, float)) and cond["op"] in (">=", ">", "<=", "<"):
            y = y * scale
        try:
            return ops[cond["op"]](x, y)
        except TypeError:
            return False

    def passes(row, step, scale=1.0, strict=False):
        """True, False, or 'unknown' (treated as a provisional pass unless strict)."""
        res = [test(row, c, scale) for c in step.get("any", step.get("all", []))]
        if "any" in step:
            out = True if True in res else ("unknown" if "unknown" in res else False)
        else:
            out = False if False in res else ("unknown" if "unknown" in res else True)
        return out if not strict else out is True

    excl = rules.get("exclude", {})
    pool = [r for r in data if r[key] not in excl]
    print(f"Start: {len(data)}; pre-excluded {len(data) - len(pool)}: " +
          "; ".join(f"{k} ({v})" for k, v in excl.items()))
    counts, cur, provisional = [], pool, collections.defaultdict(list)
    for st in rules["steps"]:
        nxt = [r for r in cur if passes(r, st) is not False]
        for r in nxt:
            if passes(r, st) == "unknown":
                provisional[r[key]].append(st["name"])
        counts.append((st["name"], len(nxt)))
        print(f"  after {st['name']}: {len(nxt)}")
        cur = nxt
    print("Shortlist: " + ", ".join(r[key] + (" (provisional)" if r[key] in provisional else "") for r in cur))
    if provisional:
        print("Provisional passes (data unknown, not counted as a fail): " +
              "; ".join(f"{k}: {', '.join(v)}" for k, v in provisional.items()))
    # near-misses: fail exactly one step and pass all others
    def miss(r, st):
        """How far a numeric condition is missed, as a share of the threshold (closest condition)."""
        best = None
        for c in st.get("any", st.get("all", [])):
            x, y = num(r.get(c["col"], "")), c["value"]
            if isinstance(x, float) and isinstance(y, (int, float)) and y and c["op"] in (">=", ">", "<=", "<"):
                gap = abs(x - y) / abs(y)
                best = gap if best is None else min(best, gap)
        return best
    near = []
    for r in pool:
        fails = [st for st in rules["steps"] if passes(r, st) is False]
        if len(fails) == 1:
            g = miss(r, fails[0])
            near.append((g if g is not None else 9, f"{r[key]} (fails only {fails[0]['name']}" +
                         (f", by {g:.0%}" if g is not None else "") + ")"))
    if near:
        print("Near-misses (fail only one step; closest first): " + "; ".join(t for _, t in sorted(near)))
    if a.out:
        with open(a.out, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["name", "status", "reason"])
            for r in data:
                if r[key] in excl:
                    w.writerow([r[key], "excluded", excl[r[key]]])
                    continue
                fails = [st["name"] for st in rules["steps"] if passes(r, st) is False]
                if fails:
                    w.writerow([r[key], "failed", "fails " + ", ".join(fails)])
                else:
                    w.writerow([r[key], "provisional" if r[key] in provisional else "passed",
                                "; ".join(provisional.get(r[key], []))])
        print(f"Status of every candidate written to {a.out}")
    s = rules.get("sensitivity", 0.1)
    print(f"Sensitivity (each step's numeric thresholds moved ±{int(s*100)}%, others unchanged):")
    for idx, st in enumerate(rules["steps"]):
        conds = st.get("any", []) + st.get("all", [])
        if not any(isinstance(c["value"], (int, float)) and c["op"] in (">=", ">", "<=", "<") for c in conds):
            print(f"  {st['name']}: not numeric; test qualitatively (who is borderline, and why?)")
            continue
        for label, scale in (("loosened", 1 - s), ("tightened", 1 + s)):
            # 'loosened' means easier to pass for >= tests
            cur2 = pool
            for j, st2 in enumerate(rules["steps"]):
                sc = scale if j == idx else 1.0
                if j == idx and any(c["op"] in ("<=", "<") for c in st2.get("any", []) + st2.get("all", [])):
                    sc = 2 - scale
                cur2 = [r for r in cur2 if passes(r, st2, sc) is not False]
            added = sorted({r[key] for r in cur2} - {r[key] for r in cur})
            removed = sorted({r[key] for r in cur} - {r[key] for r in cur2})
            print(f"  {st['name']} {label}: {len(cur2)} pass" +
                  (f"; adds {added}" if added else "") + (f"; removes {removed}" if removed else ""))


# ---------------------------------------------------------------- diagnose
def cmd_diagnose(a):
    """CSV: first column = activity, other columns = organisations, cells = A / AD / D / S / blank."""
    rdr = list(csv.reader(open(a.csv, newline="", encoding="utf-8-sig")))
    hdr, body = rdr[0], rdr[1:]
    w = csv.writer(open(a.out, "w", newline="")) if a.out else None
    out_hdr = ["activity", "accountable", "deliverers", "supporters", "suggested_issue", "suggested_action", "note"]
    if w:
        w.writerow(out_hdr)
    actions = {1: "Document and signpost", 2: "Add stakeholders", 3: "Clarify and redistribute",
               4: "Confirm ownership", 5: "Establish new remit", 6: "Stop activity"}
    tally = collections.Counter()
    for r in body:
        act, cells = r[0], [c.strip().upper() for c in r[1:]]
        acc = [hdr[i + 1] for i, c in enumerate(cells) if c in ("A", "AD")]
        dlv = [hdr[i + 1] for i, c in enumerate(cells) if c in ("D", "AD")]
        sup = [hdr[i + 1] for i, c in enumerate(cells) if c == "S"]
        if not (acc or dlv or sup):
            iss, note = 5, "No organisation involved"
        elif len(acc) >= 2:
            iss, note = 4, "Several organisations accountable"
        elif acc and not dlv:
            iss, note = 2, "Accountable owner but no deliverer: check for under-investment"
        elif len(dlv) >= 2:
            iss, note = 3, "Several deliverers: judgement: desirable (1) or undesirable (3) duplication?"
        elif not acc:
            iss, note = 4, "Delivered but nobody accountable"
        else:
            iss, note = 1, ""
        tally[iss] += 1
        row = [act, "/".join(acc), "/".join(dlv), "/".join(sup), iss, actions[iss], note]
        if w:
            w.writerow(row)
        else:
            print(" | ".join(map(str, row)))
    print("Suggested issue types:", dict(sorted(tally.items())),
          "(6 'unnecessary activity' is judgement-only; the group confirms all suggestions)")


# ---------------------------------------------------------------- matrix (impact x availability)
def cmd_matrix(a):
    """CSV: first column activity; columns starting 'impact' and 'availability' hold 1-3 scores."""
    data = list(csv.DictReader(open(a.csv, newline="", encoding="utf-8-sig")))
    cols = list(data[0].keys())
    key = cols[0]
    imp = [c for c in cols if c.lower().startswith("impact")]
    av = [c for c in cols if c.lower().startswith("avail")]
    if not imp or not av:
        raise SystemExit("Need columns starting 'impact' and 'availability'.")

    def avg(r, cs):
        v = []
        for c in cs:
            try:
                v.append(float(r[c]))
            except (TypeError, ValueError):
                pass
        return sum(v) / len(v) if v else None
    pts = [(r[key], avg(r, imp), avg(r, av)) for r in data]
    pts_ok = [p for p in pts if p[1] is not None and p[2] is not None]
    n = a.grid
    if a.bands == "relative":
        def cuts(xs):
            xs = sorted(xs)
            return [xs[int(len(xs) * k / n)] for k in range(1, n)]
        ci, ca = cuts([p[1] for p in pts_ok]), cuts([p[2] for p in pts_ok])
    else:
        fixed = {3: [1.67, 2.34], 4: [1.5, 2.0, 2.5]}[n]
        ci = ca = fixed

    def band(x, cut):
        return sum(1 for c in cut if x >= c)   # 0 = low … n-1 = high
    names = {3: ["low", "medium", "high"], 4: ["low", "lower-mid", "upper-mid", "high"]}[n]

    def zone(bi, ba):
        hi, lo = n - 1, 0
        if bi == hi and ba == hi:
            return "Principal priority"
        if bi == hi and ba == lo:
            return "Longer-term roadmap"
        if bi == lo and ba == hi:
            return "Easy extra"
        if bi == lo and ba == lo:
            return "Hand over or deprioritise"
        return "Judgement (record the call)"
    out, grid = [], collections.Counter()
    for name, i, v in pts:
        if i is None or v is None:
            out.append([name, i, v, "", "", "not scored"])
            continue
        bi, ba = band(i, ci), band(v, ca)
        grid[(bi, ba)] += 1
        out.append([name, round(i, 2), round(v, 2), names[bi], names[ba], zone(bi, ba)])
    if a.out:
        with open(a.out, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["activity", "impact", "availability", "impact band", "availability band", "zone"])
            w.writerows(out)
    print(f"{len(pts_ok)} activities placed on a {n}x{n} grid ({a.bands} bands"
          + (f": impact cuts {[round(x, 2) for x in ci]}, availability cuts {[round(x, 2) for x in ca]}" if a.bands == "relative" else "") + ")")
    print("Counts (rows = impact high→low, columns = availability low→high):")
    for bi in reversed(range(n)):
        print(f"  {names[bi]:>9} | " + " ".join(f"{grid[(bi, ba)]:>4}" for ba in range(n)))
    zc = collections.Counter(r[5] for r in out)
    print("Zones: " + "; ".join(f"{k} {v}" for k, v in zc.most_common()))
    mid = zc.get("Judgement (record the call)", 0)
    if pts_ok and mid / len(pts_ok) > 0.5:
        print(f"WARNING: {mid} of {len(pts_ok)} land in judgement cells. Averages of a few 1-3 scores bunch in the middle: "
              "try --bands relative, --grid 4, or sharper level definitions.")
    for lab, idx in (("impact", 1), ("availability", 2)):
        bs = collections.Counter(band(p[idx], ci if idx == 1 else ca) for p in pts_ok)
        if pts_ok and max(bs.values()) / len(pts_ok) > 0.7:
            print(f"WARNING: {lab} barely separates the activities ({max(bs.values())} of {len(pts_ok)} in one band); "
                  "revisit that axis before drawing conclusions.")


# ---------------------------------------------------------------- sensitivity (weighted scores)
def _read_scores(path):
    """CSV: first column option name; other columns criteria; optional row named _weight."""
    rdr = list(csv.reader(open(path, newline="", encoding="utf-8-sig")))
    crits = [c.strip() for c in rdr[0][1:]]
    weights, opts = None, {}
    for r in rdr[1:]:
        if not r or not r[0].strip():
            continue
        vals = [float(x) if str(x).strip() not in ("", "?") else None for x in r[1:1 + len(crits)]]
        if r[0].strip().lower() in ("_weight", "_weights", "weight"):
            weights = vals
        else:
            opts[r[0].strip()] = vals
    if weights is None:
        weights = [1.0] * len(crits)
    s = sum(w or 0 for w in weights) or 1.0
    return crits, [(w or 0) / s for w in weights], opts


def _totals(opts, w):
    """Weighted average over the criteria each option has scores for (unknowns are left out, not zero)."""
    out = {}
    for o, vals in opts.items():
        t = sum(v * wi for v, wi in zip(vals, w) if v is not None)
        ws = sum(wi for v, wi in zip(vals, w) if v is not None)
        out[o] = t / ws if ws else 0.0
    return out


def cmd_sensitivity(a):
    crits, w, opts = _read_scores(a.csv)
    if a.rescale:  # MCDA 0-100 per criterion, worst=0 best=100
        for j in range(len(crits)):
            col = [v[j] for v in opts.values() if v[j] is not None]
            lo, hi = min(col), max(col)
            for o in opts:
                if opts[o][j] is not None:
                    opts[o][j] = 100.0 * (opts[o][j] - lo) / (hi - lo) if hi > lo else 100.0
    tot = _totals(opts, w)
    rank = sorted(tot, key=lambda o: -tot[o])
    top, second = rank[0], rank[1] if len(rank) > 1 else None
    print("Weights (normalised): " + ", ".join(f"{c}={wi:.2f}" for c, wi in zip(crits, w)))
    missing = {o: [c for c, v in zip(crits, vals) if v is None] for o, vals in opts.items()}
    for o, m in missing.items():
        if m:
            print(f"NOTE: {o} has no score on {', '.join(m)}: its total averages the criteria it has (provisional).")
    # criteria that move together may be double counting (or trade off strongly)
    def corr(j, k):
        pairs = [(v[j], v[k]) for v in opts.values() if v[j] is not None and v[k] is not None]
        if len(pairs) < 4:
            return None
        xs, ys = zip(*pairs)
        mx_, my_ = sum(xs) / len(xs), sum(ys) / len(ys)
        sx = sum((x - mx_) ** 2 for x in xs) ** 0.5
        sy = sum((y - my_) ** 2 for y in ys) ** 0.5
        return None if not sx or not sy else sum((x - mx_) * (y - my_) for x, y in pairs) / (sx * sy)
    for j in range(len(crits)):
        for k in range(j + 1, len(crits)):
            r_ = corr(j, k)
            if r_ is not None and r_ >= 0.8:
                print(f"NOTE: {crits[j]} and {crits[k]} move together (correlation {r_:.2f}): check they aren't measuring the same thing.")
            elif r_ is not None and r_ <= -0.8:
                print(f"NOTE: {crits[j]} and {crits[k]} trade off strongly (correlation {r_:.2f}): the ranking will mostly reflect how they're weighted.")
    if len(crits) <= 3:
        print(f"NOTE: with only {len(crits)} criteria, the ranking depends heavily on the weights: show the weight ranges below.")
    smax = a.scale_max if a.scale_max is not None else max(v for vals in opts.values() for v in vals if v is not None)
    smin = min(v for vals in opts.values() for v in vals if v is not None) if a.scale_max is None else 0
    print("Ranking: " + ", ".join(f"{o} {tot[o]:.2f}" for o in rank))
    if a.rescale:
        print("(Scores rescaled 0-100 per criterion; totals are on an interval scale: compare differences, not ratios.)")

    # dominance: list each dominated option once
    by = collections.defaultdict(list)
    for o1, v1 in opts.items():
        for o2, v2 in opts.items():
            pairs = [(x, y) for x, y in zip(v1, v2) if x is not None and y is not None]
            if o1 != o2 and pairs and all(x >= y for x, y in pairs) and any(x > y for x, y in pairs):
                by[o2].append(o1)
    undominated = [o for o in rank if o not in by]
    if by:
        print(f"Options no other option beats on every criterion ({len(undominated)}): " + ", ".join(undominated))
    else:
        print("No option is beaten on every criterion by another (no dominated options).")
    if by:
        print(f"Dominated ({len(by)}; each is matched or beaten on every criterion): " +
              "; ".join(f"{o} (e.g. by {by[o][0]}{' +' + str(len(by[o]) - 1) if len(by[o]) > 1 else ''})"
                        for o in rank if o in by))

    # value for cost (cost kept out of the weighted benefit score)
    if a.cost:
        cost = {}
        for r in csv.DictReader(open(a.cost, newline="", encoding="utf-8-sig")):
            k = list(r.keys())
            cost[r[k[0]].strip()] = float(r[k[1]])
        pts = [(cost[o], tot[o], o) for o in opts if o in cost]
        frontier = [o for c, b, o in pts if not any((c2 <= c and b2 >= b and (c2 < c or b2 > b)) for c2, b2, _ in pts)]
        print("Value-for-cost frontier (no other option is both cheaper-or-equal and better): " +
              ", ".join(f"{o} (cost {cost[o]:g}, benefit {tot[o]:.2f})" for o in sorted(frontier, key=lambda o: cost[o])))
    if not second:
        return

    # weight switching values: vary one weight 0..1, others keep their relative proportions
    print(f"\nWeight sensitivity (does '{top}' stay first?):")
    for j, c in enumerate(crits):
        stays, flips = [], []
        for k in range(0, 101):
            wj = k / 100
            rest = sum(w) - w[j]
            w2 = [wj if i == j else (w[i] / rest * (1 - wj) if rest else 0) for i in range(len(w))]
            t2 = _totals(opts, w2)
            leader = max(t2, key=t2.get)
            (stays if leader == top else flips).append((wj, leader))
        if not flips:
            print(f"  {c}: '{top}' stays first for any weight 0-1 (current {w[j]:.2f})")
        else:
            lo = min(x for x, _ in stays) if stays else None
            hi = max(x for x, _ in stays) if stays else None
            nxt = sorted({l for _, l in flips})
            print(f"  {c}: '{top}' first for weights {lo:.2f}-{hi:.2f} (current {w[j]:.2f}); otherwise {', '.join(nxt)}")

    # score switching values for top vs runner-up
    margin = tot[top] - tot[second]
    print(f"\nScore switching values ('{top}' leads '{second}' by {margin:.2f}): change needed on one criterion to close the gap")
    span = smax - smin
    for j, c in enumerate(crits):
        if w[j] > 0:
            need = margin / w[j]
            print(f"  {c}: {top} down by {need:.2f} or {second} up by {need:.2f} (score units)" +
                  ("  (more than the whole scale: no single change on this criterion can do it)" if need > span else ""))

    # tornado on weights: +/- a.swing (proportion) of each weight, effect on top-vs-second margin
    print(f"\nTornado (each weight ±{int(a.swing*100)}%, others renormalised): margin '{top}' minus '{second}'")
    rows_ = []
    for j, c in enumerate(crits):
        res = []
        for f in (1 - a.swing, 1 + a.swing):
            w2 = list(w); w2[j] = w[j] * f
            s2 = sum(w2); w2 = [x / s2 for x in w2]
            t2 = _totals(opts, w2)
            res.append(t2[top] - t2[second])
        rows_.append((abs(res[1] - res[0]), c, res))
    for spread, c, (lo, hi) in sorted(rows_, reverse=True):
        print(f"  {c:20} low {lo:+.2f}  high {hi:+.2f}  swing {spread:.2f}")

    # random weights: how often is each option first / in the top k?
    if a.random:
        import random
        rnd = random.Random(1)
        k = max(1, a.top_k)
        first_n, topk_n = collections.Counter(), collections.Counter()
        for _ in range(a.random):
            g = [rnd.gammavariate(1.0, 1.0) for _ in w]
            sg = sum(g)
            t2 = _totals(opts, [x / sg for x in g])
            order = sorted(t2, key=lambda o: -t2[o])
            first_n[order[0]] += 1
            for o in order[:k]:
                topk_n[o] += 1
        print(f"\nRandom weights ({a.random} sets drawn uniformly over all possible weightings):")
        for o in rank:
            print(f"  {o:20} first {first_n[o] / a.random:5.0%}" + (f"   in top {k} {topk_n[o] / a.random:5.0%}" if k > 1 else ""))
        print("  Read with care: this ignores your agreed weights. It shows how much the ranking depends on weighting at all.")
    if a.top_k and a.top_k > 1:
        k = a.top_k
        base = set(rank[:k])
        print(f"\nTop-{k} stability (one weight moved 0-1 at a time, others in proportion): current top {k} = {sorted(base)}")
        for j, c in enumerate(crits):
            same = {}
            for step in range(0, 101):
                wj = step / 100
                rest = sum(w) - w[j]
                w2 = [wj if i == j else (w[i] / rest * (1 - wj) if rest else 0) for i in range(len(w))]
                t2 = _totals(opts, w2)
                same[step] = set(sorted(t2, key=lambda o: -t2[o])[:k])
            cur = int(round(w[j] * 100))
            lo_ = cur
            while lo_ > 0 and same[lo_ - 1] == base:
                lo_ -= 1
            hi_ = cur
            while hi_ < 100 and same[hi_ + 1] == base:
                hi_ += 1
            if lo_ == 0 and hi_ == 100:
                print(f"  {c}: top {k} unchanged for any weight")
            else:
                ins = sorted({o for v in same.values() for o in v - base})
                print(f"  {c}: top {k} holds for weights {lo_ / 100:.2f}-{hi_ / 100:.2f} (current {w[j]:.2f}); "
                      f"outside that, could bring in {', '.join(ins)}")


# ---------------------------------------------------------------- payoff tables (EV, EVPI, regret)
def cmd_payoff(a):
    """CSV: first column option; other columns scenarios; optional row _prob with probabilities."""
    rdr = list(csv.reader(open(a.csv, newline="", encoding="utf-8-sig")))
    scen = [s.strip() for s in rdr[0][1:]]
    probs, pay = None, {}
    for r in rdr[1:]:
        if not r or not r[0].strip():
            continue
        vals = [float(x) for x in r[1:1 + len(scen)]]
        if r[0].strip().lower() in ("_prob", "_probability", "prob"):
            probs = vals
        else:
            pay[r[0].strip()] = vals
    best = [max(v[j] for v in pay.values()) for j in range(len(scen))]
    regret = {o: [best[j] - v[j] for j in range(len(scen))] for o, v in pay.items()}
    print("Regret table (best payoff in scenario minus this option's payoff):")
    print("  " + " | ".join(["option"] + scen + ["max regret"]))
    for o in pay:
        print("  " + " | ".join([o] + [f"{x:g}" for x in regret[o]] + [f"{max(regret[o]):g}"]))
    mm = min(pay, key=lambda o: max(regret[o]))
    print(f"Minimax regret choice: {mm}")
    if a.threshold is not None:
        print(f"Satisficing (share of scenarios with payoff >= {a.threshold:g}):")
        for o, v in pay.items():
            share = sum(1 for x in v if x >= a.threshold) / len(v)
            if probs:
                pshare = sum(p for x, p in zip(v, probs) if x >= a.threshold)
                print(f"  {o}: {share:.0%} of scenarios; probability {pshare:.0%}")
            else:
                print(f"  {o}: {share:.0%} of scenarios")
    if probs:
        if abs(sum(probs) - 1) > 1e-6:
            print(f"WARNING: probabilities sum to {sum(probs):.3f}, not 1")
        ev = {o: sum(p * x for p, x in zip(probs, v)) for o, v in pay.items()}
        bo = max(ev, key=ev.get)
        evpi_val = sum(p * b for p, b in zip(probs, best)) - ev[bo]
        print("Expected values: " + ", ".join(f"{o} {ev[o]:g}" for o in pay) + f"  → best now: {bo}")
        print(f"EV with perfect information: {ev[bo] + evpi_val:g}; EVPI = {evpi_val:g} "
              f"(the most it is worth paying to resolve the uncertainty; imperfect information is worth less)")
        if len(scen) == 2:  # probability switching values
            print(f"Best option by P({scen[0]}) (switching values):")
            prev = None
            for k in range(0, 101):
                p = k / 100
                b = max(pay, key=lambda o: p * pay[o][0] + (1 - p) * pay[o][1])
                if b != prev:
                    print(f"  from P = {p:.2f}: {b}")
                    prev = b
    else:
        print("No _prob row: expected value and EVPI not computed (use regret / satisficing).")


# ---------------------------------------------------------------- decision tree (delegates)
def cmd_tree(a):
    """Kept for compatibility: the full tool is scripts/uncertainty.py tree."""
    import os, subprocess
    here = os.path.dirname(os.path.abspath(__file__))
    sys.exit(subprocess.call([sys.executable, os.path.join(here, "uncertainty.py"), "tree", a.json_file]))


# ---------------------------------------------------------------- audit (verification)
def cmd_audit(a):
    _, wb = load_values(a.workbook)
    issues, n, blank, agreed_bare = [], 0, 0, []
    conf = collections.Counter()
    low_by_opt = collections.Counter()
    if "Ratings" not in wb.sheetnames:
        print("No Ratings tab: this method doesn't use ratings, so only claims are checked.")
    for r in (rows(wb["Ratings"]) if "Ratings" in wb.sheetnames else []):
        n += 1
        o, i = first(r, "option_id"), first(r, "item_id")
        v = first(r, "agreed") if first(r, "agreed") not in (None, "") else first(r, "suggested")
        if v in (None, ""):
            blank += 1
            continue
        c = str(first(r, "confidence") or "").upper()[:1] or "?"
        conf[c] += 1
        if c in ("L", "?"):
            low_by_opt[o] += 1
        drafted = yes(first(r, "drafted"))
        if drafted and not first(r, "evidence"):
            issues.append(f"NO EVIDENCE: drafted rating {o}/{i} = {v}")
        if drafted and not first(r, "source"):
            issues.append(f"NO SOURCE: drafted rating {o}/{i} = {v}")
        if not drafted and not first(r, "evidence"):
            agreed_bare.append(f"{o}/{i}")
        if first(r, "agreed") not in (None, "") and first(r, "suggested") not in (None, "") \
                and str(first(r, "agreed")) != str(first(r, "suggested")) and not first(r, "override_reason"):
            issues.append(f"OVERRIDE WITHOUT REASON: {o}/{i} suggested {first(r, 'suggested')} → agreed {first(r, 'agreed')}")
    if agreed_bare:
        issues.append(f"NO EVIDENCE RECORDED for {len(agreed_bare)} agreed rating(s), e.g. {', '.join(agreed_bare[:5])}: "
                      "fine for a group judgement, but note the reasoning for any that drive the result")
    claims = list(rows(wb["Claims"])) if "Claims" in wb.sheetnames else []
    ctype = collections.Counter(str(first(c, "type") or "?").lower().split()[0] for c in claims)
    for c in claims:
        t = str(first(c, "type") or "").lower()
        if not first(c, "source"):
            issues.append(f"CLAIM WITHOUT SOURCE: {first(c, 'claim_id')} '{str(first(c, 'claim'))[:60]}'"
                          + (" (label as inference/unknown)" if t.startswith("fact") else ""))
        if not first(c, "checked"):
            issues.append(f"CLAIM NOT CHECKED: {first(c, 'claim_id')}" +
                          (" (inference/estimate: record what it rests on)" if t.startswith(("inf", "est")) else ""))
        if not first(c, "date"):
            issues.append(f"CLAIM UNDATED: {first(c, 'claim_id')} (enter a date, or 'undated' if the source has none)")
    print(f"Ratings: {n} rows, {blank} not yet rated; confidence profile of rated: " +
          (", ".join(f"{k}={v}" for k, v in sorted(conf.items())) or "none"))
    if n and blank == n:
        print("NOTHING RATED YET: no results should be read or shared until ratings are entered.")
    if low_by_opt:
        print("Low/unknown confidence by option: " + ", ".join(f"{o}={k}" for o, k in low_by_opt.most_common()))
    if claims:
        print(f"Claims: {len(claims)}; by type: " + ", ".join(f"{k}={v}" for k, v in ctype.items()))
    print(f"Issues ({len(issues)}):")
    for s_ in issues[:40]:
        print("  - " + s_)
    if len(issues) > 40:
        print(f"  … and {len(issues) - 40} more")
    print("Manual checks still needed: re-derive numbers in the outputs; re-open sources behind top options, "
          "knock-outs and deal-breakers; check currency of guidance and volatile facts; labels on drafted content.")


# ---------------------------------------------------------------- main
def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("init", help="create the appraisal workbook")
    s.add_argument("--choice", "--archetype", dest="choice", default="", help="type of choice (Tree 1)")
    s.add_argument("--methods", default="", help="comma-separated methods; adds tabs they need (e.g. decision-tree)")
    s.add_argument("--rulebook", default="")
    s.add_argument("--depth", default="")
    s.add_argument("--scorers", action="store_true", help="add a 'Scores by person' tab for private scoring")
    s.add_argument("--scores", help="import options, criteria, weights and scores from a CSV (as for sensitivity)")
    s.add_argument("--scale-max", type=float, help="top of the scoring scale when importing")
    s.add_argument("--rescale", action="store_true", help="when importing raw data, rescale each criterion 0-100")
    s.add_argument("--drafted", action="store_true", help="import scores as drafted suggestions, not agreed scores")
    s.add_argument("--excluded", help="CSV of screened-out options (e.g. thresholds --out) to list as knocked out")
    s.add_argument("--out", default="appraisal.xlsx")
    s.set_defaults(f=cmd_init)
    s = sp.add_parser("spread", help="private scoring: spread per option x item, and median as suggestion")
    s.add_argument("workbook")
    s.add_argument("--threshold", type=float, default=2, help="range that flags a cell for discussion (default 2)")
    s.add_argument("--suggest", action="store_true", help="write the median into Ratings as the suggested score")
    s.add_argument("--out")
    s.set_defaults(f=cmd_spread)
    s = sp.add_parser("rollup", help="roll up ratings and run checks")
    s.add_argument("workbook")
    s.add_argument("--out", help="write to a new file instead of overwriting")
    s.add_argument("--green", type=float, default=0.4, help="criterion Green threshold (default 0.4)")
    s.add_argument("--overall", type=float, default=0.5, help="overall Green threshold (default 0.5)")
    s.add_argument("--json", help="also dump results as JSON")
    s.set_defaults(f=cmd_rollup)
    s = sp.add_parser("matrix", help="impact x availability grid from a CSV of 1-3 scores")
    s.add_argument("csv")
    s.add_argument("--grid", type=int, choices=[3, 4], default=3)
    s.add_argument("--bands", choices=["fixed", "relative"], default="fixed",
                   help="fixed cut-offs, or relative (split the activities into equal-sized bands)")
    s.add_argument("--out", help="write placements to this CSV")
    s.set_defaults(f=cmd_matrix)
    s = sp.add_parser("thresholds", help="sequential threshold filter with sensitivity",
                      formatter_class=argparse.RawDescriptionHelpFormatter, description='''
Rules JSON:
  {"exclude": {"Home region": "already operating there"},
   "steps": [{"name": "Market size", "any": [{"col": "users", "op": ">=", "value": 150},
                                            {"col": "sites", "op": ">=", "value": 20}]},
             {"name": "Policy support", "all": [{"col": "support", "op": "in", "value": ["yes"]}]}],
   "sensitivity": 0.1}
"any" passes if one condition holds, "all" if every one does. ops: >= > <= < == in.
Blank or "unclear" values are provisional passes. Near-misses fail exactly one step.
--out writes every candidate with its status, ready for `init --scores ... --excluded`.''')
    s.add_argument("csv")
    s.add_argument("rules")
    s.add_argument("--key", help="column holding the candidate name (default: first column)")
    s.add_argument("--out", help="write each candidate's status (passed / provisional / failed step) to this CSV")
    s.set_defaults(f=cmd_thresholds)
    s = sp.add_parser("diagnose", help="suggest issue types from an A/AD/D/S matrix")
    s.add_argument("csv")
    s.add_argument("--out")
    s.set_defaults(f=cmd_diagnose)
    s = sp.add_parser("sensitivity", help="weighted-score ranking, dominance, weight/score switching values, tornado")
    s.add_argument("csv", help="options x criteria scores; optional row named _weight")
    s.add_argument("--rescale", action="store_true", help="rescale each criterion 0-100 (worst-best), MCDA style")
    s.add_argument("--swing", type=float, default=0.5, help="tornado: proportional change in each weight (default 0.5)")
    s.add_argument("--cost", help="CSV of option,cost (kept out of the benefit score) to show the value-for-cost frontier")
    s.add_argument("--scale-max", type=float, help="top of the scoring scale (default: highest score seen)")
    s.add_argument("--top-k", type=int, default=1, help="also test the stability of the top k (e.g. choosing 3 regions)")
    s.add_argument("--random", type=int, default=0, help="also draw this many random weight sets (e.g. 10000)")
    s.set_defaults(f=cmd_sensitivity)
    s = sp.add_parser("payoff", help="payoff table: expected value, EVPI, regret, satisficing")
    s.add_argument("csv", help="options x scenarios payoffs; optional row named _prob")
    s.add_argument("--threshold", type=float, help="minimum acceptable payoff for satisficing")
    s.set_defaults(f=cmd_payoff)
    s = sp.add_parser("audit", help="verification: evidence/source coverage, overrides, confidence, claim ledger")
    s.add_argument("workbook")
    s.set_defaults(f=cmd_audit)
    s = sp.add_parser("tree", help="roll back a decision tree written as JSON")
    s.add_argument("json_file")
    s.set_defaults(f=cmd_tree)
    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
