import aiohttp


class FirecrawlSearch:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.url = "https://api.firecrawl.dev/v1/scrape"

    async def scrape_url(self, url: str) -> str:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {"url": url}
        timeout = aiohttp.ClientTimeout(total=30)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.url, json=payload, headers=headers
                ) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
        except (aiohttp.ClientError, TimeoutError) as exc:
            raise RuntimeError(f"Firecrawl scrape failed: {exc}") from exc

        return data.get("data", {}).get("markdown", "") or data.get("data", {}).get(
            "content", ""
        )
