#!/usr/bin/env python3
"""Migrate Hugo flat posts to page bundles.

Baseline audit (before migration):
  Static files total:          888
    originals:                 535
    WP-resized copies:         353
  Refs in content:             864
    to resized versions:       350
  Unreferenced files:          24
    unreferenced originals:    21
  Broken refs (missing file):  0

What it does:
- Copies each post's referenced images into its bundle directory
- Strips WP-resized suffixes (image-1024x768.jpg → image.jpg)
- Rewrites /wp-content/uploads/YYYY/MM/image.jpg → image.jpg (relative)
- Normalizes .jpeg → .jpg (two-pass to handle WP artifact image.jpg.jpeg → image.jpg)
- Updates cover.image frontmatter to relative path + relative: true
- Converts content/blog/slug.md → content/blog/slug/index.md
- Converts content/*.md → content/slug/index.md (projects, 3d-prints, contact)

No filename conflict handling is required: all same-basename cases resolve to either the
same source file (resized + original → one copy) or an analysis artifact from
comma-separated gallery parameters.

Run in dry-run mode first (default), then with --apply to make changes.

Usage:
    python3 scripts/migrate_to_bundles.py          # dry run
    python3 scripts/migrate_to_bundles.py --apply  # make changes
    python3 scripts/migrate_to_bundles.py --post SLUG --apply  # single post
"""
import argparse
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).parent.parent
CONTENT = ROOT / "content"
STATIC_UPLOADS = ROOT / "static" / "wp-content" / "uploads"

# Matches /wp-content/uploads/YYYY/MM/name or /wp-content/uploads/slider/name
# The comma exclusion handles figure-gallery shortcode parameters correctly
WP_PATH_RE = re.compile(r"/wp-content/uploads/[^\s\"',)\]>]+")
RESIZED_RE = re.compile(r"^(.+?)(-\d+x\d+)(\.\w+)$")
COVER_IMAGE_RE = re.compile(
    r'^(\s*image:\s*")(/wp-content/uploads/[^"]+)(")',
    re.MULTILINE,
)
COVER_RELATIVE_RE = re.compile(r"^(\s*relative:\s*)false", re.MULTILINE)


def normalize_ext(name: str) -> str:
    """Normalize .jpeg → .jpg; handle WP double-extension artifact .jpg.jpeg → .jpg."""
    name = re.sub(r"\.jpe?g$", ".jpg", name, flags=re.I)  # .jpeg → .jpg
    name = re.sub(r"\.jpg\.jpg$", ".jpg", name, flags=re.I)  # .jpg.jpg → .jpg
    return name


def resolve_original(wp_path: str) -> Path | None:
    """Return the full-size original Path for a /wp-content/... ref.

    Strips -NNNxNNN suffix and looks for the non-resized version first.
    Returns None if no file is found on disk.
    """
    rel = wp_path.lstrip("/")
    candidate = ROOT / "static" / rel
    m = RESIZED_RE.match(candidate.name)
    if m:
        original = candidate.parent / (m.group(1) + m.group(3))
        if original.exists():
            return original
    if candidate.exists():
        return candidate
    return None


def bundle_name(wp_path: str) -> str:
    """Return the filename this wp_path will have inside its bundle."""
    src = resolve_original(wp_path)
    name = src.name if src else Path(wp_path).name
    return normalize_ext(name)


def migrate_post(md_path: Path, bundle_dir: Path, apply: bool) -> None:
    """Migrate one .md file into a page bundle."""
    text = md_path.read_text()

    # Track unique copies: bundle_filename → source Path
    copies: dict[str, Path] = {}

    def plan_ref(match: re.Match) -> str:
        wp_path = match.group(0)
        src = resolve_original(wp_path)
        name = normalize_ext(src.name if src else Path(wp_path).name)
        if src:
            copies[name] = src
        else:
            print(f"  MISSING: {wp_path}")
        return name

    new_text = WP_PATH_RE.sub(plan_ref, text)

    # Fix cover.image frontmatter
    def plan_cover(match: re.Match) -> str:
        name = bundle_name(match.group(2))
        src = resolve_original(match.group(2))
        if src:
            copies[name] = src
        return match.group(1) + name + match.group(3)

    new_text = COVER_IMAGE_RE.sub(plan_cover, new_text)
    new_text = COVER_RELATIVE_RE.sub(r"\g<1>true", new_text)

    if not apply:
        print(f"  DRY RUN → {bundle_dir.name}/  ({len(copies)} assets)")
        for name, src in copies.items():
            print(f"    {'✓' if src.exists() else '✗'} {src.relative_to(ROOT/'static')} → {name}")
        return

    bundle_dir.mkdir(parents=True, exist_ok=True)
    (bundle_dir / "index.md").write_text(new_text)
    for name, src in copies.items():
        dest = bundle_dir / name
        if not dest.exists() and src.exists():
            shutil.copy2(src, dest)
    md_path.unlink()
    print(f"  ✓ {md_path.name} → {bundle_dir.name}/  ({len(copies)} assets)")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--post", help="Migrate only this slug")
    args = parser.parse_args()

    for md_path in sorted((CONTENT / "blog").glob("*.md")):
        if args.post and md_path.stem != args.post:
            continue
        migrate_post(md_path, CONTENT / "blog" / md_path.stem, args.apply)

    for md_path in sorted(CONTENT.glob("*.md")):
        if md_path.name == "_index.md":
            continue
        if args.post and md_path.stem != args.post:
            continue
        migrate_post(md_path, CONTENT / md_path.stem, args.apply)


if __name__ == "__main__":
    main()
