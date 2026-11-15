#!/usr/bin/env python3
"""
check_consistency.py - checks that the skill's files, the offline guide and the checklists agree.

Run before every release (and after editing any reference file or scripts/build_guide.js):
    python3 scripts/check_consistency.py
Exits with status 1 and a list of problems if anything is out of step.
"""
import glob, os, re, sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
REF = os.path.join(ROOT, "references")
GUIDE = os.path.join(ROOT, "scripts", "build_guide.js")
# method file -> anchor used for it in the guide
METHOD_ANCHORS = {"threshold-filter": "mech-threshold", "scored-criteria": "mech-scored",
                  "rag-success-factors": "mech-rag", "matrix": "mech-matrix", "decision-tree": "mech-tree",
                  "quantified-tree": "mech-qtree", "pros-and-cons": "mech-proscons",
                  "responsibility-mapping": "mech-raci"}
problems = []


def read(p):
    return open(p, encoding="utf-8").read()


def rel(p):
    return os.path.relpath(p, ROOT)


md_files = [os.path.join(ROOT, "SKILL.md"), os.path.join(ROOT, "README.md")] + \
    sorted(glob.glob(os.path.join(REF, "**", "*.md"), recursive=True))

# 1. every referenced file exists
for p in md_files:
    for ref in re.findall(r"`((?:references/)?(?:steps|choices|methods|rulebooks|topics|presenting)/[a-z0-9-]+\.md)`", read(p)):
        target = os.path.join(ROOT, ref) if ref.startswith("references/") else os.path.join(REF, ref)
        if not os.path.exists(target):
            problems.append(f"{rel(p)}: refers to missing file {ref}")
    for ref in re.findall(r"`((?:scripts|assets)/[A-Za-z0-9_./-]+)`", read(p)):
        if not os.path.exists(os.path.join(ROOT, ref.rstrip("/"))):
            problems.append(f"{rel(p)}: refers to missing {ref}")

# 2. section references like `steps/08-test.md` §8.3 point at real sections
for p in md_files:
    for ref, sec in re.findall(r"`((?:steps|methods|choices|rulebooks)/[a-z0-9-]+\.md)` §([0-9]+[a-z]?(?:\.[0-9]+)?)", read(p)):
        target = os.path.join(REF, ref)
        if os.path.exists(target):
            heads = re.findall(r"^#{2,3} ([0-9]+[a-z]?(?:\.[0-9]+)?)[ .:]", read(target), re.M)
            if sec not in heads:
                problems.append(f"{rel(p)}: {ref} §{sec} has no matching heading")

# 3. every reference file except topics/presenting/glossary has a well-formed checklist
for p in glob.glob(os.path.join(REF, "*", "*.md")):
    folder = os.path.basename(os.path.dirname(p))
    if folder in ("topics", "presenting"):
        continue
    text = read(p)
    if "\n## Checklist\n" not in text:
        problems.append(f"{rel(p)}: no '## Checklist' section")
        continue
    body = text.split("\n## Checklist\n", 1)[1]
    items = [l for l in body.splitlines() if l.startswith("- ")]
    if not items:
        problems.append(f"{rel(p)}: empty checklist")
    for l in items:
        if not re.match(r"- \[(quick|standard|full)\](\[[a-z,-]+\])? \S", l):
            problems.append(f"{rel(p)}: checklist line without a [quick]/[standard]/[full] tag: {l[:60]}")

# 4. step files: header table and titles match the guide
guide = read(GUIDE) if os.path.exists(GUIDE) else ""
guide_steps = dict((int(n), t) for n, t in re.findall(r'STEP\((\d+), "([^"]+)"', guide))
for p in sorted(glob.glob(os.path.join(REF, "steps", "*.md"))):
    n = int(os.path.basename(p)[:2])
    text = read(p)
    m = re.match(r"# Step (\d+): (.+)", text)
    if not m or int(m.group(1)) != n:
        problems.append(f"{rel(p)}: first line should be '# Step {n}: ...'")
        continue
    title = re.sub(r"\s*\(.*?\)\s*$", "", m.group(2)).strip()
    for field in ("Skip if", "You'll end up with", "Next"):
        if f"| {field} |" not in text:
            problems.append(f"{rel(p)}: header table missing '{field}'")
    if guide and guide_steps.get(n, "").lower() != title.lower():
        problems.append(f"Step {n} title differs: file '{title}' vs guide '{guide_steps.get(n)}'")
if guide and len(guide_steps) != len(glob.glob(os.path.join(REF, "steps", "*.md"))):
    problems.append("Number of steps in the guide differs from references/steps/")

# 5. methods: each listed in SKILL.md, in the checklist script, and present in the guide
skill = read(os.path.join(ROOT, "SKILL.md"))
checklist_py = read(os.path.join(ROOT, "scripts", "checklist.py"))
for p in glob.glob(os.path.join(REF, "methods", "*.md")):
    name = os.path.basename(p)[:-3]
    if f'"{name}"' not in checklist_py:
        problems.append(f"methods/{name}.md is not in scripts/checklist.py METHODS")
    if guide and f'"{METHOD_ANCHORS.get(name, "?")}"' not in guide:
        problems.append(f"methods/{name}.md has no section in the guide (anchor {METHOD_ANCHORS.get(name)})")
for p in glob.glob(os.path.join(REF, "choices", "*.md")):
    name = os.path.basename(p)[:-3]
    if f"choices/{name}.md" not in skill:
        problems.append(f"choices/{name}.md is not in SKILL.md's Tree 1 table")
    if f'"{name}"' not in checklist_py:
        problems.append(f"choices/{name}.md is not in scripts/checklist.py CHOICES")

# 6. guide internal links all resolve (the build also checks this)
if guide:
    anchors = set(re.findall(r'H[123]\([^)]*?"([a-z0-9-]+)"', guide)) | set(re.findall(r'(?:MECH|CALC|TPL)\("[^"]+", "([a-z0-9-]+)"', guide))
    anchors |= {"s%d" % n for n in guide_steps} | {"t1", "t2", "t3", "guide", "trees", "toolkit"}
    for a in set(re.findall(r"\[\[[^|\]]+\|([a-z0-9-]+)\]\]", guide)):
        if a not in anchors and a != "anchor":  # "anchor" appears in the link-syntax comment
            problems.append(f"guide link to unknown anchor '{a}'")

# 7. description length limit
desc = re.search(r"^description: (.*)$", skill, re.M)
if not desc or len(desc.group(1)) > 1024:
    problems.append("SKILL.md description missing or over 1024 characters")

if problems:
    print(f"{len(problems)} problem(s):")
    for x in problems:
        print("  - " + x)
    sys.exit(1)
print("All consistency checks passed.")
