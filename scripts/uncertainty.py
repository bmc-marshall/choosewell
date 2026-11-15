#!/usr/bin/env python3
"""
uncertainty.py - probability-weighted payoffs for choosewell.

Subcommands
  tree   Fold back a decision tree written as JSON: value of each option, the recommended strategy
         (what to do at every later decision), risk profiles (chance of a loss, worst and best case),
         optional risk attitude (exponential utility, certainty equivalents), one- and two-way
         sensitivity with exact break-even values, a tornado, and export to a live Excel workbook.
  voi    Value of information from a payoff table: expected value now, the most perfect information
         is worth (EVPI), and what an imperfect test or study is worth (EVSI) given how reliable it is.
  bayes  "Tree flip": turn a prior and a test's reliability into the chance of each result and the
         updated (posterior) probabilities; combines several tests if they're independent given the truth.

All numbers are as good as the estimates behind them: run the sensitivity options before relying on a result.

TREE JSON (see references/methods/quantified-tree.md for a worked example)
  {"units": "$m", "objective": "max",          # "min" if the payoffs are costs
   "params": {"p_ok": 0.6,                     # named inputs; any number below may be an expression of these
              "build": {"value": 80, "low": 60, "high": 110, "source": "QS estimate, Mar 2026"}},
                                               # an input may carry its range and source: used by
                                               # --tornado auto and written to the Excel Inputs sheet
   "subtrees": {"launch": {...}},              # optional reusable pieces
   "tree": NODE}
  NODE is one of
   {"type": "decision", "name": "...", "options":  [{"label": "...", "cost": e, "cash": e, "node": NODE}, ...]}
   {"type": "chance",   "name": "...", "branches": [{"label": "...", "p": e, "cost": e, "cash": e, "node": NODE}, ...]}
   {"value": e}                                # end point: payoff from here on (default 0)
   {"use": "launch", "with": {"p_ok": "p_ok_after_good_test"}}   # reuse a subtree with local inputs
  "cost" is subtracted and "cash" added where it occurs in time; enter each amount once, never twice.
  The last branch of a chance node may omit "p" (it gets the remainder).
  Check whether the user's payoff figures already net off costs before adding costs as branches.

VOI JSON (see assets/examples/pilot-value.json)
  {"units": "£k", "objective": "max", "params": {...},
   "states":  {"would succeed": 0.4, "would fail": 0.6},                  # prior probabilities
   "actions": {"Roll out": {"would succeed": 900, "would fail": -400},    # payoff of each action in each state
               "Don't":    {"would succeed": 0,   "would fail": 0}},
   "tests": [{"name": "Pilot", "cost": 40,
              "signals": {"Good": {"would succeed": 0.8, "would fail": 0.3},  # P(result | state)
                          "Poor": {"would succeed": 0.2, "would fail": 0.7}}}]}
  A single listed signal gets its complement automatically. voi assumes every action is still available,
  at the same payoff, after the test result: if waiting for the result costs something (delay, a lapsing
  offer), model it as a tree instead.

BAYES JSON (see assets/examples/tree-flip.json)
  {"prior": {"state": p, ...}, "tests": {"test name": {"result": {"state": P(result|state), ...}, ...}}}
"""
import argparse, ast, copy, json, math, sys, itertools, collections

# ------------------------------------------------------------------ expressions
_BIN = {ast.Add: ("+", lambda a, b: a + b), ast.Sub: ("-", lambda a, b: a - b),
        ast.Mult: ("*", lambda a, b: a * b), ast.Div: ("/", lambda a, b: a / b),
        ast.Pow: ("**", lambda a, b: a ** b)}
_FUN = {"min": min, "max": max, "abs": abs}


def _parse(e):
    if isinstance(e, ast.AST):
        return copy.deepcopy(e)
    if isinstance(e, (int, float)):
        return ast.Constant(float(e))
    return ast.parse(str(e), mode="eval").body


def ev(e, env):
    """Safely evaluate a number or arithmetic expression of named inputs."""
    n = _parse(e) if not isinstance(e, ast.AST) else e

    def f(n):
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return float(n.value)
        if isinstance(n, ast.Name):
            if n.id not in env:
                raise SystemExit(f"Unknown input '{n.id}' (add it to params)")
            return float(env[n.id])
        if isinstance(n, ast.BinOp) and type(n.op) in _BIN:
            return _BIN[type(n.op)][1](f(n.left), f(n.right))
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.USub, ast.UAdd)):
            return -f(n.operand) if isinstance(n.op, ast.USub) else f(n.operand)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in _FUN:
            return _FUN[n.func.id](*[f(x) for x in n.args])
        raise SystemExit(f"Unsupported expression: {ast.dump(n)}")
    return f(n)


