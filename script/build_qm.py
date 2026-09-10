#!/usr/bin/env python3
"""Compile every .ts file under translate/ into .qm using pyside6-lrelease.

Usage (from project root):
    .venv/Scripts/python.exe script/build_qm.py        (Windows)
    .venv/bin/python script/build_qm.py                (Linux/macOS)

This file intentionally contains ASCII characters only.
"""

import subprocess
import sys
from pathlib import Path

# Project root = parent of this script's directory
ROOT = Path(__file__).resolve().parent.parent
TRANSLATE_DIR = ROOT / "translate"


def find_lrelease() -> str:
    """Locate pyside6-lrelease: prefer the venv binary, fall back to PATH."""
    if sys.platform == "win32":
        candidate = ROOT / ".venv" / "Scripts" / "pyside6-lrelease.exe"
    else:
        candidate = ROOT / ".venv" / "bin" / "pyside6-lrelease"
    if candidate.exists():
        return str(candidate)
    return "pyside6-lrelease"


def main() -> int:
    ts_files = sorted(TRANSLATE_DIR.glob("*.ts"))
    if not ts_files:
        print("No .ts files found in %s" % TRANSLATE_DIR)
        return 1

    lrelease = find_lrelease()
    failed = []
    for ts in ts_files:
        print("Compiling %s ..." % ts.name)
        result = subprocess.run([lrelease, str(ts)], cwd=str(ROOT))
        if result.returncode != 0:
            failed.append(ts.name)

    if failed:
        print("FAILED: %s" % ", ".join(failed))
        return 1
    print("All %d translation file(s) compiled." % len(ts_files))
    return 0


if __name__ == "__main__":
    sys.exit(main())
