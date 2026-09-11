#!/usr/bin/env python3
"""Build a single-file windowed (no console) exe with PyInstaller.

Usage (from project root):
    .venv/Scripts/python.exe script/build_exe.py        (Windows)
    .venv/bin/python script/build_exe.py               (Linux/macOS)

Output: output/BSOD_Pomodoro.exe (one file, no console window).
This file intentionally contains ASCII characters only.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "output"
APP_NAME = "BSOD_Pomodoro"
ENTRY = ROOT / "main.py"
ICON = ROOT / "icon" / "logo.ico"

# Data files required at runtime; format: "source;dest_dir" (PyInstaller syntax).
# Only the default presets are bundled: data/settings.json is runtime user
# state and is written next to the exe by utils/json_config.py, which also
# falls back to the bundled presets when no user copy exists.
DATA_FILES = [
    str(ROOT / "icon" / "logo.ico") + ";icon",
    str(ROOT / "icon" / "logo.png") + ";icon",  # startup splash image
    str(ROOT / "module" / "blue_screen" / "assets") + ";module/blue_screen/assets",
    str(ROOT / "data" / "presets.json") + ";data",
    str(ROOT / "translate" / "app.qm") + ";translate",
    str(ROOT / "translate" / "code.qm") + ";translate",
]


def find_pyinstaller() -> str:
    """Locate pyinstaller: prefer the venv binary, fall back to PATH."""
    if sys.platform == "win32":
        candidate = ROOT / ".venv" / "Scripts" / "pyinstaller.exe"
    else:
        candidate = ROOT / ".venv" / "bin" / "pyinstaller"
    if candidate.exists():
        return str(candidate)
    return "pyinstaller"


def main() -> int:
    for data in DATA_FILES:
        src = Path(data.split(";")[0])
        if not src.exists():
            print("Missing data file: %s" % src)
            return 1

    OUTPUT_DIR.mkdir(exist_ok=True)

    cmd = [
        find_pyinstaller(),
        "--noconfirm",
        "--clean",
        "--onefile",          # single exe
        "--noconsole",        # windowed app, no console window
        "--name", APP_NAME,
        "--icon", str(ICON),
        "--distpath", str(OUTPUT_DIR),
        "--workpath", str(OUTPUT_DIR / "build"),
        "--specpath", str(OUTPUT_DIR),
    ]
    for data in DATA_FILES:
        cmd += ["--add-data", data]
    cmd.append(str(ENTRY))

    print("Running: %s" % " ".join(cmd))
    result = subprocess.run(cmd, cwd=str(ROOT))
    if result.returncode != 0:
        print("Build FAILED")
        return 1

    exe = OUTPUT_DIR / (APP_NAME + ".exe")
    print("Build OK: %s" % exe)
    return 0


if __name__ == "__main__":
    sys.exit(main())
