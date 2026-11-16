"""The release file is built correctly: one choosewell/ folder, SKILL.md at its top, no repo-only files,
and no archive inside it (claude.ai rejects a skill zip that contains another zip)."""
import os, subprocess, sys, tempfile, unittest, zipfile

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


class TestPackage(unittest.TestCase):
    def test_skill_file(self):
        with tempfile.TemporaryDirectory() as d:
            r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "package.py"), d], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            names = zipfile.ZipFile(os.path.join(d, "choosewell.zip")).namelist()
        self.assertIn("choosewell/SKILL.md", names)
        self.assertTrue(all(n.startswith("choosewell/") for n in names))
        for left_out in ("choosewell/tests/", "choosewell/docs/", "choosewell/.github/", "choosewell/tools/"):
            self.assertFalse(any(n.startswith(left_out) for n in names), left_out)
        self.assertFalse([n for n in names if n.lower().endswith((".zip", ".skill", ".tar", ".gz", ".7z", ".rar"))])
        self.assertIn("choosewell/assets/choosewell-guide.docx", names)


if __name__ == "__main__":
    unittest.main()
