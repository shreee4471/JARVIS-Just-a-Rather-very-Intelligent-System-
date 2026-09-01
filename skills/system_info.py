"""
System info skill — battery percentage, RAM usage, disk space, using psutil
(cross-platform, no extra Windows-specific dependency needed).
"""

from skills.base_skill import BaseSkill

try:
    import psutil
    _PSUTIL_AVAILABLE = True
except ImportError:
    _PSUTIL_AVAILABLE = False


class SystemInfoSkill(BaseSkill):
    name = "get_system_info"
    description = (
        "Get information about the computer's current state: battery "
        "percentage, RAM/memory usage, or disk space. Use this when the "
        "user asks about battery level, how much memory or disk space "
        "is free/used, or general system status."
    )
    parameters = {
        "info_type": {
            "type": "string",
            "description": "One of: 'battery', 'memory', 'disk', 'all'",
        }
    }

    def run(self, info_type: str) -> str:
        if not _PSUTIL_AVAILABLE:
            return "System info isn't available — psutil isn't installed."

        info_type = info_type.lower().strip()
        parts = []

        if info_type in ("battery", "all"):
            battery = psutil.sensors_battery()
            if battery:
                status = "charging" if battery.power_plugged else "on battery"
                parts.append(f"Battery is at {round(battery.percent)}% ({status}).")
            else:
                parts.append("No battery detected (likely a desktop).")

        if info_type in ("memory", "all"):
            mem = psutil.virtual_memory()
            used_gb = mem.used / (1024 ** 3)
            total_gb = mem.total / (1024 ** 3)
            parts.append(f"Memory: {used_gb:.1f} GB used of {total_gb:.1f} GB ({mem.percent}%).")

        if info_type in ("disk", "all"):
            disk = psutil.disk_usage("C:\\" if _is_windows() else "/")
            used_gb = disk.used / (1024 ** 3)
            total_gb = disk.total / (1024 ** 3)
            parts.append(f"Disk: {used_gb:.1f} GB used of {total_gb:.1f} GB ({disk.percent}%).")

        if not parts:
            return f"Unknown info type: {info_type}"

        return " ".join(parts)


def _is_windows() -> bool:
    import sys
    return sys.platform == "win32"
