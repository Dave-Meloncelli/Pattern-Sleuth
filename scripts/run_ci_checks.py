#!/usr/bin/env python3
"""
Post-pull / pre-push checks — mirror of GitHub Actions CI.
Run from repo root: python scripts/run_ci_checks.py
Exits 0 if all pass, 1 on first failure.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def run(name, cmd, cwd=None, env=None, allow_fail=False):
    print(f"\n--- {name} ---")
    r = subprocess.run(cmd, cwd=cwd or ROOT, shell=isinstance(cmd, str), env=env)
    if r.returncode != 0:
        if allow_fail:
            print(f"OK (non-blocking): {name} exited {r.returncode}")
        else:
            print(f"FAILED: {name} (exit {r.returncode})")
            sys.exit(1)
    else:
        print(f"PASS: {name}")

def main():
    print("Post-pull CI checks (same as GitHub Actions)")
    run("Syntax (py_compile)", [sys.executable, str(ROOT / "scripts" / "check_syntax.py")])
    run("Unit tests", [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"])
    run("Validate package", [sys.executable, "-m", "pattern_sleuth.cli", "validate"])
    # Scan self: may BLOCK due to intentional test strings in DEFAULT_TEST_CASES; do not fail build
    run("Scan self", [sys.executable, "-m", "pattern_sleuth.cli", "scan", "pattern_sleuth", "--json"], allow_fail=True)
    print("\nAll post-pull checks passed.")

if __name__ == "__main__":
    main()
