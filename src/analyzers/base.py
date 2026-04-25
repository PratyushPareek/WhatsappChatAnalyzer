from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from src.models.chat import Chat


@dataclass
class AnalysisResult:
    section_id: str
    title: str
    stats: dict = field(default_factory=dict)
    chart_data: dict | None = None
    appendix: dict | None = None


class IAnalyzer(ABC):
    @abstractmethod
    def analyze(self, chat: Chat) -> AnalysisResult:
        ...
