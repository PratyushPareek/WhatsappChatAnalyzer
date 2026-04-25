from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class Settings:
    stop_words: list[str] = field(default_factory=list)
    conversation_gap_hours: int = 15
    min_caps_word_length: int = 3
    top_words_count: int = 20
    top_emojis_per_person: int = 5
    top_emojis_overall: int = 10
    date_format: str | None = None
    chart_style: dict = field(default_factory=lambda: {
        "figure_width": 10,
        "figure_height": 6,
        "color_palette": ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3"],
        "font_size": 12,
        "title_size": 14,
        "dpi": 150,
    })
    output_dir: str = "output"
    chats_dir: str = "chats"
    include_appendix: bool = True

    @classmethod
    def from_yaml(cls, path: str) -> "Settings":
        config_path = Path(path)
        if not config_path.exists():
            return cls()
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return cls(
            stop_words=[str(w) for w in data.get("stop_words", [])],
            conversation_gap_hours=data.get("conversation_gap_hours", 12),
            min_caps_word_length=data.get("min_caps_word_length", 3),
            top_words_count=data.get("top_words_count", 20),
            top_emojis_per_person=data.get("top_emojis_per_person", 5),
            top_emojis_overall=data.get("top_emojis_overall", 10),
            date_format=data.get("date_format", None),
            chart_style={**cls().chart_style, **data.get("chart_style", {})},
            output_dir=data.get("output_dir", "output"),
            chats_dir=data.get("chats_dir", "chats"),
            include_appendix=data.get("include_appendix", True),
        )
