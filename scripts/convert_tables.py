#!/usr/bin/env python3
"""Convert HTML table blocks in Markdown files to Markdown pipe tables.

Usage: python3 scripts/convert_tables.py content/blog/
"""
import re
import sys
from pathlib import Path


def html_table_to_markdown(html: str) -> str:
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.DOTALL)
    md_rows = []
    for row in rows:
        cells = re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", row, re.DOTALL)
        cells = [re.sub(r"<[^>]+>", "", c).replace("\n", " ").strip() for c in cells]
        md_rows.append("| " + " | ".join(cells) + " |")
    if not md_rows:
        return html
    ncols = md_rows[0].count("|") - 1
    separator = "|" + "|".join([" --- "] * ncols) + "|"
    return "\n".join([md_rows[0], separator] + md_rows[1:])


def convert_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text

    def replace(m: re.Match) -> str:
        return html_table_to_markdown(m.group(0))

    text = re.sub(
        r"<table[^>]*>.*?</table>", replace, text, flags=re.DOTALL | re.IGNORECASE
    )
    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("content/blog")
    changed = 0
    for f in target.glob("**/*.md"):
        if convert_file(f):
            print(f"  converted: {f.name}")
            changed += 1
    print(f"\nDone. {changed} files updated.")
