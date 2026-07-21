#!/usr/bin/env python3
"""Generate 301 redirect rules from old image URLs to current Hugo image URLs.

Matches by content hash (SHA-256 of file content), then groups WP resizes
to their original via base-name matching.

Two old-URL sources are covered:
1. WordPress uploads (static/wp-content/uploads/... at WP_COMMIT)
2. Old flat 3d-prints/projects section images (content/3d-prints/*.jpg,
   content/projects/*.jpg at PRE_MIGRATION_COMMIT, before they were split into
   page bundles and renamed to match their slug)

Outputs:
  scripts/image_redirect_map.json  — human-readable mapping for review
  ~/dev/cal/vps-infra/caddy/pcbisolation-image-redirects.caddy — Caddy rules

IMPORTANT — never a dead link, but always collapse to the best current
target: once a redirect is published (deployed to production Caddy), that
old_url must always resolve to *something valid* — it is never removed or
left dangling, even if a later run's hash-matching can no longer find a
match. But the *target* should always point directly at the current final
location (single hop), not at a stale intermediate URL, per standard
redirect-chain-collapsing practice (fewer hops = less latency, no diluted
SEO value, avoids crawlers giving up after N hops). So this script treats
the currently-committed scripts/image_redirect_map.json as a floor, not a
frozen record: every old_url key that was ever published stays in the
output forever, but its target is refreshed to the newly computed match
whenever one is found. Only if a previously-published old_url can no
longer be matched at all in the current run is its last-known-good target
kept as a fallback — and that's printed as a warning for manual review,
since "stopped matching entirely" (e.g. the EXIF-stripping regression this
script once hit) is the actual danger sign, not "matches a different, still
valid, more direct URL now." Run this manually after a migration/rename to
discover/refresh redirects; it is not (and should not be) run in CI.
"""
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent.parent
CONTENT = ROOT / "content"
VPSINFRA = ROOT.parent / "vps-infra"
WP_COMMIT = "7371138~1"
# Commit immediately before the 3d-prints/projects page-bundle migration
# (parent of the migration commit) — content/3d-prints/ and content/projects/
# were still flat "mega pages" with images directly alongside index.md.
PRE_MIGRATION_COMMIT = "68c0d246b38303938a95861852f164f94cab6281"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
# Extensions scripts/strip-exif.sh strips metadata from (gif/svg are excluded
# there, per .pre-commit-config.yaml). WP-era blobs still have their original
# EXIF; current content/ images had theirs stripped in a later commit, so WP
# blobs must go through the same normalization before hash-comparing.
EXIF_STRIPPED_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".tiff", ".tif"}

_slug_cache: dict[Path, str] = {}


def sha256_of_blob(blob_sha: str, ext: str = "") -> str:
    data = subprocess.check_output(["git", "cat-file", "blob", blob_sha], cwd=ROOT)
    if ext.lower() in EXIF_STRIPPED_EXTS:
        data = strip_exif_bytes(data, ext)
    return hashlib.sha256(data).hexdigest()


