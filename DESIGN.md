# Design System — WAChatAnalysis Report

CSS design tokens for the HTML report. All report styling should derive from these tokens.

## Table of Contents
1. [Color Palette](#color-palette)
2. [Typography](#typography)
3. [Spacing & Layout](#spacing--layout)
4. [Shadows & Depth](#shadows--depth)
5. [Component Patterns](#component-patterns)
6. [Scrollbar & Background](#scrollbar--background)

---

## Color Palette

```css
:root {
  /* --- BACKGROUNDS --- */
  --color-bg:             #FAF7F2;       /* warm off-white, like aged paper */
  --color-bg-warm:        #F5F0E8;       /* slightly warmer for alternating sections */
  --color-bg-code:        #1E1E2E;       /* deep indigo-charcoal (kept for future) */
  --color-text:           #2C2A28;       /* dark charcoal, easy on eyes */
  --color-text-secondary: #6B6560;       /* warm gray for secondary text */
  --color-text-muted:     #9E9790;       /* muted for labels, counts, metadata */
  --color-border:         #E5DFD6;       /* subtle warm border */
  --color-border-light:   #EEEBE5;       /* even lighter border */
  --color-surface:        #FFFFFF;       /* card surfaces */
  --color-surface-warm:   #FDF9F3;       /* warm card surface variant */

  /* --- ACCENT (vermillion) --- */
  --color-accent:         #D94F30;
  --color-accent-hover:   #C4432A;
  --color-accent-light:   #FDEEE9;       /* accent tint for backgrounds */
  --color-accent-muted:   #E8836C;

  /* --- SEMANTIC --- */
  --color-success:        #2D8B55;
  --color-success-light:  #E8F5EE;
  --color-error:          #C93B3B;
  --color-error-light:    #FDE8E8;
  --color-info:           #2A7B9B;
  --color-info-light:     #E4F2F7;

  /* --- PARTICIPANT COLORS ---
     Each chat participant gets a distinct color.
     Used for stat cards, chart series, and comparison highlights.
     Extend this list for group chats with more people. */
  --color-person-1:       #D94F30;       /* vermillion */
  --color-person-2:       #2A7B9B;       /* teal */
  --color-person-3:       #7B6DAA;       /* muted plum */
  --color-person-4:       #D4A843;       /* golden */
  --color-person-5:       #2D8B55;       /* forest */
}
```

**Rules:**
- Even-numbered sections use `--color-bg`, odd-numbered use `--color-bg-warm` (alternating backgrounds create visual rhythm)
- Participant colors must be visually distinct from each other and from the accent
- Chart colors use the participant color list for per-person series. Combined/overall charts use `--color-accent`
- The accent (vermillion) drives section heading underlines, stat card highlights, and interactive elements

---

## Typography

```css
:root {
  /* --- FONTS ---
     Display: bold, geometric, personality-driven (section titles, cover)
     Body: readable with character (stats, tables, descriptions)
     Mono: developer-friendly, clear character distinction (counts, metadata) */
  --font-display:  'Bricolage Grotesque', Georgia, serif;
  --font-body:     'DM Sans', -apple-system, sans-serif;
  --font-mono:     'JetBrains Mono', 'Fira Code', 'Consolas', monospace;

  /* --- TYPE SCALE (1.25 ratio) --- */
  --text-xs:   0.75rem;    /* 12px — labels, badges, metadata */
  --text-sm:   0.875rem;   /* 14px — secondary text, table data */
  --text-base: 1rem;       /* 16px — body text */
  --text-lg:   1.125rem;   /* 18px — lead paragraphs, key stats */
  --text-xl:   1.25rem;    /* 20px — subsection headings */
  --text-2xl:  1.5rem;     /* 24px — section subtitles, stat values */
  --text-3xl:  1.875rem;   /* 30px — section titles */
  --text-4xl:  2.25rem;    /* 36px — cover subtitle */
  --text-5xl:  3rem;       /* 48px — cover title */

  /* --- LINE HEIGHTS --- */
  --leading-tight:  1.15;  /* headings */
  --leading-snug:   1.3;   /* subheadings */
  --leading-normal: 1.6;   /* body text */
  --leading-loose:  1.8;   /* relaxed reading (appendices) */
}
```

**Google Fonts (put in `<head>`):**
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,600;12..96,700;12..96,800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400;1,9..40,500&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
```

**Usage rules:**
- Cover title: `--text-5xl`, font-display, weight 800
- Cover subtitle (participants): `--text-4xl`, font-display, weight 600, `--color-accent`
- Section titles (h2): `--text-3xl`, font-display, weight 700, `--color-accent` bottom border (2px)
- Subsection headings (h3): `--text-xl`, font-display, weight 600, `--color-accent-muted`
- Body text: `--text-base`, font-body, `--leading-normal`
- Stat card values: `--text-2xl`, font-mono, weight 700, `--color-text`
- Stat card labels: `--text-xs`, font-body, uppercase, letter-spacing 0.05em, `--color-text-muted`
- Table data: `--text-sm`, font-body
- Metadata/counts: `--text-xs`, font-mono, `--color-text-muted`

---

## Spacing & Layout

```css
:root {
  --space-1:  0.25rem;   /* 4px */
  --space-2:  0.5rem;    /* 8px */
  --space-3:  0.75rem;   /* 12px */
  --space-4:  1rem;      /* 16px */
  --space-5:  1.25rem;   /* 20px */
  --space-6:  1.5rem;    /* 24px */
  --space-8:  2rem;      /* 32px */
  --space-10: 2.5rem;    /* 40px */
  --space-12: 3rem;      /* 48px */
  --space-16: 4rem;      /* 64px */
  --space-20: 5rem;      /* 80px */

  --content-width: 900px;     /* main report column */
  --radius-sm:     8px;
  --radius-md:     12px;
  --radius-lg:     16px;
  --radius-full:   9999px;
}
```

---

## Shadows & Depth

```css
:root {
  --shadow-sm:  0 1px 2px rgba(44, 42, 40, 0.05);
  --shadow-md:  0 4px 12px rgba(44, 42, 40, 0.08);
  --shadow-lg:  0 8px 24px rgba(44, 42, 40, 0.1);
  --shadow-xl:  0 16px 48px rgba(44, 42, 40, 0.12);
}
```

Use warm-tinted RGBA `(44, 42, 40)` — never pure black shadows.

---

## Component Patterns

### Cover Section
- Full-width, generous vertical padding (`--space-20` top, `--space-16` bottom)
- Background: subtle gradient using `--color-bg-warm`
- Title: font-display, weight 800, `--color-text`
- Participants: `--color-accent`, font-display, weight 600
- Date range: `--color-text-muted`, font-body

### Stat Cards
- Background: `--color-surface`, border: `1px solid var(--color-border-light)`
- Border-radius: `--radius-md`
- Shadow: `--shadow-sm`, on hover: `--shadow-md` with slight lift
- Label: uppercase, `--text-xs`, `--color-text-muted`
- Value: `--text-2xl`, font-mono, weight 700, `--color-text`
- Grid: `repeat(auto-fit, minmax(200px, 1fr))`, gap `--space-4`

### Section Cards
- Background: `--color-surface` or `--color-surface-warm` (alternate by section index)
- Border-radius: `--radius-lg`
- Padding: `--space-8` all sides
- Shadow: `--shadow-sm`
- Section title (h2): with `--color-accent` bottom border (2px solid)

### Tables
- Header: `--color-bg-warm` background, `--color-accent` text, font-body weight 600, uppercase `--text-xs`
- Rows: `--color-surface` background, `--text-sm` font-body
- Row hover: background shifts to `--color-accent-light`
- Borders: bottom only, `--color-border-light`

### KV Rows (key-value pairs)
- Key: `--color-text-muted`, font-body weight 600, fixed width ~220px
- Value: `--color-text`, font-body
- Bottom border: `--color-border-light`
- Last child: no bottom border

### Charts (Plotly)
- Multi-person series: use `--color-person-1..5` in order
- Single-series / combined charts: use `--color-accent`
- Chart background: transparent (inherits section background)
- Grid lines: `--color-border-light`
- Plotly template: use `plotly_white`, override paper/plot bg to transparent

### Emoji Display
- Emoji size: ~1.3em
- Count label: `--text-xs`, `--color-text-muted`, font-mono
- Display: inline-block with `--space-2` padding

### Word Cloud
- CSS-based (not image) — sized by frequency, colored with participant colors
- Container: centered text, `line-height: 2.2`

### Appendix Content Blocks
- Background: `--color-bg-warm`
- Border: `1px solid var(--color-border)`
- Border-radius: `--radius-sm`
- Font: `--text-sm`, `--leading-loose`, `--color-text-secondary`
- Max-height: 400px with `overflow-y: auto`
- White-space: `pre-wrap`

### Info Tooltips (ⓘ buttons)
- Inline circle: 16×16px, `--color-border-light` background, `--color-text-muted` text
- Font: `--font-mono`, 11px, weight 700
- `cursor: help`, `border-radius: var(--radius-full)`
- Hover shows `::after` pseudo-element with `data-tip` attribute
- Tooltip: `--color-text` background, `--color-surface` text, `--text-xs`, `--radius-sm`
- Positioned above the icon, centered
- `white-space: normal`, `max-width: 300px`, `width: max-content` — long tooltips wrap instead of overflowing
- Used on: Appendix references, config-dependent metrics (gap hours, response time threshold), formula explanations

### Comparison Tables
- Used for: longest messages (Section 2), response time (Section 3), conversation length (Section 7)
- Per-person column groups separated by `2px solid var(--color-border)` vertical border
- Metric labels in first column: `font-weight: 600`, `--color-text-muted`
- Data cells: `text-align: center`

### Summary Text
- Used in Section 1 below the heading
- Font: `--text-lg`, `--font-body`, `--color-text-secondary`
- Margin-bottom: `--space-6`

### Long Words
- `.word-wrap` class: `word-break: break-all; overflow-wrap: break-word`
- Used for longest word display in Miscellaneous section

### Appendix Caution Banner
- Amber/yellow warning banner at the top of appendices
- Flexbox layout: icon (1.4rem) + text
- Background: `#fef3c7`, border: `1px solid #f59e0b`, left border: `4px solid #f59e0b`
- Text color: `#92400e`, font-weight 600 for "Caution:" label
- Appears only when at least one appendix section exists

### Chat Bubbles (Rant/Happiness Appendix)
- Used in Appendix C (rants) and D (happiest days) to show first 2 messages
- Container: `.rant-chat` — flexbox column, `gap: var(--space-2)`, max-height 400px with scroll
- Bubble: `.rant-bubble` — `--color-bg-warm` background, border, left-aligned with rounded corners (flat bottom-left)
- Timestamp: `.rant-time` — 0.7rem, `--color-text-muted`, block display above content
- Max-width: 85%, pre-wrap, word-break

---

## Scrollbar & Background

```css
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: var(--radius-full);
}

body {
  background: var(--color-bg);
  background-image: radial-gradient(
    ellipse at 20% 50%,
    rgba(217, 79, 48, 0.03) 0%,
    transparent 50%
  );
}
```
