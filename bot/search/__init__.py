from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    content: Optional[str] = field(default=None)


class BaseSearchProvider(ABC):
    @abstractmethod
    async def search(self, query: str) -> list[SearchResult]:
        ...
