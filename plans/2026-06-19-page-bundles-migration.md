# Hugo Page Bundles Migration Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate 57 blog posts and 3 pages from flat markdown files with images in `static/wp-content/uploads/` to Hugo page bundles, normalize `.jpeg` → `.jpg`, move unused assets to `unused/`, and remove WP-generated resized copies.

**Architecture:** Each post becomes a directory with `index.md` + its images co-located. A Python migration script discovers every image reference per post, always resolves to the full-size original (stripping the WP `-NNNxNNN` resize suffix), normalizes `.jpeg` → `.jpg`, copies files into the bundle, and rewrites paths in the markdown. No filename conflict handling is needed: all apparent same-basename cases are either (a) the resized version and original of the same file (resolved to one copy), or (b) shared across posts (same file, copied to each bundle independently). Unreferenced static files go to `unused/` for manual review.

**Tech Stack:** Hugo page bundles, Python 3 (migration script), PaperMod cover image page-resource resolution.

---

## Context

### Current structure

```
content/
  blog/
    post-slug.md          ← flat file
    ...
  projects.md
  3d-prints.md
  contact.md
static/
  wp-content/uploads/
    2015/07/image.jpg          ← original
    2015/07/image-1024x768.jpg ← WP-generated resize (goes to unused/ post-migration)
    2015/07/image-300x225.jpg  ← WP-generated resize (goes to unused/ post-migration)
    slider/                    ← tiny Smart Slider thumbnails (goes to unused/)
    ...
unused/                        ← does not exist yet (flat directory)
```

### Target structure

```
content/
  blog/
    post-slug/
      index.md              ← was post-slug.md
      image.jpg             ← copied from static/wp-content/uploads/YYYY/MM/
      ...
  projects/
    index.md
    image.jpg ...
  3d-prints/
    index.md
    image.jpg ...
  contact/
    index.md
static/
  wp-content/uploads/       ← gone after migration
unused/
  image.jpg                 ← all unreferenced files, flat (no subdirectories)
  image-1024x768.jpg        ← WP resizes also flat here
  ...
```

### Key migration facts

- **888 total files** in `static/wp-content/` — 353 are WP-generated resizes
- **738 unique image refs** in content — **350 point to `-NNNxNNN.jpg` resized versions**
  that must be rewritten to the original filename
- **No filename conflicts**: every apparent same-basename case resolves to either the same
  source file (resized + original in the same directory → one copy) or an analysis artifact
  from comma-separated gallery parameters. No `-2` suffix handling required.
- **4 images shared between 2 posts** (same `/wp-content/uploads/` path referenced from two
  different posts) — the file is copied into each bundle independently.
- **Extension normalization**: `.jpeg` → `.jpg` (same format, different extension).
  WP double-extension artifact `image.jpg.jpeg` → `image.jpg` (two-pass strip).
  `.png`, `.gif`, `.zip`, `.pdf`, `.xlsx`, `.csv` are kept as-is.
- **PDFs and other non-image files** referenced in content are copied into their bundle.

### How PaperMod resolves `cover.image` as a page resource

When `cover.image` is a relative path and `cover.relative: true`, PaperMod resolves it
from the bundle directory. The script must change:

```yaml
cover:
  image: "/wp-content/uploads/2025/05/standing-desk-14.jpg"
  relative: false
```

to:

```yaml
cover:
  image: "standing-desk-14.jpg"
  relative: true
```

---

## File Map

| File | Change |
|---|---|
| `scripts/migrate_to_bundles.py` | **Create** — migration script |
| `scripts/audit_images.py` | **Create** — audit script, run before and after |
| `content/blog/*/index.md` | **Create** (57 files) — was `content/blog/*.md` |
| `content/projects/index.md` | **Create** — was `content/projects.md` |
| `content/3d-prints/index.md` | **Create** — was `content/3d-prints.md` |
| `content/contact/index.md` | **Create** — was `content/contact.md` |
| `unused/*.jpg` (flat) | **Create** — all unreferenced static files moved here, flat |
| `static/wp-content/` | **Delete** entirely after migration |

---

## Task 1: Write the audit script

This gives a before/after baseline. Run before migration to record the current state.

**Files:**
- Create: `scripts/audit_images.py`

- [ ] **Step 1: Create the scripts directory and audit script**

```python
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
```

- [ ] **Step 2: Run the audit to record baseline**

```bash
cd ~/dev/cal/pcbisolation
python scripts/audit_images.py
```

Expected output (approximate, before migration):
```
Static files total:          888
  originals:                 535
  WP-resized copies:         353
Refs in content:             738
  to resized versions:       350
Unreferenced files:          ~150
  unreferenced originals:    ~50
Broken refs (missing file):  0
```

Save this output as a comment at the top of `scripts/migrate_to_bundles.py`.

- [ ] **Step 3: Commit**

