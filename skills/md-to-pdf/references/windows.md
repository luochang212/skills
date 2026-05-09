# Windows: Markdown to PDF

## Platform Overview

Windows has excellent CJK font support out of the box. The main considerations:

| Approach | Works? | Notes |
|----------|--------|-------|
| Playwright + Chromium | Excellent | Same as macOS, just different CSS fonts |
| reportlab | Good | Different font paths, otherwise identical |
| WeasyPrint | Difficult | Requires GTK runtime (libgobject, Pango) — not recommended |
| wkhtmltopdf | OK | Requires separate installer, dated but functional |
| Word COM (win32com) | OK | Windows-only, requires MS Word installed |

## System Fonts

Windows ships with these CJK-capable fonts:

| Font File | Family Name | Role |
|-----------|-------------|------|
| `msyh.ttc` | Microsoft YaHei (微软雅黑) | Sans-serif CJK, good for headings |
| `simsun.ttc` | SimSun (宋体) | Serif CJK, good for body text |
| `simhei.ttf` | SimHei (黑体) | Bold CJK sans-serif |
| `consola.ttf` | Consolas | Monospace, good for code |
| `cascadiacode.ttf` | Cascadia Code | Modern monospace with ligatures |

Font paths use Windows convention: `C:/Windows/Fonts/` (forward slashes work in Python).

## reportlab TTC Subfont Index

`.ttc` (TrueType Collection) files contain multiple fonts. The index matters:

- `msyh.ttc` subfont 0 = Microsoft YaHei (Regular)
- `msyh.ttc` subfont 1 = Microsoft YaHei Bold (or use `msyhbd.ttc` subfont 0)
- `simsun.ttc` subfont 0 = SimSun (Regular)

Always test subfont 0 first. If the output looks wrong (garbled glyphs, wrong weight), try subfont 1.

## Dependencies

```bash
# Playwright (recommended)
pip install playwright markdown mdformat pygments python-markdown-math
playwright install chromium

# reportlab (lightweight)
pip install reportlab markdown beautifulsoup4 mdformat
```

### Tencent Cloud Mirror (for users in Mainland China)

```bash
pip install <packages> --index-url https://mirrors.cloud.tencent.com/pypi/simple/
```

## WeasyPrint (not recommended on Windows)

WeasyPrint depends on GTK/Pango native libraries. On Windows this means installing the GTK3 runtime via MSYS2 or gvsbuild, which is fragile and adds ~200MB. Playwright achieves the same result (HTML+CSS→PDF via browser engine) with simpler setup. Skip WeasyPrint on Windows unless you already have GTK installed for other reasons.

## wkhtmltopdf Alternative

If you can't use Playwright (no Chromium install permissions), wkhtmltopdf is a fallback:

1. Download from https://wkhtmltopdf.org/downloads.html
2. Install and ensure `wkhtmltopdf.exe` is in PATH
3. Use `pdfkit` Python wrapper: `pip install pdfkit`

```python
import pdfkit
pdfkit.from_file('input.html', 'output.pdf')
```

CJK support requires `--encoding UTF-8` flag. Quality is lower than Playwright (older WebKit).
