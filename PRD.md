# WAChatAnalysis — Product Requirements Document

## Overview

A Python tool that reads **any** WhatsApp chat export (`.txt`), extracts insights, and generates a styled **HTML report** with interactive Plotly charts. Works with both **1-on-1 and group chats** — participants are auto-detected, and all metrics adapt to the number of participants.

---

## Input / Output

| Item | Detail |
|------|--------|
| **Input** | Any `.txt` file exported from WhatsApp, placed in `chats/` folder. Supports any number of participants. |
| **Output** | HTML report in `output/` folder, named after the input file (e.g., `team-chat.txt` → `team-chat_report.html`) |
| **Trigger** | `python -m src.main [filename]` — if no filename given, processes all `.txt` files in `chats/` |

---

## Report Sections

### 1. Overview & Basic Stats

| # | Metric | Notes |
|---|--------|-------|
| 1.1 | Total messages | Count of all user messages (excludes system messages) |
| 1.2 | Total words | Words from message content only (excludes metadata) |
| 1.3 | Total characters | Characters from message content only |
| 1.4 | Active days | `X / Y (Z%)` — days with at least one message vs total days in range |
| 1.5 | Active weeks | `X / Y (Z%)` — weeks with at least one message vs total weeks |
| 1.6 | Participants | Auto-detected count |
| 1.7 | Summary sentence | "A & B have spoken for X% of days and Y% of weeks in the last N years" |
| 1.8 | Date range | Start → end date |
| 1.9 | First message | Sender, date, time; full text in **Appendix A** (ⓘ tooltip) |

---

### 2. Per-Person Breakdown

| # | Metric | Notes |
|---|--------|-------|
| 2.1 | Message count | Per person + percentage share |
| 2.2 | Word count | Per person + average words per message |
| 2.3 | Character count | Per person (no average) |
| 2.4 | Longest messages | **Top 3** per person; side-by-side comparison table (date, words, chars); full text in **Appendix B** (ⓘ tooltip) |

---

### 3. Temporal Analysis

| # | Metric | Notes |
|---|--------|-------|
| 3.1 | Messages per week | Interactive Plotly line chart |
| 3.2 | Messages per hour of day | Bar chart (0–23h); combined, not per-person |
| 3.3 | Messages per day of week | Bar chart (Mon–Sun); combined |
| 3.4 | Messages per month | Line chart over full date range |
| 3.5 | Top 5 most active days | Combined (date + count table) |
| 3.6 | Top 5 most active hours | Combined (date + hour + count table) |
| 3.7 | Longest streak | Days count + date range (start — end) |
| 3.8 | Longest silence | Days + hours + date range (from — to) |
| 3.9 | Response time | Comparison table per person: median, 25th percentile, 75th percentile, replies ≤ 1 min. ⓘ tooltip: "Only replies within 24 hours are counted" |

---

### 4. Emoji Analysis

| # | Metric | Notes |
|---|--------|-------|
| 4.1 | Total emojis per person | Stat cards |
| 4.2 | Top emojis | Top 5 per person; top 10 overall |

---

### 5. Sticker & Media Analysis

| # | Metric | Notes |
|---|--------|-------|
| 5.1 | Media counts | Per-person table: stickers, images, videos, audio, contacts, PDFs, other, total |
| 5.2 | Unique stickers | Count per person (stat cards) |
| 5.3 | Top 5 stickers | Per person, by sticker filename/ID |

---

### 6. Word & Language Analysis

| # | Metric | Notes |
|---|--------|-------|
| 6.1 | Top 10 words per person | Excluding stop words (configurable in `config.yaml`) |
| 6.2 | Word cloud | CSS-based word cloud per person (top 50 words) |
| 6.3 | Average words per message | Per person (stat cards, separate row) |
| 6.4 | Unique vocabulary size | Per person (stat cards, separate row); subtitle: "unique words used" |

---

### 7. Conversation Dynamics

