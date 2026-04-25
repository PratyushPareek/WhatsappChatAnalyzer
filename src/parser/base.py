from abc import ABC, abstractmethod

from src.models.chat import Chat


class IChatParser(ABC):
    @abstractmethod
    def parse(self, file_path: str) -> Chat:
        ...