def subst(e, mapping):
    """Replace input names in an expression with other expressions (for subtree 'with')."""
    n = _parse(e)

    class T(ast.NodeTransformer):
        def visit_Name(self, node):
            return _parse(mapping[node.id]) if node.id in mapping else node
    return T().visit(n)


def emit(n, name=lambda s: s, excel=False):
    """Expression AST -> text (Python or Excel syntax)."""
    if not isinstance(n, ast.AST):
        n = _parse(n)
    if isinstance(n, ast.Constant):
        v = n.value
        return repr(int(v)) if float(v).is_integer() else repr(float(v))
    if isinstance(n, ast.Name):
        return name(n.id)
    if isinstance(n, ast.BinOp):
        op = _BIN[type(n.op)][0]
        if excel and op == "**":
            op = "^"
        return f"({emit(n.left, name, excel)}{op}{emit(n.right, name, excel)})"
    if isinstance(n, ast.UnaryOp):
        return ("-" if isinstance(n.op, ast.USub) else "+") + emit(n.operand, name, excel)
    if isinstance(n, ast.Call):
        fn = n.func.id.upper() if excel else n.func.id
        return f"{fn}(" + ",".join(emit(x, name, excel) for x in n.args) + ")"
    raise SystemExit(f"Unsupported expression: {ast.dump(n)}")


# ------------------------------------------------------------------ tree expansion
class Node:
    __slots__ = ("kind", "name", "kids", "value")

    def __init__(self, kind, name="", kids=None, value=None):
        self.kind, self.name, self.kids, self.value = kind, name, kids or [], value


class Edge:
    __slots__ = ("label", "p", "cash", "node")

    def __init__(self, label, p, cash, node):
        self.label, self.p, self.cash, self.node = label, p, cash, node


def expand(spec, subtrees, mapping=None, minimize=False):
    mapping = mapping or {}
    S = lambda e: subst(e if e is not None else 0, mapping)
    if spec is None:
        return Node("end", value=S(0))
    if "use" in spec:
        name = spec["use"]
        if name not in subtrees:
            raise SystemExit(f"Unknown subtree '{name}'")
        local = dict(mapping)
        for k, v in spec.get("with", {}).items():
            local[k] = subst(v, mapping)
        return expand(subtrees[name], subtrees, local, minimize)
    t = spec.get("type")
    if t == "decision":
        kids = []
        for o in spec["options"]:
            cash = _cash(S, o, minimize)
            kids.append(Edge(o["label"], None, cash, expand(o.get("node"), subtrees, mapping, minimize)))
        return Node("decision", spec.get("name", ""), kids)
    if t == "chance":
        kids, given = [], []
        brs = spec["branches"]
        for i, b in enumerate(brs):
            if "p" in b:
                p = S(b["p"])
            elif i == len(brs) - 1:
                p = ast.BinOp(ast.Constant(1.0), ast.Sub(), _sum(given)) if given else ast.Constant(1.0)
            else:
                raise SystemExit(f"Branch '{b.get('label')}' at '{spec.get('name','')}' needs a probability")
            given.append(p)
            cash = _cash(S, b, minimize)
            kids.append(Edge(b["label"], p, cash, expand(b.get("node"), subtrees, mapping, minimize)))
        return Node("chance", spec.get("name", ""), kids)
    return Node("end", value=S(spec.get("value", 0)))


def _cash(S, d, minimize):
    """Amount added to the running total on a branch. Maximising: cash - cost. Minimising (totals are
    costs): cost - cash, so a 'cost' always makes things worse and 'cash' (a saving) better."""
    if minimize:
        return ast.BinOp(S(d.get("cost", 0)), ast.Sub(), S(d.get("cash", 0)))
    return ast.BinOp(S(d.get("cash", 0)), ast.Sub(), S(d.get("cost", 0)))


def _sum(xs):
    out = xs[0]
    for x in xs[1:]:
        out = ast.BinOp(out, ast.Add(), x)
    return out


