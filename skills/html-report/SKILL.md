---
name: html-report
description: Create beautiful, self-contained single-file HTML reports, landing pages, and documents that are visual, interactive, and spatial. Use when the user wants to present information that would benefit from layout, color, diagrams, or interaction — such as project reports, product pages, architecture overviews, design documents, dashboards, slide decks, code review summaries, incident post-mortems, status reports, or any document where plain text would be too flat. Triggers include "create an HTML page", "make a report", "write a landing page", "build a dashboard", "present this information visually", or any request to communicate technical or business information in a polished, readable format.
compatibility: No dependencies required — pure HTML with inline CSS and JS
---

# HTML Fancy Report

Turn information into beautiful, self-contained single-file HTML documents. This skill captures the philosophy, design system, and practical patterns for creating reports that people actually read — not skim.

## Philosophy

### HTML is often the best medium for communication

Many documents we produce — reports, plans, overviews, summaries — are fundamentally spatial, visual, or interactive. Flattening them into linear text makes them harder to consume. A well-designed HTML page communicates structure at a glance: the reader sees hierarchy, relationships, and emphasis before reading a single word.

**When HTML beats plain text or slides:**

| Situation | Why HTML |
|-----------|----------|
| Architecture/system overviews | Boxes and arrows show structure better than paragraphs |
| Product landing pages | Visual hierarchy guides the reader through features |
| Project status reports | Small charts, colored timelines, visual priority |
| Comparison documents | Side-by-side layouts let readers compare directly |
| Code review summaries | Annotated diffs, severity tags, jump links |
| Design documents | Color swatches, type scales, component sheets |
| Incident post-mortems | Timeline visualization, log excerpts, checklist |

### The self-contained principle

Every report should be a **single `.html` file** with inline CSS and JS. No framework, no build step, no external dependencies (except images when necessary). Open it in a browser — it works. This means:

- **Zero friction** to view — no `npm install`, no build, no server
- **Permanent and portable** — the file will render the same way in 10 years
- **Easy to share** — email it, commit it, drag it into a browser
- **The medium matches the message** — the file itself embodies the philosophy

### Interaction beats description

Motion and interaction cannot be described in words — they must be felt. A small interactive element (a hover effect, a collapsible section, a tab switcher) communicates in half a second what a paragraph never could. Don't overdo it, but one well-placed interaction per page makes it feel alive.

## Design System

### Color Palettes

Don't default to generic blue. Pick colors that match the topic. One color should dominate (60-70% visual weight), with 1-2 supporting tones and one sharp accent.

| Palette | Background | Surface | Accent | Best for |
|---------|-----------|---------|--------|----------|
| **Editorial Warm** | `#FBFAF8` ivory | `#FFFFFF` white | `#C75B39` clay | Reports, docs, long-form |
| **Dark Tech** | `#0a0a0b` deep | `#111114` card | cyan/teal | Dashboards, dev tools |
| **Forest Fresh** | `#FAFBF9` | `#FFFFFF` | `#2C5F2D` | Nature, health, sustainability |
| **Midnight Navy** | `#F8F9FB` | `#FFFFFF` | `#1E2761` | Enterprise, finance, legal |
| **Warm Stone** | `#FAFAF9` stone | `#FFFFFF` | `#B85042` terracotta | Creative, design, lifestyle |
| **Charcoal Minimal** | `#FAFAFA` | `#FFFFFF` | `#36454F` | Architecture, minimal products |

**Dark backgrounds**: Use them sparingly — best for hero sections, architecture diagrams, or a "sandwich" structure (dark → light → dark).

### Typography

Use system fonts to avoid external dependencies:

```css
--serif: ui-serif, Georgia, "Times New Roman", Times, serif;
--sans:  system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
--mono:  ui-monospace, "SF Mono", Menlo, Monaco, Consolas, monospace;
```

**Pairing rule**: Serif headings + sans-serif body = editorial, trustworthy. Sans-serif headings + sans-serif body = modern, clean.

| Element | Size | Weight |
|---------|------|--------|
| Page title | `clamp(42px, 6vw, 68px)` | 500 (serif) |
| Section header | 26-30px | 500 |
| Card title | 16-20px | 500-600 |
| Body text | 14-16px | 400 |
| Captions/labels | 10-12px | 400 |

### Spacing

- 0.5" (48px) minimum edge margins
- 0.3-0.5" (12-20px) between content blocks
- Section padding: 80-120px vertical
- Leave breathing room — don't fill every pixel

### Layout Patterns

Every section should have a visual element. Text-only sections are forgettable.

1. **Hero with visual** — Title + subtitle on the left, an SVG diagram or illustration on the right (2-column grid)
2. **Card grid** — `grid-template-columns: repeat(auto-fill, minmax(300px, 1fr))` — 3-6 cards with icons
3. **Two-column install** — Side-by-side options (e.g., macOS vs Windows install)
4. **Numbered list** — For trust/safety, steps, or principles — number + heading + description
5. **Dark card in light section** — One dark-background card floating in a light section for emphasis
6. **Horizontal scroll gallery** — Screenshots or images in a horizontal strip
7. **Pill row** — Tech tags, categories, labels as rounded pills
8. **CTA box** — Centered, bordered card with a call to action and big buttons

