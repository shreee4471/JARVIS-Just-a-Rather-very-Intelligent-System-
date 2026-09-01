"""
Skill: world_cyber
Fetches recent cyber threat intelligence from World Monitor.

Trigger phrases: "any cyberattacks", "cyber threats", "hacking incidents",
                 "ransomware", "data breaches", "cyber security news"
"""

from skills.base_skill import BaseSkill
from skills.world_monitor_base import fetch_wm, WorldMonitorUnavailable


class WorldCyberSkill(BaseSkill):
    name = "world_cyber"
    description = (
        "Fetch recent cybersecurity threat intelligence from World Monitor including "
        "malware, ransomware, DDoS attacks, data breaches, and nation-state cyber activity. "
        "Use when the user asks about cyberattacks, cyber threats, hacking, ransomware, "
        "data breaches, cybersecurity incidents, or digital security news."
    )
    parameters = {
        "severity": {
            "type": "string",
            "description": (
                "Minimum severity level to report. Options: 'low', 'medium', 'high', 'critical'. "
                "Default is 'high' to filter out noise."
            ),
        },
    }

    def run(self, severity: str = "high") -> str:
        try:
            data = fetch_wm("/api/cyber/v1/ListCyberThreats?pageSize=20")
        except WorldMonitorUnavailable as e:
            return str(e)

        if not data:
            return "Could not retrieve cyber threat data from World Monitor."

        threats = data.get("threats", [])
        if not threats:
            return "World Monitor has no cyber threat data cached. Try again shortly."

        # Severity ranking for filtering
        RANK = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        min_rank = RANK.get(severity.lower(), 3)

        filtered = [
            t for t in threats
            if RANK.get((t.get("severity") or "").lower().replace("criticality_level_", ""), 0) >= min_rank
        ]

        if not filtered:
            filtered = threats  # fallback: show all if none match severity

        # Take top 5
        top = filtered[:5]
        parts = []
        for t in top:
            title = t.get("title") or t.get("name") or t.get("indicator") or "Unknown threat"
            sev = (t.get("severity") or "").replace("CRITICALITY_LEVEL_", "").title()
            threat_type = (t.get("type") or "").replace("CYBER_THREAT_TYPE_", "").replace("_", " ").title()
            source = t.get("source") or ""

            desc = title
            if threat_type and threat_type.lower() not in ("unspecified", ""):
                desc += f" ({threat_type})"
            if sev and sev.lower() not in ("unspecified", ""):
                desc += f" — severity: {sev}"
            parts.append(desc)

        count = len(top)
        return (
            f"World Monitor reports {count} notable cyber threat{'s' if count > 1 else ''}: "
            + "; ".join(parts) + "."
        )
