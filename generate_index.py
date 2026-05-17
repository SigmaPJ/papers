#!/usr/bin/env python3
"""Scan the Papers directory and emit a static index.html for GitHub Pages.

Run from the Papers root:  python3 generate_index.py
"""
import datetime
import html
import subprocess
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "index.html"

GH_USER = "SigmaPJ"
GH_REPO = "papers"
GH_BLOB = f"https://github.com/{GH_USER}/{GH_REPO}/blob/main"


def url(rel_path: str) -> str:
    return urllib.parse.quote(rel_path)


def is_git_ignored(path: Path) -> bool:
    """Return True if path is matched by .gitignore. False if not a git repo."""
    try:
        result = subprocess.run(
            ["git", "check-ignore", "-q", str(path)],
            cwd=str(ROOT),
            stderr=subprocess.DEVNULL,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


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


def link_btn(label: str, href: str, kind: str) -> str:
    return f'<a class="{kind}" href="{href}">{html.escape(label)}</a>'


def attr(val: str) -> str:
    return html.escape(val, quote=True)


def render_paper(p) -> str:
    title = p["title"] or p["folder"]
    data_attrs = (
        f'data-read="{attr(p.get("read_date") or "0000-00-00")}" '
        f'data-year="{attr(p.get("year") or "0000")}" '
        f'data-title="{attr(title.lower())}" '
        f'data-author="{attr((p.get("author") or "").lower())}"'
    )
    parts = [f'<article class="paper" {data_attrs}>']
    parts.append(f'<h3 class="paper-title">{html.escape(title)}</h3>')

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
    explainer = None
    extras = []
    for name, rel in p["html_files"]:
        if "说明文档" in name:
            explainer = (name, rel, "Explainer")
        elif "explainer" in name.lower():
            extras.append((name, rel, "Explainer (EN)"))
        else:
            extras.append((name, rel, name[:30]))
    if explainer:
        parts.append(link_btn(explainer[2], url(explainer[1]), "primary"))
    for name, rel, label in extras:
        parts.append(link_btn(label, url(rel), "primary"))
    if p["discussion_md"]:
        _, rel = p["discussion_md"]
        parts.append(link_btn("Discussion", f"{GH_BLOB}/{url(rel)}", "secondary"))
    if p["wechat_md"]:
        _, rel = p["wechat_md"]
        parts.append(link_btn("WeChat draft", f"{GH_BLOB}/{url(rel)}", "tertiary"))
    for name, rel in p["other_md"]:
        parts.append(link_btn(name[:30], f"{GH_BLOB}/{url(rel)}", "tertiary"))
    if p["pdf"]:
        parts.append(link_btn("PDF", url(p["pdf"]), "tertiary"))
    parts.append("</div>")
    parts.append("</article>")
    return "\n".join(parts)


CSS = """
:root {
  --bg: #f6f7fc;
  --paper: #ffffff;
  --ink: #1e1b3a;
  --muted: #6b6f8f;
  --muted-2: #9da1bf;
  --line: #e4e6f3;
  --line-hover: #c9cce6;
  --accent: #7c7fe8;
  --accent-soft: #ebecf9;
  --accent-hover: #6366d4;
  --accent-tint: #d8daf3;
  --shadow: 0 1px 2px rgba(70, 70, 130, 0.04), 0 1px 8px rgba(70, 70, 130, 0.03);
  --shadow-hover: 0 2px 4px rgba(70, 70, 130, 0.06), 0 4px 16px rgba(70, 70, 130, 0.06);
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
               "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  line-height: 1.65;
  -webkit-font-smoothing: antialiased;
  font-feature-settings: "kern", "liga";
}
.container { max-width: 880px; margin: 0 auto; padding: 64px 28px 96px; }

header.site-header { margin-bottom: 28px; }
h1 {
  font-size: 2em;
  margin: 0 0 8px;
  letter-spacing: -0.012em;
  font-weight: 700;
}
.subtitle { color: var(--muted); margin: 0; font-size: 0.97em; }

.toolbar {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 32px 0 28px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--line);
  flex-wrap: wrap;
}
.toolbar-label {
  color: var(--muted);
  font-size: 0.82em;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  margin-right: 8px;
}
.sort-btn {
  background: transparent;
  border: 1px solid transparent;
  color: var(--muted);
  font: inherit;
  font-size: 0.9em;
  padding: 5px 12px;
  border-radius: 999px;
  cursor: pointer;
  transition: background 0.15s ease, color 0.15s ease;
}
.sort-btn:hover { color: var(--ink); background: rgba(124,127,232,0.06); }
.sort-btn.active {
  background: var(--accent-soft);
  color: var(--accent);
}
.sort-btn .arrow {
  font-size: 0.85em;
  margin-left: 1px;
  opacity: 0.75;
  font-variant-numeric: tabular-nums;
}

.section-heading {
  font-size: 0.78em;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--muted);
  margin: 36px 0 14px;
}

.papers-list { display: flex; flex-direction: column; gap: 12px; }

.paper {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 18px 22px;
  box-shadow: var(--shadow);
  transition: border-color 0.18s ease, box-shadow 0.18s ease, transform 0.18s ease;
}
.paper:hover {
  border-color: var(--line-hover);
  box-shadow: var(--shadow-hover);
}

.paper-title {
  font-weight: 600;
  font-size: 1.02em;
  margin: 0 0 5px;
  color: var(--ink);
  letter-spacing: -0.003em;
  line-height: 1.45;
}
.meta { color: var(--muted); font-size: 0.85em; margin-bottom: 2px; }
.meta em { font-style: italic; }
.read-date {
  color: var(--muted-2);
  font-size: 0.78em;
  margin-bottom: 12px;
  font-variant-numeric: tabular-nums;
}

.links { display: flex; flex-wrap: wrap; gap: 6px; }
.links a {
  display: inline-flex;
  align-items: center;
  padding: 3px 11px;
  border-radius: 999px;
  font-size: 0.82em;
  font-weight: 500;
  text-decoration: none;
  transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease;
}
.links a.primary {
  background: var(--accent);
  color: #ffffff;
}
.links a.primary:hover { background: var(--accent-hover); }
.links a.secondary {
  background: var(--accent-soft);
  color: var(--accent);
}
.links a.secondary:hover { background: var(--accent-tint); }
.links a.tertiary {
  color: var(--muted);
  border: 1px solid var(--line);
  background: transparent;
}
.links a.tertiary:hover { color: var(--ink); border-color: var(--line-hover); }

footer {
  margin-top: 56px;
  padding-top: 22px;
  border-top: 1px solid var(--line);
  color: var(--muted);
  font-size: 0.82em;
}
footer a { color: var(--accent); text-decoration: none; }
footer a:hover { text-decoration: underline; }
footer code {
  background: var(--accent-soft);
  color: var(--accent-hover);
  padding: 1px 6px;
  border-radius: 4px;
  font-size: 0.92em;
}

@media (max-width: 600px) {
  .container { padding: 40px 18px 60px; }
  h1 { font-size: 1.55em; }
}
"""


SORT_JS = """
(function () {
  const list = document.getElementById('papers-list');
  if (!list) return;
  const buttons = Array.from(document.querySelectorAll('.sort-btn'));
  let activeSort = 'read';
  let activeDir = 'desc';

  function applySort() {
    const papers = Array.from(list.children);
    papers.sort((a, b) => {
      const av = (a.dataset[activeSort] || '');
      const bv = (b.dataset[activeSort] || '');
      const cmp = av < bv ? -1 : av > bv ? 1 : 0;
      return activeDir === 'asc' ? cmp : -cmp;
    });
    papers.forEach((p) => list.appendChild(p));
  }

  function updateButtons() {
    buttons.forEach((b) => {
      const active = b.dataset.sort === activeSort;
      b.classList.toggle('active', active);
      const arrow = b.querySelector('.arrow');
      if (arrow) arrow.textContent = active ? (activeDir === 'asc' ? ' ↑' : ' ↓') : '';
    });
  }

  buttons.forEach((b) => {
    b.addEventListener('click', () => {
      const sort = b.dataset.sort;
      const defaultDir = b.dataset.defaultDir || 'asc';
      if (activeSort === sort) {
        activeDir = activeDir === 'asc' ? 'desc' : 'asc';
      } else {
        activeSort = sort;
        activeDir = defaultDir;
      }
      updateButtons();
      applySort();
    });
  });

  updateButtons();
})();
"""


def main():
    papers = []
    standalone_html = []
    for entry in sorted(ROOT.iterdir()):
        if entry.name.startswith(".") or entry.name.startswith("_"):
            continue
        if entry.is_symlink():
            continue
        if entry.is_dir() and not entry.name.endswith("_files"):
            if is_git_ignored(entry):
                continue
            has_notes = any(
                f.is_file()
                and (f.name.lower().endswith(".md") or f.name.lower().endswith(".html"))
                for f in entry.iterdir()
            )
            if has_notes:
                papers.append(collect_paper(entry))
        elif entry.is_file() and entry.suffix.lower() == ".html" and entry.name != "index.html":
            standalone_html.append(entry.name)

    def sort_key(p):
        return (p.get("read_date") or "0000-00-00", p["author"], p["title"])

    papers.sort(key=sort_key, reverse=True)

    doc = [f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Paper Reading Notes — 罗重威</title>
<style>{CSS}</style>
</head>
<body>
<div class="container">
<header class="site-header">
  <h1>Paper Reading Notes</h1>
  <p class="subtitle">罗重威 · Tsinghua University · patch-clamp electrophysiology &amp; neuromodulation</p>
</header>

<div class="toolbar" role="toolbar" aria-label="Sort papers">
  <span class="toolbar-label">排序</span>
  <button class="sort-btn active" data-sort="read" data-default-dir="desc">阅读时间<span class="arrow"></span></button>
  <button class="sort-btn" data-sort="year" data-default-dir="desc">发表年份<span class="arrow"></span></button>
  <button class="sort-btn" data-sort="title" data-default-dir="asc">标题<span class="arrow"></span></button>
  <button class="sort-btn" data-sort="author" data-default-dir="asc">第一作者<span class="arrow"></span></button>
</div>

<div class="papers-list" id="papers-list">"""]

    for p in papers:
        doc.append(render_paper(p))

    doc.append("</div>")

    if standalone_html:
        doc.append('<h2 class="section-heading">Standalone notes</h2>')
        doc.append('<div class="papers-list">')
        for n in standalone_html:
            doc.append(
                '<article class="paper">'
                f'<h3 class="paper-title">{html.escape(n)}</h3>'
                '<div class="links">'
                + link_btn("Open", url(n), "primary")
                + "</div></article>"
            )
        doc.append("</div>")

    doc.append(f"""<footer>
<p>HTML 说明文档（深色按钮）由 Pages 直接渲染；Discussion 链接到 GitHub 上的 Markdown 视图；PDF 在浏览器内置打开。</p>
<p>Source: <a href="https://github.com/{GH_USER}/{GH_REPO}">github.com/{GH_USER}/{GH_REPO}</a> ·
重新生成索引：<code>python3 generate_index.py</code></p>
</footer>
</div>
<script>{SORT_JS}</script>
</body>
</html>
""")

    OUT.write_text("\n".join(doc), encoding="utf-8")
    print(f"Wrote {OUT} ({len(papers)} papers, {len(standalone_html)} standalone)")


if __name__ == "__main__":
    main()
