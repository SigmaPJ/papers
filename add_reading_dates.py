#!/usr/bin/env python3
"""Patch each 说明文档 - *.html with an 阅读时间 info-card.

Reads the mtime of the paper's discussion / 解读 markdown (treated as "read time"),
inserts or updates an info-card in the .info-grid. Idempotent.

Usage:  python3 add_reading_dates.py
"""
from __future__ import annotations

import datetime
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def find_md_for(folder: Path) -> Path | None:
    candidates = []
    for f in folder.iterdir():
        if not f.is_file() or not f.name.lower().endswith(".md"):
            continue
        if f.name.startswith("discussion") or "解读" in f.name:
            candidates.append(f)
    if not candidates:
        return None
    return max(candidates, key=lambda f: f.stat().st_mtime)


def find_explainer_html(folder: Path) -> Path | None:
    for f in folder.iterdir():
        if f.is_file() and f.name.startswith("说明文档") and f.name.endswith(".html"):
            return f
    return None


def find_info_grid_close(html: str) -> tuple[int, str]:
    """Return (close_index, card_class) for the closing </div> of the meta grid."""
    for open_tag, card_class in (
        ('<div class="info-grid">', "info-card"),
        ('<div class="meta-grid">', "meta"),
    ):
        open_pos = html.find(open_tag)
        if open_pos < 0:
            continue
        pos = open_pos + len(open_tag)
        break
    else:
        return -1, ""
    depth = 1
    while pos < len(html):
        nxt_open = html.find("<div", pos)
        nxt_close = html.find("</div>", pos)
        if nxt_close < 0:
            return -1, ""
        if nxt_open < 0 or nxt_close < nxt_open:
            depth -= 1
            if depth == 0:
                return nxt_close, card_class
            pos = nxt_close + len("</div>")
        else:
            depth += 1
            pos = nxt_open + len("<div")
    return -1, ""


def patch_html(html: str, date_str: str) -> tuple[str, str]:
    """Insert or update the 阅读时间 card. Returns (new_html, action)."""
    if "阅读时间" in html:
        new_html, n = re.subn(
            r"(<strong>阅读时间</strong>\s*)\n(\s*)\d{4}-\d{2}-\d{2}",
            lambda m: f"{m.group(1)}\n{m.group(2)}{date_str}",
            html,
            count=1,
        )
        if n:
            return new_html, "updated"
        return html, "noop"

    close_pos, card_class = find_info_grid_close(html)
    if close_pos < 0:
        return html, "skipped (no info/meta-grid)"

    line_start = html.rfind("\n", 0, close_pos) + 1
    indent_match = re.match(r"\s*", html[line_start:])
    grid_indent = indent_match.group(0) if indent_match else "          "
    card_indent = grid_indent + "  "

    new_card = (
        f"{card_indent}<div class=\"{card_class}\">\n"
        f"{card_indent}  <strong>阅读时间</strong>\n"
        f"{card_indent}  {date_str}\n"
        f"{card_indent}</div>\n"
        f"{grid_indent}"
    )
    return html[:line_start] + new_card + html[line_start:], "inserted"


def main():
    rows = []
    for folder in sorted(ROOT.iterdir()):
        if not folder.is_dir() or folder.is_symlink():
            continue
        if folder.name.startswith(".") or folder.name.endswith("_files"):
            continue

        md = find_md_for(folder)
        html_path = find_explainer_html(folder)
        if not md or not html_path:
            if html_path and not md:
                rows.append((folder.name, "no-md, html unchanged"))
            continue

        date_str = datetime.date.fromtimestamp(md.stat().st_mtime).isoformat()
        html = html_path.read_text(encoding="utf-8")
        new_html, action = patch_html(html, date_str)
        if new_html != html:
            html_path.write_text(new_html, encoding="utf-8")
        rows.append((html_path.name, f"{action} → {date_str}"))

    print(f"Patched {len(rows)} files:")
    for name, status in rows:
        print(f"  {status:30s}  {name}")


if __name__ == "__main__":
    main()
