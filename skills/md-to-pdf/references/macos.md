# macOS: Markdown to PDF

## Platform Overview

macOS has first-class CJK font support and ships with excellent typefaces. Both backends work well.

## System Fonts

| Font File | Family Name | Role |
|-----------|-------------|------|
| `STHeiti Medium.ttc` | STHeiti SC (subfont 1) | Sans-serif CJK, for headings |
| `Supplemental/Songti.ttc` | Songti SC (subfont 0) | Serif CJK, for body text |
| `Menlo.ttc` | Menlo | Monospace, for code |

Font paths: `/System/Library/Fonts/` and `/System/Library/Fonts/Supplemental/`.

## reportlab TTC Subfont Index

- `STHeiti Medium.ttc`: subfont 0 = Heiti TC (繁體), subfont 1 = Heiti SC (简体)
- `Songti.ttc`: subfont 0 = Songti SC (简体)

Always test the subfont index — using the wrong index produces garbled glyphs or fallback squares.

## Dependencies

```bash
# Playwright (recommended)
uv pip install playwright markdown mdformat pygments python-markdown-math
playwright install chromium

# reportlab (lightweight)
uv pip install reportlab markdown beautifulsoup4 mdformat
```

### Tencent Cloud Mirror (for users in Mainland China)

```bash
uv pip install <packages> --index-url https://mirrors.cloud.tencent.com/pypi/simple/
```

## Platform-Specific Notes

- **Playwright** — Chromium on macOS supports all system fonts natively. No font registration needed.
- **reportlab** — Requires manual font registration via `TTFont`. `.ttc` files need correct `subfontIndex`.
- **Apple Silicon** — Playwright's Chromium binary supports arm64 natively.
- **CJK box-drawing chars** — Playwright renders them natively. reportlab needs the ASCII replacement table (see Fix 1 in convert_reportlab.py).
