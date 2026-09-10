#!/usr/bin/env python3
"""Turn blogs.md into a mobile-friendly index.html."""

from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "blogs.md"

HEADING = re.compile(r"^##\s+(.+)$")
LINK = re.compile(
    r"^-\s+(?:(\d{4}-\d{2}-\d{2})\s+)?\[([^\]]+)\]\((https?://[^)]+)\)\s*$"
)


def parse(markdown: str) -> list[dict]:
    sections: list[dict] = []
    current: dict | None = None
    seen: set[str] = set()

    for raw in markdown.splitlines():
        line = raw.strip()
        heading = HEADING.match(line)
        if heading:
            current = {"title": heading.group(1).strip(), "items": []}
            sections.append(current)
            continue
        if current is None:
            continue
        link = LINK.match(line)
        if not link:
            continue
        date, title, url = link.group(1) or "", link.group(2).strip(), link.group(3).strip()
        if url in seen:
            continue
        seen.add(url)
        current["items"].append({"date": date, "title": title, "url": url})

    for section in sections:
        section["items"].sort(key=lambda item: (item["date"], item["title"].lower()), reverse=True)

    return [section for section in sections if section["items"]]


def render_item(item: dict) -> str:
    title = html.escape(item["title"])
    url = html.escape(item["url"], quote=True)
    date = html.escape(item["date"])
    host = html.escape(host_of(item["url"]))
    search = html.escape(f"{item['date']} {item['title']}".lower(), quote=True)
    date_html = f'<time class="item-date" datetime="{date}">{date}</time>' if item["date"] else '<span class="item-date"></span>'
    return (
        f'        <a class="item" href="{url}" data-title="{search}">'
        f"{date_html}"
        f'<span class="item-body"><span class="item-title">{title}</span>'
        f'<span class="item-host">{host}</span></span></a>'
    )


