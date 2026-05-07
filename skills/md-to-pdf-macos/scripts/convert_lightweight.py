#!/usr/bin/env python3
"""Convert Markdown to PDF with full CJK support — lightweight, pure Python, macOS."""

import re
import sys

import markdown
from bs4 import BeautifulSoup, NavigableString, Tag

import mdformat

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, ListFlowable, ListItem,
)
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily

# ── Fonts (macOS) ──
# STHeiti Medium.ttc: subfont 0 = Heiti TC (繁体), subfont 1 = Heiti SC (简体)
# Songti.ttc:          subfont 0 = Songti SC (简体), subfont 1-3 = variants
# Menlo.ttc:           subfont 0 = Menlo Regular
_FONTS = [
    ('Heiti',  '/System/Library/Fonts/STHeiti Medium.ttc',           1),  # Heiti SC
    ('Songti', '/System/Library/Fonts/Supplemental/Songti.ttc',      0),  # Songti SC
    ('Menlo',  '/System/Library/Fonts/Menlo.ttc',                    0),  # Menlo Regular
]

for name, path, idx in _FONTS:
    try:
        pdfmetrics.registerFont(TTFont(name, path, subfontIndex=idx))
    except Exception as e:
        sys.exit(f"Failed to load font {name} from {path} (subfont {idx}): {e}")
registerFontFamily('Menlo', normal='Menlo', bold='Menlo', italic='Menlo', boldItalic='Menlo')

PAGE_W, PAGE_H = A4
MARGIN = 2 * cm

# ── Colors ──
C_HEADING   = HexColor('#1a1a2e')
C_ACCENT    = HexColor('#16213e')
C_BODY      = HexColor('#333333')
C_TH_BG     = HexColor('#1a1a2e')
C_TH_FG     = HexColor('#ffffff')
C_TD_BORDER = HexColor('#cccccc')
C_TD_ALT    = HexColor('#f8f9fa')
C_CODE_BG   = HexColor('#f5f5f5')

# ── Styles ──
S = {
    'h1': ParagraphStyle('H1', fontName='Heiti', fontSize=20, leading=26,
                          textColor=C_HEADING, spaceAfter=8, spaceBefore=16),
    'h2': ParagraphStyle('H2', fontName='Heiti', fontSize=15, leading=20,
                          textColor=C_HEADING, spaceAfter=6, spaceBefore=14),
    'h3': ParagraphStyle('H3', fontName='Heiti', fontSize=12, leading=17,
                          textColor=C_ACCENT, spaceAfter=4, spaceBefore=10),
    'body': ParagraphStyle('Body', fontName='Songti', fontSize=10.5, leading=17,
                           textColor=C_BODY, spaceAfter=6, alignment=TA_JUSTIFY),
    'code_para': ParagraphStyle('CodePara', fontName='Menlo', fontSize=8.5, leading=13,
                                textColor=C_BODY, leftIndent=8, backColor=C_CODE_BG,
                                spaceAfter=0, spaceBefore=0),
    'th': ParagraphStyle('TH', fontName='Heiti', fontSize=9, leading=13,
                         textColor=C_TH_FG, alignment=TA_LEFT),
    'td': ParagraphStyle('TD', fontName='Songti', fontSize=9, leading=13,
                         textColor=C_BODY, alignment=TA_LEFT),
    'quote': ParagraphStyle('Quote', fontName='Songti', fontSize=10, leading=16,
                            textColor=HexColor('#555555'), leftIndent=16,
                            borderPadding=(0, 0, 0, 4), spaceAfter=6),
}

# ── Fix 1: Unicode box-drawing / arrow -> ASCII ──
_UNI_TO_ASCII = str.maketrans({
    # Box-drawing
    '─': '-', '━': '=', '│': '|', '┃': '||',
    '┌': '+', '┐': '+', '└': '+', '┘': '+',
    '├': '+', '┤': '+', '┬': '+', '┴': '+', '┼': '+',
    '┏': '+', '┓': '+', '┗': '+', '┛': '+',
    '┣': '+', '┫': '+', '┳': '+', '┻': '+', '╋': '+',
    # Arrows
    '→': '->', '←': '<-', '↑': '^',  '↓': 'v',
    '↔': '<->','↕': '^v',
    '↗': '/^','↘': '\\v','↙': '\\v','↖': '/^',
    # Misc
    '•': '*',  '…': '...', '·': '.',
})

