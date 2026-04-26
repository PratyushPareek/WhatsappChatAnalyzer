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
| 3.9 | Response time | Comparison table per person: median, 25th percentile, 75th percentile, replies ≤ 1 min. ⓘ tooltip: "Only replies within {conversation_gap_hours}h are counted" |
| 3.10 | Daily message count distribution | Histogram (50 bins) + KDE curve. Shows how many days had N messages (excludes zero-message days). ⓘ tooltip explains distribution |

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

### 8. Happiness Analysis

| # | Metric | Notes |
|---|--------|-------|
| 8.1 | Happy message count | Per person (count + %). Uses keyword + emoji matching. ⓘ tooltip: "Only days in the 25th–75th percentile of daily message volume are included" |
| 8.2 | Happiest month | Month with highest happy-message density (happy/total) |
| 8.3 | Happiest days | Top 5 days ranked by `happy_count / total^0.1` (10th root penalty). Only days above the 75th percentile in message count are included. First 2 messages of each in **Appendix D**. ⓘ tooltip explains formula |

---

### 9. Miscellaneous

| # | Metric | Notes |
|---|--------|-------|
| 9.1 | Deleted messages | Per person count |
| 9.2 | Longest word | Per person — word-wrap enabled for display |
| 9.3 | Manners | Messages containing polite words (thank you, sorry, please, etc.) per person — count + percentage. Keywords configurable via `manners_words` in `config.yaml` (regex fragments, e.g. `th(?:a|e)nk\s?(?:you|u|ss*)`) |
| 9.4 | Rants | Streaks of 4+ consecutive messages (each with ≥ 2 words, within 2 min of each other) by one person — count + longest streak per person + date reference. Short fillers (≤3 chars) are ignored without breaking streaks. ⓘ tooltip explains criteria |

---

### Appendices

| Appendix | Content |
|----------|---------|
| **Caution banner** | Shown at the top of appendices: "Actual messages from your chat appear below" (amber caution UI) |
| **A** | First message sent by each participant (full text) |
| **B** | Top 3 longest messages per participant (full text, numbered) |
| **C** | Longest rant per person — first 2 messages shown as chat bubbles |
| **D** | Happiest days — first 2 messages of each top-5 day shown as chat bubbles |

---

## Architecture

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for the full SOLID architecture, directory structure, interfaces, data model, pipeline, and class definitions.

---

## Data Model

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for the full `Message` and `Chat` dataclass definitions.

---

## Parsing Rules

See [`NOTES.md`](NOTES.md) for the full WhatsApp format specification, regex patterns, encoding quirks, media detection, and date format detection.

---

## Configuration (`config.yaml`)

| Key | Default | Description |
|-----|---------|-------------|
| `stop_words` | English + Hinglish list | Words excluded from word frequency analysis |
| `manners_words` | Polite phrases list | Words/phrases counted as manners (regex fragments, e.g. `thank\s?you`) |
| `conversation_gap_hours` | 15 | Hours of silence that define a new conversation |
| `min_caps_word_length` | 3 | Min chars for SHOUTING detection |

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
4. **Section 3** — Stat cards (streak/silence) + tables (top days/hours) + response time table + 5 Plotly charts (incl. daily distribution histogram + KDE)
5. **Section 4** — Emoji stat cards + top emoji lists
6. **Section 5** — Media table + unique sticker cards + top sticker tables
7. **Section 6** — Avg W/M cards + vocabulary cards + top-10 word tables + word clouds
8. **Section 7** — Conversations card + KV sections (initiator, morning, ghost, consec, questions, laughs) + conversation length table
9. **Section 8** — Deleted messages + longest word per person + manners + rants
10. **Appendix caution banner** — Warns that actual messages appear below
11. **Appendix A** — First messages (full text)
12. **Appendix B** — Top 3 longest messages per person (full text)
13. **Appendix C** — Longest rant per person (first 2 messages, chat-bubble UI)
14. **Appendix D** — Happiest days (first 2 messages per top-5 day, chat-bubble UI)

All sections include ⓘ info tooltips where configurable assumptions are used.

---

## Design

Warm light theme with vermillion accent. See `DESIGN.md` for full token reference:
- Fonts: Bricolage Grotesque (display), DM Sans (body), JetBrains Mono (stats)
- Background: `#FAF7F2` warm off-white
- Accent: `#D94F30` vermillion
- Participant colors: vermillion, teal, plum, golden, forest
- Interactive Plotly charts with transparent backgrounds
