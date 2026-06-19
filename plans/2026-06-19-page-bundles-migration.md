# Hugo Page Bundles Migration Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate 57 blog posts and 3 pages from flat markdown files with images in `static/wp-content/uploads/` to Hugo page bundles, normalize `.jpeg` → `.jpg` extensions, move unused assets to `unused/`, and remove WP-generated resized copies.

**Architecture:** Each post becomes a directory with `index.md` + its images co-located. A Python migration script handles the transformation: it discovers every image reference per post, resolves the original (not the WP-resized version), normalizes `.jpeg` → `.jpg`, handles same-basename-different-content conflicts by incrementing a numeric suffix (`image.jpg` / `image-2.jpg`), rewrites paths in the markdown, and moves all unreferenced static files to `unused/`. Pages (`projects`, `3d-prints`) are treated identically.

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
    2015/07/image-1024x768.jpg ← WP-generated resize (unused post-migration)
    2015/07/image-300x225.jpg  ← WP-generated resize (unused post-migration)
    ...
unused/                        ← does not exist yet
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
  wp-content/uploads/...    ← everything not referenced by any post; human reviews and deletes
```

### Key migration facts

- **888 total files** in `static/wp-content/` — 353 are WP-generated resizes
- **738 unique image refs** in content — **350 point to `-NNNxNNN.jpg` resized versions**
  that must be rewritten to the original filename
- **Filename collisions** (same basename, different content): three pairs exist:
  - `Reflow_Oven_8.jpg`: `2017/04/` (3620×2413) vs `slider/` (112×75)
  - `cnc_computer_2.jpg`: `2015/07/` (1059×834) vs `slider/` (750×591)
  - `sound-reactor-3.jpg`: `2016/08/` (4234×2831) vs `slider/` (750×502)
  
  Resolution: if two different source files would land as the same name in a bundle,
  the second one is written as `name-2.jpg` and its reference in the markdown is updated
  to match. (Determined by MD5 comparison — identical files get one copy, no suffix.)
- **4 images shared between 2 posts** (both reference the same WP path); the file is
  copied into each bundle independently.
- **Extension normalization**: `.jpeg` → `.jpg` (rename only — JPEG and JPEG are the same
  format). Affects `frameless-gate-10.jpg.jpeg` → `frameless-gate-10.jpg` and the one
  other `.jpeg` file.  `.png`, `.gif`, `.zip`, `.pdf`, `.xlsx`, `.csv` are kept as-is.
- **PDFs and other non-image files** referenced in content are copied into their bundle.
- **Non-referenced files** (all WP-resized copies + truly unused originals) are moved to
  `unused/wp-content/uploads/...` preserving their relative paths.

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
| `unused/wp-content/uploads/...` | **Create** — unreferenced static files moved here |
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
- Normalizes .jpeg → .jpg extensions
- Detects same-basename collisions by MD5:
    - identical content → one copy, both refs point to same name
    - different content → second gets -2 suffix (image.jpg / image-2.jpg)
- Updates cover.image frontmatter to relative path + relative: true
- Converts content/blog/slug.md → content/blog/slug/index.md
- Converts content/*.md → content/slug/index.md

Run in dry-run mode first (default), then with --apply to make changes.

Usage:
    python scripts/migrate_to_bundles.py          # dry run
    python scripts/migrate_to_bundles.py --apply  # make changes
    python scripts/migrate_to_bundles.py --post SLUG --apply  # single post
"""
import argparse
import hashlib
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).parent.parent
CONTENT = ROOT / "content"
STATIC_UPLOADS = ROOT / "static" / "wp-content" / "uploads"

WP_PATH_RE = re.compile(
    r"/wp-content/uploads/(?:(\d{4})/(\d{2})/|slider/)([^\s\"')\]>]+)"
)
RESIZED_RE = re.compile(r"^(.+?)(-\d+x\d+)(\.\w+)$")
COVER_IMAGE_RE = re.compile(
    r'^(\s*image:\s*")(/wp-content/uploads/[^"]+/([^"/]+))(")',
    re.MULTILINE,
)
COVER_RELATIVE_RE = re.compile(r"^(\s*relative:\s*)false", re.MULTILINE)


def md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def normalize_ext(name: str) -> str:
    """Normalize .jpeg → .jpg. Leave all other extensions unchanged."""
    if name.endswith(".jpeg"):
        return name[:-5] + ".jpg"
    return name


def resolve_original(wp_path: str) -> Path | None:
    """Return the Path of the original (non-resized) file for a /wp-content/... ref.

    Strips -NNNxNNN suffix and checks for the original. Falls back to the resized
    version if no original exists. Returns None if the file is not found anywhere.
    """
    rel = wp_path.lstrip("/")  # e.g. "wp-content/uploads/2015/07/image-1024x768.jpg"
    candidate = ROOT / "static" / rel
    if candidate.exists():
        # Already the original (no resize suffix), or the only version available
        m = RESIZED_RE.match(candidate.name)
        if m:
            # Try stripping the resize suffix
            no_resize = candidate.parent / (m.group(1) + m.group(3))
            if no_resize.exists():
                return no_resize
        return candidate
    return None


def unique_dest(bundle_dir: Path, name: str, src: Path) -> tuple[Path, str]:
    """Return a (destination Path, final name) that avoids collisions.

    If a file with `name` already exists in bundle_dir:
    - same MD5 → reuse the existing file, return its path
    - different MD5 → append -2, -3, ... until a free name is found
    """
    dest = bundle_dir / name
    if not dest.exists():
        return dest, name
    if md5(dest) == md5(src):
        return dest, name  # identical content, share the file
    # Different content: find a free -N suffix
    stem = Path(name).stem
    ext = Path(name).suffix
    counter = 2
    while True:
        new_name = f"{stem}-{counter}{ext}"
        new_dest = bundle_dir / new_name
        if not new_dest.exists():
            return new_dest, new_name
        if md5(new_dest) == md5(src):
            return new_dest, new_name
        counter += 1


def migrate_post(md_path: Path, bundle_dir: Path, apply: bool) -> None:
    """Migrate one .md file into a page bundle."""
    text = md_path.read_text()

    # Map original wp path → final bundle filename (built during substitution)
    path_to_name: dict[str, str] = {}
    # Queue of (src_path, dest_name) to copy
    pending_copies: list[tuple[Path, str]] = []

    def plan_copy(wp_path: str) -> str:
        """Determine the bundle filename for a wp_path; record copy if new."""
        if wp_path in path_to_name:
            return path_to_name[wp_path]

        src = resolve_original(wp_path)
        if src is None:
            print(f"  MISSING: {wp_path}")
            path_to_name[wp_path] = Path(wp_path).name  # best effort
            return path_to_name[wp_path]

        name = normalize_ext(src.name)
        # Resolve collision against already-planned copies
        # Build a temporary in-memory view of what's in the bundle
        existing: dict[str, Path] = {}
        for _, planned_name in pending_copies:
            existing[planned_name] = src  # placeholder; collision check uses src md5
        # Use unique_dest logic manually for the planning phase
        candidate = name
        counter = 2
        for planned_src, planned_name in pending_copies:
            if planned_name == candidate:
                if md5(planned_src) == md5(src):
                    break  # same file, reuse
                candidate = f"{Path(name).stem}-{counter}{Path(name).suffix}"
                counter += 1

        path_to_name[wp_path] = candidate
        pending_copies.append((src, candidate))
        return candidate

    def replace_wp_ref(match: re.Match) -> str:
        return plan_copy(match.group(0))

    new_text = WP_PATH_RE.sub(replace_wp_ref, text)

    # Fix cover.image frontmatter
    def replace_cover(match: re.Match) -> str:
        name = plan_copy(match.group(2))
        return match.group(1) + name + match.group(4)

    new_text = COVER_IMAGE_RE.sub(replace_cover, new_text)
    new_text = COVER_RELATIVE_RE.sub(r"\g<1>true", new_text)

    if not apply:
        print(f"  DRY RUN → {bundle_dir.name}/index.md  ({len(pending_copies)} assets)")
        for src, name in pending_copies:
            print(f"    {'✓' if src.exists() else '✗'} {src.relative_to(ROOT/'static')} → {name}")
        return

    bundle_dir.mkdir(parents=True, exist_ok=True)
    (bundle_dir / "index.md").write_text(new_text)
    for src, name in pending_copies:
        dest = bundle_dir / name
        if not dest.exists() and src.exists():
            shutil.copy2(src, dest)
    md_path.unlink()
    print(f"  ✓ {md_path.name} → {bundle_dir.name}/  ({len(pending_copies)} assets)")


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

Pick the cedar gate post (images, PDF, cover image, `.jpeg` double-extension):

```bash
cd ~/dev/cal/pcbisolation
python scripts/migrate_to_bundles.py --post fabricating-a-frameless-cedar-gate
```

Expected output (no `✗` lines):
```
  DRY RUN → fabricating-a-frameless-cedar-gate/index.md  (N assets)
    ✓ wp-content/uploads/2023/10/frameless-gate-1.pdf → frameless-gate-1.pdf
    ✓ wp-content/uploads/2023/10/frameless-gate-10.jpg.jpeg → frameless-gate-10.jpg
    ✓ wp-content/uploads/2023/10/frameless-gate-04.jpg → frameless-gate-04.jpg
    ...
