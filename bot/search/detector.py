import re

_TRIGGER_KEYWORDS = [
    "latest",
    "current",
    "today",
    "tonight",
    "yesterday",
    "tomorrow",
    "right now",
    "this week",
    "this month",
    "this year",
    "news",
    "update",
    "recent",
    "live",
    "price of",
    "stock price",
    "weather",
    "score",
    "who won",
    "results of",
    "release date",
    "when does",
    "when did",
    "how much is",
    "what happened",
    "trending",
    "breaking",
]

_TRIGGER_PATTERNS = [
    re.compile(r"\b(2024|2025|2026)\b"),
    re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"),
    re.compile(r"\bcurrent(ly)?\b", re.IGNORECASE),
    re.compile(r"\b(latest|newest|most recent)\b", re.IGNORECASE),
    re.compile(r"\btoday'?s?\b", re.IGNORECASE),
    re.compile(r"\bright now\b", re.IGNORECASE),
]


def search_needed(query: str) -> bool:
    """Heuristic check whether a query needs internet search."""
    query_lower = query.lower()

    for keyword in _TRIGGER_KEYWORDS:
        if keyword in query_lower:
            return True

    for pattern in _TRIGGER_PATTERNS:
        if pattern.search(query):
            return True

    return False
