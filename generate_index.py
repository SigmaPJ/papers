#!/usr/bin/env python3
"""Scan the Papers directory and emit a static index.html for GitHub Pages.

Run from the Papers root:  python3 generate_index.py
"""
import datetime
import html
import re
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "index.html"

GH_USER = "SigmaPJ"
GH_REPO = "papers"
GH_BLOB = f"https://github.com/{GH_USER}/{GH_REPO}/blob/main"


def url(rel_path: str) -> str:
    return urllib.parse.quote(rel_path)


def parse_folder(name: str):
    parts = name.split(" - ", 3)
    if len(parts) == 4:
        return {"journal": parts[0], "year": parts[1], "author": parts[2], "title": parts[3]}
    return {"journal": "", "year": "", "author": "", "title": name}


def collect_paper(folder: Path):
    info = parse_folder(folder.name)
    info["folder"] = folder.name
    info["pdf"] = None
    info["html_files"] = []
    info["discussion_md"] = None
    info["wechat_md"] = None
    info["other_md"] = []
    info["read_date"] = None
    read_mtime = 0.0
    for f in sorted(folder.iterdir()):
        if not f.is_file():
            continue
        n = f.name
        rel = f"{folder.name}/{n}"
        if n.lower().endswith(".pdf"):
            info["pdf"] = rel
        elif n.lower().endswith(".html"):
            info["html_files"].append((n, rel))
        elif n.lower().endswith(".md"):
            if n.startswith("discussion") or "解读" in n:
                info["discussion_md"] = (n, rel)
                mt = f.stat().st_mtime
                if mt > read_mtime:
                    read_mtime = mt
            elif "公众号" in n or "微信" in n:
                info["wechat_md"] = (n, rel)
            else:
                info["other_md"].append((n, rel))
    if read_mtime:
        info["read_date"] = datetime.date.fromtimestamp(read_mtime).isoformat()
    return info


def link_btn(label: str, href: str, kind: str = "") -> str:
    cls = f' class="{kind}"' if kind else ""
    return f'<a{cls} href="{href}">{html.escape(label)}</a>'


def render_paper(p) -> str:
    parts = []
    parts.append('<div class="paper">')
    title = p["title"] or p["folder"]
    parts.append(f'<div class="title">{html.escape(title)}</div>')
    meta_bits = []
    if p["author"]:
        meta_bits.append(html.escape(p["author"]))
    if p["year"]:
        meta_bits.append(html.escape(p["year"]))
    if p["journal"]:
        meta_bits.append(f'<em>{html.escape(p["journal"])}</em>')
    if meta_bits:
        parts.append(f'<div class="meta">{" · ".join(meta_bits)}</div>')
    if p.get("read_date"):
        parts.append(f'<div class="read-date">阅读 {p["read_date"]}</div>')

    parts.append('<div class="links">')
    for name, rel in p["html_files"]:
        label = "Explainer (中文)" if "说明文档" in name else "Explainer"
        if "explainer" in name.lower() and "说明文档" not in name:
            label = "Explainer (EN)"
        parts.append(link_btn(label, url(rel), "html"))
    if p["discussion_md"]:
        name, rel = p["discussion_md"]
        parts.append(link_btn("Discussion", f"{GH_BLOB}/{url(rel)}", "md"))
    if p["wechat_md"]:
        name, rel = p["wechat_md"]
        parts.append(link_btn("WeChat draft", f"{GH_BLOB}/{url(rel)}", "md"))
    for name, rel in p["other_md"]:
        parts.append(link_btn(name[:40], f"{GH_BLOB}/{url(rel)}", "md"))
    if p["pdf"]:
        parts.append(link_btn("PDF", url(p["pdf"]), "pdf"))
    parts.append("</div>")
    parts.append("</div>")
    return "\n".join(parts)


