#!/usr/bin/env python3
"""Hand the finished front page to the make.fun harness.

The image itself is rendered ahead of time by build_image.py and shipped
in this repository as entry.png. This program only copies that one file
into the folder the harness points at with $MAKEFUN_OUTPUT_DIR, then
checks the copy byte for byte. Standard library only, no network, and
the same bytes come out on every run.
"""

import hashlib
import os
import shutil
import sys
from pathlib import Path


def digest(path: Path) -> str:
    """SHA-256 of a file, read in chunks."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def output_folder() -> Path:
    """The harness output folder, from $MAKEFUN_OUTPUT_DIR."""
    raw = os.environ.get("MAKEFUN_OUTPUT_DIR", "").strip()
    if not raw:
        raise SystemExit(
            "MAKEFUN_OUTPUT_DIR is not set; the harness must set it first."
        )
    folder = Path(raw).expanduser()
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def deliver() -> int:
    """Copy entry.png to the output folder and verify the copy."""
    here = Path(__file__).resolve().parent
    source = here / "entry.png"
    if not source.is_file():
        raise SystemExit(f"entry image missing: {source}")
    target = output_folder() / "entry.png"
    shutil.copyfile(source, target)
    if digest(source) != digest(target):
        target.unlink(missing_ok=True)
        raise SystemExit("copy check failed: hashes differ; bad copy removed.")
    print(
        f"delivered {target} "
        f"({target.stat().st_size} bytes, sha256 {digest(target)})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(deliver())
