"""
Skill: world_earthquakes
Fetches recent significant earthquakes from World Monitor (USGS data via seismology API).

Trigger phrases: "earthquakes", "any quakes", "seismic activity",
                 "earthquake today", "recent earthquakes"
"""

from skills.base_skill import BaseSkill
from skills.world_monitor_base import fetch_wm, WorldMonitorUnavailable


class WorldEarthquakesSkill(BaseSkill):
    name = "world_earthquakes"
    description = (
        "Fetch recent earthquake data from World Monitor using USGS seismic data. "
        "Use when the user asks about earthquakes, seismic activity, tremors, or quakes. "
        "Can filter by minimum magnitude or region."
    )
    parameters = {
        "min_magnitude": {
            "type": "string",
            "description": (
                "Minimum earthquake magnitude to report. Default is '4.5'. "
                "Use '6.0' for major quakes only, '2.5' for all activity."
            ),
        },
        "region": {
            "type": "string",
            "description": (
                "Optional region/country to filter by, e.g. 'Japan', 'Turkey', 'California'. "
                "Leave empty for worldwide."
            ),
        },
    }

    def run(self, min_magnitude: str = "4.5", region: str = "") -> str:
        try:
            data = fetch_wm("/api/seismology/v1/ListEarthquakes?pageSize=50")
        except WorldMonitorUnavailable as e:
            return str(e)

        if not data:
            return "Could not retrieve earthquake data from World Monitor."

        earthquakes = data.get("earthquakes", [])
        if not earthquakes:
            return "World Monitor has no earthquake data cached yet. Try again in a moment."

        try:
            min_mag = float(min_magnitude)
        except ValueError:
            min_mag = 4.5

        # Filter by magnitude
        quakes = [
            q for q in earthquakes
            if (q.get("magnitude") or 0) >= min_mag
        ]

        # Filter by region if specified
        if region:
            region_lower = region.lower()
            quakes = [
                q for q in quakes
                if region_lower in (q.get("place") or q.get("location") or "").lower()
            ]

        if not quakes:
            region_str = f" near {region}" if region else ""
            return (
                f"No earthquakes of magnitude {min_mag}+{region_str} in World Monitor's current data."
            )

        # Sort by magnitude descending, take top 5
        quakes = sorted(quakes, key=lambda q: q.get("magnitude") or 0, reverse=True)[:5]

        parts = []
        for q in quakes:
            mag = q.get("magnitude", "?")
            place = q.get("place") or q.get("location") or q.get("region") or "Unknown location"
            # Truncate overly long place names
            if len(place) > 50:
                place = place[:47] + "..."
            parts.append(f"magnitude {mag} near {place}")

        count = len(quakes)
        intro = f"Reporting {count} earthquake{'s' if count > 1 else ''}: "
        return intro + "; ".join(parts) + "."
