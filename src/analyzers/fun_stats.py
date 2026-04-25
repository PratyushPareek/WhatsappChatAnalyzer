import re
from collections import Counter

from src.analyzers.base import AnalysisResult, IAnalyzer
from src.config.settings import Settings
from src.models.chat import Chat


class FunStatsAnalyzer(IAnalyzer):
    def __init__(self, config: Settings):
        self._config = config

    def analyze(self, chat: Chat) -> AnalysisResult:
        user_msgs = [m for m in chat.messages if not m.is_system]
        text_msgs = [m for m in user_msgs if not m.is_media and not m.is_deleted and not m.is_call]
        stop_words = set(w.lower() for w in self._config.stop_words)

        # 8.1 Deleted messages per person
        deleted_counts = Counter()
        for m in user_msgs:
            if m.is_deleted:
                deleted_counts[m.sender] += 1
        deleted_stats = {p: deleted_counts.get(p, 0) for p in chat.participants}

        # 8.2 Most used single word per person (excluding stop words)
        most_used_word = {}
        for p in chat.participants:
            words = []
            for m in text_msgs:
                if m.sender == p:
                    words.extend(w.lower() for w in m.content.split() if w.isalpha() and len(w) > 1)
            filtered = [w for w in words if w not in stop_words]
            if filtered:
                word, count = Counter(filtered).most_common(1)[0]
                most_used_word[p] = {"word": word, "count": count}

        # 8.3 Longest word used per person
        longest_word_per_person = {}
        for p in chat.participants:
            best = ""
            for m in text_msgs:
                if m.sender == p:
                    for w in m.content.split():
                        cleaned = re.sub(r"[^a-zA-Z]", "", w)
                        if len(cleaned) > len(best):
                            best = cleaned
            if best:
                longest_word_per_person[p] = best

        # 8.4 SHOUTING index — % of messages with ALL-CAPS words (min length)
        min_len = self._config.min_caps_word_length
        shouting: dict[str, dict] = {}
        for p in chat.participants:
            p_text = [m for m in text_msgs if m.sender == p]
            if not p_text:
                shouting[p] = {"count": 0, "pct": 0.0}
                continue
            caps_count = 0
            for m in p_text:
                words = m.content.split()
                if any(w.isupper() and len(w) >= min_len and w.isalpha() for w in words):
                    caps_count += 1
            shouting[p] = {
                "count": caps_count,
                "pct": round(caps_count / len(p_text) * 100, 1),
            }

        stats = {
            "deleted_messages": deleted_stats,
            "most_used_word": most_used_word,
            "longest_word_per_person": longest_word_per_person,
            "shouting_index": shouting,
        }

        return AnalysisResult(
            section_id="fun_stats",
            title="Miscellaneous",
            stats=stats,
        )
