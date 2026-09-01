"""
Real-time web search using Tavily's free API (1,000 searches/month, no card required).
"""

import os
import requests
from skills.base_skill import BaseSkill


class WebSearchSkill(BaseSkill):
    name = "web_search"
    description = (
        "Search the web and return real, current results as text. "
        "Use this tool for general web searches, weather, sports scores, and random facts. "
        "DO NOT use this tool for global news headlines, financial market prices (stocks/crypto/commodities), "
        "earthquakes, military conflicts, cyber threats, or wildfires — use the specific 'world_*' skills for those instead. "
        "Your own training data has a cutoff date and is NOT reliable for time-sensitive queries, "
        "so rely on tools for current information."
    )
    parameters = {
        "query": {
            "type": "string",
            "description": "What to search for, e.g. 'current president of the United States'",
        }
    }

    API_URL = "https://api.tavily.com/search"

    def run(self, query: str, max_results: int = 4) -> str:
        api_key = os.environ.get("TAVILY_API_KEY")
        if not api_key:
            return (
                "Web search is not configured — TAVILY_API_KEY environment "
                "variable is missing. Set it and restart Jarvis."
            )

        try:
            resp = requests.post(
                self.API_URL,
                json={
                    "api_key": api_key,
                    "query": query,
                    "max_results": max_results,
                    "include_answer": True,
                },
                timeout=15,
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            return f"Search failed due to a network error: {e}"

        data = resp.json()
        lines = [f"Search results for '{query}':"]

        answer = data.get("answer")
        if answer:
            lines.append(f"Quick answer: {answer}")

        for r in data.get("results", [])[:max_results]:
            title = r.get("title", "")
            content = r.get("content", "")
            if title or content:
                lines.append(f"- {title}: {content[:300]}")

        if len(lines) == 1:
            return f"No search results found for '{query}'."

        return "\n".join(lines)