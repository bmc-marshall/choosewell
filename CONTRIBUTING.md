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

Bump the version in `CHANGELOG.md`, then zip the skill folder without repository-only files (`tests/`, `.github/`, `docs/`) as `choosewell.skill`, and attach it and the guide to the GitHub release.
