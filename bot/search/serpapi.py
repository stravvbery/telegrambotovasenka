import aiohttp

from bot.search import BaseSearchProvider, SearchResult


class SerpAPISearch(BaseSearchProvider):
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.url = "https://serpapi.com/search"

    async def search(self, query: str) -> list[SearchResult]:
        params = {
            "q": query,
            "api_key": self.api_key,
            "engine": "google",
        }
        timeout = aiohttp.ClientTimeout(total=30)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(self.url, params=params, timeout=timeout) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
        except (aiohttp.ClientError, TimeoutError) as exc:
            raise RuntimeError(f"SerpAPI search failed: {exc}") from exc

        results: list[SearchResult] = []
        for item in data.get("organic_results", []):
            results.append(
                SearchResult(
                    title=item.get("title", ""),
                    url=item.get("link", ""),
                    snippet=item.get("snippet", ""),
                    content=None,
                )
            )
        return results
