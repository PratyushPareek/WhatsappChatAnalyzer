import re
from collections import Counter
from datetime import timedelta

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

        # 8.3 Longest word used per person (filter out URLs, filenames, and link fragments)
        _SKIP_PATTERNS = {"http", "https", "www", "com", "org", "net", "io", "co",
                          "html", "pdf", "jpg", "png", "webp", "gif", "mp4", "mp3",
                          "whatsapp", "youtu", "instagram", "facebook", "twitter"}
        longest_word_per_person = {}
        for p in chat.participants:
            best = ""
            for m in text_msgs:
                if m.sender == p:
                    for w in m.content.split():
                        # Skip anything that looks like a URL or filepath
                        w_lower = w.lower()
                        if any(ind in w_lower for ind in ("http", "www.", "://", ".com", ".org", ".html", ".pdf", ".jpg", ".png")):
                            continue
                        cleaned = re.sub(r"[^a-zA-Z]", "", w)
                        if not cleaned:
                            continue
                        cleaned_lower = cleaned.lower()
                        if any(ind in cleaned_lower for ind in _SKIP_PATTERNS):
                            continue
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

        # 8.5 Manners — messages containing polite words (thank you, sorry, etc.)
        pattern = r"\b(" + "|".join(self._config.manners_words) + r")\b"
        _MANNERS_RE = re.compile(pattern, re.IGNORECASE)
        manners: dict[str, dict] = {}
        for p in chat.participants:
            p_text = [m for m in text_msgs if m.sender == p]
            count = sum(1 for m in p_text if _MANNERS_RE.search(m.content))
            manners[p] = {
                "count": count,
                "pct": round(count / len(p_text) * 100, 1) if p_text else 0.0,
            }

        # 8.6 Rants — streaks of consecutive messages by one person (≥ 4 in a row, each with ≥ 2 words)
        # Skip short filler messages (≤ 3 chars) from others without breaking streaks.
        # A gap of ≥ 2 minutes between messages breaks any streak (temporal contiguity).
        _RANT_THRESHOLD = 4
        gap = timedelta(minutes=2)
        rant_counts: dict[str, int] = {p: 0 for p in chat.participants}
        rant_longest: dict[str, int] = {p: 0 for p in chat.participants}
        streak = 0
        streak_sender: str | None = None
        last_dt = None
        for m in user_msgs:
            # Conversation gap breaks the streak
            if last_dt is not None and m.datetime - last_dt >= gap:
                if streak >= _RANT_THRESHOLD and streak_sender:
                    rant_counts[streak_sender] += 1
                    rant_longest[streak_sender] = max(rant_longest[streak_sender], streak)
                streak = 0
                streak_sender = None
            last_dt = m.datetime

            # Skip short filler messages (≤ 3 chars) from anyone
            if len(m.content.strip()) <= 3:
                continue

            # Must have at least 2 words to count as a rant message
            if len(m.content.split()) < 2:
                if m.sender != streak_sender:
                    if streak >= _RANT_THRESHOLD and streak_sender:
                        rant_counts[streak_sender] += 1
                        rant_longest[streak_sender] = max(rant_longest[streak_sender], streak)
                    streak = 0
                    streak_sender = None
                continue

            if m.sender == streak_sender:
                streak += 1
            else:
                if streak >= _RANT_THRESHOLD and streak_sender:
                    rant_counts[streak_sender] += 1
                    rant_longest[streak_sender] = max(rant_longest[streak_sender], streak)
                streak = 1
                streak_sender = m.sender
        # Handle last streak
        if streak >= _RANT_THRESHOLD and streak_sender:
            rant_counts[streak_sender] += 1
            rant_longest[streak_sender] = max(rant_longest[streak_sender], streak)

        rants: dict[str, dict] = {}
        for p in chat.participants:
            rants[p] = {
                "count": rant_counts[p],
                "longest_streak": rant_longest[p],
            }

        stats = {
            "deleted_messages": deleted_stats,
            "most_used_word": most_used_word,
            "longest_word_per_person": longest_word_per_person,
            "shouting_index": shouting,
            "manners": manners,
            "rants": rants,
        }

        return AnalysisResult(
            section_id="fun_stats",
            title="Miscellaneous",
            stats=stats,
        )
