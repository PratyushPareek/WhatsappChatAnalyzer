from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class Message:
    datetime: datetime
    sender: str
    content: str
    is_system: bool = False
    is_media: bool = False
    media_type: str | None = None
    is_deleted: bool = False
    is_call: bool = False
    call_type: str | None = None
