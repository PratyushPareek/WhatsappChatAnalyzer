from __future__ import annotations

from collections import Counter

from src.analyzers.base import AnalysisResult, IAnalyzer
from src.config.settings import Settings
from src.models.chat import Chat


class MediaAnalyzer(IAnalyzer):
    def __init__(self, config: Settings):
        self._config = config

    def analyze(self, chat: Chat) -> AnalysisResult:
        user_msgs = [m for m in chat.messages if not m.is_system]
        media_msgs = [m for m in user_msgs if m.is_media]

        per_person: dict[str, dict] = {}
        for p in chat.participants:
            p_media = [m for m in media_msgs if m.sender == p]
            type_counts = Counter(m.media_type for m in p_media)
            media_count = len(p_media)

            per_person[p] = {
                "stickers": type_counts.get("sticker", 0),
                "images": type_counts.get("image", 0),
                "videos": type_counts.get("video", 0),
                "audio": type_counts.get("audio", 0),
                "documents": type_counts.get("document", 0),
                "contacts": type_counts.get("contact", 0),
                "pdfs": type_counts.get("pdf", 0),
                "unknown_media": type_counts.get("unknown", 0),
                "total_media": media_count,
            }

        # Totals
        total_type_counts = Counter(m.media_type for m in media_msgs)
        total_stats = {
            "stickers": total_type_counts.get("sticker", 0),
            "images": total_type_counts.get("image", 0),
            "videos": total_type_counts.get("video", 0),
            "audio": total_type_counts.get("audio", 0),
            "documents": total_type_counts.get("document", 0),
            "unknown_media": total_type_counts.get("unknown", 0),
            "total_media": len(media_msgs),
        }

        # Top 5 stickers per person (by filename/ID)
        import re
        _FILE_RE = re.compile(r"^(.+)\s\(file attached\)$")
        top_stickers_per_person = {}
        for p in chat.participants:
            sticker_ids: list[str] = []
            for m in media_msgs:
                if m.sender == p and m.media_type == "sticker":
                    match = _FILE_RE.match(m.content.strip())
                    if match:
                        sticker_ids.append(match.group(1))
            top_stickers_per_person[p] = Counter(sticker_ids).most_common(5)

        # Unique stickers per person
        unique_stickers_per_person = {}
        for p in chat.participants:
            sticker_set = set()
            for m in media_msgs:
                if m.sender == p and m.media_type == "sticker":
                    match = _FILE_RE.match(m.content.strip())
                    if match:
                        sticker_set.add(match.group(1))
            unique_stickers_per_person[p] = len(sticker_set)

        return AnalysisResult(
            section_id="media",
            title="Sticker & Media Analysis",
            stats={"per_person": per_person, "totals": total_stats, "top_stickers_per_person": top_stickers_per_person, "unique_stickers_per_person": unique_stickers_per_person},
        )
