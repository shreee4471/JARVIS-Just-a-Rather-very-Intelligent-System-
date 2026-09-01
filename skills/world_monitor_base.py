"""
Shared base helper for World Monitor API integration.

World Monitor must be running locally:
  cd worldmonitor && npm run dev   (starts at localhost:3000)

All World Monitor skills import `fetch_wm` from here.
"""

import urllib.request
import urllib.error
import json
import yaml
import os


def _load_base_url() -> str:
    """Read base_url from config.yaml, fallback to localhost:3000."""
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
    try:
        with open(config_path) as f:
            cfg = yaml.safe_load(f)
        return cfg.get("world_monitor", {}).get("base_url", "http://localhost:3000")
    except Exception:
        return "http://localhost:3000"


WM_BASE_URL = _load_base_url()

_NOT_RUNNING_MSG = (
    "World Monitor is not running. "
    "Please start it with: cd worldmonitor && npm run dev"
)


def fetch_wm(path: str, timeout: int = 8) -> dict | list | None:
    """
    GET {WM_BASE_URL}{path} and return parsed JSON.

    Returns None on any error (connection refused, timeout, bad JSON).
    Raises WorldMonitorUnavailable if the server is not reachable.
    """
    url = f"{WM_BASE_URL}{path}"
    try:
        req = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json",
                "Origin": "http://localhost:3000",
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body)
    except urllib.error.URLError as e:
        if "refused" in str(e).lower() or "connect" in str(e).lower():
            raise WorldMonitorUnavailable(_NOT_RUNNING_MSG) from e
        return None
    except Exception:
        return None


class WorldMonitorUnavailable(RuntimeError):
    """Raised when World Monitor server is not reachable."""
