from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from src.models.message import Message


@dataclass
class Chat:
    messages: list[Message]
    participants: list[str]
    source_file: str
    date_range: tuple[datetime, datetime]
