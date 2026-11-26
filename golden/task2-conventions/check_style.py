"""Fails while library code prints, per AGENTS.md. Run: python check_style.py"""
import pathlib
import sys

bad = []
for path in pathlib.Path(".").glob("*.py"):
    if path.name.startswith("test_") or path.name == "check_style.py":
        continue
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if "print(" in line:
            bad.append("%s:%d uses print()" % (path, n))

for item in bad:
    print(item)
sys.exit(1 if bad else 0)
