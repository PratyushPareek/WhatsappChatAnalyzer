# WAChatAnalysis — Product Requirements Document

## Overview

A Python tool that reads **any** WhatsApp chat export (`.txt`), extracts insights, and generates a styled PDF report. Works with both **1-on-1 and group chats** — participants are auto-detected from the file, and all metrics adapt to the number of participants found.

---

## Input / Output

| Item | Detail |
|------|--------|
| **Input** | Any `.txt` file exported from WhatsApp, placed in `chats/` folder. Supports any number of participants. |
| **Output** | PDF report in `output/` folder, named after the input file (e.g., `team-chat.txt` → `team-chat_report.pdf`) |
| **Trigger** | Run `python src/main.py [filename]` — if no filename given, processes all `.txt` files in `chats/` |

---

## Report Sections

### 1. Overview & Basic Stats

| # | Metric | Notes |
|---|--------|-------|
| 1.1 | Total messages | Count of all user messages (excludes system messages) |
| 1.2 | Total words | Words from message content only (excludes sender name, date, timestamps) |
| 1.3 | Total characters | Characters from message content only (excludes sender name, date, timestamps) |
| 1.4 | Date range | First message date → last message date |
| 1.5 | Number of participants | Auto-detected from the chat |
| 1.6 | First message | Date, time, and sender shown here; full message text in **Appendix A** (one per participant) |
| 1.7 | Active days | Number of days where at least one message was sent by any participant |

---

### 2. Per-Person Breakdown

| # | Metric | Notes |
|---|--------|-------|
| 2.1 | Message count | Total messages per person + percentage share |
| 2.2 | Word count | Total words per person + average words per message |
| 2.3 | Character count | Total characters per person (no average) |
| 2.4 | Longest message | Date, time, and length (word count + character count) shown in main report; full text in **Appendix B** |

---

### 3. Temporal Analysis

| # | Metric | Notes |
|---|--------|-------|
| 3.1 | Messages per week | Line chart over time, aggregated at week level (avoids noise from zero-message days) |
| 3.2 | Messages per hour of day | Histogram (0–23h); combined for all participants, not per-person |
| 3.3 | Messages per day of week | Bar chart (Mon–Sun); combined for all participants, not per-person |
| 3.4 | Messages per month | Bar/line chart showing monthly volume over the full date range |
| 3.5 | Most active day per person | The single calendar day each person sent the most messages |
| 3.6 | Most active hour per person | The hour of day each person is most active |
| 3.7 | Longest streak | Longest run of consecutive calendar days with at least one message |
| 3.8 | Longest silence | Largest gap (in days/hours) between any two consecutive messages |
| 3.9 | Response time | Average time-to-reply per person (median + average) |

---

### 4. Emoji Analysis

| # | Metric | Notes |
|---|--------|-------|
| 4.1 | Total emojis per person | Count of all emoji characters used |
| 4.2 | Top emojis | Top 5 most used emojis per person; top 10 overall |
| 4.3 | Emoji usage over time | Trend chart — emoji count per month |

---

### 5. Sticker & Media Analysis

| # | Metric | Notes |
|---|--------|-------|
| 5.1 | Stickers sent per person | Detected via `STK-*` filenames or `<Media omitted>` heuristics |
| 5.2 | Images shared per person | Detected via `IMG-*` filenames |
| 5.3 | Videos, GIFs, audio messages shared | Grouped count per person |
| 5.4 | Media-to-text ratio | Ratio of media messages to text messages per person |

---

### 6. Word & Language Analysis

| # | Metric | Notes |
|---|--------|-------|
| 6.1 | Most common words | Top 20 words (excluding stop words) — overall and per person |
| 6.2 | Word cloud data | Top 50 words per person (data for word cloud visualization) |
| 6.3 | Average sentence length | Average words per message per person |
| 6.4 | Unique vocabulary size | Number of distinct words used per person |

---

### 7. Conversation Dynamics

| # | Metric | Notes |
|---|--------|-------|
| 7.1 | Conversation initiator | Who starts conversations more often; a "conversation" begins after a **12-hour** gap |
| 7.2 | Double/triple texting | Who sends more consecutive messages (2+ messages in a row without reply) |
| 7.3 | Question frequency | Messages containing `?` per person |
| 7.4 | Laugh analysis | Frequency of `haha`, `hahaha`, `lol`, `😂`, `🤣`, `lmao` etc. per person |

---

### 8. Fun & Novelty Stats

| # | Metric | Notes |
|---|--------|-------|
| 8.1 | Deleted messages | Count of `This message was deleted` + `You deleted this message` per person |
| 8.2 | Most used single word | The single most frequently used word per person (excluding stop words) |
| 8.3 | Longest word used | The longest single word that appeared in the chat |
| 8.4 | SHOUTING index | Percentage of messages containing ALL-CAPS words (3+ chars) per person |

