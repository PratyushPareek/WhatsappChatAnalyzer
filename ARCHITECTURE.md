# WAChatAnalysis — Architecture Plan

## Design Principles

- **SOLID** throughout
- Each module is independently replaceable (swap PDF engine, chart library, etc.)
- All inter-module communication goes through **data classes and interfaces (ABCs/Protocols)**, never concrete implementations
- Configuration is injected, never hard-coded

---

## Directory Structure

```
WAChatAnalysis/
│
├── chats/                          # Input: drop .txt exports here
│
├── src/
│   ├── __init__.py
│   ├── main.py                     # Entry point & orchestrator
│   │
│   ├── models/                     # Pure data structures (no logic)
│   │   ├── __init__.py
│   │   ├── message.py              # Message dataclass
│   │   └── chat.py                 # Chat dataclass (holds list[Message] + metadata)
│   │
│   ├── parser/                     # Parsing layer
│   │   ├── __init__.py
│   │   ├── base.py                 # IChatParser (abstract)
│   │   └── whatsapp_parser.py      # WhatsApp-specific implementation
│   │
│   ├── analyzers/                  # Analysis layer — one analyzer per report section
│   │   ├── __init__.py
│   │   ├── base.py                 # IAnalyzer (abstract)
│   │   ├── basic_stats.py          # Section 1: overview & basic stats
│   │   ├── per_person.py           # Section 2: per-person breakdown
│   │   ├── temporal.py             # Section 3: temporal analysis
│   │   ├── emoji_analyzer.py       # Section 4: emoji analysis
│   │   ├── media.py                # Section 5: sticker & media analysis
│   │   ├── word_analysis.py        # Section 6: word & language analysis
│   │   ├── dynamics.py             # Section 7: conversation dynamics
│   │   └── fun_stats.py            # Section 8: fun & novelty stats
│   │
│   ├── visualizers/                # Chart generation layer
│   │   ├── __init__.py
│   │   ├── base.py                 # IVisualizer (abstract)
│   │   └── matplotlib_visualizer.py # Matplotlib implementation
│   │
│   ├── report/                     # PDF generation layer
│   │   ├── __init__.py
│   │   ├── base.py                 # IReportGenerator (abstract)
│   │   └── pdf_report.py           # FPDF2 implementation
│   │
│   ├── config/                     # Configuration
│   │   ├── __init__.py
│   │   └── settings.py             # Config loader (reads config.yaml)
│   │
│   └── pipeline.py                 # Pipeline: wires parser → analyzers → visualizer → report
│
├── output/                         # Generated reports
├── config.yaml                     # User-editable settings
├── requirements.txt
└── PRD.md
```

---

## Core Interfaces & Classes

### 1. Models (`src/models/`)

Pure data holders. No business logic. Immutable where possible.

```python
# message.py
@dataclass(frozen=True)
class Message:
    datetime: datetime
    sender: str
    content: str              # raw message text
    is_system: bool
    is_media: bool
    media_type: str | None    # "sticker", "image", "video", "audio", "unknown", None
    is_deleted: bool
    is_call: bool
    call_type: str | None     # "voice", "video", None

# chat.py
@dataclass
class Chat:
    messages: list[Message]
    participants: list[str]
    source_file: str
    date_range: tuple[datetime, datetime]
```

**Principle**: Single Responsibility — models only hold data.

---

### 2. Parser (`src/parser/`)

```python
# base.py
class IChatParser(ABC):
    @abstractmethod
    def parse(self, file_path: str) -> Chat:
        """Read a chat export file and return a Chat object."""
        ...

# whatsapp_parser.py
class WhatsAppParser(IChatParser):
    def __init__(self, config: Settings):
        self._config = config

    def parse(self, file_path: str) -> Chat:
        ...

    def _parse_line(self, line: str) -> ...:
        ...

    def _detect_date_format(self, lines: list[str]) -> str:
        ...

    def _classify_message(self, raw_content: str) -> tuple[bool, str | None, bool, bool, str | None]:
        """Returns (is_media, media_type, is_deleted, is_call, call_type)"""
        ...
```

**Principle**: Open/Closed — add a `TelegramParser(IChatParser)` or `SignalParser(IChatParser)` later without touching existing code. Dependency Inversion — pipeline depends on `IChatParser`, not `WhatsAppParser`.

---

### 3. Analyzers (`src/analyzers/`)

Each analyzer handles **one section** of the report. All share a common interface.