def sanitize_unicode(text):
    return text.translate(_UNI_TO_ASCII)

# ── Fix 2: CJK regex ──
_CJK_RE = re.compile(r'([一-鿿㐀-䶿　-〿＀-￯⺀-⻿㇀-㇯]+)')

# ── HTML inline → reportlab XML ──

def _inline_tags(html_text):
    """Convert HTML inline markup to reportlab XML tags inside a block element."""
    text = html_text
    # Fix 3: strip italic/emphasis entirely
    text = re.sub(r'</?(em|i)>', '', text)
    # <strong> and <b> → <b>
    text = re.sub(r'</?strong>', lambda m: m.group().replace('strong', 'b'), text)
    # Inline <code> → <font> (for Latin text within paragraphs)
    text = re.sub(r'<code>(.*?)</code>',
                  r'<font face="Menlo" size="9" color="#c7254e">\1</font>', text)
    # <img> → placeholder
    text = re.sub(r'<img[^>]*alt="([^"]*)"[^>]*>', r'[Image: \1]', text)
    text = re.sub(r'<img[^>]*>', '[Image]', text)
    # <br> → <br/>
    text = re.sub(r'<br\s*/?>', '<br/>', text)
    # Anchor tags — keep as-is, reportlab supports them
    return text.strip()

def _get_text(el):
    """Get the inner HTML of an element, preserving tags, without the outer wrapper."""
    if isinstance(el, NavigableString):
        return str(el)
    return ''.join(str(c) for c in el.children)

# ── Code block handling (Fix 2) ──

def _code_flowables(code_text):
    """Convert a <pre> code block to flowables with CJK-aware font fallback."""
    flowables = [Spacer(1, 4)]
    for line in code_text.split('\n'):
        escaped = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        escaped = _CJK_RE.sub(r'<font face="Songti">\1</font>', escaped)
        flowables.append(Paragraph(escaped, S['code_para']))
    flowables.append(Spacer(1, 4))
    return flowables

# ── Table handling ──

