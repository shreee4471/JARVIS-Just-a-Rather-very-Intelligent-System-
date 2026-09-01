"""
YouTube playback skill — searches YouTube and opens the top result directly
in the browser, auto-playing. Uses YouTube's own search-results page (no
API key required, no quota limits) and parses the first video ID out of
the page so we can jump straight to /watch?v=... instead of just opening
a generic search results page.
"""

import re
import webbrowser
import urllib.parse
import requests
from skills.base_skill import BaseSkill


class YouTubePlaySkill(BaseSkill):
    name = "play_youtube_video"
    description = (
        "Search YouTube for a video and play it by opening it in the browser. "
        "Use this when the user asks to play a specific video, song, or content "
        "on YouTube (e.g. 'play Bohemian Rhapsody on youtube', 'play the trailer "
        "for the new Batman movie')."
    )
    parameters = {
        "query": {
            "type": "string",
            "description": "What to search for and play, e.g. 'Bohemian Rhapsody Queen official video'",
        }
    }

    SEARCH_URL = "https://www.youtube.com/results"
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
    }

    def run(self, query: str) -> str:
        search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"

        try:
            resp = requests.get(search_url, headers=self.HEADERS, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as e:
            # Fall back to just opening the search page if the request itself fails
            webbrowser.open(search_url)
            return f"Couldn't fetch results directly ({e}), opened the YouTube search page instead."

        # YouTube embeds video IDs in the page as "videoId":"XXXXXXXXXXX"
        match = re.search(r'"videoId":"([a-zA-Z0-9_-]{11})"', resp.text)

        if match:
            video_id = match.group(1)
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            webbrowser.open(video_url)
            return f"Playing '{query}' on YouTube."

        # No video ID found — fall back to opening the search results page itself
        webbrowser.open(search_url)
        return f"Couldn't find a direct video match, opened YouTube search results for '{query}' instead."
