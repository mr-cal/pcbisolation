#!/usr/bin/env python3
"""Move all files from static/wp-content/ to unused/ as a flat directory.

Handles basename collisions (same name, different paths) by appending -2, -3, etc.
"""
import shutil
from pathlib import Path

ROOT = Path(__file__).parent.parent
SRC = ROOT / "static" / "wp-content"
DST = ROOT / "unused"
DST.mkdir(exist_ok=True)

for src_file in sorted(SRC.rglob("*")):
    if not src_file.is_file():
        continue
    dest = DST / src_file.name
    if dest.exists():
        # Collision: different paths produced the same basename
        stem, suffix = src_file.stem, src_file.suffix
        counter = 2
        while dest.exists():
            dest = DST / f"{stem}-{counter}{suffix}"
            counter += 1
    shutil.move(str(src_file), dest)

shutil.rmtree(SRC)
print(f"Moved files to {DST}")
print(f"Files in unused/: {len(list(DST.iterdir()))}")
