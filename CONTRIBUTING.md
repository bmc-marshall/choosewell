# Contributing

Thanks for helping improve Choosewell. Suggestions, corrections and new worked examples are all welcome: open an issue or a pull request.

## Ground rules

- **No client or confidential material.** Worked examples must be invented, or composites with identifying details changed. No organisation names, people, quotes or figures from real engagements.
- **Write for people.** Follow `references/presenting/writing.md`: plain words, explain each method the first time, show calculations, name sources.
- **One home for each idea.** Each concept is explained once, in the file listed in `references/glossary.md`; elsewhere, point to it.
- **Cite sources** for any external method in `references/presenting/sources-of-methods.md`.

## Before you open a pull request

```bash
pip install -r requirements.txt
python3 scripts/check_consistency.py          # skill files, guide and checklists agree
python3 -m unittest discover -s tests -v       # scripts give the right answers
```

If you changed anything that also appears in the offline guide (step names, methods, calculations), update `scripts/build_guide.js` and rebuild:

```bash
npm install docx                                # once
node scripts/build_guide.js                     # writes assets/choosewell-guide.docx
```

Diagrams live in `assets/guide/*.mmd`; re-render with Mermaid CLI (`mmdc -i file.mmd -o file.png`).

## Keeping guidance current

The UK and US rulebooks summarise official guidance that changes. When you update one, check the source, change the "as of" date at the top of the file, and add a line to `CHANGELOG.md`.

## Packaging a release

Versions follow [semantic versioning](https://semver.org): a **patch** (1.0.0 → 1.0.1) for fixes that add nothing new, a **minor** version (1.0.0 → 1.1.0) for new methods, steps, checks or script features that don't break existing use, and a **major** version (1.x → 2.0.0) for changes that do, such as renamed files or script commands that people's workbooks depend on.

Add an entry to `CHANGELOG.md`, then publish a release on GitHub with a new tag like `v1.1.0`. The workflow builds `choosewell.skill` with `tools/package.py` and attaches it and the Word guide to the release. To build it yourself, run `python3 tools/package.py` (it writes `dist/choosewell.skill`).
