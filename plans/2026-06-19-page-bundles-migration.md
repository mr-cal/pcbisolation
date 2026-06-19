# Hugo Page Bundles Migration Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate 57 blog posts and 3 pages from flat markdown files with images in `static/wp-content/uploads/` to Hugo page bundles, remove 353 WP-generated resized images, and delete all unreferenced static assets.

**Architecture:** Each post becomes a directory with `index.md` + its images co-located. A Python migration script handles the transformation: it discovers every image reference per post, copies the original (not the WP-resized version) into the bundle, rewrites paths in the markdown, and deletes no longer needed files from `static/`. Pages (`projects`, `3d-prints`) are treated identically.

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
    2015/07/image-1024x768.jpg ← WP-generated resize (UNUSED post-migration)
    2015/07/image-300x225.jpg  ← WP-generated resize (UNUSED post-migration)
    ...
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
  wp-content/uploads/       ← empty after migration (removed)
```

### Key migration facts

- **888 total files** in `static/wp-content/` — 353 are WP-generated resizes
- **738 unique image refs** in content — **350 point to `-NNNxNNN.jpg` resized versions**
  that must be rewritten to the original filename
- **5 filename collisions**: `Reflow_Oven_8.jpg`, `cnc_computer_2.jpg`, `Brake-Light-5.jpg`,
  `sound-reactor-3.jpg`, `frameless-gate-10.jpg.jpeg` — each basename appears under two
  different year/month paths; resolved by prefixing with `YYYYMM-`
- **4 images shared between 2 posts** (both reference the same `/wp-content/uploads/` path);
  the image is copied into each bundle independently
- **PDFs** (`.pdf`) in `static/wp-content/uploads/` are treated like images — copied into
  the bundle that references them

### How PaperMod resolves `cover.image` as a page resource

When `cover.image` is set to a relative path (e.g., `image.jpg`) and `cover.relative: true`,
PaperMod resolves it as a page resource from the bundle directory. The script must change:

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
| `static/wp-content/` | **Delete** entirely after migration |

---

## Task 1: Write the audit script

This gives a before/after baseline. Run it before migration to record the current state.

**Files:**
- Create: `scripts/audit_images.py`

- [ ] **Step 1: Create the scripts directory and audit script**

```python
#!/usr/bin/env python3
"""Audit image references in Hugo content vs files in static/.

Usage:
    python scripts/audit_images.py
"""
import os
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
        for match in re.findall(r"/wp-content/uploads/[^\s\"')\]>]+", text):
            refs[match].append(str(md.relative_to(ROOT)))
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

Save this output somewhere (e.g., copy to a comment in the migration script).

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

