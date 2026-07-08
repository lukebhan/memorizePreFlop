#!/usr/bin/env python3
"""Build a self-contained Memorize PreFlop bundle with PyInstaller.

Produces dist/MemorizePreflop/ (a folder containing the executable plus the
cardimages, ranges and reports it needs) and zips it into
builds/MemorizePreflop<OS>.zip.

PyInstaller does NOT cross-compile: run this on each target OS to produce that
OS's binary (Windows on Windows, macOS on macOS, Linux on Linux). The
.github/workflows/build.yml workflow does exactly that for all three.

Usage:  python build.py
"""
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
DIST = os.path.join(ROOT, "dist")
BUILDS = os.path.join(ROOT, "builds")
NAME = "MemorizePreflop"

OS_SUFFIX = {"win32": "Windows", "darwin": "MacOS", "linux": "Linux"}.get(
    sys.platform, sys.platform
)


def main():
    # One-folder build (not one-file) so the app dir stays writable for saved
    # reports/ranges. No --windowed: a plain executable keeps the layout and
    # data/cwd model identical on every OS.
    subprocess.run(
        [
            sys.executable, "-m", "PyInstaller",
            "--noconfirm", "--clean",
            "--name", NAME,
            "--paths", SRC,
            os.path.join(SRC, "sol.py"),
        ],
        check=True,
    )

    # The executable lives in dist/MemorizePreflop/; copy the runtime data next
    # to it so the app (which chdir's to the executable's dir) finds it.
    appdir = os.path.join(DIST, NAME)
    for name, source in [
        ("cardimages", os.path.join(SRC, "cardimages")),
        ("ranges", os.path.join(ROOT, "ranges")),
        ("reports", os.path.join(ROOT, "reports")),
    ]:
        shutil.copytree(source, os.path.join(appdir, name), dirs_exist_ok=True)

    os.makedirs(BUILDS, exist_ok=True)
    archive = os.path.join(BUILDS, f"{NAME}{OS_SUFFIX}")
    shutil.make_archive(archive, "zip", DIST, NAME)
    print(f"\nBuilt {appdir}\nZipped -> {archive}.zip")


if __name__ == "__main__":
    main()