---

### Appendices

| Appendix | Content |
|----------|---------|
| **A** | First message sent by each participant (full text) |
| **B** | Longest message sent by each participant (full text) |

---

## Architecture

```
WAChatAnalysis/
│
├── chats/                  # Drop any WhatsApp .txt export(s) here
│   └── *.txt
│
├── src/
│   ├── main.py             # Orchestrator: parse → analyze → visualize → PDF
│   ├── parser.py           # Parse WhatsApp .txt into structured data (list of dicts / DataFrame)
│   ├── analyzer.py         # Compute all insights from parsed data
│   ├── visualizer.py       # Generate charts (matplotlib)
│   └── pdf_generator.py    # Assemble insights + charts into a PDF
│
├── output/                 # Generated PDFs
├── config.yaml             # Stop words, thresholds, settings
├── requirements.txt
├── NOTES.md                # Parsing format notes
└── PRD.md                  # This file
```

---

## Data Model

After parsing, each message becomes a record with:

| Field | Type | Example |
|-------|------|---------|
| `datetime` | `datetime` | `2023-09-25 19:26:00` |
| `date` | `date` | `2023-09-25` |
| `time` | `time` | `19:26` |
| `hour` | `int` | `19` |
| `day_of_week` | `str` | `Monday` |
| `sender` | `str` | `Pratyush` |
| `message` | `str` | `Haan` |
| `is_media` | `bool` | `False` |
| `media_type` | `str\|None` | `sticker`, `image`, `video`, `audio`, `None` |
| `is_deleted` | `bool` | `False` |
| `is_system` | `bool` | `False` |
| `word_count` | `int` | `1` |
| `char_count` | `int` | `4` |
| `emoji_list` | `list[str]` | `['😂', '🤣']` |
| `emoji_count` | `int` | `2` |

---

## Parsing Rules

1. **Message line regex**: `^(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2}[\s\u202f][APap][Mm])\s-\s`
2. **User message**: line matches regex AND contains `: ` after sender name
3. **System message**: line matches regex but no `: ` pattern for sender
4. **Multi-line message**: line does NOT match regex → append to previous message
5. **Participant detection**: all unique sender names are auto-extracted from the parsed messages; no hardcoded names
6. **Media detection**:
   - `<Media omitted>` → `is_media = True`, `media_type = unknown`
   - `STK-*.webp (file attached)` → `media_type = sticker`
   - `IMG-*.jpg (file attached)` → `media_type = image`
   - `VID-* (file attached)` → `media_type = video`
   - `PTT-* (file attached)` → `media_type = audio`
7. **Deleted**: message is exactly `This message was deleted` or `You deleted this message`
8. **Missed calls**: message is exactly `Missed voice call` or `Missed video call`
9. **Encoding**: handle both regular space and `\u202F` (narrow no-break space) before AM/PM
10. **Date format flexibility**: support both `M/D/YY` (US) and `D/M/YY` (international) — auto-detect based on values > 12 in the first field, or fall back to config

---

## Libraries

| Purpose | Library |
|---------|---------|
| Parsing | `re`, `datetime` |
| Data handling | `pandas` |
| Emoji extraction | `emoji` |
| Visualization | `matplotlib` |
| PDF generation | `fpdf2` |
| Stop words | `config.yaml` (custom list; default includes English + Hinglish; user can extend) |

---

## PDF Layout (High-Level)

1. **Cover page** — title, participants, date range
2. **Section 1** — Overview stats (table / key-value cards)
3. **Section 2** — Per-person breakdown (side-by-side comparison)
4. **Section 3** — Temporal charts (weekly trend, hourly histogram, day-of-week bar, monthly trend)
5. **Section 4** — Emoji summary + trend chart
6. **Section 5** — Media summary (table)
7. **Section 6** — Word analysis (word clouds + top-words table)
8. **Section 7** — Conversation dynamics (table / infographic)
9. **Section 8** — Fun stats (cards / callouts)
10. **Appendix A** — First messages
11. **Appendix B** — Longest messages

---

## Build Order

| Phase | What | Depends On |
|-------|------|------------|
| **P0** | `parser.py` — parse .txt into DataFrame | — |
| **P1** | `analyzer.py` — Sections 1, 2 (basic stats + per-person) | P0 |
| **P2** | `analyzer.py` — Sections 3, 4, 5 (temporal, emoji, media) | P0 |
| **P3** | `analyzer.py` — Sections 6, 7, 8 (words, dynamics, fun) | P0 |
| **P4** | `visualizer.py` — all charts | P1–P3 |
| **P5** | `pdf_generator.py` — assemble PDF | P4 |
| **P6** | Polish — styling, edge cases, config | P5 |