| # | Metric | Notes |
|---|--------|-------|
| 7.1 | Total conversations | Stat card. ⓘ: based on `conversation_gap_hours` config |
| 7.2 | Conversation initiator | Per person (count + %). ⓘ: gap-based |
| 7.3 | Morning texter | Who sends the first message of the day after 5 AM. ⓘ: "First message of the day after 5 AM" |
| 7.4 | Left on read | Whose message was last before a gap. ⓘ: gap-based |
| 7.5 | Conversation length | Comparison table: p25/median/p75 for message count and duration. ⓘ: gap-based |
| 7.6 | Double/triple texting | Per person: double (2 consecutive) and triple+ (3+) counts |
| 7.7 | Question frequency | Messages containing `?` per person |
| 7.8 | Laugh analysis | Messages with `haha`, `lol`, `lmao`, `😂`, `🤣` etc. per person |

---

### 8. Miscellaneous

| # | Metric | Notes |
|---|--------|-------|
| 8.1 | Deleted messages | Per person count |

---

### Appendices

| Appendix | Content |
|----------|---------|
| **A** | First message sent by each participant (full text) |
| **B** | Top 3 longest messages per participant (full text, numbered) |

---

## Architecture

```
WAChatAnalysis/
│
├── chats/                              # Drop any WhatsApp .txt export(s) here
│   └── *.txt
│
├── src/
│   ├── __init__.py
│   ├── main.py                         # Entry point: composes object graph, runs pipeline
│   ├── pipeline.py                     # AnalysisPipeline: parse → analyze → visualize → report
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── message.py                  # Message dataclass (frozen)
│   │   └── chat.py                     # Chat dataclass
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py                 # Settings dataclass, loads config.yaml
│   │
│   ├── parser/
│   │   ├── __init__.py
│   │   ├── base.py                     # IChatParser (ABC)
│   │   └── whatsapp_parser.py          # WhatsApp .txt parser
│   │
│   ├── analyzers/
│   │   ├── __init__.py
│   │   ├── base.py                     # IAnalyzer (ABC) + AnalysisResult
│   │   ├── basic_stats.py              # Section 1
│   │   ├── per_person.py               # Section 2
│   │   ├── temporal.py                 # Section 3
│   │   ├── emoji_analyzer.py           # Section 4
│   │   ├── media.py                    # Section 5
│   │   ├── word_analysis.py            # Section 6
│   │   ├── dynamics.py                 # Section 7
│   │   └── fun_stats.py               # Section 8
│   │
│   ├── visualizers/
│   │   ├── __init__.py
│   │   ├── base.py                     # IVisualizer (ABC)
│   │   ├── plotly_visualizer.py        # Plotly interactive charts (active)
│   │   └── matplotlib_visualizer.py    # Matplotlib static charts (fallback)
│   │
│   └── report/
│       ├── __init__.py
│       ├── base.py                     # IReportGenerator (ABC)
│       ├── html_report.py             # HTML report with design system (active)
│       └── pdf_report.py              # PDF report (legacy, not actively used)
│
├── output/                             # Generated reports + chart assets
├── config.yaml                         # User-editable settings
├── requirements.txt
├── ARCHITECTURE.md                     # SOLID architecture plan
├── DESIGN.md                           # CSS design system tokens
├── NOTES.md                            # Parsing format notes
└── PRD.md                              # This file
```

---

## Data Model

### Message (frozen dataclass)

| Field | Type | Example |
|-------|------|---------|
| `datetime` | `datetime` | `2023-09-25 19:26:00` |
| `sender` | `str` | `Alice` |
| `content` | `str` | `Haan` |
| `is_system` | `bool` | `False` |
| `is_media` | `bool` | `False` |
| `media_type` | `str\|None` | `sticker`, `image`, `video`, `audio`, `contact`, `pdf`, `document`, `unknown`, `None` |
| `is_deleted` | `bool` | `False` |
| `is_call` | `bool` | `False` |
| `call_type` | `str\|None` | `voice`, `video`, `None` |