# ------------------------------------------------------------------ folding back
def param_values(doc):
    """Input values from a document's params (a number, or {"value": ..., "low": ..., ...})."""
    return {k: float(v["value"] if isinstance(v, dict) else v) for k, v in doc.get("params", {}).items()}


def utility(x, R):
    return 1 - math.exp(min(700.0, -x / R))   # capped so tiny risk tolerances can't overflow


def cert_equiv(eu, R):
    return -R * math.log(1 - eu) if eu < 1 else float("inf")


def score(dist, sign, R):
    if R:
        return sum(p * utility(sign * x, R) for x, p in dist)
    return sum(p * sign * x for x, p in dist)


def solve(node, env, sign=1, R=None, acc=0.0, path=(), log=None, tol=1e-9):
    """Return the payoff distribution [(total payoff, prob)] under the best policy from this node.
       log collects (path, node name, chosen label, {label: value}) for every decision visited."""
    if node.kind == "end":
        return [(acc + ev(node.value, env), 1.0)]
    if node.kind == "chance":
        out, tot = [], 0.0
        for e in node.kids:
            p = ev(e.p, env)
            if p < -tol or p > 1 + tol:
                raise SystemExit(f"Probability {p:.3f} out of range at '{node.name}' → {e.label}")
            tot += p
            for x, q in solve(e.node, env, sign, R, acc + ev(e.cash, env), path + (e.label,), log):
                out.append((x, p * q))
        if abs(tot - 1) > 1e-6:
            print(f"WARNING: probabilities at '{node.name}' sum to {tot:.4f}, not 1")
        return out
    best, bd, vals = None, None, {}
    sub = [] if log is not None else None
    for e in node.kids:
        d = solve(e.node, env, sign, R, acc + ev(e.cash, env), path + (e.label,), sub)
        s = score(d, sign, R)
        vals[e.label] = (d, s)
        if bd is None or s > bd + tol:
            best, bd = e.label, s
    if log is not None:
        log.append((path, node.name, best, vals))
        # keep only the sub-decisions under the chosen option
        log.extend(x for x in sub if x[0][len(path):len(path) + 1] == (best,))
    return vals[best][0]


def summary(dist, R=None):
    m = sum(x * p for x, p in dist)
    live = [x for x, p in dist if p > 1e-12] or [x for x, _ in dist]
    out = {"ev": m, "p_loss": sum(p for x, p in dist if x < -1e-12),
           "worst": min(live), "best": max(live)}
    if R:
        out["ce"] = cert_equiv(sum(p * utility(x, R) for x, p in dist), R)
    return out


def root_options(root, env, sign, R):
    """Value of each option at the first decision (or the whole tree if it starts with chance)."""
    if root.kind != "decision":
        return {"(tree)": solve(root, env, sign, R)}
    return {e.label: solve(e.node, env, sign, R, ev(e.cash, env)) for e in root.kids}


def find_decision(node, name):
    if node.kind == "decision" and node.name == name:
        return node
    for e in node.kids:
        r = find_decision(e.node, name)
        if r:
            return r
    return None


def find_all(node, name, out=None):
    out = [] if out is None else out
    if node.kind == "decision" and node.name == name:
        out.append(node)
    for e in node.kids:
        find_all(e.node, name, out)
    return out


def best_label(opts, sign, R):
    return max(opts, key=lambda k: score(opts[k], sign, R))


def fmt(x):
    if abs(x) < 1e-9:
        x = 0.0
    return f"{x:,.4g}" if abs(x) < 1e4 else f"{x:,.0f}"


def frange(spec):
    name, rng = spec.split("=")
    parts = [float(v) for v in rng.split(":")]
    lo, hi = parts[0], parts[1]
    n = int(parts[2]) if len(parts) > 2 else 20
    return name.strip(), [lo + (hi - lo) * i / n for i in range(n + 1)]