def main():
    papers = []
    standalone_html = []
    for entry in sorted(ROOT.iterdir()):
        if entry.name.startswith(".") or entry.name.startswith("_"):
            continue
        if entry.is_symlink():
            continue
        if entry.is_dir() and not entry.name.endswith("_files"):
            # Skip empty/special dirs
            has_files = any(f.is_file() for f in entry.iterdir())
            if has_files:
                papers.append(collect_paper(entry))
        elif entry.is_file() and entry.suffix.lower() == ".html" and entry.name != "index.html":
            standalone_html.append(entry.name)

    def sort_key(p):
        return (p.get("read_date") or "0000-00-00", p["author"], p["title"])

    papers.sort(key=sort_key, reverse=True)

    html_doc = []
    html_doc.append("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Paper Reading Notes — LZW</title>
<style>
  :root { --accent: #2563eb; --green: #10b981; --gray: #6b7280; --bg: #f9fafb; }
  * { box-sizing: border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif;
         max-width: 900px; margin: 0 auto; padding: 2em 1.2em; line-height: 1.6; color: #111827; }
  h1 { font-size: 1.7em; margin: 0 0 0.2em; }
  .subtitle { color: var(--gray); margin-bottom: 2em; font-size: 0.95em; }
  h2 { font-size: 1.1em; margin-top: 2em; color: var(--gray); font-weight: 600;
       border-bottom: 1px solid #e5e7eb; padding-bottom: 0.3em; }
  .paper { padding: 0.9em 1em; margin: 0.8em 0; background: var(--bg);
           border-left: 3px solid var(--accent); border-radius: 4px; }
  .title { font-weight: 600; font-size: 1.02em; margin-bottom: 0.25em; }
  .meta { color: var(--gray); font-size: 0.88em; margin-bottom: 0.3em; }
  .read-date { color: #94a3b8; font-size: 0.78em; margin-bottom: 0.5em; font-variant-numeric: tabular-nums; }
  .links a { display: inline-block; margin: 0.15em 0.4em 0.15em 0;
             padding: 0.25em 0.7em; background: var(--accent); color: white;
             text-decoration: none; border-radius: 3px; font-size: 0.82em; font-weight: 500; }
  .links a:hover { opacity: 0.85; }
  .links a.html { background: #f59e0b; }
  .links a.md   { background: var(--green); }
  .links a.pdf  { background: var(--gray); }
  footer { margin-top: 3em; color: var(--gray); font-size: 0.85em;
           border-top: 1px solid #e5e7eb; padding-top: 1em; }
  code { background: #e5e7eb; padding: 0 0.3em; border-radius: 3px; font-size: 0.9em; }
</style>
</head>
<body>
<h1>Paper Reading Notes</h1>
<p class="subtitle">罗重威 (Luo Zhongwei) · Tsinghua University · patch-clamp electrophysiology &amp; neuromodulation</p>
""")

    if papers:
        html_doc.append("<h2>Papers</h2>")
        for p in papers:
            html_doc.append(render_paper(p))

    if standalone_html:
        html_doc.append("<h2>Standalone notes</h2>")
        for n in standalone_html:
            html_doc.append(
                '<div class="paper"><div class="title">'
                + html.escape(n)
                + '</div><div class="links">'
                + link_btn("Open", url(n), "html")
                + "</div></div>"
            )

    html_doc.append(f"""<footer>
<p>HTML files (orange) render directly on GitHub Pages.
Markdown files (green) link to the GitHub source view for nicer rendering.
PDFs (gray) are served directly.</p>
<p>Source: <a href="https://github.com/{GH_USER}/{GH_REPO}">github.com/{GH_USER}/{GH_REPO}</a> ·
Regenerate this index with <code>python3 generate_index.py</code></p>
</footer>
</body>
</html>
""")

    OUT.write_text("\n".join(html_doc), encoding="utf-8")
    print(f"Wrote {OUT} ({len(papers)} papers, {len(standalone_html)} standalone)")


if __name__ == "__main__":
    main()
