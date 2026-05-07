#!/usr/bin/env python3
"""Convert Markdown to PDF — Playwright/Chromium backend (default, best quality)."""

import sys
import mdformat
import markdown
from pygments.formatters import HtmlFormatter
from playwright.sync_api import sync_playwright

CSS = """
body {
  font-family: "Songti SC", "STSong", serif; font-size: 11pt; line-height: 1.7;
  color: #333; max-width: 700px; margin: 40px auto;
}
h1, h2, h3 { font-family: "STHeiti", "PingFang SC", sans-serif; color: #1a1a2e; }
h1 { font-size: 20pt; }
h2 { font-size: 15pt; }
h3 { font-size: 12pt; color: #16213e; }
code { font-family: "Menlo", monospace; font-size: 9pt; background: #f5f5f5; padding: 1px 3px; }
pre { padding: 10px; border-radius: 4px; overflow-x: auto; }
pre code { background: none; padding: 0; font-size: 9pt; }
table { border-collapse: collapse; width: 100%; }
th { background: #1a1a2e; color: #fff; padding: 6px 8px; text-align: left; }
td { padding: 6px 8px; border: 0.5px solid #ccc; }
tr:nth-child(even) td { background: #f8f9fa; }
blockquote { color: #555; border-left: 3px solid #ddd; margin-left: 0; padding-left: 16px; }
hr { border: none; border-top: 1px solid #ddd; }
ul, ol { padding-left: 20px; }
li { margin-bottom: 2px; }
a { color: #1a1a2e; }
img { max-width: 100%; }
"""


def convert(inp, out):
    with open(inp, 'r', encoding='utf-8') as f:
        md_text = f.read()

    md_text = mdformat.text(md_text)
    html_body = markdown.markdown(
        md_text,
        extensions=['tables', 'fenced_code', 'codehilite', 'mdx_math'],
        extension_configs={'codehilite': {'guess_lang': False}},
    )

    code_css = HtmlFormatter(style='monokai').get_style_defs('.codehilite')

    KATEX_CDN = "https://cdn.jsdelivr.net/npm/katex@0.16.11/dist"
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<link rel="stylesheet" href="{KATEX_CDN}/katex.min.css">
<style>{CSS}
{code_css}
.katex {{ font-size: 1.05em; }}
.katex-display {{ margin: 0.6em 0; }}
</style>
</head>
<body>
{html_body}
<script src="{KATEX_CDN}/katex.min.js"></script>
<script src="{KATEX_CDN}/contrib/auto-render.min.js"></script>
</body>
</html>"""

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html)
        # Render LaTeX math (if present and KaTeX CDN is reachable)
        try:
            page.wait_for_function("() => typeof renderMathInElement !== 'undefined'", timeout=5000)
            page.evaluate("""() => renderMathInElement(document.body, {
                delimiters: [
                    {left: "$$", right: "$$", display: true},
                    {left: "$", right: "$", display: false},
                    {left: "\\\\[", right: "\\\\]", display: true},
                    {left: "\\\\(", right: "\\\\)", display: false},
                ]
            })""")
        except Exception:
            pass  # KaTeX CDN unreachable — math stays as LaTeX source
        page.pdf(path=out, format='A4', margin={"top": "2cm", "right": "2cm", "bottom": "2cm", "left": "2cm"})
        browser.close()


def main():
    inp = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else inp.replace('.md', '.pdf')
    convert(inp, out)
    print(f'PDF created: {out}')


if __name__ == '__main__':
    main()
