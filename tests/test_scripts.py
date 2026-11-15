"""
Tests for choosewell's scripts. Run from the repository root:
    python3 -m unittest discover -s tests -v
Needs openpyxl (and python-docx for the Word checklist test, which is skipped without it).
Expected values were worked out by hand and checked against published textbook and course examples.
"""
import csv, importlib.util, json, os, re, subprocess, sys, tempfile, unittest

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SCRIPTS = os.path.join(ROOT, "scripts")
EXAMPLES = os.path.join(ROOT, "assets", "examples")


def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(SCRIPTS, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


U = load("uncertainty")


def run(*args):
    r = subprocess.run([sys.executable, *args], capture_output=True, text=True, cwd=ROOT)
    if r.returncode != 0:
        raise AssertionError(f"{' '.join(args)} failed:\n{r.stdout}\n{r.stderr}")
    return r.stdout


def tree_values(doc, params=None, at=None, R=None):
    """Expected value (or certainty equivalent) of each option at a decision."""
    p = U.param_values(doc)
    p.update(params or {})
    sign = -1 if doc.get("objective", "max") == "min" else 1
    root = U.expand(doc.get("tree", doc), doc.get("subtrees", {}), minimize=sign < 0)
    node = U.find_decision(root, at) if at else root
    out = {}
    for e in node.kids:
        d = U.solve(e.node, p, sign, R, U.ev(e.cash, p))
        s = U.summary(d, R)
        out[e.label] = s["ce"] if R else s["ev"]
    return out


def ex(name):
    with open(os.path.join(EXAMPLES, name), encoding="utf-8") as f:
        return json.load(f)


class TestExpressions(unittest.TestCase):
    def test_arithmetic_and_names(self):
        self.assertAlmostEqual(U.ev("1 - (a + b) * 2", {"a": 0.1, "b": 0.2}), 0.4)
        self.assertEqual(U.ev("max(a, 3)", {"a": 5}), 5)

    def test_rejects_code(self):
        with self.assertRaises(SystemExit):
            U.ev("__import__('os')", {})

    def test_unknown_input(self):
        with self.assertRaises(SystemExit):
            U.ev("missing + 1", {})


class TestTree(unittest.TestCase):
    def test_staged_programme(self):
        doc = ex("staged-programme.json")
        self.assertAlmostEqual(tree_values(doc)["Start"], 53.0, places=6)
        launch = tree_values(doc, at="Launch")
        self.assertAlmostEqual(launch["Full-scale launch"], 300.0)
        self.assertAlmostEqual(launch["Limited launch"], 220.0)

    def test_break_evens(self):
        doc = ex("staged-programme.json")
        p = U.param_values(doc)
        root = U.expand(doc["tree"], {})
        node = U.find_decision(root, "Launch")
        f = lambda t: {e.label: U.solve(e.node, dict(p, p_sup=t), 1, None) for e in node.kids}
        x = U.breakeven(f, 0.4, 0.5, "Limited launch", "Full-scale launch", 1, None)
        self.assertAlmostEqual(x, 5 / 11, places=6)        # 0.4545
        y = U.breakeven(f, 0.1, 0.2, "No launch", "Limited launch", 1, None)
        self.assertAlmostEqual(y, 1 / 9, places=6)         # 0.1111

    def test_subtrees_and_test_market(self):
        doc = {"params": {"test": 50, "win": 1200, "lose": -500, "p_ts": 0.6, "p0": 0.5, "p_good": 0.7, "p_bad": 0.2},
               "subtrees": {"nat": {"type": "decision", "name": "Go?", "options": [
                   {"label": "Go", "node": {"type": "chance", "name": "R", "branches": [
                       {"label": "S", "p": "p", "node": {"value": "win"}}, {"label": "F", "node": {"value": "lose"}}]}},
                   {"label": "Stop"}]}},
               "tree": {"type": "decision", "name": "Test?", "options": [
                   {"label": "Test", "cost": "test", "node": {"type": "chance", "name": "T", "branches": [
                       {"label": "Good", "p": "p_ts", "node": {"use": "nat", "with": {"p": "p_good"}}},
                       {"label": "Bad", "node": {"use": "nat", "with": {"p": "p_bad"}}}]}},
                   {"label": "No test", "node": {"use": "nat", "with": {"p": "p0"}}}]}}
        v = tree_values(doc)
        self.assertAlmostEqual(v["Test"], 364)
        self.assertAlmostEqual(v["No test"], 350)
        # the test is worth 64: at a cost of 64 the two options tie
        v2 = tree_values(doc, {"test": 64})
        self.assertAlmostEqual(v2["Test"], v2["No test"])

    def test_minimising_costs_and_order(self):
        doc = ex("risky-steps-order.json")
        v = tree_values(doc)
        self.assertAlmostEqual(v["Fallback now"], 1000)
        self.assertAlmostEqual(v["A first"], 1020)
        self.assertAlmostEqual(v["B first"], 940)
        v = tree_values(doc, {"late": 1000})          # no extra cost for a late failure: ratio rule holds
        self.assertAlmostEqual(v["A first"], 860)
        self.assertAlmostEqual(v["B first"], 880)

    def test_learning_between_related_choices(self):
        v = tree_values(ex("learn-then-decide.json"))
        # 0.2 x (240 + max(0.65*320-80, 0)) + 0.8 x (-80 + max(0.1*320-80, 0))
        self.assertAlmostEqual(v["Enter market B first"], 0.2 * (240 + 128) + 0.8 * (-80))

    def test_certainty_equivalents(self):
        v = tree_values(ex("risk-attitude.json"), R=2)
        self.assertAlmostEqual(v["Gamble"], 0.1324, places=3)
        venture = {"tree": {"type": "decision", "name": "x", "options": [
            {"label": "Go", "node": {"type": "chance", "name": "r", "branches": [
                {"label": "a", "p": 0.35, "node": {"value": -1}}, {"label": "b", "p": 0.6, "node": {"value": 0.5}},
                {"label": "c", "p": 0.05, "node": {"value": 3}}]}}, {"label": "No"}]}}
        self.assertAlmostEqual(tree_values(venture, R=1.92)["Go"], -0.1157, places=3)
        self.assertAlmostEqual(tree_values(venture)["Go"], 0.1)

    def test_risk_profile(self):
        doc = ex("staged-programme.json")
        p = U.param_values(doc)
        d = U.solve(U.expand(doc["tree"], {}), p)
        s = U.summary(d)
        self.assertAlmostEqual(sum(q for _, q in d), 1.0)
        self.assertAlmostEqual(s["p_loss"], 0.82)
        self.assertAlmostEqual(s["worst"], -385)

    def test_excel_export(self):
        with tempfile.TemporaryDirectory() as t:
            out = os.path.join(t, "tree.xlsx")
            run(os.path.join(SCRIPTS, "uncertainty.py"), "tree", os.path.join(EXAMPLES, "staged-programme.json"), "--xlsx", out)
            import openpyxl
            wb = openpyxl.load_workbook(out)
            self.assertIn("Inputs", wb.sheetnames)
            self.assertTrue(str(wb["Tree"]["D2"].value).startswith("="))

    def test_cli_sweep_reports_break_even(self):
        out = run(os.path.join(SCRIPTS, "uncertainty.py"), "tree", os.path.join(EXAMPLES, "staged-programme.json"),
                  "--at", "Launch", "--sweep", "p_sup=0:1:10")
        self.assertIn("0.4545", out)


class TestValueOfInformation(unittest.TestCase):
    def test_pilot(self):
        out = run(os.path.join(SCRIPTS, "uncertainty.py"), "voi", os.path.join(EXAMPLES, "pilot-value.json"))
        self.assertRegex(out, r"EVPI = 240")
        self.assertRegex(out, r"EVSI \(what the test is worth\) = 96")
        self.assertIn("worth buying", out)

    def test_study_not_worth_its_cost(self):
        doc = {"states": {"wet": 0.2, "dry": 0.8}, "actions": {"Drill": {"wet": 240, "dry": -80}, "No": {"wet": 0, "dry": 0}},
               "tests": [{"name": "survey", "cost": 5, "signals": {"seen": {"wet": 0.9, "dry": 0.6}}}]}
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(doc, f)
        try:
            out = run(os.path.join(SCRIPTS, "uncertainty.py"), "voi", f.name)
        finally:
            os.unlink(f.name)
        self.assertIn("EVPI = 48", out)
        self.assertRegex(out, r"EVSI \(what the test is worth\) = 4\.8")
        self.assertIn("not worth buying", out)

    def test_bayes_flip(self):
        out = run(os.path.join(SCRIPTS, "uncertainty.py"), "bayes", os.path.join(EXAMPLES, "tree-flip.json"))
        self.assertIn("0.588", out)
        self.assertIn("0.357", out)


class TestAppraise(unittest.TestCase):
    def test_init_and_payoff(self):
        with tempfile.TemporaryDirectory() as t:
            wb = os.path.join(t, "a.xlsx")
            run(os.path.join(SCRIPTS, "appraise.py"), "init", "--choice", "who", "--out", wb)
            import openpyxl
            self.assertIn("Claims", openpyxl.load_workbook(wb).sheetnames)
            pay = os.path.join(t, "p.csv")
            with open(pay, "w", newline="") as f:
                csv.writer(f).writerows([["option", "good", "bad"], ["A", 10, -5], ["B", 4, 2], ["_prob", 0.6, 0.4]])
            out = run(os.path.join(SCRIPTS, "appraise.py"), "payoff", pay)
            self.assertIn("A 4", out)              # 0.6*10 + 0.4*-5
            self.assertIn("EVPI = 2.8", out)        # 0.6*10 + 0.4*2 - 4

    def test_sensitivity(self):
        with tempfile.TemporaryDirectory() as t:
            sc = os.path.join(t, "s.csv")
            with open(sc, "w", newline="") as f:
                csv.writer(f).writerows([["option", "c1", "c2"], ["X", 3, 1], ["Y", 1, 3], ["Z", 1, 1], ["_weight", 0.6, 0.4]])
            out = run(os.path.join(SCRIPTS, "appraise.py"), "sensitivity", sc)
            self.assertIn("X", out)
            self.assertRegex(out, r"(?i)dominat")


class TestChecklist(unittest.TestCase):
    def test_markdown_checklist(self):
        with tempfile.TemporaryDirectory() as t:
            out = os.path.join(t, "c.md")
            run(os.path.join(SCRIPTS, "checklist.py"), "--choice", "who", "--methods", "scored-criteria,quantified-tree",
                "--depth", "quick", "--skip", "3", "--out", out)
            text = open(out, encoding="utf-8").read()
            self.assertIn("## Step 1: Frame the decision", text)
            self.assertNotIn("## Step 3:", text)
            self.assertIn("Method: quantified decision tree", text)
            self.assertIn("Type of choice: Who", text)
            self.assertGreater(text.count("- [ ]"), 20)

    def test_old_option_names_still_work(self):
        with tempfile.TemporaryDirectory() as t:
            out = os.path.join(t, "c.md")
            run(os.path.join(SCRIPTS, "checklist.py"), "--archetype", "structure-conditional", "--mechanisms", "rag-csf",
                "--context", "uk-gov", "--out", out)
            self.assertIn("Green Book", open(out, encoding="utf-8").read())

    def test_word_checklist(self):
        try:
            import docx  # noqa: F401
        except ImportError:
            self.skipTest("python-docx not installed")
        with tempfile.TemporaryDirectory() as t:
            out = os.path.join(t, "c.docx")
            run(os.path.join(SCRIPTS, "checklist.py"), "--choice", "where", "--out", out)
            self.assertTrue(os.path.getsize(out) > 5000)



def make_workbook(path, options, criteria, indicators, ratings):
    import openpyxl
    run(os.path.join(SCRIPTS, "appraise.py"), "init", "--out", path)
    wb = openpyxl.load_workbook(path)
    for r in options:
        wb["Options"].append(r)
    for r in criteria:
        wb["Criteria"].append(r)
    for r in indicators:
        wb["Indicators"].append(r)
    for r in ratings:
        wb["Ratings"].append(r)
    wb.save(path)


class TestRollupFixes(unittest.TestCase):
    def test_setup_ongoing_split_does_not_spoil_other_criteria(self):
        with tempfile.TemporaryDirectory() as t:
            wb = os.path.join(t, "w.xlsx")
            make_workbook(wb, [["O1", "All good", "", "", "", "y", "n", ""]],
                          [["C1", "c1", "", "", 1, "rag", "", "", "main"], ["C2", "c2", "", "", 1, "rag", "", "", "main"]],
                          [["C1", "I1", "s", "n"], ["C2", "I2", "s", "n"]],
                          [["O1", "I1", "", "✓"], ["O1", "I2", "setup", "✓"], ["O1", "I2", "ongoing", "✓"]])
            out = run(os.path.join(SCRIPTS, "appraise.py"), "rollup", wb)
            self.assertIn("C1:G C2:G → G", out)

    def test_unrated_is_not_amber(self):
        with tempfile.TemporaryDirectory() as t:
            wb = os.path.join(t, "w.xlsx")
            make_workbook(wb, [["O1", "x", "", "", "", "n", "n", ""]], [["C1", "c1", "", "", 1, "rag", "", "", "main"]],
                          [["C1", "I1", "s", "n"]], [])
            out = run(os.path.join(SCRIPTS, "appraise.py"), "rollup", wb)
            self.assertIn("not rated", out)
            self.assertNotIn("MARGINAL", out)

    def test_gates_text_weights_and_blank_scores(self):
        with tempfile.TemporaryDirectory() as t:
            wb = os.path.join(t, "w.xlsx")
            make_workbook(wb, [["O1", "a", "", "", "", "n", "n", ""], ["O2", "b", "", "", "", "n", "n", ""],
                               ["O3", "c", "", "", "", "n", "n", ""]],
                          [["G1", "licence", "", "", "", "rag", "", "", "gate"],
                           ["C1", "c1", "", "", "TBD", "score", 3, "", "main"], ["C2", "c2", "", "", 1, "score", 3, "", "main"]],
                          [],
                          [["O1", "G1", "", "✗"], ["O1", "C1", "", 3], ["O1", "C2", "", 3],
                           ["O2", "C1", "", 3], ["O2", "C2", "", ""], ["O3", "C1", "", 1], ["O3", "C2", "", 1]])
            out = run(os.path.join(SCRIPTS, "appraise.py"), "rollup", wb)
            self.assertIn("failed a gate: 1", out)
            self.assertIn("score 3.00/3 (missing 1)", out)     # blank isn't zero
            self.assertIn("WEIGHTS", out)

    def test_import_scores_finds_dominance_and_flips(self):
        with tempfile.TemporaryDirectory() as t:
            sc = os.path.join(t, "s.csv")
            with open(sc, "w", newline="") as f:
                csv.writer(f).writerows([["option", "a", "b"], ["Hub", 3, 1], ["Hybrid", 3, 2], ["Other", 1, 3],
                                         ["_weight", 0.5, 0.5]])
            wb = os.path.join(t, "w.xlsx")
            run(os.path.join(SCRIPTS, "appraise.py"), "init", "--scores", sc, "--out", wb)
            out = run(os.path.join(SCRIPTS, "appraise.py"), "rollup", wb)
            self.assertIn("DOMINATED: O1", out)
            self.assertIn("MARGINAL", out)

    def test_spread_and_audit_on_blank(self):
        with tempfile.TemporaryDirectory() as t:
            wb = os.path.join(t, "w.xlsx")
            run(os.path.join(SCRIPTS, "appraise.py"), "init", "--scorers", "--out", wb)
            import openpyxl
            w = openpyxl.load_workbook(wb)
            for who, v in (("Ann", 0), ("Bo", 3), ("Cy", 2)):
                w["Scores by person"].append([who, "O1", "C1", v, ""])
            w["Ratings"].append(["O1", "C2", "", "", ""])
            w.save(wb)
            out = run(os.path.join(SCRIPTS, "appraise.py"), "spread", wb, "--suggest")
            self.assertIn("1 with a range of 2 or more", out)
            out = run(os.path.join(SCRIPTS, "appraise.py"), "audit", wb)
            self.assertIn("1 not yet rated", out)

    def test_thresholds_unknowns_and_near_misses(self):
        with tempfile.TemporaryDirectory() as t:
            d = os.path.join(t, "d.csv")
            with open(d, "w", newline="") as f:
                csv.writer(f).writerows([["name", "size", "support"], ["A", 10, "yes"], ["B", 2, "yes"], ["C", 10, "unclear"]])
            r = os.path.join(t, "r.json")
            json.dump({"steps": [{"name": "Size", "all": [{"col": "size", "op": ">=", "value": 5}]},
                                 {"name": "Support", "all": [{"col": "support", "op": "in", "value": ["yes"]}]}]},
                      open(r, "w"))
            out = run(os.path.join(SCRIPTS, "appraise.py"), "thresholds", d, r)
            self.assertIn("C (provisional)", out)
            self.assertIn("B (fails only Size", out)

    def test_matrix(self):
        with tempfile.TemporaryDirectory() as t:
            d = os.path.join(t, "m.csv")
            with open(d, "w", newline="") as f:
                csv.writer(f).writerows([["activity", "impact1", "availability1"], ["x", 3, 3], ["y", 1, 3], ["z", 2, 2]])
            out = run(os.path.join(SCRIPTS, "appraise.py"), "matrix", d)
            self.assertIn("Principal priority 1", out)
            self.assertIn("Easy extra 1", out)


class TestUncertaintyFixes(unittest.TestCase):
    PILOT = {"units": "£k", "params": {"p": 0.35, "win": 2000, "lose": -800, "pilot": 60, "g_s": 0.75, "g_f": 0.25},
             "subtrees": {"launch": {"type": "decision", "name": "Launch?", "options": [
                 {"label": "Launch", "node": {"type": "chance", "name": "R", "branches": [
                     {"label": "Hit", "p": "q", "node": {"value": "win"}}, {"label": "Flop", "node": {"value": "lose"}}]}},
                 {"label": "Stop"}]}},
             "tree": {"type": "decision", "name": "Start", "options": [
                 {"label": "Launch now", "node": {"type": "chance", "name": "R", "branches": [
                     {"label": "Hit", "p": "p", "node": {"value": "win"}}, {"label": "Flop", "node": {"value": "lose"}}]}},
                 {"label": "Pilot first", "cost": "pilot", "node": {"type": "chance", "name": "Pilot", "branches": [
                     {"label": "Good", "p": "p*g_s + (1-p)*g_f",
                      "node": {"use": "launch", "with": {"q": "p*g_s/(p*g_s + (1-p)*g_f)"}}},
                     {"label": "Poor", "node": {"use": "launch", "with": {"q": "p*(1-g_s)/(p*(1-g_s) + (1-p)*(1-g_f))"}}}]}},
                 {"label": "Don't"}]}}

    def _run(self, *extra):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(self.PILOT, f)
        try:
            return run(os.path.join(SCRIPTS, "uncertainty.py"), "tree", f.name, *extra)
        finally:
            os.unlink(f.name)

    def test_risk_tolerance_flip_compares_with_true_expected_value_choice(self):
        out = self._run("--risk-tolerance", "300")
        self.assertIn("differs from the expected-value choice (Pilot first)", out)
        m = re.search(r"exceeds about ([\d,\.]+)", out)
        self.assertAlmostEqual(float(m.group(1).replace(",", "")), 1137, delta=3)

    def test_sure_thing_against_gamble_does_not_overflow(self):
        doc = {"units": "$m", "tree": {"type": "decision", "name": "Settle?", "options": [
            {"label": "Settle", "cash": 3},
            {"label": "Trial", "cost": 2, "node": {"type": "chance", "name": "Win?", "branches": [
                {"label": "Win", "p": 0.42, "node": {"value": 9}}, {"label": "Lose", "node": {"value": -2}}]}}]}}
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(doc, f)
        try:
            out = run(os.path.join(SCRIPTS, "uncertainty.py"), "tree", f.name, "--risk-tolerance", "7.2")
        finally:
            os.unlink(f.name)
        self.assertIn("stays the same however risk-averse", out)

    def test_tornado_measures_the_lead(self):
        out = self._run("--tornado", "p=0.2:0.5,lose=-1000:-600")
        self.assertIn("lead of Pilot first over Launch now", out)

    def test_zero_probability_branches_ignored_in_worst_case(self):
        doc = {"tree": {"type": "decision", "name": "x", "options": [
            {"label": "A", "node": {"type": "chance", "name": "c", "branches": [
                {"label": "never", "p": 0, "node": {"value": -999}}, {"label": "always", "node": {"value": 5}}]}},
            {"label": "B"}]}}
        d = U.solve(U.expand(doc["tree"]["options"][0]["node"], {}), {})
        self.assertEqual(U.summary(d)["worst"], 5)

    def test_inputs_with_ranges(self):
        out = run(os.path.join(SCRIPTS, "uncertainty.py"), "tree", os.path.join(EXAMPLES, "staged-programme.json"),
                  "--tornado", "auto")
        self.assertIn("p_sup", out)


class TestChecklistFixes(unittest.TestCase):
    def test_method_tags_drop_irrelevant_items(self):
        with tempfile.TemporaryDirectory() as t:
            out = os.path.join(t, "c.md")
            run(os.path.join(SCRIPTS, "checklist.py"), "--choice", "whether", "--methods", "quantified-tree", "--out", out)
            text = open(out, encoding="utf-8").read()
            self.assertNotIn("Score flips", text)
            self.assertIn("Break-even values for the key inputs", text)

    def test_workbook_fields_parsed_exactly(self):
        with tempfile.TemporaryDirectory() as t:
            wb = os.path.join(t, "w.xlsx")
            run(os.path.join(SCRIPTS, "appraise.py"), "init", "--choice", "design-choices", "--methods", "pros-and-cons",
                "--out", wb)
            import openpyxl
            w = openpyxl.load_workbook(wb)
            for row in w["Frame"].iter_rows():
                if row[0].value == "steps_skipped":
                    row[1].value = "3 (no long list needed); Step 8 limited"
                if row[0].value == "assumptions":
                    row[1].value = "decision tree not used; structured approach"
            w.save(wb)
            out = os.path.join(t, "c.md")
            run(os.path.join(SCRIPTS, "checklist.py"), "--workbook", wb, "--out", out)
            text = open(out, encoding="utf-8").read()
            self.assertIn("Type of choice: Design choices", text)
            self.assertNotIn("## Step 3:", text)
            self.assertIn("## Step 8:", text)
            self.assertNotIn("Method: decision tree", text)


class TestConsistency(unittest.TestCase):
    def test_files_guide_and_checklists_agree(self):
        run(os.path.join(SCRIPTS, "check_consistency.py"))


if __name__ == "__main__":
    unittest.main()
