# WhatsappChatAnalyzer

Turn any WhatsApp chat export into an interactive HTML report with charts, stats, and insights.

![Python](https://img.shields.io/badge/Python-3.10+-blue)

> **Best viewed on a PC or tablet browser** — the report has interactive charts and comparison tables that benefit from a wider screen.

## What's this for?

The report isn't just a bunch of numbers — it's a conversation starter. Use it as a guide to **revisit your best moments together**. Sit with the person whose chat you're analyzing, and:

- Look up the **happiest conversations** by date and relive them in the actual chat
- Check out the **top stickers** you've spammed each other with
- Read the **longest messages** you've ever sent
- See who's the **morning texter**, who gets **left on read**, and who asks more questions
- Revisit your **most active days** and remember what was happening

It's a map of your relationship through chat data. The stats are just the starting point — the real fun is scrolling back to those moments together.

## Features

- **9 analysis sections**: basic stats, per-person breakdown, temporal trends, conversation dynamics, happiness analysis, emoji usage, media & stickers, word analysis, and more
- **Interactive Plotly charts**: weekly trends, hourly/daily distributions, monthly volume
- **Conversation dynamics**: who initiates, morning texter, left on read, response times, conversation length
- **Happiness analysis**: detects happy moments using keyword + emoji matching
- **Word clouds**: CSS-based per-person word clouds
- **Configurable**: stop words (English + Hinglish), conversation gap, emoji counts via `config.yaml`
- **Works with any chat**: 1-on-1 or group, any number of participants, auto-detected

## Quick Start

### Prerequisites

- **Python 3.10+** — [Download here](https://www.python.org/downloads/)
  - On Windows, check **"Add Python to PATH"** during installation

### 1. Clone the repo

```bash
git clone https://github.com/PratyushPareek/WhatsappChatAnalyzer.git
cd WhatsappChatAnalyzer
```

### 2. Export your WhatsApp chat

1. Open a WhatsApp chat
2. Tap **⋮** → **More** → **Export chat** → **Without media** (or with media)
3. Save the `.txt` file into the `chats/` folder

You can add **multiple chat files** — each one generates its own report.

### 3. First-time setup & run

**Windows:**
```
run.bat
```

**macOS / Linux:**
```bash
chmod +x run.sh
./run.sh
```

This creates a virtual environment, installs dependencies, runs the analysis, and outputs HTML reports in `output/`.

### 4. Run again (after setup)

Just double-click `run.bat` (Windows) or `./run.sh` (macOS/Linux) again — it skips setup if already done and re-generates all reports.

Or run manually:
```bash
# Windows
venv\Scripts\python.exe -m src.main

# macOS / Linux
venv/bin/python -m src.main
```

To process a specific file:
```bash
venv\Scripts\python.exe -m src.main chats\my-chat.txt
```

### Manual setup (if you prefer)

```bash
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
python -m src.main
```

## Report Sections

| # | Section | Highlights |
|---|---------|-----------|
| 1 | Overview & Basic Stats | Total messages/words/chars, active days/weeks %, summary sentence |
| 2 | Per-Person Breakdown | Message/word/char counts, top 3 longest messages (comparison table) |
| 3 | Temporal Analysis | Weekly/monthly trends, hourly/daily charts, streak, silence, response time |
| 4 | Conversation Dynamics | Initiator, morning texter, left on read, conversation length, questions, laughs |
| 5 | Happiness Analysis | Happy message count, happiest month, top 5 happiest moments |
| 6 | Emoji Analysis | Total/unique emojis, top 5 per person, top 10 overall |
| 7 | Sticker & Media | Stickers/images/videos/audio/contacts/PDFs, unique stickers, top 5 stickers |
| 8 | Word & Language | Top 10 words per person, vocabulary size, word clouds |
| 9 | Miscellaneous | Deleted messages, longest word per person, manners (polite words), rants (message streaks) |

Plus **Appendix A** (first messages) and **Appendix B** (top 3 longest messages per person).

## Configuration

Edit `config.yaml` to customize:

```yaml
conversation_gap_hours: 15    # hours of silence = new conversation
top_emojis_per_person: 5
top_emojis_overall: 10
date_format: null             # null = auto-detect, or "MDY" / "DMY"
include_appendix: true        # set to false to skip appendices in the report
stop_words:                   # add/remove words from frequency analysis
  - hai
  - toh
  # ...
manners_words:                # polite words/phrases to count (regex fragments)
  - "thank\\s?you"
  - thanks
  - sorry
  - please
  # ...
```

## Project Structure

```
WAChatAnalysis/
├── chats/              # Drop .txt exports here
├── output/             # Generated HTML reports
├── src/
│   ├── main.py         # Entry point
│   ├── pipeline.py     # Parse → Analyze → Visualize → Report
│   ├── models/         # Message & Chat dataclasses
│   ├── config/         # Settings loader
│   ├── parser/         # WhatsApp .txt parser
│   ├── analyzers/      # 9 independent analyzers (one per section)
│   ├── visualizers/    # Plotly chart generator
│   └── report/         # HTML report builder
├── config.yaml         # User settings
├── run.bat             # Windows one-click runner
├── run.sh              # macOS/Linux one-click runner
└── requirements.txt
```

## Architecture

SOLID design — each component is independently replaceable:
- **Parser**: `IChatParser` → `WhatsAppParser` (add `TelegramParser` etc.)
- **Analyzers**: `IAnalyzer` → 9 concrete analyzers (add new sections without touching existing code)
- **Visualizer**: `IVisualizer` → `PlotlyVisualizer` (swap for matplotlib etc.)
- **Report**: `IReportGenerator` → `HTMLReportGenerator` (swap for PDF etc.)

See `ARCHITECTURE.md` for full details.

## License

MIT
