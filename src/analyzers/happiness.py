import re
from collections import Counter
from datetime import datetime, timedelta

import emoji as emoji_lib

from src.analyzers.base import AnalysisResult, IAnalyzer
from src.config.settings import Settings
from src.models.chat import Chat

# Happy / laughing
_HAPPY_WORDS = re.compile(
    r"\b(haha|hahaha|hahahaha|lol|lmao|lmfao|rofl|xd|"
    r"happy|yay|yaaay|yayyy|woohoo|wohoo|hurray|hooray|"
    r"amazing|awesome|fantastic|wonderful|great|nice|perfect|"
    r"excited|celebrate|party|fun|joy|blessed|grateful)\b",
    re.IGNORECASE,
)
_HAPPY_EMOJIS = {
    "😂", "🤣", "😄", "😁", "😆", "😃", "😀", "😊", "🥳", "🎉", "🎊",
    "😹", "🤩", "😍", "🥰", "😎", "✨", "🙌", "💃", "🕺", "🎶", "😜",
    "😝", "😛", "🤗", "🤭", "😏", "🫶",
}



class HappinessAnalyzer(IAnalyzer):
    def __init__(self, config: Settings):
        self._config = config

    def analyze(self, chat: Chat) -> AnalysisResult:
        user_msgs = [m for m in chat.messages if not m.is_system
                     and not m.is_media and not m.is_deleted and not m.is_call]

        # Per-person counts
        happy_counts = {p: 0 for p in chat.participants}

        # Monthly tracking
        monthly_happy: Counter = Counter()

        for m in user_msgs:
            content_emojis = set(m.content)
            month_key = m.datetime.strftime("%Y-%m")

            is_happy = bool(_HAPPY_WORDS.search(m.content)) or bool(_HAPPY_EMOJIS & content_emojis)
            if is_happy:
                happy_counts[m.sender] += 1
                monthly_happy[month_key] += 1

        total_text = len(user_msgs)

        # Per-person stats
        per_person = {}
        for p in chat.participants:
            p_msgs = sum(1 for m in user_msgs if m.sender == p)
            per_person[p] = {
                "happy_count": happy_counts[p],
                "happy_pct": round(happy_counts[p] / p_msgs * 100, 1) if p_msgs else 0,
            }

        total_happy = sum(happy_counts.values())

        # Happiest month
        happiest_month = None
        if monthly_happy:
            best_month, best_count = monthly_happy.most_common(1)[0]
            dt = datetime.strptime(best_month, "%Y-%m")
            happiest_month = {
                "month": dt.strftime("%B %Y"),
                "count": best_count,
            }

        # Happiest moments — score each conversation by happy+love density
        gap = timedelta(hours=self._config.conversation_gap_hours)
        conversations: list[list] = []
        convo: list = [user_msgs[0]] if user_msgs else []
        for i in range(1, len(user_msgs)):
            if user_msgs[i].datetime - user_msgs[i - 1].datetime >= gap:
                conversations.append(convo)
                convo = []
            convo.append(user_msgs[i])
        if convo:
            conversations.append(convo)

        scored_convos = []
        for convo_msgs in conversations:
            if len(convo_msgs) < 5:
                continue
            score = 0
            for m in convo_msgs:
                content_emojis = set(m.content)
                if bool(_HAPPY_WORDS.search(m.content)) or bool(_HAPPY_EMOJIS & content_emojis):
                    score += 1
            density = score / len(convo_msgs)
            scored_convos.append({
                "date": convo_msgs[0].datetime.strftime("%B %d, %Y"),
                "time": convo_msgs[0].datetime.strftime("%I:%M %p"),
                "messages": len(convo_msgs),
                "score": score,
                "density": round(density * 100, 1),
                "preview": convo_msgs[0].content[:80],
                "sender": convo_msgs[0].sender,
            })

        scored_convos.sort(key=lambda x: x["score"], reverse=True)
        happiest_moments = scored_convos[:5]

        stats = {
            "per_person": per_person,
            "total_happy": total_happy,
            "total_happy_pct": round(total_happy / total_text * 100, 1) if total_text else 0,
            "happiest_month": happiest_month,
            "happiest_moments": happiest_moments,
        }

        return AnalysisResult(
            section_id="happiness",
            title="Happiness Analysis",
            stats=stats,
        )