```bash
git add scripts/audit_images.py
git commit -m "chore: add image audit script"
```

---

## Task 2: Write the migration script (dry-run mode)

**Files:**
- Create: `scripts/migrate_to_bundles.py`

- [ ] **Step 1: Create the migration script**

```python
#!/usr/bin/env python3
"""Migrate Hugo flat posts to page bundles.

What it does:
- Copies each post's referenced images into its bundle directory
- Strips WP-resized suffixes (image-1024x768.jpg → image.jpg)
- Rewrites /wp-content/uploads/YYYY/MM/image.jpg → image.jpg (relative)
- Normalizes .jpeg → .jpg (two-pass to handle WP artifact image.jpg.jpeg → image.jpg)
- Updates cover.image frontmatter to relative path + relative: true
- Converts content/blog/slug.md → content/blog/slug/index.md
- Converts content/*.md → content/slug/index.md (projects, 3d-prints, contact)

No filename conflict handling is required: all same-basename cases resolve to the
same source file (resized + original → one copy).

Run in dry-run mode first (default), then with --apply to make changes.

Usage:
    python scripts/migrate_to_bundles.py          # dry run
    python scripts/migrate_to_bundles.py --apply  # make changes
    python scripts/migrate_to_bundles.py --post SLUG --apply  # single post
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
```

- [ ] **Step 2: Run dry-run on one post to validate**

Pick the cedar gate post (images, PDF, cover image, `.jpg.jpeg` double-extension):

```bash
cd ~/dev/cal/pcbisolation
python scripts/migrate_to_bundles.py --post fabricating-a-frameless-cedar-gate
```

Expected output (no `✗` lines):
```
  DRY RUN → fabricating-a-frameless-cedar-gate/  (N assets)
    ✓ wp-content/uploads/2023/10/frameless-gate-1.pdf → frameless-gate-1.pdf
    ✓ wp-content/uploads/2023/10/frameless-gate-10.jpg.jpeg → frameless-gate-10.jpg
    ✓ wp-content/uploads/2023/10/frameless-gate-04.jpg → frameless-gate-04.jpg
    ...
```

Confirm `frameless-gate-10.jpg.jpeg` → `frameless-gate-10.jpg` (not `frameless-gate-10.jpg.jpg`).

- [ ] **Step 3: Run dry-run on all posts**

```bash
cd ~/dev/cal/pcbisolation
python scripts/migrate_to_bundles.py 2>&1 | grep -c "DRY RUN"   # expect 60
python scripts/migrate_to_bundles.py 2>&1 | grep "MISSING"       # expect empty
```

Fix any MISSING files before proceeding.

- [ ] **Step 4: Commit the scripts**

```bash
git add scripts/
git commit -m "chore: add page bundle migration scripts (dry-run validated)"
```

---

## Task 3: Migrate one post end-to-end, verify the build

- [ ] **Step 1: Run the migration on one post**

```bash
cd ~/dev/cal/pcbisolation
python scripts/migrate_to_bundles.py --post fabricating-a-frameless-cedar-gate --apply
```

- [ ] **Step 2: Verify bundle contents**

```bash
ls content/blog/fabricating-a-frameless-cedar-gate/
# Lists: index.md + all images with .jpg extensions (no .jpeg)
# frameless-gate-10.jpg.jpeg is now frameless-gate-10.jpg

grep "frameless-gate" content/blog/fabricating-a-frameless-cedar-gate/index.md | head -5
# Shows relative filenames: frameless-gate-01.jpg  (no /wp-content/ prefix)

grep -A3 "cover:" content/blog/fabricating-a-frameless-cedar-gate/index.md
# Shows:  image: "frameless-gate-04.jpg"
#         relative: true
```

- [ ] **Step 3: Build and verify**

```bash
cd ~/dev/cal/pcbisolation
make build 2>&1 | grep -E "ERROR|WARN"   # expect: no output
make serve &
# Visit http://localhost:1313/blog/fabricating-a-frameless-cedar-gate/
# Verify: cover image, inline images, PDF embed, YouTube embed all render correctly
kill %1
```

- [ ] **Step 4: Roll back the test post**

```bash
git checkout -- content/blog/fabricating-a-frameless-cedar-gate.md
git clean -fd content/blog/fabricating-a-frameless-cedar-gate/
```

---

## Task 4: Run the full migration

- [ ] **Step 1: Run the full migration**

```bash
cd ~/dev/cal/pcbisolation
python scripts/migrate_to_bundles.py --apply 2>&1 | tee /tmp/migration.log
grep "MISSING" /tmp/migration.log    # expect: empty
```

- [ ] **Step 2: Verify all posts are now bundles**

