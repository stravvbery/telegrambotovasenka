import aiohttp

from bot.search import BaseSearchProvider, SearchResult


class TavilySearch(BaseSearchProvider):
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.url = "https://api.tavily.com/search"

    async def search(self, query: str) -> list[SearchResult]:
        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": "basic",
            "max_results": 5,
        }
        timeout = aiohttp.ClientTimeout(total=30)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(self.url, json=payload) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
        except (aiohttp.ClientError, TimeoutError) as exc:
            raise RuntimeError(f"Tavily search failed: {exc}") from exc

        results: list[SearchResult] = []
        for item in data.get("results", []):
            results.append(
                SearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    snippet=item.get("content", ""),
                    content=item.get("raw_content"),
                )
            )
        return results
