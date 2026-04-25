from src.analyzers.base import AnalysisResult, IAnalyzer
from src.config.settings import Settings
from src.models.chat import Chat


class PerPersonAnalyzer(IAnalyzer):
    def __init__(self, config: Settings):
        self._config = config

    def analyze(self, chat: Chat) -> AnalysisResult:
        user_msgs = [m for m in chat.messages if not m.is_system]
        text_msgs = [m for m in user_msgs if not m.is_media and not m.is_deleted and not m.is_call]
        total = len(user_msgs)

        per_person: dict[str, dict] = {}
        for p in chat.participants:
            p_msgs = [m for m in user_msgs if m.sender == p]
            p_text = [m for m in text_msgs if m.sender == p]
            msg_count = len(p_msgs)
            word_count = sum(len(m.content.split()) for m in p_text)
            char_count = sum(len(m.content) for m in p_text)

            # Top 3 longest messages
            sorted_by_len = sorted(p_text, key=lambda m: len(m.content), reverse=True)[:3]
            top_longest = [
                {
                    "date": msg.datetime.strftime("%B %d, %Y"),
                    "time": msg.datetime.strftime("%I:%M %p"),
                    "word_count": len(msg.content.split()),
                    "char_count": len(msg.content),
                }
                for msg in sorted_by_len
            ]

            per_person[p] = {
                "message_count": msg_count,
                "message_pct": round(msg_count / total * 100, 1) if total else 0,
                "word_count": word_count,
                "avg_words_per_msg": round(word_count / len(p_text), 1) if p_text else 0,
                "char_count": char_count,
                "longest_messages": top_longest,
            }

        # Appendix B: top 3 longest message full text per person
        appendix = {}
        for p in chat.participants:
            p_text = [m for m in text_msgs if m.sender == p]
            if p_text:
                sorted_by_len = sorted(p_text, key=lambda m: len(m.content), reverse=True)[:3]
                appendix[p] = [
                    {
                        "date": msg.datetime.strftime("%B %d, %Y"),
                        "time": msg.datetime.strftime("%I:%M %p"),
                        "content": msg.content,
                    }
                    for msg in sorted_by_len
                ]

        return AnalysisResult(
            section_id="per_person",
            title="Per-Person Breakdown",
            stats={"per_person": per_person},
            appendix={"longest_messages": appendix},
        )
