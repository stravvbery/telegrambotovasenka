from __future__ import annotations

from typing import Any

from bot.search.detector import search_needed
from bot.search.manager import SearchManager


def get_search_tool_schema() -> dict[str, Any]:
    """Return the web_search tool schema in OpenAI function-calling format."""
    return {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the internet for current information about a topic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to look up on the internet.",
                    }
                },
                "required": ["query"],
            },
        },
    }


def get_gemini_search_tool() -> dict[str, Any]:
    """Return Google format tool declaration for Gemini's built-in google_search."""
    return {"google_search": {}}


class ToolExecutor:
    def __init__(self, search_manager: SearchManager) -> None:
        self.search_manager = search_manager

    async def execute_tool_calls(self, tool_calls: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Execute search tool calls and return results for the next LLM turn."""
        results: list[dict[str, Any]] = []
        for call in tool_calls:
            func_name = call.get("function", {}).get("name", "")
            if func_name == "web_search":
                import json

                args = call.get("function", {}).get("arguments", "{}")
                if isinstance(args, str):
                    args = json.loads(args)
                query = args.get("query", "")
                search_results = await self.search_manager.search(query)
                formatted = SearchManager.format_results(search_results)
                results.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.get("id", ""),
                        "name": func_name,
                        "content": formatted,
                    }
                )
            else:
                results.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.get("id", ""),
                        "name": func_name,
                        "content": f"Unknown tool: {func_name}",
                    }
                )
        return results


async def enhance_with_search(query: str, search_manager: SearchManager) -> str:
    """For models without tool support: perform search if needed, return context string."""
    if not search_needed(query):
        return ""
    results = await search_manager.search(query)
    formatted = SearchManager.format_results(results)
    if not formatted:
        return ""
    return (
        "Here is relevant information from the internet:\n\n"
        f"{formatted}\n\n"
        "Use the above information to answer the user's question.\n"
    )