def render(sections: list[dict]) -> str:
    total = sum(len(section["items"]) for section in sections)
    chips = "\n".join(
        f'      <button type="button" class="chip" data-section="{html.escape(section["title"], quote=True)}">{html.escape(section["title"])} <span>{len(section["items"])}</span></button>'
        for section in sections
    )
    blocks = []
    for index, section in enumerate(sections):
        items = "\n".join(render_item(item) for item in section["items"])
        blocks.append(
            f'''    <section class="section" data-section="{html.escape(section["title"], quote=True)}" id="sec-{index}">
      <h2>{html.escape(section["title"])} <em>{len(section["items"])}</em></h2>
      <div class="items">
{items}
      </div>
    </section>'''
        )

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="theme-color" content="#f6f1e8">
  <title>Blog 推荐</title>
  <style>
    :root {{
      --bg: #f6f1e8;
      --ink: #1c1916;
      --muted: #6b635a;
      --card: rgba(255, 252, 247, 0.92);
      --line: rgba(28, 25, 22, 0.08);
      --accent: #b45309;
    }}
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "PingFang SC", "Noto Sans SC", sans-serif;
      background:
        radial-gradient(1200px 600px at 10% -10%, #ffe7c2 0%, transparent 50%),
        radial-gradient(900px 500px at 100% 0%, #ead7c3 0%, transparent 46%),
        var(--bg);
      color: var(--ink);
      min-height: 100vh;
    }}
    .wrap {{
      width: min(1280px, calc(100% - 24px));
      max-width: 1280px;
      margin: 0 auto;
      padding: 24px 0 64px;
    }}
    header h1 {{
      margin: 0;
      font-size: clamp(1.6rem, 2.4vw, 2.1rem);
      letter-spacing: -0.03em;
    }}
    .search {{
      position: sticky;
      top: 0;
      z-index: 2;
      margin: 18px 0 10px;
      padding: 10px 0 8px;
      background: linear-gradient(var(--bg) 70%, transparent);
    }}
    .search input {{
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 14px 16px;
      font: inherit;
      font-size: 16px;
      background: var(--card);
      box-shadow: 0 8px 24px rgba(28, 25, 22, 0.05);
    }}
    .chips {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      padding: 4px 0 10px;
    }}
    .chip, .chip-all {{
      flex: 0 0 auto;
      border: 0;
      border-radius: 999px;
      padding: 8px 12px;
      font: inherit;
      font-size: 13px;
      background: rgba(28, 25, 22, 0.06);
      color: var(--ink);
    }}
    .chip span, .count {{
      color: var(--muted);
    }}
    .chip.active, .chip-all.active {{
      background: var(--ink);
      color: #fff;
    }}
    .chip.active span {{ color: #f3d5b0; }}
    .section {{ margin-top: 28px; }}
    .section h2 {{
      margin: 0 0 10px;
      font-size: 1.05rem;
    }}
    .section h2 em {{
      font-style: normal;
      color: var(--muted);
      font-weight: 500;
    }}
    .items {{
      display: grid;
      grid-template-columns: 1fr;
      gap: 8px;
    }}
    @media (min-width: 880px) {{
      .items {{ grid-template-columns: 1fr 1fr; }}
    }}
    .item {{
      display: grid;
      grid-template-columns: 6.6rem minmax(0, 1fr);
      gap: 10px 14px;
      align-items: start;
      text-decoration: none;
      color: inherit;
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 12px 14px;
      min-height: 72px;
    }}
    .item-date {{
      font-variant-numeric: tabular-nums;
      font-size: 13px;
      color: var(--accent);
      padding-top: 2px;
    }}
    .item-title {{
      display: block;
      line-height: 1.4;
      font-weight: 600;
    }}
    .item-host {{
      display: block;
      margin-top: 6px;
      color: var(--muted);
      font-size: 12px;
      word-break: break-all;
    }}
    @media (max-width: 640px) {{
      .wrap {{ width: min(100% - 20px, 1280px); }}
      .item {{
        grid-template-columns: 1fr;
        gap: 4px;
      }}
    }}
    .empty {{
      display: none;
      margin-top: 40px;
      text-align: center;
      color: var(--muted);
    }}
    body.is-empty .empty {{ display: block; }}
    .hidden {{ display: none !important; }}
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <h1>Blog 推荐</h1>
    </header>
    <div class="search">
      <input id="q" type="search" placeholder="搜索标题、网站或日期" enterkeyhint="search" autocomplete="off">
    </div>
    <div class="chips">
      <button type="button" class="chip-all active" data-section="">全部 <span class="count">{total}</span></button>
{chips}
    </div>
    <p class="empty">没有匹配的文章</p>
{chr(10).join(blocks)}
  </div>
  <script>
    const q = document.getElementById("q");
    const buttons = [...document.querySelectorAll(".chip, .chip-all")];
    let activeSection = "";

    function filter() {{
      const query = q.value.trim().toLowerCase();
      let shown = 0;
      document.querySelectorAll(".section").forEach((section) => {{
        const name = section.dataset.section;
        const sectionMatch = !activeSection || activeSection === name;
        let sectionShown = 0;
        section.querySelectorAll(".item").forEach((item) => {{
          const hit = !query || item.dataset.title.includes(query) || item.href.toLowerCase().includes(query);
          const visible = sectionMatch && hit;
          item.classList.toggle("hidden", !visible);
          if (visible) {{
            sectionShown += 1;
            shown += 1;
          }}
        }});
        section.classList.toggle("hidden", sectionShown === 0);
      }});
      document.body.classList.toggle("is-empty", shown === 0);
    }}

    q.addEventListener("input", filter);
    buttons.forEach((button) => {{
      button.addEventListener("click", () => {{
        activeSection = button.dataset.section || "";
        buttons.forEach((b) => b.classList.toggle("active", b === button));
        filter();
      }});
    }});
  </script>
</body>
</html>
"""


def host_of(url: str) -> str:
    return re.sub(r"^https?://(www\.)?", "", url).split("/")[0]


def main() -> None:
    sections = parse(SRC.read_text(encoding="utf-8"))
    (ROOT / "index.html").write_text(render(sections), encoding="utf-8")
    print(f"Wrote index.html with {sum(len(s['items']) for s in sections)} links in {len(sections)} sections.")


if __name__ == "__main__":
    main()