def cmd_tree(a):
    doc = json.load(open(a.json_file, encoding="utf-8"))
    if "tree" not in doc:  # old format: the document is the tree
        doc = {"tree": doc}
    meta = {k: v for k, v in doc.get("params", {}).items() if isinstance(v, dict)}
    params = {k: float(v["value"] if isinstance(v, dict) else v) for k, v in doc.get("params", {}).items()}
    for s in a.set or []:
        k, v = s.split("=")
        params[k.strip()] = float(v)
    units = doc.get("units", "")
    sign = -1 if doc.get("objective", "max") == "min" else 1
    R = a.risk_tolerance
    root = expand(doc["tree"], doc.get("subtrees", {}), minimize=sign < 0)
    target = root
    if a.at:
        nm, _, k = a.at.partition("#")
        found = find_all(root, nm)
        if not found:
            raise SystemExit(f"No decision named '{nm}'")
        idx = int(k) - 1 if k else 0
        if len(found) > 1 and not k:
            print(f"NOTE: {len(found)} decisions are named '{nm}'; using the first. Use --at '{nm}#2' etc. for the others.")
        target = found[idx]
    word = "expected cost" if sign < 0 else "expected value"

    def opts_at(env, RR=R):
        if target is root:
            return root_options(root, env, sign, RR)
        return {e.label: solve(e.node, env, sign, RR, ev(e.cash, env)) for e in target.kids}

    if a.xlsx:
        to_xlsx(root, params, doc, a.xlsx, sign, meta)
        print(f"Wrote {a.xlsx}: Inputs sheet (named cells) and a Tree sheet with live formulas. "
              "Change an input and the tree recalculates; use Excel's Data Table or Goal Seek for sensitivity.")

    # ---- base case
    log = []
    dist = solve(root, params, sign, R, log=log)
    print(f"Inputs: " + ", ".join(f"{k}={fmt(v)}" for k, v in params.items()) if params else "Inputs: none named")
    print(f"Criterion: {'expected utility, risk tolerance ' + fmt(R) + ' ' + units if R else word}"
          f"{' (lower is better)' if sign < 0 else ''}\n")
    opts = opts_at(params)
    where = f"at '{target.name}'" if target is not root else "at the first decision"
    note = " (values from this point on; amounts earlier in the path are excluded)" if target is not root else ""
    thr = a.loss_threshold
    print(f"Options {where}{note}:")
    hdr = ["option", word] + (["certainty equiv."] if R else []) + (["P(loss)"] if sign > 0 else []) + \
        ([f"P(loss > {fmt(thr)})"] if thr is not None and sign > 0 else []) + ["worst", "best"]
    print("  " + " | ".join(hdr))
    for k, d in opts.items():
        s_ = summary(d, R)
        worst, bst = (s_["worst"], s_["best"]) if sign > 0 else (s_["best"], s_["worst"])
        row = [k, fmt(s_["ev"])] + ([fmt(s_["ce"])] if R else []) + ([f"{s_['p_loss']:.0%}"] if sign > 0 else []) + \
            ([f"{p_below(d, -thr):.0%}"] if thr is not None and sign > 0 else []) + [fmt(worst), fmt(bst)]
        print("  " + " | ".join(row))
    b_now = best_label(opts, sign, R)
    print(f"→ best {where}: {b_now}")
    tie = near_tie(opts, sign, R)
    if tie:
        print(f"  NOTE: {tie[0]} and {tie[1]} are tied (difference under 0.01% of the values); treat them as equal.")
    print()

    print("Recommended strategy (what to do at each decision you could reach; values are totals for the whole path):")
    for path, name, choice, vals in log:
        p = " → ".join(path) if path else "Start"
        alts = "; ".join(f"{k} {fmt(sign * (v[1]) if not R else cert_equiv(v[1], R) * sign)}"
                         for k, v in vals.items())
        print(f"  {p}: at '{name}' choose {choice}   ({alts})")

    # ---- risk profiles of every option at the decision
    print(f"\nRisk profiles ({units}; results with zero probability are left out):")
    for k, d in opts.items():
        mark = "  ← recommended" if k == b_now else ""
        print(f"  {k}{mark}")
        agg = collections.defaultdict(float)
        for x, q in d:
            if q > 1e-12:
                agg[round(x, 9)] += q
        for x in sorted(agg):
            print(f"    {fmt(x):>10}  {agg[x]:6.1%}  " + "█" * int(round(agg[x] * 40)))

    # ---- one-way sweeps and break-evens
    sweeps = [frange(x) for x in (a.sweep or [])]
    if len(sweeps) == 1:
        name, grid = sweeps[0]
        print(f"\nSensitivity to {name} ({where}):")
        labels = list(opts)
        print("  " + " | ".join([name] + labels + ["best"]))
        prev, pv = None, None
        for v in grid:
            env = dict(params, **{name: v})
            o = opts_at(env)
            b = best_label(o, sign, R)
            t = near_tie(o, sign, R)
            vals = [fmt(summary(o[k], R)["ce" if R else "ev"]) for k in labels]
            print("  " + " | ".join([fmt(v)] + vals + [b + (f" (tied with {t[1] if t[0] == b else t[0]})" if t else "")]))
            if prev and b != prev:
                x = breakeven(lambda tt: opts_at(dict(params, **{name: tt})), pv, v, prev, b, sign, R)
                print(f"    ↳ best switches from {prev} to {b} at {name} ≈ {x:.4g}")
            prev, pv = b, v
        if len({best_label(opts_at(dict(params, **{name: v})), sign, R) for v in grid}) == 1:
            print(f"    No break-even in this range: {prev} is best throughout.")
    elif len(sweeps) == 2:
        (n1, g1), (n2, g2) = sweeps
        print(f"\nBest option {where} by {n1} (rows) and {n2} (columns):")
        print("  " + " | ".join([f"{n1}\\{n2}"] + [fmt(v) for v in g2]))
        for v1 in g1:
            row = [best_label(opts_at(dict(params, **{n1: v1, n2: v2})), sign, R) for v2 in g2]
            print("  " + " | ".join([fmt(v1)] + row))

    # ---- tornado: on the gap between the recommended option and the runner-up
    if a.tornado == "auto":
        ranged = [f"{k}={m['low']}:{m['high']}" for k, m in meta.items() if "low" in m and "high" in m]
        if not ranged:
            print("\n--tornado auto: no inputs have low/high values in params; give ranges explicitly.")
            a.tornado = None
        else:
            a.tornado = ",".join(ranged)
    if a.tornado:
        val = lambda d: summary(d, R)["ce" if R else "ev"]
        ranked = sorted(opts, key=lambda k: score(opts[k], sign, R), reverse=True)
        lead, runner = ranked[0], (ranked[1] if len(ranked) > 1 else ranked[0])
        res = []
        for item in a.tornado.split(","):
            name, rng = item.split("=")
            name = name.strip()
            lo, hi = [float(v) for v in rng.split(":")]
            ends = []
            for v in (lo, hi):
                o = opts_at(dict(params, **{name: v}))
                gap = sign * (val(o[lead]) - val(o[runner]))
                ends.append((gap, best_label(o, sign, R), {k: val(o[k]) for k in o}))
            res.append((abs(ends[1][0] - ends[0][0]), name, lo, hi, ends))
        base_gap = sign * (val(opts[lead]) - val(opts[runner]))
        print(f"\nTornado: how much each input moves the lead of {lead} over {runner} {where} "
              f"(now {fmt(base_gap)}; below 0 means {runner} or another option wins):")
        for sw, name, lo, hi, ends in sorted(res, reverse=True):
            flip = "" if ends[0][1] == lead == ends[1][1] else f"   best becomes {ends[0][1]} / {ends[1][1]}"
            print(f"  {name:<18} at {fmt(lo)}: lead {fmt(ends[0][0])}   at {fmt(hi)}: lead {fmt(ends[1][0])}   "
                  f"swing {fmt(sw)}{flip}")

    # ---- risk tolerance at which the choice changes
    if R:
        opts_ev = opts_at(params, None)
        b0 = best_label(opts_ev, sign, None)
        bR = best_label(opts, sign, R)
        if b0 != bR:
            print(f"\nWith risk tolerance {fmt(R)} the choice ({bR}) differs from the expected-value choice ({b0}).")
            lo, hi = R, R
            while best_label(opts_at(params, hi), sign, hi) != b0 and hi < R * 1e6:
                lo, hi = hi, hi * 2
            if best_label(opts_at(params, hi), sign, hi) != b0:
                print("No risk tolerance up to a million times this one restores the expected-value choice.")
            else:
                for _ in range(60):
                    mid = (lo + hi) / 2
                    if best_label(opts_at(params, mid), sign, mid) == b0:
                        hi = mid
                    else:
                        lo = mid
                print(f"{b0} becomes the better choice once risk tolerance exceeds about {fmt(hi)} {units}.")
        else:
            print(f"\nWith risk tolerance {fmt(R)} the choice is the same as the expected-value choice ({b0}).")
            lo, hi = R, R
            while best_label(opts_at(params, lo), sign, lo) == b0 and lo > R * 1e-3:
                hi, lo = lo, lo / 2
            if best_label(opts_at(params, lo), sign, lo) == b0:
                print("It stays the same however risk-averse the decision-maker is (tested down to a thousandth of this tolerance).")
            else:
                for _ in range(60):
                    mid = (lo + hi) / 2
                    if best_label(opts_at(params, mid), sign, mid) == b0:
                        hi = mid
                    else:
                        lo = mid
                alt = best_label(opts_at(params, lo), sign, lo)
                print(f"It switches to {alt} if risk tolerance falls below about {fmt(hi)} {units} "
                      f"(i.e. if you wouldn't accept a 50-50 chance of winning {fmt(hi)} or losing {fmt(hi / 2)}).")


