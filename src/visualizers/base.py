from abc import ABC, abstractmethod


class IVisualizer(ABC):
    @abstractmethod
    def create_chart(self, chart_type: str, data: dict, title: str, **kwargs) -> str:
        """Generate a chart image and return the file path."""
        ...
