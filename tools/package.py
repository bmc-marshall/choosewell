"""Build choosewell.zip: the installable skill, for claude.ai uploads and GitHub releases.

Run from the repository root:
    python3 tools/package.py            # writes dist/choosewell.zip
    python3 tools/package.py OUT_DIR    # writes OUT_DIR/choosewell.zip

The file is a zip holding one folder, choosewell/, with SKILL.md at its top. Repository-only files (tests, the
GitHub workflow, docs, tools) are left out. claude.ai rejects a skill that contains another zip, so the build
stops if it finds an archive inside the skill.
"""
import os
import sys
import zipfile

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
LEAVE_OUT_DIRS = {".git", ".github", "tests", "docs", "tools", "dist", "node_modules", "__pycache__"}
LEAVE_OUT_FILES = {".gitignore", ".DS_Store"}
ARCHIVES = (".zip", ".skill", ".tar", ".gz", ".tgz", ".7z", ".rar")


def skill_files(root=ROOT):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in LEAVE_OUT_DIRS)
        for f in sorted(filenames):
            if f in LEAVE_OUT_FILES or f.endswith(".pyc") or f.startswith("~$"):
                continue
            yield os.path.join(dirpath, f)


def build(out_dir):
    files = list(skill_files())
    nested = [os.path.relpath(p, ROOT) for p in files if p.lower().endswith(ARCHIVES)]
    if nested:
        sys.exit(f"Stopped: the skill contains archives, which claude.ai rejects: {', '.join(nested)}")
    if not os.path.exists(os.path.join(ROOT, "SKILL.md")):
        sys.exit("Stopped: no SKILL.md at the repository root")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "choosewell.zip")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in files:
            z.write(p, os.path.join("choosewell", os.path.relpath(p, ROOT)))
    return out


if __name__ == "__main__":
    print(build(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "dist")))
