---
name: md-to-pdf
description: Use when converting Markdown files (.md) to PDF on macOS, Windows, or Linux, especially files containing CJK (Chinese/Japanese/Korean) text. Triggers include "convert md to pdf", "markdown to pdf", "generate pdf from markdown", "export md as pdf", "md转pdf". Two cross-platform backends: Playwright/Chromium for best quality (default), reportlab for pure-Python lightweight fallback.
---

# Markdown to PDF Converter

Two cross-platform backends. Choose based on your situation:

| | Playwright (`convert_playwright.py`) | reportlab (`convert_reportlab.py`) |
|------|-----------|------------|
| Quality | Perfect — full browser rendering | Good — manual Flowable layout |
| CJK | Native — system fonts just work | Manual font registration per platform |
| Special chars | Native — box-drawing, arrows, emoji | Replaced with ASCII (see Fix 1 in script) |
| CSS theming | Full CSS | Hardcoded HexColor values |
| Images | Rendered | Placeholder text |
| Italic | Rendered | Intentionally skipped (conflicts with code tags) |
| Dependencies | ~150MB (Chromium) | ~10MB (pure Python) |
| Platforms | macOS, Windows, Linux | macOS, Windows, Linux |

## Usage

```bash
# Playwright (best quality, needs Chromium)
python scripts/convert_playwright.py input.md [output.pdf]

# reportlab (pure Python, no Chromium needed)
python scripts/convert_reportlab.py input.md [output.pdf]
```

If no output path is given, replaces `.md` with `.pdf`.

## Playwright Backend (`convert_playwright.py`)

The recommended default. Pipeline:

```
.md → mdformat → markdown → HTML + CSS → Playwright/Chromium → PDF
```

- **Auto-detects platform** — selects appropriate CJK fonts for macOS, Windows, or Linux
- **CSS theme** — edit the `CSS` variable to change colors, fonts, spacing
- **Syntax highlighting** — Monokai dark theme via Pygments `codehilite` extension
- **LaTeX math** — via `mdx_math` + KaTeX CDN (falls back to LaTeX source if offline)
- **Zero CJK issues** — Chromium's text stack handles CJK, box-drawing, emoji, and mixed-language natively

### Dependencies

```bash
pip install playwright markdown mdformat pygments python-markdown-math
playwright install chromium
```

## Lightweight Backend (`convert_reportlab.py`)

Pure Python, no browser dependency. Pipeline:

```
.md → mdformat → sanitize_unicode() → markdown → BeautifulSoup → Flowables → reportlab → PDF
```

- **Auto-detects platform** — registers correct fonts for macOS or Windows
- **Linux** prints a warning with font path hints (you'll need to adjust `_FONTS`)
- Same Three Fixes as the original macOS version (Unicode→ASCII, CJK-in-code, skip italic)

### Dependencies

```bash
pip install reportlab markdown beautifulsoup4 mdformat
```

## Platform-Specific Details

When deeper platform guidance is needed, read the relevant reference:

- **macOS**: `references/macos.md` — font paths, TTC subfont indices, Apple Silicon notes
- **Windows**: `references/windows.md` — font paths, WeasyPrint caveat, wkhtmltopdf alternative

## Linux Notes

Playwright works on Linux if Chromium dependencies are installed (`playwright install-deps chromium`). The reportlab backend uses generic CJK font names by default — you may need to edit `_FONTS` in `convert_reportlab.py` to match your distribution's font paths.

## Dependencies in Mainland China

Add Tencent Cloud mirror:

```bash
pip install <packages> --index-url https://mirrors.cloud.tencent.com/pypi/simple/
```
