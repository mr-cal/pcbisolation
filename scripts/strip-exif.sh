#!/usr/bin/env bash
# Strip EXIF metadata from images, preserving orientation so images don't appear rotated.
# Usage:
#   scripts/strip-exif.sh [file ...]   # strip specific files (used by pre-commit)
#   scripts/strip-exif.sh              # strip all images under content/ (used by make)
set -euo pipefail

if ! command -v exiftool &>/dev/null; then
    echo "Error: exiftool is required." >&2
    echo "  Install with: sudo apt install libimage-exiftool-perl" >&2
    exit 1
fi

if [[ $# -gt 0 ]]; then
    files=("$@")
else
    mapfile -d '' files < <(
        find content/ -type f \( \
            -iname "*.jpg" -o -iname "*.jpeg" -o \
            -iname "*.png" -o -iname "*.webp" -o \
            -iname "*.tiff" -o -iname "*.tif" \
        \) -print0
    )
fi

if [[ ${#files[@]} -eq 0 ]]; then
    echo "No image files found."
    exit 0
fi

echo "Stripping EXIF from ${#files[@]} file(s)..."

# -all=             remove all metadata
# -tagsfromfile @   copy tags back from the original before overwriting
# -orientation      restore only the orientation tag (prevents display rotation)
# -overwrite_original  edit in place without leaving _original backup files
exiftool -all= -tagsfromfile @ -orientation -overwrite_original "${files[@]}"
