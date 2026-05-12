from bot.config import Settings
from bot.search import SearchResult
from bot.search.firecrawl import FirecrawlSearch
from bot.search.serpapi import SerpAPISearch
from bot.search.tavily import TavilySearch


class SearchManager:
    def __init__(self, settings: Settings) -> None:
        self.tavily = TavilySearch(settings.tavily_api_key)
        self.serpapi = SerpAPISearch(settings.serpapi_key)
        self.firecrawl = FirecrawlSearch(settings.firecrawl_api_key)

    async def search(self, query: str) -> list[SearchResult]:
        """Try Tavily first, fall back to SerpAPI on error."""
        try:
            return await self.tavily.search(query)
        except Exception:
            return await self.serpapi.search(query)

    async def scrape_url(self, url: str) -> str:
        """Scrape a specific URL using Firecrawl."""
        return await self.firecrawl.scrape_url(url)

    @staticmethod
    def format_results(results: list[SearchResult]) -> str:
        """Format search results into concise text for LLM context."""
        if not results:
            return ""
        lines: list[str] = []
        for i, r in enumerate(results, 1):
            lines.append(f"{i}. {r.title}")
            lines.append(f"   URL: {r.url}")
            lines.append(f"   {r.snippet}")
            lines.append("")
        return "\n".join(lines).strip()