### Avoid (Hallmarks of AI-Generated Slides/Pages)

- Centered body text — left-align paragraphs, center only short titles
- Accent lines under titles — use whitespace or background instead
- Default blue color scheme — pick colors specific to the topic
- Text-only layouts — add at least one visual element per section
- Mixing random spacing — choose consistent gaps and stick to them
- Low-contrast text — ensure readability against backgrounds

## Practical Patterns

### Base HTML Template

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Document Title</title>
<style>
  :root {
    /* Define your palette here */
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html { scroll-behavior: smooth; }
  body {
    background: var(--bg);
    color: var(--text);
    font-family: var(--sans);
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
  }
</style>
</head>
<body>
  <!-- Content -->
</body>
</html>
```

### SVG Diagrams Inline

Inline SVG is one of HTML's superpowers. Use it for architecture diagrams, flowcharts, and data visualizations. The agent can draw precise diagrams that convey structure instantly.

Key SVG patterns:
- Rounded rects (`rx="8"`) for boxes/nodes
- Dashed lines (`stroke-dasharray="5 3"`) for relationships
- Color coding — warm for primary, cool for secondary, neutral for supporting
- Small labels (font-size 9-11px) for annotations
- A caption div below the SVG for context

### Interactive Elements Worth Adding

1. **Copy buttons** on code blocks — small, satisfying, useful
2. **Smooth scroll** — `html { scroll-behavior: smooth; }` and anchor links
3. **Card hover effects** — subtle lift (`translateY(-3px)`) + shadow
4. **Collapsible sections** — `<details>/<summary>` for FAQs or deep dives
5. **Tab switchers** — for comparing options or showing multiple languages

### Responsive Design

Always include at least two breakpoints:
- Tablet (768px) — switch to single column, reduce padding
- Phone (480px) — smaller fonts, full-width cards

Test by resizing the browser. Scroll-snap can cause issues on mobile — disable it in media queries.

### Typography & Statistics

For data-heavy reports, use large stat callouts:
- Big numbers (60-72pt) with small labels below
- One key metric per "stat card"
- Visual hierarchy: number > label > context

## Workflow

### Before Writing Code

1. **Identify the audience** — developer? executive? general public?
2. **Choose a palette** — pick from the table above, adapted to the topic
3. **Sketch the sections** — what are the 4-7 sections the reader needs?
4. **Pick a visual for each section** — diagram, cards, gallery, pills, CTA

### While Writing

1. Start with the hero — title, subtitle, one visual element
2. Write one section at a time, top to bottom
3. Add interaction last — it's seasoning, not the meal
4. Keep the CSS organized with clear section comments (`/* ── Section Name ── */`)

### After Writing

1. Open in a browser and scroll through
2. Resize to mobile width and verify readability
3. Check contrast — can you read everything comfortably?
4. Remove anything that doesn't earn its place

## Questions to ask before starting

If the user's request is vague, clarify:
- What's the primary message? (one sentence)
- Who will read this? (audience)
- How many sections? (scope — aim for 4-7)
- Any existing brand colors or assets to incorporate?

## Bundled Reference: HTML Effectiveness Demos

The `references/html-effectiveness/` directory contains 20 concrete demos from [ThariqS/html-effectiveness](https://github.com/ThariqS/html-effectiveness). Each demo is a self-contained `.html` file. Each is a self-contained `.html` file — open directly in a browser.

**Read `references/html-effectiveness/index.html` first** — it's the catalog page and the single best example of the design system in practice (warm editorial palette, card grid, SVG thumbnails, responsive layout).

### When to consult specific demos

| User asks for | Look at these demos |
|---------------|---------------------|
| A product landing page or project overview | `index.html` (the catalog structure), `09-slide-deck.html` (section-based layout) |
| A comparison or code review summary | `03-code-review-pr.html`, `17-pr-writeup.html`, `01-exploration-code-approaches.html` |
| A design system or style guide | `05-design-system.html`, `06-component-variants.html` |
| A status report or incident post-mortem | `11-status-report.html` (weekly status with charts), `12-incident-report.html` (timeline + log excerpts) |
| An architecture diagram or flowchart | `04-code-understanding.html` (module map), `13-flowchart-diagram.html` (clickable flow) |
| A slide deck for presentations | `09-slide-deck.html` (arrow-key navigation) |
| An interactive tool or editor | `18-editor-triage-board.html` (drag + export), `20-editor-prompt-tuner.html` (live preview) |
| Visual design exploration | `02-exploration-visual-designs.html` (layout + palette options) |
| An explainer or tutorial | `14-research-feature-explainer.html` (collapsible sections, tabbed code), `15-research-concept-explainer.html` (interactive concept) |

**How to use these references**: Don't copy-paste. Study the design language — the spacing, the color use, the typography, how SVGs are used as thumbnails, how sections are structured. Then apply the same principles to the user's specific topic with a fresh design. The goal is to internalize the philosophy, not reproduce the examples.