```

Note `frameless-gate-10.jpg.jpeg` becomes `frameless-gate-10.jpg`.

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
# Should list: index.md, frameless-gate-01.jpg, frameless-gate-10.jpg (normalized), etc.
# Should NOT list: frameless-gate-10.jpg.jpeg (double extension gone)

grep "frameless-gate" content/blog/fabricating-a-frameless-cedar-gate/index.md | head -5
# Should show relative filenames like: frameless-gate-01.jpg  (no /wp-content/ prefix)

grep -A3 "cover:" content/blog/fabricating-a-frameless-cedar-gate/index.md
# Should show:  image: "frameless-gate-04.jpg"
#               relative: true
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

If htmlproofer reports broken image links, the migration missed a reference (e.g., an
image path in a shortcode parameter or raw HTML block). Fix in the affected `index.md`:

```bash
grep -r "/wp-content" content/ --include="*.md"    # should return nothing
```

- [ ] **Step 4: Commit**

```bash
git add content/
git commit -m "feat: migrate all posts and pages to Hugo page bundles"
```

---

## Task 5: Move unused static assets to `unused/`

Now that all referenced images are in bundles, everything left in `static/wp-content/`
is either a WP-resized copy or a file never referenced by any post.

- [ ] **Step 1: Confirm nothing is still referenced**

```bash
cd ~/dev/cal/pcbisolation
python scripts/audit_images.py
# "Refs in content: 0" confirms nothing references /wp-content/... any more
```

If refs remain, fix them in content before continuing.

- [ ] **Step 2: Move all remaining static files to `unused/`**

```bash
mkdir -p unused
mv static/wp-content unused/wp-content
```

This preserves the full directory tree under `unused/` so you can browse and identify
files before permanently deleting them.

- [ ] **Step 3: Build the site**

```bash
make build 2>&1 | grep -E "ERROR|WARN"
make validate
```

If htmlproofer reports broken links, restore the specific file from `unused/` into the
correct bundle:

```bash
cp unused/wp-content/uploads/YYYY/MM/missing-file.jpg \
   content/blog/affected-post/missing-file.jpg
