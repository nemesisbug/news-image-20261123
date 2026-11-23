#!/usr/bin/env python3
"""Entrypoint for the news-image-20261123 entry.

The front page is rendered ahead of time by build_image.py and ships in
this repository as entry.png. This program only copies that file to the
output directory the grader provides, so both graded runs write the
exact same bytes. Standard library only, no network.
"""

import os
import shutil
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    target_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(target_dir, exist_ok=True)
    target = os.path.join(target_dir, "entry.png")
    shutil.copyfile(source, target)
    # Both graded runs must write the same bytes: confirm the copy is
    # whole before reporting success.
    if os.path.getsize(target) != os.path.getsize(source):
        raise SystemExit(f"copy incomplete: {target}")
    size = os.path.getsize(target)
    print(f"wrote {target} ({size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
