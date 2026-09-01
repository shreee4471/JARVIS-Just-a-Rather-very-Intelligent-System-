"""
Skill: world_news
Fetches the latest global news headlines from World Monitor's RSS digest API.

Trigger phrases: "what's in the news", "latest headlines", "top stories",
                 "any news", "global news", "world news"
"""

from skills.base_skill import BaseSkill
from skills.world_monitor_base import fetch_wm, WorldMonitorUnavailable


class WorldNewsSkill(BaseSkill):
    name = "world_news"
    description = (
        "Fetch the latest global news headlines and top stories from the World Monitor dashboard. "
        "Use when the user asks about current news, headlines, top stories, global events, "
        "or what is happening in the world. Returns a spoken summary of the top headlines."
    )
    parameters = {
        "category": {
            "type": "string",
            "description": (
                "Optional news category to filter by. One of: "
                "'geopolitics', 'military', 'economy', 'technology', 'climate', "
                "'health', 'energy', 'cyber', 'disaster', 'diplomacy', or 'all' for general news. "
                "Default is 'all'."
            ),
        }
    }

    def run(self, category: str = "all") -> str:
        try:
            # World Monitor's news digest endpoint (variant=full for all categories)
            data = fetch_wm("/api/news/v1/ListFeedDigest?variant=full&pageSize=20")
        except WorldMonitorUnavailable as e:
            return str(e)

        if not data:
            return "Could not retrieve news from World Monitor right now."

        # Response shape: { buckets: [{ category, items: [{ title, source, url }] }] }
        # or flat: { items: [...] }
        items = []

        if isinstance(data, dict):
            buckets = data.get("buckets", [])
            if buckets:
                for bucket in buckets:
                    bucket_cat = bucket.get("category", "").lower()
                    if category != "all" and category.lower() not in bucket_cat:
                        continue
                    for item in bucket.get("items", [])[:3]:
                        title = item.get("title") or item.get("headline", "")
                        source = item.get("source", "")
                        if title:
                            items.append(f"{title} ({source})" if source else title)
            else:
                # Flat items list
                for item in data.get("items", [])[:8]:
                    title = item.get("title") or item.get("headline", "")
                    source = item.get("source", "")
                    if title:
                        items.append(f"{title} ({source})" if source else title)

        if not items:
            return "World Monitor returned no news items right now. The news feeds may still be loading."

        # Limit to top 5 for a speakable response
        items = items[:5]
        headline_text = ". ".join(items)
        return f"Here are the latest headlines: {headline_text}."