```bash
ls content/blog/*.md 2>/dev/null && echo "PROBLEM: flat .md files remain" || echo "OK"
ls content/*.md 2>/dev/null | grep -v "_index.md" && echo "PROBLEM" || echo "OK"
ls -d content/blog/*/ | wc -l   # expect 57
```

- [ ] **Step 3: Build and validate**

```bash
make build 2>&1 | grep -E "ERROR|WARN"
make validate    # htmlproofer — expect all internal links pass
```

If htmlproofer reports broken image links, the migration missed a reference. Find them:

```bash
grep -r "/wp-content" content/ --include="*.md"    # should return nothing
```

Fix any remaining `/wp-content/` refs manually in the affected `index.md`.

- [ ] **Step 4: Commit**

```bash
git add content/
git commit -m "feat: migrate all posts and pages to Hugo page bundles"
```

---

## Task 5: Move unused static assets to `unused/` (flat)

All references now use bundle-relative paths. Everything in `static/wp-content/` is either
a WP-resized copy or an unreferenced original. Move them all into a single flat directory
so you can browse them at once and decide what to keep.

- [ ] **Step 1: Confirm no /wp-content/ refs remain**

```bash
cd ~/dev/cal/pcbisolation
python scripts/audit_images.py
# "Refs in content: 0" — nothing references /wp-content/... any more
```

- [ ] **Step 2: Flatten and move to `unused/`**

```python
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
```

Save as `scripts/flatten_unused.py` and run:

```bash
python scripts/flatten_unused.py
ls unused/ | wc -l   # expect ~888
ls static/wp-content 2>/dev/null && echo "PROBLEM" || echo "OK: static/wp-content gone"
```

- [ ] **Step 3: Build and validate**

```bash
make build 2>&1 | grep -E "ERROR|WARN"
make validate
```

If htmlproofer reports broken links, restore the specific file from `unused/` into the
correct bundle:

```bash
cp unused/missing-file.jpg content/blog/affected-post/missing-file.jpg
```

Then re-run `make validate`.

- [ ] **Step 4: Commit**

```bash
git add -A scripts/ static/ unused/
git commit -m "chore: move unused static assets to unused/ (flat) for review"
```

---

## Task 6: Verify and clean up

- [ ] **Step 1: Push and watch CI**

```bash
git push
```

All steps should pass: validate → Hugo build → htmlproofer → gh-pages → vps-infra dispatch.
Watch at https://github.com/mr-cal/pcbisolation/actions.

- [ ] **Step 2: Browse locally**

```bash
cd ~/dev/cal/pcbisolation && make serve
```

Spot-check:

| Page | What to verify |
|---|---|
| `/blog/` | All post cards show thumbnails |
| `/blog/fabricating-a-frameless-cedar-gate/` | Images, PDF embed, YouTube embed |
| `/blog/building-a-standing-desk-with-a-charging-drawer-and-cable-tray/` | Gallery, YouTube embed |
| `/projects/` | All galleries show full-size images, PhotoSwipe lightbox works |
| `/3d-prints/` | All images visible, section breaks present |

- [ ] **Step 3: Review `unused/` at your leisure**

```bash
ls unused/ | wc -l          # ~888 files: 353 WP-resizes + unreferenced originals
ls unused/*.jpg | head -20  # browse the flat list
```

Delete the directory when you're done — this is a manual step outside the plan.

---

## Notes

### Why no collision handling is needed

All 308 apparent same-basename cases in the content refs are `(image-1024x768.jpg, image.jpg)`
pairs from the **same directory** — the WP thumbnail/original link pattern:

```markdown
[![](image-1024x768.jpg)](image.jpg)
```

Both resolve to `image.jpg` from the same source file. One copy lands in the bundle.
There are no cases where two different source files would produce the same target name.

### Extension normalization scope

Only `.jpeg` → `.jpg` (two-pass to handle the WP artifact `image.jpg.jpeg`):

```python
name = re.sub(r"\.jpe?g$", ".jpg", name, flags=re.I)  # .jpeg → .jpg
name = re.sub(r"\.jpg\.jpg$", ".jpg", name, flags=re.I)  # .jpg.jpg → .jpg
```

`.png`, `.gif`, `.zip`, `.pdf`, `.xlsx`, `.csv` are left unchanged.

### Future: Hugo image processing

After this migration, images are page resources and Hugo can generate responsive sizes
and WebP automatically. To enable in `figure-gallery.html`:

```go
{{ $img := .Page.Resources.GetMatch $src }}
{{ if $img }}
  {{ $thumb := $img.Resize "560x webp" }}
  <img src="{{ $thumb.RelPermalink }}" ...>
{{ end }}
```

### Frontmatter `url:` cleanup

`content/projects.md`, `content/3d-prints.md`, and `content/contact.md` have `url: "/slug/"`
in frontmatter. After migration to `content/slug/index.md`, Hugo derives the URL from the
directory name automatically — the `url:` override can be removed.