```python
# base.py
class AnalysisResult:
    """Container for analysis output — section name, stats dict, and any data needed for charts."""
    def __init__(self, section_id: str, title: str, stats: dict, chart_data: dict | None = None,
                 appendix: dict | None = None):
        self.section_id = section_id
        self.title = title
        self.stats = stats              # key-value pairs for the report
        self.chart_data = chart_data    # structured data the visualizer can plot
        self.appendix = appendix        # long-form text for appendices

class IAnalyzer(ABC):
    @abstractmethod
    def analyze(self, chat: Chat) -> AnalysisResult:
        """Run analysis on the chat and return structured results."""
        ...
```

**Concrete analyzers** (one per section):

| Class | Section | Key Output |
|-------|---------|------------|
| `BasicStatsAnalyzer` | 1 | total msgs, words, chars, date range, active days |
| `PerPersonAnalyzer` | 2 | per-person msg/word/char counts, longest message |
| `TemporalAnalyzer` | 3 | weekly/hourly/daily/monthly aggregations, streaks, response times |
| `EmojiAnalyzer` | 4 | emoji counts, top emojis, monthly trend data |
| `MediaAnalyzer` | 5 | sticker/image/video/audio counts, media-to-text ratio |
| `WordAnalyzer` | 6 | top words, word cloud data, vocab size |
| `DynamicsAnalyzer` | 7 | initiator counts, consecutive msgs, questions, laughs |
| `FunStatsAnalyzer` | 8 | deleted msgs, longest word, shouting index |

**Principle**: Single Responsibility — each analyzer does one thing. Interface Segregation — analyzers don't need to know about charts or PDFs. New sections = new analyzer class, no changes to existing ones (Open/Closed).

---

### 4. Visualizer (`src/visualizers/`)

```python
# base.py
class IVisualizer(ABC):
    @abstractmethod
    def create_chart(self, chart_type: str, data: dict, title: str, **kwargs) -> str:
        """Generate a chart image and return the file path to the saved image."""
        ...

# matplotlib_visualizer.py
class MatplotlibVisualizer(IVisualizer):
    def __init__(self, output_dir: str, style: dict | None = None):
        self._output_dir = output_dir
        self._style = style or {}

    def create_chart(self, chart_type: str, data: dict, title: str, **kwargs) -> str:
        ...

    def _line_chart(self, data, title, **kwargs) -> str: ...
    def _bar_chart(self, data, title, **kwargs) -> str: ...
    def _histogram(self, data, title, **kwargs) -> str: ...
    def _word_cloud(self, data, title, **kwargs) -> str: ...
```

**Principle**: Liskov Substitution — swap in a `PlotlyVisualizer(IVisualizer)` and everything still works. Dependency Inversion — pipeline depends on `IVisualizer`, not matplotlib.

---

### 5. Report Generator (`src/report/`)

```python
# base.py
class IReportGenerator(ABC):
    @abstractmethod
    def generate(self, results: list[AnalysisResult], chart_paths: dict[str, list[str]],
                 metadata: dict) -> str:
        """Assemble the final report. Returns the output file path."""
        ...

# pdf_report.py
class PDFReportGenerator(IReportGenerator):
    def __init__(self, output_dir: str, config: Settings):
        self._output_dir = output_dir
        self._config = config

    def generate(self, results: list[AnalysisResult], chart_paths: dict[str, list[str]],
                 metadata: dict) -> str:
        ...

    def _cover_page(self, metadata: dict): ...
    def _section_page(self, result: AnalysisResult, charts: list[str]): ...
    def _appendix_page(self, title: str, content: str): ...
```

**Principle**: Open/Closed — add `HTMLReportGenerator(IReportGenerator)` without touching PDF code.

---

### 6. Configuration (`src/config/`)

```python
# settings.py
@dataclass
class Settings:
    stop_words: list[str]
    conversation_gap_hours: int        # default 12
    min_caps_word_length: int          # default 3 (for SHOUTING detection)
    top_words_count: int               # default 20
    top_emojis_per_person: int         # default 5
    top_emojis_overall: int            # default 10
    date_format: str | None            # None = auto-detect, "MDY" or "DMY"
    chart_style: dict                  # colors, fonts, sizes
    output_dir: str
    chats_dir: str

    @classmethod
    def from_yaml(cls, path: str) -> "Settings":
        ...
```

**Principle**: Single source of truth. Injected into all components that need it.

---

### 7. Pipeline (`src/pipeline.py`)

The orchestrator that wires everything together.