### Chat

| Field | Type |
|-------|------|
| `messages` | `list[Message]` |
| `participants` | `list[str]` |
| `source_file` | `str` |
| `date_range` | `tuple[datetime, datetime]` |

---

## Parsing Rules

1. **Message line regex**: `^(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2}[\s\u202f][APap][Mm])\s-\s`
2. **User message**: matches regex AND has `: ` after sender name
3. **System message**: matches regex but no `: ` sender pattern
4. **Multi-line message**: does NOT match regex → append to previous message
5. **Participant detection**: auto-extracted from unique sender names
6. **Media detection**:
   - `<Media omitted>` → `media_type = unknown`
   - `STK-*.webp (file attached)` → `sticker`
   - `IMG-*.jpg (file attached)` → `image`
   - `VID-* (file attached)` → `video`
   - `PTT-* / AUD-* (file attached)` → `audio`
   - `DOC-* (file attached)` → `document`
   - `*.vcf (file attached)` → `contact`
   - `*.pdf (file attached)` → `pdf`
7. **Deleted**: `This message was deleted` or `You deleted this message`
8. **Missed calls**: `Missed voice call` or `Missed video call`
9. **Encoding**: handles both regular space and `\u202F` (narrow no-break space) before AM/PM
10. **Date format**: auto-detects `M/D/YY` (US) vs `D/M/YY` (international); configurable override

---

## Configuration (`config.yaml`)

| Key | Default | Description |
|-----|---------|-------------|
| `stop_words` | English + Hinglish list | Words excluded from word frequency analysis |
| `conversation_gap_hours` | 15 | Hours of silence that define a new conversation |
| `min_caps_word_length` | 3 | Min chars for SHOUTING detection |
| `top_words_count` | 20 | (analyzer-side; HTML shows top 10 per person) |
| `top_emojis_per_person` | 5 | Top N emojis shown per person |
| `top_emojis_overall` | 10 | Top N emojis shown overall |
| `date_format` | `null` (auto) | Force `MDY` or `DMY` |
| `chart_style` | colors, fonts, sizes | Plotly chart styling |
| `output_dir` | `output` | Where reports are saved |
| `chats_dir` | `chats` | Where input files are read |
| `include_appendix` | `true` | Set to `false` to generate reports without appendices |

---

## Libraries

| Purpose | Library |
|---------|---------|
| Parsing | `re`, `datetime` |
| Data handling | `pandas` (available, not heavily used) |
| Emoji extraction | `emoji` |
| Visualization | `plotly` (active), `matplotlib` (fallback) |
| Report generation | HTML string builder (active), `fpdf2` (legacy) |
| Config | `pyyaml` |

---

## Report Layout (HTML)

1. **Cover** — title, participants, date range
2. **Section 1** — Summary sentence + stat cards + KV rows
3. **Section 2** — Per-person table + longest messages comparison table
4. **Section 3** — Stat cards (streak/silence) + tables (top days/hours) + response time table + 4 Plotly charts
5. **Section 4** — Emoji stat cards + top emoji lists
6. **Section 5** — Media table + unique sticker cards + top sticker tables
7. **Section 6** — Avg W/M cards + vocabulary cards + top-10 word tables + word clouds
8. **Section 7** — Conversations card + KV sections (initiator, morning, ghost, consec, questions, laughs) + conversation length table
9. **Section 9** — Deleted messages
10. **Appendix A** — First messages (full text)
11. **Appendix B** — Top 3 longest messages per person (full text)

All sections include ⓘ info tooltips where configurable assumptions are used.

---

## Design

Warm light theme with vermillion accent. See `DESIGN.md` for full token reference:
- Fonts: Bricolage Grotesque (display), DM Sans (body), JetBrains Mono (stats)
- Background: `#FAF7F2` warm off-white
- Accent: `#D94F30` vermillion
- Participant colors: vermillion, teal, plum, golden, forest
- Interactive Plotly charts with transparent backgrounds