def strip_exif_bytes(data: bytes, ext: str) -> bytes:
    """Run the same exiftool normalization as scripts/strip-exif.sh on in-memory bytes.

    WP-era blobs still carry their original EXIF; current content/ images had
    theirs stripped in a later commit (58a7cf3). Without this, hash-matching
    against WP blobs silently fails for almost every image.
    """
    with tempfile.NamedTemporaryFile(suffix=ext) as tmp:
        tmp.write(data)
        tmp.flush()
        subprocess.run(
            ["exiftool", "-all=", "-tagsfromfile", "@", "-orientation", "-overwrite_original", tmp.name],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return Path(tmp.name).read_bytes()


def sha256_of_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def get_wp_files() -> dict[str, str]:
    """Return {wp_path: blob_sha} for all image files at WP_COMMIT."""
    out = subprocess.check_output(
        ["git", "ls-tree", "-r", WP_COMMIT, "--", "static/wp-content/uploads/"],
        cwd=ROOT,
        text=True,
    )
    result = {}
    for line in out.splitlines():
        # format: <mode> blob <sha>\t<path>
        parts = line.split("\t", 1)
        if len(parts) != 2:
            continue
        wp_path = parts[1]
        blob_sha = parts[0].split()[2]
        ext = Path(wp_path).suffix.lower()
        if ext in IMAGE_EXTS:
            result[wp_path] = blob_sha
    return result


def get_old_section_files() -> dict[str, str]:
    """Return {old_flat_path: blob_sha} for 3d-prints/projects images at PRE_MIGRATION_COMMIT.

    Before the page-bundle migration, these images lived directly under
    content/3d-prints/ and content/projects/ (flat, one directory level).
    """
    out = subprocess.check_output(
        [
            "git", "ls-tree", "-r", PRE_MIGRATION_COMMIT,
            "--", "content/3d-prints/", "content/projects/",
        ],
        cwd=ROOT,
        text=True,
    )
    result = {}
    for line in out.splitlines():
        parts = line.split("\t", 1)
        if len(parts) != 2:
            continue
        path = parts[1]
        blob_sha = parts[0].split()[2]
        ext = Path(path).suffix.lower()
        # Only flat, top-level section images (skip anything already nested,
        # e.g. if this commit is re-run after a future migration).
        if ext in IMAGE_EXTS and len(Path(path).parts) == 3:
            result[path] = blob_sha
    return result


def is_wp_resize(filename: str) -> bool:
    """Return True if filename has a WP resize suffix (-NNNxNNN).

    Does NOT treat -scaled as a resize — those are originals.
    """
    stem = Path(filename).stem
    return bool(re.search(r"-\d+x\d+$", stem))


def get_base_stem(stem: str) -> str:
    """Strip -NNNxNNN AND -scaled suffixes from a stem."""
    # Strip resize first, then scaled
    stem = re.sub(r"-\d+x\d+$", "", stem)
    stem = re.sub(r"-scaled$", "", stem)
    return stem


def get_bundle_slug(bundle_dir: Path) -> str:
    if bundle_dir in _slug_cache:
        return _slug_cache[bundle_dir]
    index = bundle_dir / "index.md"
    slug = bundle_dir.name  # fallback to directory name
    if index.exists():
        m = re.search(r'^slug:\s+"?([^"\n]+)"?', index.read_text(), re.MULTILINE)
        if m:
            slug = m.group(1).strip()
    _slug_cache[bundle_dir] = slug
    return slug


def get_hugo_url(img: Path) -> str:
    """Return the URL at which Hugo serves this image."""
    rel_parts = img.relative_to(CONTENT).parts
    # Blog leaf bundles: content/blog/YYYY-MM-DD-slug/image.jpg
    if len(rel_parts) == 3 and rel_parts[0] == "blog":
        slug = get_bundle_slug(CONTENT / rel_parts[0] / rel_parts[1])
        return f"/{rel_parts[0]}/{slug}/{rel_parts[2]}"
    # Section images: content/3d-prints/image.jpg, content/projects/image.jpg
    return "/" + "/".join(rel_parts)


def pick_best_hugo_url(wp_path: str, candidates: list[tuple[Path, str]]) -> str:
    """Pick the best Hugo URL when multiple content files share the same hash.

    Preference:
    1. Blog bundle whose directory name starts with YYYY-MM matching the WP upload
    2. Any blog bundle over projects/3d-prints
    3. First candidate
    """
    if len(candidates) == 1:
        return candidates[0][1]
    # Extract YYYY/MM from WP upload path: static/wp-content/uploads/YYYY/MM/...
    m = re.search(r"/(\d{4})/(\d{2})/", wp_path)
    if m:
        ym = f"{m.group(1)}-{m.group(2)}"
        for path, url in candidates:
            rel = path.relative_to(CONTENT)
            if rel.parts[0] == "blog" and rel.parts[1].startswith(ym):
                return url
    # Fallback: prefer blog over other sections
    blog_candidates = [
        (p, u) for p, u in candidates if p.relative_to(CONTENT).parts[0] == "blog"
    ]
    if blog_candidates:
        return blog_candidates[0][1]
    return candidates[0][1]


def load_existing_redirects(map_path: Path) -> dict[str, str]:
    """Load the permanent baseline of already-published redirects, if any."""
    if not map_path.exists():
        return {}
    data = json.loads(map_path.read_text())
    return dict(data.get("redirects", {}))


def main() -> None:
    print("Scanning current Hugo images…")
    # Build hash → [(path, hugo_url)] map (preserve all candidates for duplicate resolution)
    hash_to_hugo: dict[str, list[tuple[Path, str]]] = {}
    for img in CONTENT.rglob("*"):
        if img.suffix.lower() in IMAGE_EXTS and img.is_file():
            h = sha256_of_file(img)
            if h not in hash_to_hugo:
                hash_to_hugo[h] = []
            hash_to_hugo[h].append((img, get_hugo_url(img)))

    print(f"  {len(hash_to_hugo)} unique current images indexed")

    print("Loading WP files from git history…")
    wp_files = get_wp_files()
    print(f"  {len(wp_files)} WP image files found")

    # Phase 1: hash-match WP originals (non-resizes) → Hugo URL
    # Also build base_to_hugo: base_stem (with no resize/scaled suffix) → hugo URL
    base_to_hugo: dict[str, str] = {}  # key: "<dir>/<base_stem><ext>" → hugo url
    matched_originals: dict[str, str] = {}   # wp_path → hugo_url
    unmatched_originals: list[str] = []

    print("Matching WP originals by hash…")
    for wp_path, blob_sha in wp_files.items():
        p = Path(wp_path)
        if is_wp_resize(p.name):
            continue
        h = sha256_of_blob(blob_sha, p.suffix)
        candidates = hash_to_hugo.get(h)
        if candidates:
            hugo_url = pick_best_hugo_url(wp_path, candidates)
            matched_originals[wp_path] = hugo_url
            # Register base key (with -scaled stripped) for resize variant lookup.
            base_stem = get_base_stem(p.stem)
            key = str(p.parent / (base_stem + p.suffix.lower()))
            base_to_hugo[key] = hugo_url
        else:
            unmatched_originals.append(wp_path)

    print(f"  Matched originals:   {len(matched_originals)}")
    print(f"  Unmatched originals: {len(unmatched_originals)}")

    # Phase 2: map WP resizes → Hugo URL.
    # Strategy A: direct hash match (handles cases where only the resize was migrated).
    # Strategy B: base-name lookup in base_to_hugo (handles resizes of matched originals).
    matched_resizes: dict[str, str] = {}
    unmatched_resizes: list[str] = []

    for wp_path, blob_sha in wp_files.items():
        p = Path(wp_path)
        if not is_wp_resize(p.name):
            continue
        # Strategy A: direct hash match
        h = sha256_of_blob(blob_sha, p.suffix)
        candidates = hash_to_hugo.get(h)
        if candidates:
            matched_resizes[wp_path] = pick_best_hugo_url(wp_path, candidates)
            continue
        # Strategy B: base-name lookup
        base_stem = get_base_stem(p.stem)
        key = str(p.parent / (base_stem + p.suffix.lower()))
        hugo_url = base_to_hugo.get(key)
        if hugo_url:
            matched_resizes[wp_path] = hugo_url
        else:
            unmatched_resizes.append(wp_path)

    print(f"  Matched resizes:     {len(matched_resizes)}")
    print(f"  Unmatched resizes:   {len(unmatched_resizes)}")

    # Build redirect map: old WP URL → Hugo URL
    redirects: dict[str, str] = {}
    for wp_path, hugo_url in {**matched_originals, **matched_resizes}.items():
        # Convert static/wp-content/uploads/... → /wp-content/uploads/...
        old_url = "/" + wp_path.removeprefix("static/")
        redirects[old_url] = hugo_url

    print(f"\nTotal WP redirect rules: {len(redirects)}")

    # Old flat 3d-prints/projects section image URLs → new nested/renamed Hugo URL
    print("\nLoading old flat 3d-prints/projects images from git history…")
    old_section_files = get_old_section_files()
    print(f"  {len(old_section_files)} old section image files found")

    matched_section: dict[str, str] = {}
    unmatched_section: list[str] = []
    for old_path, blob_sha in old_section_files.items():
        h = sha256_of_blob(blob_sha, Path(old_path).suffix)
        candidates = hash_to_hugo.get(h)
        if candidates:
            matched_section[old_path] = pick_best_hugo_url(old_path, candidates)
        else:
            unmatched_section.append(old_path)

    print(f"  Matched:   {len(matched_section)}")
    print(f"  Unmatched: {len(unmatched_section)}")

    for old_path, hugo_url in matched_section.items():
        old_url = "/" + old_path.removeprefix("content/")
        redirects[old_url] = hugo_url

    computed_total = len(redirects)
    print(f"\nTotal computed redirect rules: {computed_total}")

    # Merge against the permanent record of every old_url ever published:
    # - refresh the target for any key that matched again this run (collapses
    #   stale intermediate hops to the current final destination — that's an
    #   improvement, not a regression, since the new target is guaranteed
    #   valid: it comes straight from this run's scan of current content/).
    # - never remove a previously-published key; if it didn't match at all
    #   this run, keep its last-known-good target as a fallback and warn,
    #   since "stopped matching" is the actual danger sign to investigate.
    map_path = ROOT / "scripts" / "image_redirect_map.json"
    existing_redirects = load_existing_redirects(map_path)
    final_redirects = dict(existing_redirects)
    new_keys: list[str] = []
    updated_keys: list[tuple[str, str, str]] = []
    for old_url, new_url in redirects.items():
        if old_url not in final_redirects:
            new_keys.append(old_url)
        elif final_redirects[old_url] != new_url:
            updated_keys.append((old_url, final_redirects[old_url], new_url))
        final_redirects[old_url] = new_url

    stale_keys = sorted(set(existing_redirects) - set(redirects))

    print(f"  New redirects added:            {len(new_keys)}")
    print(f"  Targets refreshed/collapsed:    {len(updated_keys)}")
    if stale_keys:
        print(f"  WARNING: {len(stale_keys)} previously-published URL(s) did not match this run — kept last-known-good target:")
        for old_url in stale_keys:
            print(f"    {old_url} -> {final_redirects[old_url]}")

    total_redirects = len(final_redirects)
    print(f"\nTotal redirect rules: {total_redirects}")

    # Write JSON map
    map_data = {
        "summary": {
            "matched_originals": len(matched_originals),
            "unmatched_originals": unmatched_originals,
            "matched_resizes": len(matched_resizes),
            "unmatched_resizes": unmatched_resizes,
            "matched_old_section_urls": len(matched_section),
            "unmatched_old_section_urls": unmatched_section,
            "new_redirects_added": new_keys,
            "targets_refreshed": [
                {"old_url": u, "previous": p, "current": c} for u, p, c in updated_keys
            ],
            "stale_urls_kept_as_is": stale_keys,
            "total_redirects": total_redirects,
        },
        "redirects": dict(sorted(final_redirects.items())),
    }
    map_path.write_text(json.dumps(map_data, indent=2) + "\n")
    print(f"Written: {map_path}")

    # Write Caddy redirect file
    caddy_dir = VPSINFRA / "caddy"
    caddy_path = caddy_dir / "pcbisolation-image-redirects.caddy"
    lines = [
        "# Auto-generated by scripts/generate_image_redirects.py",
        "# WordPress → Hugo image 301 redirects, plus old flat 3d-prints/projects",
        "# image URLs → new page-bundle image URLs",
        "",
    ]
    for old_url, new_url in sorted(final_redirects.items()):
        lines.append(f"redir {old_url} {new_url} 301")
    caddy_path.write_text("\n".join(lines) + "\n")
    print(f"Written: {caddy_path}")


if __name__ == "__main__":
    main()
