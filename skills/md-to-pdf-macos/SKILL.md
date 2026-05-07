---
name: md-to-pdf-macos
description: Use when converting Markdown files (.md) to PDF on macOS, especially files containing CJK (Chinese/Japanese/Korean) text. Triggers include "convert md to pdf", "markdown to pdf", "generate pdf from markdown", "export md as pdf". Two backends: Playwright/Chromium for best quality (default), reportlab for pure-Python lightweight fallback.
---

# Markdown to PDF Converter (macOS)

Two backends, choose based on your needs:

| | Playwright (`convert.py`) | reportlab (`convert_lightweight.py`) |
|------|-----------|------------|
| Quality | Perfect — full browser rendering | Good — manual Flowable layout |
| CJK | Native — macOS system fonts just work | Manual font registration + CJK detection |
| Special chars | Native — box-drawing, arrows, emoji | Must be replaced with ASCII (see Fix 1) |
| CSS theming | Full CSS | Hardcoded HexColor values |
| Images | Rendered | Placeholder text |
| Italic | Rendered | Intentionally skipped (conflicts with code tags) |
| Dependencies | ~150MB (Chromium) | ~25MB (pure Python) |
| Install | `pip install playwright` + `playwright install chromium` | `pip install reportlab markdown beautifulsoup4 mdformat` |

## Usage

```bash
# Default — Playwright (best quality, needs Chromium)
python scripts/convert.py input.md [output.pdf]

# Lightweight — reportlab (pure Python, no Chromium)
python scripts/convert_lightweight.py input.md [output.pdf]
```

If no output path is given, replaces `.md` with `.pdf`.

## Playwright Backend (`convert.py`)

The recommended default. Pipeline:

```
.md → mdformat → markdown → HTML + CSS → Playwright/Chromium → PDF
```

- **50 lines of code** — no manual HTML-to-PDF conversion, no font registration, no special-char workarounds
- **CSS theme** — edit the `CSS` variable in `convert.py` to change colors, fonts, spacing
- **Syntax highlighting** — Monokai dark theme via Pygments `codehilite` extension
- **LaTeX math** — via `mdx_math` + KaTeX CDN (gracefully falls back to LaTeX source if offline)
- **Zero CJK issues** — Chromium's text stack handles CJK, box-drawing, emoji, and mixed-language content natively

### Dependencies

```bash
uv pip install playwright markdown mdformat pygments python-markdown-math
playwright install chromium
```

## Lightweight Backend (`convert_lightweight.py`)

Pure Python, no native dependencies. Pipeline:

```
.md → mdformat → sanitize_unicode() → markdown → BeautifulSoup → Flowables → reportlab → PDF
```

Uses the mature [Python-Markdown](https://python-markdown.github.io/) library (same parser as Jupyter, MkDocs, Pelican) plus reportlab + macOS system TTF fonts.

### Dependencies

```bash
uv pip install reportlab markdown beautifulsoup4 mdformat
```

### Three Fixes (reportlab-specific)

These are only needed for the reportlab backend — the Playwright backend handles all of these natively.

#### Fix 1: Replace Unicode box-drawing / arrow chars with ASCII

reportlab can't render box-drawing characters (`─│┌┐├┤→←` etc.) reliably across TTC subfonts and PDF viewers. Replace with ASCII equivalents before parsing.

#### Fix 2: CJK in code blocks must use Songti, not Menlo

Menlo has zero CJK glyphs. Detect CJK runs in code lines and wrap in `<font face="Songti">`.

#### Fix 3: Skip italic formatting

reportlab's `<i>` handling conflicts with inline `<font>` code tags. Strip `<em>` and `<i>` during HTML→XML conversion.

### Font Registration

```python
# STHeiti Medium.ttc: subfont 0 = Heiti TC (繁体), subfont 1 = Heiti SC (简体)
pdfmetrics.registerFont(TTFont('Heiti', '/System/Library/Fonts/STHeiti Medium.ttc', subfontIndex=1))
pdfmetrics.registerFont(TTFont('Songti', '/System/Library/Fonts/Supplemental/Songti.ttc', subfontIndex=0))
pdfmetrics.registerFont(TTFont('Menlo', '/System/Library/Fonts/Menlo.ttc', subfontIndex=0))
```

### Font Selection

| Role | Font | Why |
|------|------|-----|
| Headings | STHeiti SC (subfont 1) | Sans-serif CJK |
| Body | Songti SC (subfont 0) | Serif CJK |
| Code (Latin) | Menlo | Monospace |
| Code (CJK) | Songti (via `<font>` tag) | Menlo has no CJK glyphs |

## For Users in Mainland China

Add Tencent Cloud mirror:

```bash
uv pip install <packages> --index-url https://mirrors.cloud.tencent.com/pypi/simple/
```
