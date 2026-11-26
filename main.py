"""Deliver the bundled front page to the grader output directory.

The newspaper image for this entry is pre-rendered and committed next to
this script as entry.png. Running the entry simply copies that file into
the output directory the grader provides through MAKEFUN_OUTPUT_DIR (or
into a local out/ folder when the variable is not set), so the entry
runs anywhere with nothing but the Python standard library.
"""

import os
import shutil
import sys
from pathlib import Path

IMAGE_NAME = "entry.png"


def output_directory() -> Path:
    configured = os.environ.get("MAKEFUN_OUTPUT_DIR", "").strip()
    if configured:
        return Path(configured)
    return Path(__file__).resolve().parent / "out"


def main() -> int:
    here = Path(__file__).resolve().parent
    source = here / IMAGE_NAME
    if not source.is_file():
        print(f"bundled image not found: {source}", file=sys.stderr)
        return 1

    destination_dir = output_directory()
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / IMAGE_NAME
    shutil.copyfile(source, destination)

    print(f"{IMAGE_NAME} copied to {destination} ({destination.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