def p_below(dist, x):
    return sum(q for v, q in dist if v < x - 1e-12)


def near_tie(opts, sign, R):
    ranked = sorted(opts, key=lambda k: score(opts[k], sign, R), reverse=True)
    if len(ranked) < 2:
        return None
    s1, s2 = score(opts[ranked[0]], sign, R), score(opts[ranked[1]], sign, R)
    scale = max(abs(s1), abs(s2), 1e-9)
    return (ranked[0], ranked[1]) if abs(s1 - s2) <= 1e-4 * scale else None


def breakeven(f, lo, hi, a_lab, b_lab, sign, R, it=60):
    """Point between lo (where a_lab is best) and hi (where it isn't) at which the best option changes."""
    for _ in range(it):
        mid = (lo + hi) / 2
        if best_label(f(mid), sign, R) == a_lab:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# ------------------------------------------------------------------ Excel export
def to_xlsx(root, params, doc, path, sign, meta=None):
    meta = meta or {}
    import re
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.workbook.defined_name import DefinedName
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Inputs"
    ws.append(["Input", "Value", "Low", "High", "Source or basis", "Note"])
    safe = {}
    for i, (k, v) in enumerate(params.items(), start=2):
        nm = k if not re.fullmatch(r"[A-Za-z]{1,3}\d+|[RrCc]", k) else "in_" + k
        safe[k] = nm
        m = meta.get(k, {})
        ws.append([k, v, m.get("low", ""), m.get("high", ""), m.get("source", ""),
                   m.get("note", doc.get("notes", {}).get(k, ""))])
        dn = DefinedName(nm, attr_text=f"Inputs!$B${i}")
        try:
            wb.defined_names[nm] = dn
        except TypeError:  # older openpyxl
            wb.defined_names.append(dn)
    ws.column_dimensions["A"].width = 24
    ws.column_dimensions["E"].width = 40
    ws.column_dimensions["F"].width = 50
    t = wb.create_sheet("Tree")
    t.append(["Step", "Probability", "Cash on this branch", "Value from here", "Best choice", "Node type"])
    for c in t[1]:
        c.font = Font(bold=True)
    X = lambda e: "=" + emit(e, lambda s: safe.get(s, s), excel=True)
    rows = []  # filled recursively; returns the row index whose D cell holds value from here

    def add(label, depth, p, cash, node):
        r = t.max_row + 1
        t.cell(r, 1, ("    " * depth) + label)
        if p is not None:
            t.cell(r, 2, X(p)).number_format = "0.0%"
        t.cell(r, 3, X(cash) if cash is not None else 0)
        t.cell(r, 6, node.kind)
        kids = [add(e.label, depth + 1, e.p if node.kind == "chance" else None, e.cash, e.node) for e in node.kids]
        if node.kind == "end":
            t.cell(r, 4, f"=C{r}+({X(node.value)[1:]})")
        elif node.kind == "chance":
            t.cell(r, 4, f"=C{r}+" + "+".join(f"B{k}*D{k}" for k in kids))
        else:
            fn = "MAX" if sign > 0 else "MIN"
            t.cell(r, 4, f"=C{r}+{fn}(" + ",".join(f"D{k}" for k in kids) + ")")
            t.cell(r, 5, "=" + _bestf(kids, node, fn))
            t.cell(r, 5).font = Font(bold=True)
        if node.kind != "end":
            t.cell(r, 1).value = t.cell(r, 1).value + (f"  [{node.name}]" if node.name else "")
        return r

    add("Start", 0, None, None, root)
    t.column_dimensions["A"].width = 60
    for col in "BCDE":
        t.column_dimensions[col].width = 18
    t.freeze_panes = "A2"
    wb.save(path)