def _table_flowables(table_el):
    """Convert a BeautifulSoup <table> to a reportlab Table flowable."""
    rows = []
    for tr in table_el.find_all('tr'):
        cells = []
        for cell in tr.find_all(['th', 'td']):
            cells.append(_inline_tags(_get_text(cell)))
        rows.append(cells)
    if not rows:
        return [Spacer(1, 0)]

    ncols = max(len(r) for r in rows)
    avail_w = PAGE_W - 2 * MARGIN
    col_w = [avail_w / ncols] * ncols

    data = []
    for ri, row in enumerate(rows):
        padded = row + [''] * (ncols - len(row))
        st = S['th'] if ri == 0 else S['td']
        data.append([Paragraph(c, st) for c in padded])

    tbl = Table(data, colWidths=col_w, repeatRows=1)
    tbl.setStyle(TableStyle([
        ('BACKGROUND',     (0, 0), (-1, 0),  C_TH_BG),
        ('TEXTCOLOR',      (0, 0), (-1, 0),  C_TH_FG),
        ('ALIGN',          (0, 0), (-1, 0),  'CENTER'),
        ('VALIGN',         (0, 0), (-1, -1), 'TOP'),
        ('GRID',           (0, 0), (-1, -1), 0.5, C_TD_BORDER),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [None, C_TD_ALT]),
        ('TOPPADDING',     (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING',  (0, 0), (-1, -1), 4),
        ('LEFTPADDING',    (0, 0), (-1, -1), 6),
        ('RIGHTPADDING',   (0, 0), (-1, -1), 6),
    ]))
    return [Spacer(1, 4), tbl, Spacer(1, 4)]

# ── HTML tree → Flowables ──

def html_to_flowables(soup):
    """Walk a BeautifulSoup HTML tree and produce reportlab Flowables."""
    flowables = []
    # Use soup.body if present, otherwise soup itself
    root = soup.body if soup.body else soup

    for child in root.children:
        if isinstance(child, NavigableString):
            text = str(child).strip()
            if text:
                flowables.append(Paragraph(text, S['body']))
            continue

        if not isinstance(child, Tag):
            continue

        tag = child.name

        if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            lvl = min(int(tag[1]), 3)
            text = _inline_tags(_get_text(child))
            if text:
                flowables.append(Paragraph(text, S[f'h{lvl}']))

        elif tag == 'p':
            text = _inline_tags(_get_text(child))
            if text:
                flowables.append(Paragraph(text, S['body']))

        elif tag == 'pre':
            code_el = child.find('code')
            code_text = code_el.get_text() if code_el else child.get_text()
            flowables.extend(_code_flowables(code_text))

        elif tag in ('ul', 'ol'):
            _walk_list(child, flowables, depth=0)

        elif tag == 'table':
            flowables.extend(_table_flowables(child))

        elif tag == 'blockquote':
            for p in child.find_all('p', recursive=False):
                text = _inline_tags(_get_text(p))
                if text:
                    flowables.append(Paragraph(text, S['quote']))
            # Also handle non-<p> text inside blockquote
            for c in child.children:
                if isinstance(c, Tag) and c.name == 'p':
                    continue
                if isinstance(c, NavigableString) and str(c).strip():
                    flowables.append(Paragraph(_inline_tags(str(c)), S['quote']))

        elif tag == 'hr':
            flowables.append(HRFlowable(
                width='100%', thickness=1, color=HexColor('#ddd'),
                spaceBefore=4, spaceAfter=4))

        elif tag == 'div':
            # Recurse into divs (used by some markdown extensions)
            flowables.extend(html_to_flowables(child))

        else:
            # Unknown block element — try to render its text as body
            text = _inline_tags(_get_text(child))
            if text:
                flowables.append(Paragraph(text, S['body']))

    return flowables


def _walk_list(list_el, flowables, depth):
    """Recursively walk <ul>/<ol> and produce bullet/numbered Paragraphs."""
    is_ordered = list_el.name == 'ol'
    item_index = 0
    for li in list_el.children:
        if isinstance(li, NavigableString):
            continue
        if not isinstance(li, Tag) or li.name != 'li':
            continue
        item_index += 1

        # Build inline text from direct text children and inline tags
        parts = []
        nested_lists = []
        for c in li.children:
            if isinstance(c, NavigableString):
                parts.append(str(c))
            elif isinstance(c, Tag) and c.name in ('ul', 'ol'):
                nested_lists.append(c)
            elif isinstance(c, Tag):
                parts.append(str(c))

        prefix = f'{item_index}.' if is_ordered else '-'
        text = _inline_tags(''.join(parts))
        indent = 18 + depth * 14
        sty = ParagraphStyle(
            f'li_d{depth}',
            fontName='Songti', fontSize=10.5, leading=17,
            textColor=C_BODY,
            leftIndent=indent, firstLineIndent=-12,
            spaceAfter=2, spaceBefore=1,
            alignment=TA_LEFT,
        )
        flowables.append(Paragraph(f'{prefix} {text}', sty))

        for nested in nested_lists:
            _walk_list(nested, flowables, depth + 1)


# ── Main ──

def convert(md_text):
    """Convert Markdown text to a list of reportlab Flowables."""
    md_text = sanitize_unicode(md_text)  # Fix 1
    md_text = mdformat.text(md_text)     # normalize formatting (blank lines, indentation, etc.)
    html = markdown.markdown(md_text, extensions=['tables', 'fenced_code'])
    soup = BeautifulSoup(html, 'html.parser')
    return html_to_flowables(soup)


def main():
    inp = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else inp.replace('.md', '.pdf')
    with open(inp, 'r', encoding='utf-8') as f:
        md = f.read()
    doc = SimpleDocTemplate(out, pagesize=A4,
                            leftMargin=MARGIN, rightMargin=MARGIN,
                            topMargin=MARGIN, bottomMargin=MARGIN)
    doc.build(convert(md))
    print(f'PDF created: {out}')


if __name__ == '__main__':
    main()
