from __future__ import annotations

from collections import Counter

import emoji

from src.analyzers.base import AnalysisResult, IAnalyzer
from src.config.settings import Settings
from src.models.chat import Chat


class EmojiAnalyzer(IAnalyzer):
    def __init__(self, config: Settings):
        self._config = config

    def analyze(self, chat: Chat) -> AnalysisResult:
        user_msgs = [m for m in chat.messages if not m.is_system and not m.is_media
                     and not m.is_deleted and not m.is_call]

        # Extract emojis per person
        per_person_emojis: dict[str, list[str]] = {p: [] for p in chat.participants}
        all_emojis: list[str] = []
        monthly_emoji_counts: Counter = Counter()

        for m in user_msgs:
            emojis_in_msg = [e["emoji"] for e in emoji.emoji_list(m.content)]
            if emojis_in_msg:
                per_person_emojis[m.sender].extend(emojis_in_msg)
                all_emojis.extend(emojis_in_msg)
                month_key = m.datetime.strftime("%Y-%m")
                monthly_emoji_counts[month_key] += len(emojis_in_msg)

        # 4.1 Total emojis per person
        total_per_person = {p: len(emojis) for p, emojis in per_person_emojis.items()}

        # 4.2 Top emojis
        top_per_person = {}
        for p, emojis in per_person_emojis.items():
            top_per_person[p] = Counter(emojis).most_common(self._config.top_emojis_per_person)

        top_overall = Counter(all_emojis).most_common(self._config.top_emojis_overall)

        stats = {
            "total_per_person": total_per_person,
            "unique_per_person": {p: len(set(emojis)) for p, emojis in per_person_emojis.items()},
            "top_per_person": {p: [(e, c) for e, c in tops] for p, tops in top_per_person.items()},
            "top_overall": [(e, c) for e, c in top_overall],
        }

        return AnalysisResult(
            section_id="emoji",
            title="Emoji Analysis",
            stats=stats,
        )