# Then re-run make validate
```

- [ ] **Step 4: Commit**

```bash
git add -A static/ unused/
git commit -m "chore: move unused static assets to unused/ for review"
```

---

## Task 6: Verify the deployed site

- [ ] **Step 1: Push and watch CI**

```bash
git push
```

All CI steps should pass: validate → Hugo build → htmlproofer → gh-pages → vps-infra dispatch.
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

- [ ] **Step 3: Delete `unused/` when you're done reviewing**

Browse `unused/wp-content/uploads/` in your file manager or with:

```bash
ls unused/wp-content/uploads/
# 353 WP-resized copies + unreferenced originals
```

When satisfied nothing important is there:

```bash
git rm -r unused/
git commit -m "chore: delete reviewed unused assets"
```

---

## Notes

### Why 350 refs point to resized images

WordPress generates multiple sizes on upload (`-150x100`, `-300x225`, `-1024x768`, `-scaled`).
In post content, WordPress inserts the 1024-wide version for display and links to the full-size.
The migration script strips the `-NNNxNNN` suffix and resolves to the original.

### Extension normalization scope

Only `.jpeg` → `.jpg` is done (same format, different extension). Files with `.png`, `.gif`,
`.zip`, `.pdf`, `.xlsx`, `.csv` are left unchanged — converting formats is out of scope.

### Future: Hugo image processing

After this migration, images are page resources and Hugo can generate responsive sizes and
WebP automatically. To enable in `figure-gallery.html`:

```go
{{ $img := .Page.Resources.GetMatch $src }}
{{ if $img }}
  {{ $thumb := $img.Resize "560x webp" }}
  <img src="{{ $thumb.RelPermalink }}" ...>
{{ end }}
```

This eliminates the need to serve large originals (4000×3000px) to browsers and is a
natural follow-on task after the bundle migration is stable.

### Frontmatter `url:` cleanup

`content/projects.md`, `content/3d-prints.md`, and `content/contact.md` all have
`url: "/slug/"` in frontmatter. After migration to `content/slug/index.md`, Hugo derives
the URL from the directory name automatically. The `url:` override can be removed.
