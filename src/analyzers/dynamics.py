import re
from collections import Counter
from datetime import timedelta

from src.analyzers.base import AnalysisResult, IAnalyzer
from src.config.settings import Settings
from src.models.chat import Chat

_LAUGH_PATTERNS = re.compile(r"\b(ha(ha)+|lol|lmao|lmfao|rofl)\b", re.IGNORECASE)
_LAUGH_EMOJIS = {"😂", "🤣"}


class DynamicsAnalyzer(IAnalyzer):
    def __init__(self, config: Settings):
        self._config = config

    def analyze(self, chat: Chat) -> AnalysisResult:
        user_msgs = [m for m in chat.messages if not m.is_system]
        if not user_msgs:
            return AnalysisResult(section_id="dynamics", title="Conversation Dynamics", stats={})

        gap = timedelta(hours=self._config.conversation_gap_hours)

        # 7.1 Conversation initiator
        initiator_counts: Counter = Counter()
        # First message is always an initiation
        initiator_counts[user_msgs[0].sender] += 1
        for i in range(1, len(user_msgs)):
            if user_msgs[i].datetime - user_msgs[i - 1].datetime >= gap:
                initiator_counts[user_msgs[i].sender] += 1
        total_convos = sum(initiator_counts.values())

        initiator_stats = {
            p: {
                "count": initiator_counts.get(p, 0),
                "pct": round(initiator_counts.get(p, 0) / total_convos * 100, 1) if total_convos else 0,
            }
            for p in chat.participants
        }

        # 7.2 Double/triple texting (consecutive messages)
        consecutive: dict[str, dict] = {p: {"double": 0, "triple_plus": 0} for p in chat.participants}
        streak = 1
        for i in range(1, len(user_msgs)):
            if user_msgs[i].sender == user_msgs[i - 1].sender:
                streak += 1
            else:
                if streak == 2:
                    consecutive[user_msgs[i - 1].sender]["double"] += 1
                elif streak >= 3:
                    consecutive[user_msgs[i - 1].sender]["triple_plus"] += 1
                streak = 1
        # Handle last streak
        if streak == 2:
            consecutive[user_msgs[-1].sender]["double"] += 1
        elif streak >= 3:
            consecutive[user_msgs[-1].sender]["triple_plus"] += 1

        # 7.3 Question frequency
        question_counts = Counter()
        for m in user_msgs:
            if "?" in m.content:
                question_counts[m.sender] += 1
        question_stats = {p: question_counts.get(p, 0) for p in chat.participants}

        # 7.4 Laugh analysis
        laugh_counts = Counter()
        for m in user_msgs:
            has_laugh = bool(_LAUGH_PATTERNS.search(m.content))
            has_emoji = bool(_LAUGH_EMOJIS & set(m.content))
            if has_laugh or has_emoji:
                laugh_counts[m.sender] += 1
        laugh_stats = {p: laugh_counts.get(p, 0) for p in chat.participants}

        # 7.5 Morning texter — who sends the first message of the day (after 5 AM) more often?
        morning_counts: Counter = Counter()
        seen_dates: set = set()
        for m in user_msgs:
            d = m.datetime.date()
            if d not in seen_dates and m.datetime.hour >= 5:
                seen_dates.add(d)
                morning_counts[m.sender] += 1
        total_mornings = sum(morning_counts.values())
        morning_stats = {
            p: {
                "count": morning_counts.get(p, 0),
                "pct": round(morning_counts.get(p, 0) / total_mornings * 100, 1) if total_mornings else 0,
            }
            for p in chat.participants
        }

        # 7.6 Ghost / Left on read — whose message was last before a gap
        ghost_counts: Counter = Counter()
        for i in range(1, len(user_msgs)):
            if user_msgs[i].datetime - user_msgs[i - 1].datetime >= gap:
                ghost_counts[user_msgs[i - 1].sender] += 1
        ghost_stats = {
            p: {
                "count": ghost_counts.get(p, 0),
                "pct": round(ghost_counts.get(p, 0) / total_convos * 100, 1) if total_convos else 0,
            }
            for p in chat.participants
        }

        # 7.7 Conversation length (messages and duration) — p25, median, p75
        convo_lengths_msgs: list[int] = []
        convo_lengths_secs: list[float] = []
        convo_start_idx = 0
        for i in range(1, len(user_msgs)):
            if user_msgs[i].datetime - user_msgs[i - 1].datetime >= gap:
                # End of previous conversation
                msg_count = i - convo_start_idx
                duration = (user_msgs[i - 1].datetime - user_msgs[convo_start_idx].datetime).total_seconds()
                convo_lengths_msgs.append(msg_count)
                convo_lengths_secs.append(duration)
                convo_start_idx = i
        # Last conversation
        msg_count = len(user_msgs) - convo_start_idx
        duration = (user_msgs[-1].datetime - user_msgs[convo_start_idx].datetime).total_seconds()
        convo_lengths_msgs.append(msg_count)
        convo_lengths_secs.append(duration)

        def _percentiles(data: list) -> dict:
            s = sorted(data)
            n = len(s)
            if n == 0:
                return {"p25": 0, "median": 0, "p75": 0}
            return {
                "p25": s[n // 4],
                "median": s[n // 2],
                "p75": s[(3 * n) // 4],
            }

        convo_msg_pcts = _percentiles(convo_lengths_msgs)
        convo_dur_pcts = _percentiles(convo_lengths_secs)

        convo_length_stats = {
            "messages": {
                "p25": convo_msg_pcts["p25"],
                "median": convo_msg_pcts["median"],
                "p75": convo_msg_pcts["p75"],
            },
            "duration": {
                "p25": self._format_duration(convo_dur_pcts["p25"]),
                "median": self._format_duration(convo_dur_pcts["median"]),
                "p75": self._format_duration(convo_dur_pcts["p75"]),
            },
        }

        stats = {
            "total_conversations": total_convos,
            "initiator": initiator_stats,
            "consecutive_messages": consecutive,
            "questions": question_stats,
            "laughs": laugh_stats,
            "morning_texter": morning_stats,
            "ghost": ghost_stats,
            "conversation_length": convo_length_stats,
        }

        return AnalysisResult(
            section_id="dynamics",
            title="Conversation Dynamics",
            stats=stats,
        )

    @staticmethod
    def _format_duration(seconds: float) -> str:
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        if h > 0:
            return f"{h}h {m}m"
        return f"{m}m {s}s"
