from abc import ABC, abstractmethod

from src.analyzers.base import AnalysisResult


class IReportGenerator(ABC):
    @abstractmethod
    def generate(self, results: list[AnalysisResult], chart_paths: dict[str, list[str]],
                 metadata: dict) -> str:
        """Assemble the final report. Returns the output file path."""
        ...
