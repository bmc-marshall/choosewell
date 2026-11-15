#!/usr/bin/env python3
"""
checklist.py - build a choosewell checklist tailored to the choices made.

Items come from the "## Checklist" section at the end of each reference file, so the
checklist always matches the steps. Each item is tagged [quick], [standard] or [full];
the checklist includes items at or below the chosen depth.

Usage:
  python checklist.py --choice who --methods scored-criteria --rulebook general-method --depth standard --out checklist.docx
  python checklist.py --workbook appraisal.xlsx --out checklist.docx   (reads choices from the Frame tab)
  python checklist.py --skip 3,6 ...                                   (leave out steps the user is skipping)

Types of choice: scope, what, where, structure, structure-by-situation, who, design-choices, whether
Methods:  threshold-filter, scored-criteria, rag-success-factors, matrix, decision-tree,
          quantified-tree, pros-and-cons, responsibility-mapping
Rulebook: green-book, us-federal, general-method        Depth: quick, standard, full
Writes .docx if python-docx is installed (and --out ends with .docx), otherwise Markdown.
"""
import argparse, datetime, glob, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.normpath(os.path.join(HERE, "..", "references"))
LEVEL = {"quick": 0, "standard": 1, "full": 2}
CHOICES = ["scope", "what", "where", "structure", "structure-by-situation", "who", "design-choices", "whether"]
METHODS = ["threshold-filter", "scored-criteria", "rag-success-factors", "matrix", "decision-tree",
           "quantified-tree", "pros-and-cons", "responsibility-mapping"]
RULEBOOKS = ["green-book", "us-federal", "general-method"]
# old names still accepted
ALIASES = {"structure-conditional": "structure-by-situation", "rag-csf": "rag-success-factors",
           "pros-cons": "pros-and-cons", "uk-gov": "green-book", "general": "general-method"}
ITEM = re.compile(r"^- \[(quick|standard|full)\](?:\[([a-z,-]+)\])?\s+(.*)$")
# applicability tags on items: a method, a type of choice, or one of these groups
GROUPS = {"scores": {"scored-criteria", "rag-success-factors", "matrix"},
          "weights": {"scored-criteria", "rag-success-factors"},
          "rag": {"rag-success-factors"},
          "structure": {"structure", "structure-by-situation"}}


def norm(x):
    x = x.strip().lower().replace(" ", "-")
    return ALIASES.get(x, x)


def read_file(path):
    """Return (title, [(depth, item)]) from a reference file's Checklist section."""
    title, items, inside = "", [], False
    for line in open(path, encoding="utf-8"):
        line = line.rstrip()
        if not title and line.startswith("# "):
            title = line[2:].strip().replace("*", "")
        elif line.startswith("## "):
            inside = line.strip().lower() == "## checklist"
        elif inside:
            m = ITEM.match(line)
            if m:
                items.append((m.group(1), m.group(3), m.group(2) or ""))
    return title, items


METHOD_ALIASES = {"rag": "rag-success-factors", "red/amber/green": "rag-success-factors", "csf": "rag-success-factors",
                  "scored": "scored-criteria", "scoring": "scored-criteria", "swing weighting": "scored-criteria",
                  "filter": "threshold-filter", "thresholds": "threshold-filter", "pros and cons": "pros-and-cons",
                  "tree": "decision-tree", "matching tree": "decision-tree", "quantified tree": "quantified-tree",
                  "expected value": "quantified-tree", "raci": "responsibility-mapping", "impact x availability": "matrix",
                  "eisenhower": "matrix"}


def from_workbook(path):
    """Read the structured Frame fields only (type_of_choice, methods, rulebook, depth, steps_skipped)."""
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    fr = {str(r[0]).strip().lower(): str(r[1] or "").strip() for r in wb["Frame"].iter_rows(min_row=1, values_only=True)
          if r and r[0]}
    raw = norm(fr.get("type_of_choice") or fr.get("archetype") or "")
    raw = raw.replace("-(conditional)", "-by-situation").replace("(conditional)", "by-situation")
    choice = raw if raw in CHOICES else next((c for c in sorted(CHOICES, key=len, reverse=True) if raw.startswith(c)), "")
    if raw and not choice:
        print(f"NOTE: type_of_choice '{fr.get('type_of_choice')}' not recognised; use one of {', '.join(CHOICES)}")
    methods = []
    for part in re.split(r"[,;/+]| then | and ", fr.get("methods") or fr.get("mechanism") or ""):
        x = part.strip().lower()
        if not x:
            continue
        m = norm(x)
        m = m if m in METHODS else METHOD_ALIASES.get(x, "")
        if m and m not in methods:
            methods.append(m)
        elif not m:
            print(f"NOTE: method '{part.strip()}' not recognised; use one of {', '.join(METHODS)}")
    d = fr.get("depth", "").lower()
    depth = "full" if d.startswith("full") else "quick" if d.startswith("quick") else "standard"
    rbt = fr.get("rulebook", "").lower()
    rb = "green-book" if "green" in rbt else "us-federal" if ("us" in rbt.split() or "federal" in rbt) else "general-method"
    m = re.match(r"\s*((?:10|[1-9])(?:\s*,\s*(?:10|[1-9]))*)\s*(?:$|[;(.])", fr.get("steps_skipped", ""))
    skip = [int(n) for n in re.findall(r"10|[1-9]", m.group(1))] if m else []
    if fr.get("steps_skipped") and not m:
        print("NOTE: steps_skipped should hold step numbers only (e.g. '3, 6'); nothing was skipped.")
    return choice, methods, rb, depth, skip, fr.get("decision", "")