- Copies each post's referenced images into its bundle directory
- Rewrites WP-resized refs (image-1024x768.jpg) to originals (image.jpg)
- Rewrites /wp-content/uploads/YYYY/MM/image.jpg to image.jpg (relative)
- Updates cover.image frontmatter to relative path + relative: true
- Converts content/blog/slug.md → content/blog/slug/index.md
- Converts content/*.md → content/slug/index.md (for projects, 3d-prints, contact)
- Disambiguates filename collisions by prefixing with YYYYMM-

Run in dry-run mode first (default), then with --apply to make changes.

Usage:
    python scripts/migrate_to_bundles.py          # dry run
    python scripts/migrate_to_bundles.py --apply  # make changes
"""
import argparse
import os
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).parent.parent
CONTENT = ROOT / "content"
STATIC_UPLOADS = ROOT / "static" / "wp-content" / "uploads"

# These basenames appear under two different YYYY/MM paths.
# We disambiguate by prefixing with YYYYMM- when copying.
KNOWN_COLLISIONS = {
    "Reflow_Oven_8.jpg",
    "cnc_computer_2.jpg",
    "Brake-Light-5.jpg",
    "sound-reactor-3.jpg",
    "frameless-gate-10.jpg.jpeg",
}

WP_PATH_RE = re.compile(
    r"/wp-content/uploads/(\d{4})/(\d{2})/([^\s\"')\]>]+)"
)
RESIZED_RE = re.compile(r"^(.+?)(-\d+x\d+)(\.\w+)$")
COVER_IMAGE_RE = re.compile(
    r'^(\s*image:\s*")(/wp-content/uploads/\d{4}/\d{2}/([^"]+))(")',
    re.MULTILINE,
)
COVER_RELATIVE_RE = re.compile(r"^(\s*relative:\s*)false", re.MULTILINE)


def original_path(resized_path: str) -> Path:
    """Return the static/ path for the original file, stripping the -NNNxNNN suffix.
    
    If the resized variant is the only thing that exists, returns that path.
    """
    m = RESIZED_RE.match(resized_path)
    if m:
        original = m.group(1) + m.group(3)  # drop -NNNxNNN
        orig_static = STATIC_UPLOADS.parent.parent / original.lstrip("/")
        if orig_static.exists():
            return orig_static
    return STATIC_UPLOADS.parent.parent / resized_path.lstrip("/")


def target_filename(wp_path: str, year: str, month: str, basename: str) -> str:
    """Return the filename to use in the bundle, disambiguating collisions."""
    if basename in KNOWN_COLLISIONS:
        return f"{year}{month}-{basename}"
    return basename


def migrate_post(md_path: Path, bundle_dir: Path, apply: bool) -> None:
    """Migrate a single .md file to a page bundle."""
    text = md_path.read_text()
    new_text = text

    # Collect all image references and plan copies
    copies: list[tuple[Path, Path]] = []  # (src, dst)

    def replace_ref(match: re.Match) -> str:
        year, month, raw_basename = match.group(1), match.group(2), match.group(3)
        src = original_path(match.group(0))
        new_basename = target_filename(match.group(0), year, month, os.path.basename(src))
        dst = bundle_dir / new_basename
        if src.exists():
            copies.append((src, dst))
        else:
            print(f"  MISSING: {match.group(0)}")
        return new_basename  # relative path in bundle

    new_text = WP_PATH_RE.sub(replace_ref, new_text)

    # Fix cover.image frontmatter
    def replace_cover(match: re.Match) -> str:
        full_wp_path = match.group(2)
        raw_basename = match.group(3)
        src = original_path(full_wp_path)
        new_basename = target_filename(
            full_wp_path,
            *re.search(r"/(\d{4})/(\d{2})/", full_wp_path).groups(),
            os.path.basename(src),
        )
        if src.exists():
            copies.append((src, bundle_dir / new_basename))
        return match.group(1) + new_basename + match.group(4)

    new_text = COVER_IMAGE_RE.sub(replace_cover, new_text)
    new_text = COVER_RELATIVE_RE.sub(r"\g<1>true", new_text)

    # Deduplicate copies (same src may appear multiple times)
    unique_copies = {dst: src for src, dst in copies}

    if not apply:
        print(f"  DRY RUN: {md_path.relative_to(ROOT)} → {bundle_dir.relative_to(ROOT)}/index.md")
        for dst, src in unique_copies.items():
            status = "✓" if src.exists() else "✗ MISSING"
            print(f"    {status} copy {src.name} → {dst.name}")
        return

    # Apply: create bundle dir, write index.md, copy images
    bundle_dir.mkdir(parents=True, exist_ok=True)
    index_md = bundle_dir / "index.md"
    index_md.write_text(new_text)
    for dst, src in unique_copies.items():
        if src.exists():
            shutil.copy2(src, dst)
    md_path.unlink()  # remove original .md
    print(f"  ✓ {md_path.name} → {bundle_dir.name}/index.md  ({len(unique_copies)} images)")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Apply changes (default: dry run)")
    parser.add_argument("--post", help="Migrate only this slug (for testing)")
    args = parser.parse_args()

    # Blog posts: content/blog/slug.md → content/blog/slug/index.md
    blog_dir = CONTENT / "blog"
    for md_path in sorted(blog_dir.glob("*.md")):
        if args.post and md_path.stem != args.post:
            continue
        bundle_dir = blog_dir / md_path.stem
        migrate_post(md_path, bundle_dir, args.apply)

    # Top-level pages: content/slug.md → content/slug/index.md
    for md_path in sorted(CONTENT.glob("*.md")):
        if md_path.name == "_index.md":
            continue
        if args.post and md_path.stem != args.post:
            continue
        bundle_dir = CONTENT / md_path.stem
        migrate_post(md_path, bundle_dir, args.apply)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run dry-run on one post to validate**

Pick the cedar gate post (it has images, a PDF, and a cover image):

```bash
cd ~/dev/cal/pcbisolation
python scripts/migrate_to_bundles.py --post fabricating-a-frameless-cedar-gate
```

Expected output:
```
  DRY RUN: content/blog/fabricating-a-frameless-cedar-gate.md → content/blog/fabricating-a-frameless-cedar-gate/index.md
    ✓ copy frameless-gate-1.pdf → frameless-gate-1.pdf
    ✓ copy frameless-gate-10.jpg → 202310-frameless-gate-10.jpg.jpeg
    ✓ copy frameless-gate-01.jpg → frameless-gate-01.jpg
    ... (all images)
```

No `✗ MISSING` lines. If there are any, resolve them before proceeding.

- [ ] **Step 3: Run dry-run on all posts**

```bash
cd ~/dev/cal/pcbisolation
python scripts/migrate_to_bundles.py 2>&1 | grep -c "DRY RUN"   # should be 60 (57 posts + 3 pages)
python scripts/migrate_to_bundles.py 2>&1 | grep "MISSING"       # should be empty
```

Fix any MISSING files before proceeding.

- [ ] **Step 4: Commit the migration script**

```bash
git add scripts/migrate_to_bundles.py
git commit -m "chore: add page bundle migration script (dry-run only)"
```

---

## Task 3: Migrate one post end-to-end, verify the build

Before migrating all 57 posts, validate the full round-trip on one.

**Files:**
- Create: `content/blog/fabricating-a-frameless-cedar-gate/index.md`
- Delete: `content/blog/fabricating-a-frameless-cedar-gate.md`

- [ ] **Step 1: Run the migration on one post**

```bash
cd ~/dev/cal/pcbisolation
python scripts/migrate_to_bundles.py --post fabricating-a-frameless-cedar-gate --apply
```

Expected:
```
  ✓ fabricating-a-frameless-cedar-gate.md → fabricating-a-frameless-cedar-gate/index.md  (N images)
```

- [ ] **Step 2: Verify bundle contents**

```bash
ls content/blog/fabricating-a-frameless-cedar-gate/
# Should list: index.md, frameless-gate-01.jpg, frameless-gate-1.pdf, etc.
# Should NOT list: frameless-gate-10.jpg.jpeg (collision → 202310-frameless-gate-10.jpg.jpeg)

grep "frameless-gate" content/blog/fabricating-a-frameless-cedar-gate/index.md | head -5
# Should show relative paths like: frameless-gate-01.jpg  (no /wp-content/... prefix)

grep "cover:" -A3 content/blog/fabricating-a-frameless-cedar-gate/index.md
# Should show:
#   cover:
#     image: "frameless-gate-04.jpg"  (or similar)
#     relative: true
#     hidden: false
```

- [ ] **Step 3: Build the site and check the post renders correctly**

```bash
cd ~/dev/cal/pcbisolation
make build    # runs hugo --minify
# Expected: no ERRORs or WARNs about missing images

make serve &  # start local server
# Open http://localhost:1313/blog/fabricating-a-frameless-cedar-gate/
# Verify: cover image, inline images, PDF embed, YouTube embed all render
kill %1
```

- [ ] **Step 4: Roll back the test post**

```bash
# Revert so the full migration in Task 4 starts clean
git checkout -- content/blog/fabricating-a-frameless-cedar-gate.md
git clean -fd content/blog/fabricating-a-frameless-cedar-gate/
```

---

## Task 4: Run the full migration

- [ ] **Step 1: Run the full migration**

```bash
cd ~/dev/cal/pcbisolation
python scripts/migrate_to_bundles.py --apply 2>&1 | tee /tmp/migration.log
```

Check the log for any MISSING files:
```bash
grep MISSING /tmp/migration.log
```

If there are any missing files, investigate and resolve before continuing.

- [ ] **Step 2: Verify all posts are now bundles**

```bash
# There should be no .md files directly in content/blog/ (only directories)
ls content/blog/*.md 2>/dev/null && echo "PROBLEM: flat .md files remain" || echo "OK: all posts are bundles"

# There should be no flat .md files in content/ (except _index.md if it exists)
ls content/*.md 2>/dev/null | grep -v "_index.md" && echo "PROBLEM: flat pages remain" || echo "OK: all pages are bundles"

# Count bundles
ls -d content/blog/*/ | wc -l   # expect 57
ls -d content/*/    | wc -l     # expect 57 + 3 pages
```

- [ ] **Step 3: Build the site**

```bash
cd ~/dev/cal/pcbisolation
make build 2>&1 | grep -E "ERROR|WARN"
# Expected: no output (no errors or warnings)
```

- [ ] **Step 4: Run htmlproofer**

```bash
make validate
# Expected: all internal links pass
```

If htmlproofer reports broken image links, the migration script missed a reference. Fix
in `index.md` for the affected post. Common cause: dynamic references in shortcodes or
HTML blocks that the regex didn't match.

- [ ] **Step 5: Commit the migrated content**

```bash
git add content/
git commit -m "feat: migrate all posts and pages to Hugo page bundles"
```

---

## Task 5: Delete unreferenced and resized static files

Now that images are in bundles, `static/wp-content/` contains only unreferenced files.

**Files:**
- Delete: `static/wp-content/` (entire directory)

- [ ] **Step 1: Run the audit to confirm nothing is still referenced**

```bash
cd ~/dev/cal/pcbisolation
python scripts/audit_images.py
```

Expected output after migration:
```
Static files total:          888
  ...
Refs in content:             0      ← no more /wp-content/... refs
  to resized versions:       0
Unreferenced files:          888    ← everything in static/wp-content/ is now orphaned
Broken refs (missing file):  0      ← images moved to bundles, refs updated
```

If "Refs in content" is not 0, there are leftover `/wp-content/` references. Find and
fix them:

```bash
grep -r "/wp-content" content/ --include="*.md" | grep -v "^Binary"
```

- [ ] **Step 2: Delete the entire wp-content static directory**

```bash
cd ~/dev/cal/pcbisolation
rm -rf static/wp-content/
```

- [ ] **Step 3: Build the site and run htmlproofer**

```bash
make build 2>&1 | grep -E "ERROR|WARN"
make validate
```

If htmlproofer reports broken links, the audit missed some references. Restore the
specific missing file from git:

```bash
git checkout HEAD -- static/wp-content/uploads/YYYY/MM/missing-file.jpg
# Then copy it to the correct bundle manually and re-delete from static/
```

- [ ] **Step 4: Check the slider directory**

The `static/wp-content/uploads/slider/` directory holds 112×75px thumbnails that are
no longer referenced post-migration. Confirm it is gone:

```bash
ls static/wp-content/ 2>/dev/null && echo "STILL EXISTS" || echo "OK: deleted"
```

- [ ] **Step 5: Commit the deletion**

```bash
git add -A static/
git commit -m "chore: remove static/wp-content/ — all assets moved to page bundles"
```

---

## Task 6: Verify the deployed site

- [ ] **Step 1: Push and check CI**

```bash
git push
```

Watch the CI run at https://github.com/mr-cal/pcbisolation/actions. All steps should
pass: validate → Hugo build → htmlproofer → gh-pages → vps-infra dispatch.

- [ ] **Step 2: Browse the site locally end-to-end**

```bash
cd ~/dev/cal/pcbisolation && make serve
```

Spot-check these pages (they cover most image types):

| Page | What to verify |
|---|---|
| `/blog/` | All post cards show thumbnails |
| `/blog/fabricating-a-frameless-cedar-gate/` | Images, PDF embed, YouTube embed |
| `/blog/building-a-standing-desk-with-a-charging-drawer-and-cable-tray/` | Gallery, YouTube embed |
| `/projects/` | All galleries show full-size images, PhotoSwipe works |
| `/3d-prints/` | All images visible, section breaks present |

- [ ] **Step 3: Commit the migration scripts**

```bash
git add scripts/
git commit -m "chore: keep migration scripts for reference"
```

---

## Notes

### Why 350 refs point to resized images

WordPress generates multiple sizes on upload (`-150x100`, `-300x225`, `-1024x768`, `-scaled`).
In post content, WordPress inserts the 1024-wide version for display and links to the
full-size. The migration script strips the `-NNNxNNN` suffix and resolves to the original.

### Future: Hugo image processing

After this migration, images are page resources and Hugo can process them. To generate
responsive images automatically, change `figure-gallery.html` to use:

```go
{{ $img := .Page.Resources.GetMatch $src }}
{{ if $img }}
  {{ $thumb := $img.Resize "560x webp" }}
  <img src="{{ $thumb.RelPermalink }}" ...>
{{ end }}
```

This would also enable automatic WebP conversion and eliminate the need for large
original images to be served directly to browsers. This is a separate task.

### Slug conflicts

`content/contact.md` currently has `url: "/contact/"` in frontmatter. Converting to
`content/contact/index.md` makes the URL `/contact/` automatically — the `url` override
in frontmatter can be removed.

Same applies to `content/projects.md` (url: "/projects/") and `content/3d-prints.md`
(url: "/3d-prints/") — the frontmatter `url` field can be removed after migration since
Hugo derives the URL from the directory name.
