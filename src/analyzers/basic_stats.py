from datetime import timedelta

from src.analyzers.base import AnalysisResult, IAnalyzer
from src.config.settings import Settings
from src.models.chat import Chat


class BasicStatsAnalyzer(IAnalyzer):
    def __init__(self, config: Settings):
        self._config = config

    def analyze(self, chat: Chat) -> AnalysisResult:
        user_msgs = [m for m in chat.messages if not m.is_system]
        text_msgs = [m for m in user_msgs if not m.is_media and not m.is_deleted and not m.is_call]

        total_messages = len(user_msgs)
        total_words = sum(len(m.content.split()) for m in text_msgs)
        total_chars = sum(len(m.content) for m in text_msgs)

        active_dates = {m.datetime.date() for m in user_msgs}
        active_days = len(active_dates)

        # Total days in range
        total_days = (chat.date_range[1].date() - chat.date_range[0].date()).days + 1
        active_days_pct = round(active_days / total_days * 100, 1) if total_days else 0

        # Weeks: active weeks (at least one message) vs total weeks in range
        active_weeks = len({d.isocalendar()[:2] for d in active_dates})
        total_weeks = (total_days + 6) // 7  # ceiling division
        active_weeks_pct = round(active_weeks / total_weeks * 100, 1) if total_weeks else 0

        first_msg = user_msgs[0] if user_msgs else None

        stats = {
            "total_messages": total_messages,
            "total_words": total_words,
            "total_characters": total_chars,
            "date_range_start": chat.date_range[0].strftime("%B %d, %Y"),
            "date_range_end": chat.date_range[1].strftime("%B %d, %Y"),
            "num_participants": len(chat.participants),
            "participants": chat.participants,
            "total_days": total_days,
            "active_days": active_days,
            "active_days_pct": active_days_pct,
            "total_weeks": total_weeks,
            "active_weeks": active_weeks,
            "active_weeks_pct": active_weeks_pct,
            "total_years": round(total_days / 365.25, 1),
            "first_message": {
                "sender": first_msg.sender,
                "date": first_msg.datetime.strftime("%B %d, %Y"),
                "time": first_msg.datetime.strftime("%I:%M %p"),
            } if first_msg else None,
        }

        # Appendix A: first message per participant
        appendix = {}
        seen = set()
        for m in user_msgs:
            if m.sender not in seen:
                seen.add(m.sender)
                appendix[m.sender] = {
                    "date": m.datetime.strftime("%B %d, %Y"),
                    "time": m.datetime.strftime("%I:%M %p"),
                    "content": m.content,
                }

        return AnalysisResult(
            section_id="basic_stats",
            title="Overview & Basic Stats",
            stats=stats,
            appendix={"first_messages": appendix},
        )
