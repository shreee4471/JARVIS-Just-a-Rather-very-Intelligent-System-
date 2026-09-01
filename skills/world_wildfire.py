"""
Skill: world_wildfire
Fetches active wildfire detections from World Monitor (NASA FIRMS satellite data).

Trigger phrases: "wildfires", "active fires", "any fires burning",
                 "forest fires", "fire alerts", "wildfire news"
"""

from skills.base_skill import BaseSkill
from skills.world_monitor_base import fetch_wm, WorldMonitorUnavailable


# Region bounding boxes (lat_min, lat_max, lon_min, lon_max)
REGIONS = {
    "california": (32.0, 42.0, -124.5, -114.0),
    "australia":  (-44.0, -10.0, 113.0, 154.0),
    "amazon":     (-20.0, 5.0, -74.0, -44.0),
    "canada":     (49.0, 70.0, -141.0, -52.0),
    "europe":     (36.0, 71.0, -10.0, 40.0),
    "siberia":    (50.0, 72.0, 60.0, 160.0),
    "africa":     (-35.0, 37.0, -18.0, 52.0),
    "india":      (8.0, 37.0, 68.0, 97.0),
    "usa":        (24.0, 50.0, -125.0, -66.0),
}


def _in_region(lat: float, lon: float, region: str) -> bool:
    bounds = REGIONS.get(region.lower())
    if not bounds:
        return True  # unknown region → don't filter
    lat_min, lat_max, lon_min, lon_max = bounds
    return lat_min <= lat <= lat_max and lon_min <= lon <= lon_max


class WorldWildfireSkill(BaseSkill):
    name = "world_wildfire"
    description = (
        "Fetch active wildfire and fire detection data from World Monitor using NASA FIRMS satellite data. "
        "Use when the user asks about wildfires, forest fires, active fires, fire alerts, "
        "or burning areas anywhere in the world."
    )
    parameters = {
        "region": {
            "type": "string",
            "description": (
                "Optional geographic region to filter fires by. Examples: "
                "'California', 'Australia', 'Amazon', 'Canada', 'Europe', 'India'. "
                "Leave empty for worldwide overview."
            ),
        },
    }

    def run(self, region: str = "") -> str:
        try:
            data = fetch_wm("/api/wildfire/v1/ListFireDetections")
        except WorldMonitorUnavailable as e:
            return str(e)

        if not data:
            return "Could not retrieve wildfire data from World Monitor."

        detections = data.get("fireDetections", [])
        if not detections:
            return "World Monitor has no active fire detection data cached yet. Try again shortly."

        # Filter by region if specified
        if region:
            filtered = []
            for d in detections:
                lat = d.get("latitude") or d.get("lat") or 0
                lon = d.get("longitude") or d.get("lon") or 0
                try:
                    lat, lon = float(lat), float(lon)
                except (TypeError, ValueError):
                    continue
                if _in_region(lat, lon, region):
                    filtered.append(d)
            detections = filtered

        total = len(detections)
        if total == 0:
            return f"No active fires detected{f' in {region}' if region else ''} by World Monitor's satellite data."

        # Group by country or region if available
        countries: dict[str, int] = {}
        for d in detections:
            country = d.get("country") or d.get("region") or "Unknown region"
            countries[country] = countries.get(country, 0) + 1

        # Top 5 countries by fire count
        top_countries = sorted(countries.items(), key=lambda x: x[1], reverse=True)[:5]
        breakdown = ", ".join(f"{name} ({count} detection{'s' if count > 1 else ''})"
                              for name, count in top_countries)

        region_str = f" in {region}" if region else " globally"
        return (
            f"World Monitor's satellite data shows {total:,} active fire detections{region_str}. "
            f"Highest concentration: {breakdown}."
        )
