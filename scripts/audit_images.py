#!/usr/bin/env python3
"""Audit image references in Hugo content vs files in static/.

Usage:
    python scripts/audit_images.py
"""
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent.parent
CONTENT = ROOT / "content"
STATIC = ROOT / "static" / "wp-content" / "uploads"


def find_all_refs() -> dict[str, list[str]]:
    """Return {wp_path: [content_files_that_reference_it]}."""
    refs: dict[str, list[str]] = defaultdict(list)
    for md in CONTENT.rglob("*.md"):
        text = md.read_text()
        # Split on commas and whitespace to handle gallery shortcode parameters
        for raw in re.findall(r"/wp-content/uploads/[^\s\"',)\]>]+", text):
            refs[raw].append(str(md.relative_to(ROOT)))
    return dict(refs)


def find_all_static() -> set[str]:
    """Return all files in static/wp-content/uploads/ as /wp-content/... paths."""
    paths = set()
    if STATIC.exists():
        for f in STATIC.rglob("*"):
            if f.is_file():
                paths.add("/" + str(f.relative_to(ROOT / "static")))
    return paths


def main() -> None:
    refs = find_all_refs()
    static = find_all_static()

    referenced = set(refs.keys())
    resized = {p for p in static if re.search(r"-\d+x\d+\.\w+$", p)}
    originals = static - resized

    unreferenced = static - referenced
    unreferenced_originals = unreferenced - resized
    broken = referenced - static  # referenced but missing from disk

    print(f"Static files total:          {len(static)}")
    print(f"  originals:                 {len(originals)}")
    print(f"  WP-resized copies:         {len(resized)}")
    print(f"Refs in content:             {len(referenced)}")
    print(f"  to resized versions:       {len([p for p in referenced if re.search(r'-\d+x\d+\.\w+$', p)])}")
    print(f"Unreferenced files:          {len(unreferenced)}")
    print(f"  unreferenced originals:    {len(unreferenced_originals)}")
    print(f"Broken refs (missing file):  {len(broken)}")
    if broken:
        for p in sorted(broken):
            print(f"  BROKEN: {p}")


if __name__ == "__main__":
    main()
