#!/usr/bin/env python3
"""Compile all Python files under pattern_sleuth/ to catch syntax errors. Exit 0 on success, 1 on failure."""
import py_compile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKAGE_DIR = ROOT / "pattern_sleuth"

def main():
    failed = []
    for f in sorted(PACKAGE_DIR.rglob("*.py")):
        try:
            py_compile.compile(str(f), doraise=True)
        except py_compile.PyCompileError as e:
            failed.append((f, e))
    if failed:
        for path, err in failed:
            print(f"{path}: {err}", file=sys.stderr)
        sys.exit(1)
    print(f"OK: compiled {len(list(PACKAGE_DIR.rglob('*.py')))} files")
    sys.exit(0)

if __name__ == "__main__":
    main()
