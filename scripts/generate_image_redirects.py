#!/usr/bin/env python3
"""Generate 301 redirect rules from old WP image URLs to new Hugo image URLs.

Matches by content hash (SHA-256 of file content), then groups WP resizes
to their original via base-name matching.

Outputs:
  scripts/image_redirect_map.json  — human-readable mapping for review
  ~/dev/cal/vps-infra/caddy/pcbisolation-image-redirects.caddy — Caddy rules
"""
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent.parent
CONTENT = ROOT / "content"
VPSINFRA = ROOT.parent / "vps-infra"
WP_COMMIT = "7371138~1"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

_slug_cache: dict[Path, str] = {}


def sha256_of_blob(blob_sha: str) -> str:
    data = subprocess.check_output(["git", "cat-file", "blob", blob_sha], cwd=ROOT)
    return hashlib.sha256(data).hexdigest()


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
        h = sha256_of_blob(blob_sha)
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
        h = sha256_of_blob(blob_sha)
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

    total_redirects = len(redirects)
    print(f"\nTotal redirect rules: {total_redirects}")

    # Write JSON map
    map_path = ROOT / "scripts" / "image_redirect_map.json"
    map_data = {
        "summary": {
            "matched_originals": len(matched_originals),
            "unmatched_originals": unmatched_originals,
            "matched_resizes": len(matched_resizes),
            "unmatched_resizes": unmatched_resizes,
            "total_redirects": total_redirects,
        },
        "redirects": dict(sorted(redirects.items())),
    }
    map_path.write_text(json.dumps(map_data, indent=2) + "\n")
    print(f"Written: {map_path}")

    # Write Caddy redirect file
    caddy_dir = VPSINFRA / "caddy"
    caddy_path = caddy_dir / "pcbisolation-image-redirects.caddy"
    lines = [
        "# Auto-generated by scripts/generate_image_redirects.py",
        "# WordPress → Hugo image 301 redirects",
        "",
    ]
    for old_url, new_url in sorted(redirects.items()):
        lines.append(f"redir {old_url} {new_url} 301")
    caddy_path.write_text("\n".join(lines) + "\n")
    print(f"Written: {caddy_path}")


if __name__ == "__main__":
    main()
