import re
from datetime import datetime
from pathlib import Path

from src.config.settings import Settings
from src.models.chat import Chat
from src.models.message import Message
from src.parser.base import IChatParser

# Regex: date, time, separator, then rest of line
# Format A: 1/23/25, 4:56 PM - Sender: message
_LINE_RE_A = re.compile(
    r"^(\d{1,2}/\d{1,2}/\d{2,4}),\s"        # date
    r"(\d{1,2}:\d{2}[\s\u202f][APap][Mm])"    # time (space or narrow-no-break-space before AM/PM)
    r"\s-\s"                                   # separator
    r"(.+)$"                                   # rest
)

# Format B: [14/07/25, 16:33:03] Sender: message  (may have U+200E prefix)
_LINE_RE_B = re.compile(
    r"^\u200e?\[(\d{1,2}/\d{1,2}/\d{2,4}),\s"   # optional LTR mark + [ + date
    r"(\d{1,2}:\d{2}:\d{2})\]\s"                 # 24h time with seconds + ]
    r"(.+)$"                                      # rest
)

_MEDIA_OMITTED = "<Media omitted>"
_FILE_ATTACHED_RE = re.compile(r"^(.+)\s\(file attached\)$")
# Format B uses "X omitted" (with optional U+200E prefix)
_OMITTED_RE = re.compile(r"^\u200e?(sticker|image|video|audio|document|GIF|Contact card) omitted$")
_MEDIA_PREFIX_MAP = {
    "STK": "sticker",
    "IMG": "image",
    "VID": "video",
    "PTT": "audio",
    "AUD": "audio",
    "DOC": "document",
}

_DELETED_MESSAGES = {"This message was deleted", "You deleted this message"}
_CALL_MESSAGES = {
    "Missed voice call": "voice",
    "Missed video call": "video",
}


class WhatsAppParser(IChatParser):
    def __init__(self, config: Settings):
        self._config = config

    def parse(self, file_path: str) -> Chat:
        path = Path(file_path)
        lines = path.read_text(encoding="utf-8").splitlines()

        self._line_re = self._detect_format(lines)
        date_format = self._config.date_format or self._detect_date_format(lines)
        raw_messages = self._extract_raw_messages(lines)
        messages = [self._build_message(r, date_format) for r in raw_messages]

        participants = sorted({m.sender for m in messages if not m.is_system})
        user_messages = [m for m in messages if not m.is_system]
        date_range = (user_messages[0].datetime, user_messages[-1].datetime) if user_messages else (
            messages[0].datetime, messages[-1].datetime
        )

        return Chat(
            messages=messages,
            participants=participants,
            source_file=path.name,
            date_range=date_range,
        )

    def _extract_raw_messages(self, lines: list[str]) -> list[dict]:
        raw: list[dict] = []
        for line in lines:
            m = self._line_re.match(line)
            if m:
                date_str, time_str, rest = m.group(1), m.group(2), m.group(3)
                # Try to split sender: message
                colon_pos = rest.find(": ")
                if colon_pos != -1:
                    sender = rest[:colon_pos]
                    content = rest[colon_pos + 2:]
                    raw.append({
                        "date": date_str,
                        "time": time_str,
                        "sender": sender,
                        "content": content,
                        "is_system": False,
                    })
                else:
                    # System message
                    raw.append({
                        "date": date_str,
                        "time": time_str,
                        "sender": "",
                        "content": rest,
                        "is_system": True,
                    })
            elif raw:
                # Continuation of previous message
                raw[-1]["content"] += "\n" + line
        return raw

    def _build_message(self, raw: dict, date_format: str) -> Message:
        dt = self._parse_datetime(raw["date"], raw["time"], date_format)
        content = raw["content"].lstrip("\u200e")
        is_system = raw["is_system"]

        is_media, media_type = self._detect_media(content)
        is_deleted = content.strip() in _DELETED_MESSAGES
        is_call = content.strip() in _CALL_MESSAGES
        call_type = _CALL_MESSAGES.get(content.strip())

        return Message(
            datetime=dt,
            sender=raw["sender"],
            content=content,
            is_system=is_system,
            is_media=is_media,
            media_type=media_type,
            is_deleted=is_deleted,
            is_call=is_call,
            call_type=call_type,
        )

    def _parse_datetime(self, date_str: str, time_str: str, date_format: str) -> datetime:
        # Normalize narrow no-break space to regular space
        time_str = time_str.replace("\u202f", " ")
        parts = date_str.split("/")
        if date_format == "DMY":
            day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
        else:  # MDY
            month, day, year = int(parts[0]), int(parts[1]), int(parts[2])

        if year < 100:
            year += 2000

        # Parse time — 12h (AM/PM) or 24h (HH:MM:SS)
        time_str = time_str.strip()
        if ":" in time_str and time_str.count(":") == 2:
            # 24-hour format: HH:MM:SS
            t = datetime.strptime(time_str, "%H:%M:%S")
        else:
            # 12-hour format: H:MM AM/PM
            t = datetime.strptime(time_str, "%I:%M %p")
        return datetime(year, month, day, t.hour, t.minute, t.second)

    def _detect_format(self, lines: list[str]) -> re.Pattern:
        """Detect whether the file uses format A (AM/PM) or format B (brackets, 24h)."""
        for line in lines[:50]:
            if _LINE_RE_A.match(line):
                return _LINE_RE_A
            if _LINE_RE_B.match(line):
                return _LINE_RE_B
        return _LINE_RE_A  # default

    def _detect_date_format(self, lines: list[str]) -> str:
        """Auto-detect MDY vs DMY by scanning date fields for values > 12."""
        first_fields = []
        second_fields = []
        for line in lines[:500]:
            m = self._line_re.match(line)
            if m:
                parts = m.group(1).split("/")
                first_fields.append(int(parts[0]))
                second_fields.append(int(parts[1]))

        first_max = max(first_fields) if first_fields else 0
        second_max = max(second_fields) if second_fields else 0

        if first_max > 12:
            return "DMY"
        if second_max > 12:
            return "MDY"
        # Ambiguous — default to MDY (US WhatsApp default)
        return "MDY"

    def _detect_media(self, content: str) -> tuple[bool, str | None]:
        content = content.strip()
        if content == _MEDIA_OMITTED:
            return True, "unknown"

        # Format B: "sticker omitted", "image omitted", etc.
        om = _OMITTED_RE.match(content)
        if om:
            _omitted_type_map = {
                "sticker": "sticker",
                "image": "image",
                "video": "video",
                "audio": "audio",
                "document": "document",
                "GIF": "image",
                "Contact card": "contact",
            }
            return True, _omitted_type_map.get(om.group(1), "unknown")

        m = _FILE_ATTACHED_RE.match(content)
        if m:
            filename = m.group(1)
            # Check by file extension first
            ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
            if ext == "vcf":
                return True, "contact"
            if ext == "pdf":
                return True, "pdf"
            # Then by WhatsApp prefix
            prefix = filename.split("-")[0].upper() if "-" in filename else ""
            media_type = _MEDIA_PREFIX_MAP.get(prefix, "unknown")
            return True, media_type

        return False, None
