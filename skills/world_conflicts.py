"""
Skill: world_conflicts
Fetches active conflict events from World Monitor (ACLED + UCDP data).

Trigger phrases: "any conflicts", "war updates", "military incidents",
                 "geopolitical events", "battle reports", "armed conflict"
"""

from skills.base_skill import BaseSkill
from skills.world_monitor_base import fetch_wm, WorldMonitorUnavailable


class WorldConflictsSkill(BaseSkill):
    name = "world_conflicts"
    description = (
        "Fetch recent armed conflict and military incident data from World Monitor "
        "using ACLED and UCDP geopolitical data. "
        "Use when the user asks about wars, conflicts, military activity, battles, "
        "explosions, violence against civilians, or geopolitical tensions. "
        "Can filter by country."
    )
    parameters = {
        "country": {
            "type": "string",
            "description": (
                "Optional country to filter conflicts by, e.g. 'Ukraine', 'Sudan', 'Myanmar'. "
                "Leave empty for all countries worldwide."
            ),
        },
    }

    def run(self, country: str = "") -> str:
        # Build query params
        path = "/api/conflict/v1/ListAcledEvents"
        if country:
            # URL-encode the country param
            import urllib.parse
            path += f"?country={urllib.parse.quote(country)}"

        try:
            data = fetch_wm(path)
        except WorldMonitorUnavailable as e:
            return str(e)

        if not data:
            return "Could not retrieve conflict data from World Monitor."

        events = data.get("events", [])
        if not events:
            region_str = f" in {country}" if country else ""
            return f"No recent conflict events reported{region_str} by World Monitor."

        # Sort by most recent (occurredAt desc), take top 5
        events = sorted(events, key=lambda e: e.get("occurredAt") or 0, reverse=True)[:5]

        parts = []
        for ev in events:
            event_type = ev.get("eventType", "Incident")
            location = ev.get("admin1") or ev.get("location") or ""
            ev_country = ev.get("country", "")
            fatalities = ev.get("fatalities", 0)
            actors = ev.get("actors", [])

            place = f"{location}, {ev_country}".strip(", ") if location else ev_country

            desc = f"{event_type} in {place}" if place else event_type
            if fatalities and fatalities > 0:
                desc += f" ({fatalities} fatality{'ies' if fatalities != 1 else 'y'})"
            if actors:
                desc += f" involving {' and '.join(actors[:2])}"
            parts.append(desc)

        count = len(events)
        region_str = f" in {country}" if country else " worldwide"
        intro = f"World Monitor reports {count} recent conflict event{'s' if count > 1 else ''}{region_str}: "
        return intro + "; ".join(parts) + "."