def _bestf(kids, node, fn):
    agg = f"{fn}(" + ",".join(f"D{k}" for k in kids) + ")"
    out = '""'
    for k, e in zip(reversed(kids), reversed(node.kids)):
        out = f'IF(D{k}={agg},"{e.label}",{out})'
    return out


# ------------------------------------------------------------------ value of information
def load_voi(path):
    doc = json.load(open(path, encoding="utf-8"))
    env = {k: float(v["value"] if isinstance(v, dict) else v) for k, v in doc.get("params", {}).items()}
    E = lambda e: ev(e, env)
    states = {k: E(v) for k, v in doc["states"].items()}
    acts = {a: {s: E(v) for s, v in d.items()} for a, d in doc["actions"].items()}
    tests = doc.get("tests") or ([doc["test"]] if "test" in doc else [])
    out = []
    for t in tests:
        sig = {k: {s: E(v) for s, v in d.items()} for k, d in t["signals"].items()}
        if len(sig) == 1:  # add the complement
            (k, d), = sig.items()
            sig["not " + k] = {s: 1 - p for s, p in d.items()}
        out.append((t.get("name", "test"), E(t.get("cost", 0)), sig))
    return doc, states, acts, out


def cmd_voi(a):
    doc, states, acts, tests = load_voi(a.json_file)
    units = doc.get("units", "")
    sign = -1 if doc.get("objective", "max") == "min" else 1
    R = a.risk_tolerance
    if abs(sum(states.values()) - 1) > 1e-6:
        print(f"WARNING: state probabilities sum to {sum(states.values()):.3f}")

    def value(probs, shift=0.0):
        """best action and its value (EV, or CE with utility) given state probabilities."""
        best, bs = None, None
        for act, pay in acts.items():
            if R:
                s = sum(p * utility(sign * (pay[st] - shift), R) for st, p in probs.items())
            else:
                s = sum(p * sign * (pay[st] - shift) for st, p in probs.items())
            if bs is None or s > bs:
                best, bs = act, s
        return best, bs

    def show(s):
        return sign * (cert_equiv(s, R) if R else s)

    b0, s0 = value(states)
    crit = "certainty equivalent" if R else ("expected cost" if sign < 0 else "expected value")
    print(f"Without more information: choose {b0} ({crit} {fmt(show(s0))} {units})")
    for act, pay in acts.items():
        e = sum(p * pay[st] for st, p in states.items())
        print(f"  {act}: expected {fmt(e)}")
    # perfect information
    if R:
        eu = sum(p * max(utility(sign * acts[x][st], R) for x in acts) for st, p in states.items())
        evpi = show(eu) - show(s0)
    else:
        eu = sum(p * max(sign * acts[x][st] for x in acts) for st, p in states.items())
        evpi = show(eu) - show(s0)
    evpi *= sign
    print(f"\nPerfect information (knowing the outcome in advance): best action by outcome = " +
          ", ".join(f"{st}: {max(acts, key=lambda x: sign * acts[x][st])}" for st in states))
    print(f"  {crit} with perfect information {fmt(show(eu))}; EVPI = {fmt(evpi)} {units}")
    print("  No study or test can be worth more than this; a real one is worth less.")

    for name, cost, sig in tests:
        print(f"\nTest: {name} (cost {fmt(cost)} {units})")
        for st in states:
            tot = sum(sig[k][st] for k in sig)
            if abs(tot - 1) > 1e-6:
                print(f"  WARNING: results' probabilities given '{st}' sum to {tot:.3f}")
        p_sig = {k: sum(states[st] * sig[k][st] for st in states) for k in sig}
        rule, eu_t = {}, 0.0
        print("  " + " | ".join(["result", "P(result)"] + [f"P({st}|result)" for st in states] + ["best action", crit]))
        for k in sig:
            if p_sig[k] <= 0:
                continue
            post = {st: states[st] * sig[k][st] / p_sig[k] for st in states}
            b, s = value(post)
            rule[k] = b
            eu_t += p_sig[k] * s
            print("  " + " | ".join([k, f"{p_sig[k]:.3f}"] + [f"{post[st]:.3f}" for st in states] + [b, fmt(show(s))]))
        evsi = sign * (show(eu_t) - show(s0))
        print(f"  {crit} with the test (before its cost): {fmt(show(eu_t))}")
        print(f"  EVSI (what the test is worth) = {fmt(evsi)} {units};  EVSI/EVPI = {evsi / evpi:.0%}" if evpi else
              f"  EVSI = {fmt(evsi)} {units}")
        if len(set(rule.values())) == 1:
            print("  Every result leads to the same action, so the test can't change the decision: worth 0.")
        if R:  # with utility, cost is not simply subtracted: find the most worth paying
            lo, hi = 0.0, max(abs(evpi) * 2, 1e-9)
            for _ in range(80):
                mid = (lo + hi) / 2
                e2 = sum(p_sig[k] * value({st: states[st] * sig[k][st] / p_sig[k] for st in states}, sign * mid)[1]
                         for k in sig if p_sig[k] > 0)
                if e2 >= s0:
                    lo = mid
                else:
                    hi = mid
            worth = lo
        else:
            worth = evsi
        verdict = "worth buying" if cost < worth - 1e-12 else "not worth buying"
        print(f"  Most worth paying: {fmt(worth)}; cost {fmt(cost)} → {verdict} "
              f"(net {'gain' if worth >= cost else 'loss'} {fmt(abs(worth - cost))}).")
        print("  Decision rule if bought: " + "; ".join(f"{k} → {v}" for k, v in rule.items()))
    print("\nAssumes every action is still available, at the same payoff, once the result is known. If waiting "
          "costs something (delay, a lapsing offer), model it as a tree instead.")


