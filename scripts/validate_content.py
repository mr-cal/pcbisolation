#!/usr/bin/env python3
"""Validate Hugo content directory for migration completeness.

Checks:
- Post count matches expected
- No posts contain raw <table HTML (all converted)
- Posts with sliders have {{< figure-gallery shortcodes
- All image paths in content exist in static/

Usage: python3 scripts/validate_content.py
Exit code 0 = pass, 1 = failures found.
"""
import re
import sys
from pathlib import Path

CONTENT_DIR = Path("content/blog")
STATIC_DIR = Path("static")
EXPECTED_POST_COUNT = 57

# Posts that must have pipe tables (verified from live site).
# html2text converts tables to the `col | col` format with `---` separators.
POSTS_WITH_TABLES = {
    "led-strip-current-and-power",
    "cost-of-living-breakdown-for-college-students",
    "cheapest-sources-of-protein-calories-and-macros-comparison-tables",
}

# Posts that must have figure-gallery shortcodes (Smart Slider replacements).
POSTS_WITH_GALLERIES = {
    "motorola-razr-v3-real-vs-counterfeit-teardown",
    "repairing-and-adding-bluetooth-to-a-90s-delco-radio",
    "fabricating-fold-down-bench-seats-for-a-chevy-van",
    "yeti-rambler-1-gallon-jug-vs-ozark-trail-1-gallon-jug",
    "waterproof-sound-proof-generator-enclosure",
    "making-a-dual-jet-ski-trailer-from-a-boat-trailer",
    "fabricating-a-frameless-cedar-gate",
}

failures = []

posts = list(CONTENT_DIR.glob("*.md"))
if len(posts) < EXPECTED_POST_COUNT:
    failures.append(
        f"Post count: {len(posts)} found, expected >= {EXPECTED_POST_COUNT}"
    )

for post in posts:
    slug = post.stem
    text = post.read_text(encoding="utf-8")

    if re.search(r"<table", text, re.IGNORECASE):
        failures.append(f"{post.name}: contains raw <table> HTML (not converted)")

    if slug in POSTS_WITH_TABLES:
        # html2text uses `---|` or `| --- |` separator formats — both are valid
        if not re.search(r"[-]+\s*\|", text):
            failures.append(f"{post.name}: expected pipe table not found")

    if slug in POSTS_WITH_GALLERIES:
        if "figure-gallery" not in text:
            failures.append(f"{post.name}: expected figure-gallery shortcode not found")

    # Match individual image paths — exclude shortcode images= CSV values (they contain commas)
    # Skip image existence check when static/ has no media (e.g. in CI without large files).
    if not (STATIC_DIR / "wp-content").exists():
        continue
    for img_path in re.findall(r"/wp-content/uploads/[^\s\"',)>]+", text):
        img_path = img_path.rstrip(".,;)")
        if not re.search(r"\.(jpg|jpeg|png|gif|webp|svg|pdf|mp4|zip)$", img_path, re.I):
            continue
        full_path = STATIC_DIR / img_path.lstrip("/")
        if not full_path.exists():
            failures.append(f"{post.name}: missing image {img_path}")

if failures:
    print(f"FAIL: {len(failures)} issue(s) found:")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
else:
    print(f"PASS: {len(posts)} posts validated, no issues found.")
