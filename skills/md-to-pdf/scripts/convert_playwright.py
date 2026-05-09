#!/usr/bin/env python3
"""Convert Markdown to PDF — Playwright/Chromium backend (cross-platform, best quality)."""

import sys
import platform
import mdformat
import markdown
from pygments.formatters import HtmlFormatter
from playwright.sync_api import sync_playwright

# ── Platform-specific CSS fonts ──
_OS = platform.system()

if _OS == 'Darwin':
    BODY_FONT = '"Songti SC", "STSong", serif'
    HEADING_FONT = '"STHeiti", "PingFang SC", sans-serif'
    CODE_FONT = '"Menlo", monospace'
elif _OS == 'Windows':
    BODY_FONT = '"SimSun", "Microsoft YaHei", serif'
    HEADING_FONT = '"Microsoft YaHei", "SimHei", sans-serif'
    CODE_FONT = '"Cascadia Code", "Consolas", monospace'
else:  # Linux / unknown — fall back to generic CJK fonts
    BODY_FONT = '"Noto Serif CJK SC", "WenQuanYi Micro Hei", serif'
    HEADING_FONT = '"Noto Sans CJK SC", "WenQuanYi Micro Hei", sans-serif'
    CODE_FONT = '"DejaVu Sans Mono", "Noto Sans Mono CJK SC", monospace'

CSS = f"""
body {{
  font-family: {BODY_FONT}; font-size: 11pt; line-height: 1.7;
  color: #333; max-width: 750px; margin: 40px auto;
}}
h1, h2, h3 {{ font-family: {HEADING_FONT}; color: #1a1a2e; }}
h1 {{ font-size: 20pt; }}
h2 {{ font-size: 15pt; }}
h3 {{ font-size: 12pt; color: #16213e; }}
code {{ font-family: {CODE_FONT}; font-size: 9pt; background: #f5f5f5; padding: 1px 3px; }}
pre {{ padding: 10px; border-radius: 4px; overflow-x: auto; }}
pre code {{ background: none; padding: 0; font-size: 9pt; }}
table {{ border-collapse: collapse; width: 100%; }}
th {{ background: #1a1a2e; color: #fff; padding: 6px 8px; text-align: left; }}
td {{ padding: 6px 8px; border: 0.5px solid #ccc; }}
tr:nth-child(even) td {{ background: #f8f9fa; }}
blockquote {{ color: #555; border-left: 3px solid #ddd; margin-left: 0; padding-left: 16px; }}
hr {{ border: none; border-top: 1px solid #ddd; }}
ul, ol {{ padding-left: 20px; }}
li {{ margin-bottom: 2px; }}
a {{ color: #1a1a2e; }}
img {{ max-width: 100%; }}
"""

KATEX_CDN = "https://cdn.jsdelivr.net/npm/katex@0.16.11/dist"


def convert(inp, out):
    with open(inp, 'r', encoding='utf-8') as f:
        md_text = f.read()

    md_text = mdformat.text(md_text, options={"wrap": "keep"})

    # Build extensions list — mdx_math is optional (for LaTeX math)
    extensions = ['tables', 'fenced_code', 'codehilite']
    try:
        import mdx_math  # noqa: F401
        extensions.append('mdx_math')
    except ImportError:
        pass

    html_body = markdown.markdown(
        md_text,
        extensions=extensions,
        extension_configs={'codehilite': {'guess_lang': False}},
    )

    code_css = HtmlFormatter(style='monokai').get_style_defs('.codehilite')

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
        try:
            page.wait_for_function(
                "() => typeof renderMathInElement !== 'undefined'", timeout=5000)
            page.evaluate("""() => renderMathInElement(document.body, {
                delimiters: [
                    {left: "$$", right: "$$", display: true},
                    {left: "$", right: "$", display: false},
                    {left: "\\\\[", right: "\\\\]", display: true},
                    {left: "\\\\(", right: "\\\\)", display: false},
                ]
            })""")
        except Exception:
            pass
        page.pdf(path=out, format='A4',
                 margin={"top": "2cm", "right": "2cm", "bottom": "2cm", "left": "2cm"})
        browser.close()


def main():
    inp = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else inp.replace('.md', '.pdf')
    convert(inp, out)
    print(f'PDF created: {out}')


if __name__ == '__main__':
    main()