# ------------------------------------------------------------------ Bayes / tree flip
def cmd_bayes(a):
    doc = json.load(open(a.json_file, encoding="utf-8"))
    prior = {k: float(v) for k, v in doc["prior"].items()}
    tests = {}
    for name, sig in doc["tests"].items():
        sig = {k: {s: float(p) for s, p in d.items()} for k, d in sig.items()}
        if len(sig) == 1:
            (k, d), = sig.items()
            sig["not " + k] = {s: 1 - p for s, p in d.items()}
        tests[name] = sig
    print("Prior: " + ", ".join(f"{s} {p:.3f}" for s, p in prior.items()))
    for name, sig in tests.items():
        print(f"\nTest: {name}  (flipping 'P(result | truth)' into 'P(truth | result)')")
        print("  " + " | ".join(["result", "P(result)"] + [f"P({s}|result)" for s in prior]))
        for k, d in sig.items():
            joint = {s: prior[s] * d[s] for s in prior}
            pk = sum(joint.values())
            post = [f"{joint[s] / pk:.3f}" if pk else "n/a" for s in prior]
            print("  " + " | ".join([k, f"{pk:.3f}"] + post))
    if len(tests) > 1:
        print("\nCombined results (assumes the tests are independent once the truth is known):")
        names = list(tests)
        print("  " + " | ".join(names + ["P(results)"] + [f"P({s}|results)" for s in prior]))
        for combo in itertools.product(*[list(tests[n]) for n in names]):
            joint = {s: prior[s] * math.prod(tests[n][k][s] for n, k in zip(names, combo)) for s in prior}
            pk = sum(joint.values())
            print("  " + " | ".join(list(combo) + [f"{pk:.4f}"] + [f"{joint[s] / pk:.3f}" if pk else "n/a" for s in prior]))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("tree", help="fold back a decision tree (JSON)")
    s.add_argument("json_file")
    s.add_argument("--set", action="append", help="override an input, e.g. --set p_ok=0.5 (repeatable)")
    s.add_argument("--risk-tolerance", type=float, help="use exponential utility with this risk tolerance")
    s.add_argument("--at", help="report the options at the decision with this name (default: the first)")
    s.add_argument("--sweep", action="append", help="name=low:high[:intervals] (default 20 intervals, so 21 rows); give twice for a two-way table")
    s.add_argument("--tornado", help="name=low:high,name2=low:high,... or 'auto' to use the ranges in params")
    s.add_argument("--xlsx", help="also write a live Excel version of the tree")
    s.add_argument("--loss-threshold", type=float, help="also report the chance of losing more than this amount")
    s.set_defaults(f=cmd_tree)
    s = sp.add_parser("voi", help="value of perfect and imperfect information (JSON)")
    s.add_argument("json_file")
    s.add_argument("--risk-tolerance", type=float)
    s.set_defaults(f=cmd_voi)
    s = sp.add_parser("bayes", help="tree flip: posteriors from prior and test reliability (JSON)")
    s.add_argument("json_file")
    s.set_defaults(f=cmd_bayes)
    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
