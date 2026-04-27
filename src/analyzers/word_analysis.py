from __future__ import annotations

from collections import Counter

from src.analyzers.base import AnalysisResult, IAnalyzer
from src.config.settings import Settings
from src.models.chat import Chat


class WordAnalyzer(IAnalyzer):
    def __init__(self, config: Settings):
        self._config = config
        self._stop_words = set(w.lower() for w in config.stop_words)

    def analyze(self, chat: Chat) -> AnalysisResult:
        text_msgs = [m for m in chat.messages if not m.is_system and not m.is_media
                     and not m.is_deleted and not m.is_call]

        # Collect words per person
        per_person_words: dict[str, list[str]] = {p: [] for p in chat.participants}
        all_words: list[str] = []

        for m in text_msgs:
            words = self._extract_words(m.content)
            per_person_words[m.sender].extend(words)
            all_words.extend(words)

        # Filter stop words
        filtered_all = [w for w in all_words if w not in self._stop_words]
        filtered_per_person = {
            p: [w for w in words if w not in self._stop_words]
            for p, words in per_person_words.items()
        }

        # 6.1 Most common words
        top_per_person = {
            p: Counter(words).most_common(10)
            for p, words in filtered_per_person.items()
        }

        # 6.2 Word cloud data (top 50)
        wordcloud_per_person = {
            p: dict(Counter(words).most_common(50))
            for p, words in filtered_per_person.items()
        }

        # 6.3 Average words per message per person
        avg_words = {}
        for p in chat.participants:
            p_text = [m for m in text_msgs if m.sender == p]
            if p_text:
                total_w = sum(len(m.content.split()) for m in p_text)
                avg_words[p] = round(total_w / len(p_text), 1)
            else:
                avg_words[p] = 0

        # 6.4 Unique vocabulary size
        vocab_size = {
            p: len(set(words)) for p, words in per_person_words.items()
        }

        stats = {
            "top_words_per_person": {
                p: [(w, c) for w, c in tops] for p, tops in top_per_person.items()
            },
            "avg_words_per_message": avg_words,
            "vocab_size": vocab_size,
        }

        chart_data = {
            f"wordcloud_{p}": {
                "type": "wordcloud",
                "title": f"Word Cloud — {p}",
                "data": wc_data,
                "kwargs": {},
            }
            for p, wc_data in wordcloud_per_person.items() if wc_data
        }

        return AnalysisResult(
            section_id="words",
            title="Word & Language Analysis",
            stats=stats,
            chart_data=chart_data if chart_data else None,
        )

    @staticmethod
    def _extract_words(text: str) -> list[str]:
        """Extract lowercase words from text, stripping surrounding punctuation."""
        import re
        return [w for w in (re.sub(r"^[^\w']+|[^\w']+$", "", token).lower() for token in text.split()) if len(w) > 1]