```python
class AnalysisPipeline:
    def __init__(
        self,
        parser: IChatParser,
        analyzers: list[IAnalyzer],
        visualizer: IVisualizer,
        report_generator: IReportGenerator,
    ):
        self._parser = parser
        self._analyzers = analyzers
        self._visualizer = visualizer
        self._report_generator = report_generator

    def run(self, file_path: str) -> str:
        """Full pipeline: parse → analyze → visualize → report. Returns report path."""

        # 1. Parse
        chat = self._parser.parse(file_path)

        # 2. Analyze (run all analyzers)
        results: list[AnalysisResult] = []
        for analyzer in self._analyzers:
            results.append(analyzer.analyze(chat))

        # 3. Visualize (generate charts from analysis results)
        chart_paths: dict[str, list[str]] = {}
        for result in results:
            if result.chart_data:
                paths = []
                for chart_id, chart_spec in result.chart_data.items():
                    path = self._visualizer.create_chart(
                        chart_type=chart_spec["type"],
                        data=chart_spec["data"],
                        title=chart_spec["title"],
                        **chart_spec.get("kwargs", {}),
                    )
                    paths.append(path)
                chart_paths[result.section_id] = paths

        # 4. Generate report
        metadata = {
            "participants": chat.participants,
            "source_file": chat.source_file,
            "date_range": chat.date_range,
        }
        return self._report_generator.generate(results, chart_paths, metadata)
```

**Principle**: Dependency Inversion — pipeline depends only on abstractions. Single Responsibility — pipeline only orchestrates, it doesn't parse/analyze/render. Open/Closed — add analyzers to the list without modifying pipeline code.

---

### 8. Entry Point (`src/main.py`)

```python
def main():
    config = Settings.from_yaml("config.yaml")

    # Compose the object graph
    parser = WhatsAppParser(config)
    analyzers = [
        BasicStatsAnalyzer(config),
        PerPersonAnalyzer(config),
        TemporalAnalyzer(config),
        EmojiAnalyzer(config),
        MediaAnalyzer(config),
        WordAnalyzer(config),
        DynamicsAnalyzer(config),
        FunStatsAnalyzer(config),
    ]
    visualizer = MatplotlibVisualizer(output_dir="output/charts", style=config.chart_style)
    report_gen = PDFReportGenerator(output_dir="output", config=config)

    pipeline = AnalysisPipeline(parser, analyzers, visualizer, report_gen)

    # Run for each file
    for file_path in get_chat_files(config.chats_dir, sys.argv[1:]):
        report_path = pipeline.run(file_path)
        print(f"Report generated: {report_path}")
```

**Principle**: Composition root — all wiring happens here. Everything else receives its dependencies via constructor injection.

---

## Data Flow

```
  .txt file
      │
      ▼
  IChatParser.parse()
      │
      ▼
  Chat (list[Message])
      │
      ├──► IAnalyzer[0].analyze() ──► AnalysisResult (stats + chart_data)
      ├──► IAnalyzer[1].analyze() ──► AnalysisResult
      ├──► ...
      └──► IAnalyzer[N].analyze() ──► AnalysisResult
                                           │
                                           ▼
                                   IVisualizer.create_chart()
                                           │
                                           ▼
                                     chart image paths
                                           │
                                           ▼
                              IReportGenerator.generate()
                                           │
                                           ▼
                                      report.pdf
```

---

## SOLID Summary

| Principle | How It's Applied |
|-----------|-----------------|
| **S** — Single Responsibility | Each class has one job: `Message` holds data, `WhatsAppParser` parses, `EmojiAnalyzer` analyzes emojis, `MatplotlibVisualizer` draws charts, `PDFReportGenerator` assembles PDFs |
| **O** — Open/Closed | New chat formats → new parser class. New analysis sections → new analyzer class. New output formats → new report generator. No existing code modified. |
| **L** — Liskov Substitution | Any `IAnalyzer` subclass is interchangeable. Swap `MatplotlibVisualizer` for `PlotlyVisualizer` seamlessly. |
| **I** — Interface Segregation | Analyzers don't depend on visualizer interfaces. Visualizers don't depend on report interfaces. Each sees only what it needs. |
| **D** — Dependency Inversion | `Pipeline` depends on `IChatParser`, `IAnalyzer`, `IVisualizer`, `IReportGenerator` — never concrete classes. Wiring happens only in `main.py`. |

---

## Extensibility Examples

| Want to... | Just... |
|------------|---------|
| Add Telegram support | Create `TelegramParser(IChatParser)` |
| Add a new insight (e.g., sentiment) | Create `SentimentAnalyzer(IAnalyzer)`, add to analyzer list in `main.py` |
| Switch to Plotly charts | Create `PlotlyVisualizer(IVisualizer)`, swap in `main.py` |
| Generate HTML instead of PDF | Create `HTMLReportGenerator(IReportGenerator)`, swap in `main.py` |
| Change stop words | Edit `config.yaml` |