def applies(tag, choice, methods, solo):
    if not tag:
        return True
    have = set(methods) | ({choice} if choice else set())
    for t in tag.split(","):
        if t == "group":
            if solo:
                return False
            continue
        if not methods and t in GROUPS and t != "structure":
            return True        # no methods named: keep everything
        if t in have or (GROUPS.get(t, set()) & have):
            continue
        return False
    return True


def build(choice, methods, rulebook, depth, skip, solo=False):
    lim = LEVEL[depth]
    keep = lambda items: [i for d, i, t in items if LEVEL[d] <= lim and applies(t, choice, methods, solo)]
    sections = []
    for path in sorted(glob.glob(os.path.join(REF, "steps", "*.md"))):
        n = int(os.path.basename(path)[:2])
        if n in skip:
            continue
        title, items = read_file(path)
        sections.append((title, keep(items)))
    extra = [("rulebooks", rulebook)] + [("methods", m) for m in methods] + ([("choices", choice)] if choice else [])
    for folder, name in extra:
        path = os.path.join(REF, folder, name + ".md")
        if not os.path.exists(path):
            raise SystemExit(f"Unknown {folder[:-1]}: {name}")
        title, items = read_file(path)
        sections.append((title, keep(items)))
    return [s for s in sections if s[1]]


def write_md(path, title, meta, sections):
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n{meta}\n\n")
        for s, items in sections:
            f.write(f"## {s}\n\n" + "".join(f"- [ ] {i}\n" for i in items) + "\n")


def write_docx(path, title, meta, sections):
    from docx import Document
    from docx.shared import Pt, Inches
    d = Document()
    sec = d.sections[0]
    sec.left_margin = sec.right_margin = Inches(0.75)
    st = d.styles["Normal"]; st.font.name = "Arial"; st.font.size = Pt(10)
    d.add_heading(title, level=1)
    d.add_paragraph(meta)
    d.add_paragraph("Tick each item when it's done, or write why it doesn't apply. Space is left for handwriting.")
    widths = [Inches(0.35), Inches(3.75), Inches(0.95), Inches(0.8), Inches(1.15)]
    for s, items in sections:
        d.add_heading(s, level=2)
        t = d.add_table(rows=1, cols=5)
        t.style = "Table Grid"
        t.autofit = False
        for c, h in zip(t.rows[0].cells, ["", "Item", "Owner", "Date", "Notes"]):
            c.text = h
            for r in c.paragraphs[0].runs:
                r.bold = True
        for i in items:
            row = t.add_row()
            row.height = Inches(0.42)
            row.cells[0].text = "☐"; row.cells[1].text = i
        for j, wd in enumerate(widths):
            t.columns[j].width = wd
            for c in t.columns[j].cells:
                c.width = wd
    d.save(path)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--choice", "--archetype", dest="choice", default="")
    p.add_argument("--methods", "--mechanisms", dest="methods", default="", help="comma-separated")
    p.add_argument("--rulebook", "--context", dest="rulebook", default="general-method")
    p.add_argument("--depth", default="standard", choices=list(LEVEL))
    p.add_argument("--skip", default="", help="comma-separated step numbers to leave out")
    p.add_argument("--workbook", help="read choices from the workbook Frame tab")
    p.add_argument("--solo", action="store_true", help="one person is scoring: leave out group-scoring items")
    p.add_argument("--title", default="")
    p.add_argument("--out", default="choosewell-checklist.docx")
    a = p.parse_args()
    decision = ""
    if a.workbook:
        choice, methods, rb, depth, skip, decision = from_workbook(a.workbook)
    else:
        choice = norm(a.choice) if a.choice else ""
        methods = [norm(m) for m in a.methods.split(",") if m.strip()]
        rb, depth = norm(a.rulebook), a.depth
        skip = [int(x) for x in a.skip.split(",") if x.strip()]
    sections = build(choice, methods, rb, depth, skip, a.solo)
    title = a.title or "Choosewell checklist" + (f": {decision}" if decision else "")
    meta = (f"Type of choice: {choice or 'n/a'} | Methods: {', '.join(methods) or 'n/a'} | Rulebook: {rb} | "
            f"Depth: {depth}" + (f" | Steps skipped: {', '.join(map(str, skip))}" if skip else "") +
            f" | Generated {datetime.date.today().isoformat()}")
    out = a.out
    if out.endswith(".docx"):
        try:
            write_docx(out, title, meta, sections)
        except ImportError:
            out = out[:-5] + ".md"
            write_md(out, title, meta, sections)
            print("python-docx not installed: wrote Markdown instead")
    else:
        write_md(out, title, meta, sections)
    print(f"Wrote {out} ({sum(len(v) for _, v in sections)} items)")


if __name__ == "__main__":
    main()
