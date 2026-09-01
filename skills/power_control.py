"""
Power control skill — shutdown, restart, or sleep the PC. These are
destructive/disruptive actions, so this skill requires the LLM to have
already confirmed with the user (the system prompt instructs the model
to always ask "are you sure?" before calling this) and additionally
gives a short delay + cancellable warning via Windows' own shutdown
command, rather than executing instantly with zero recovery window.
"""

import subprocess
import sys
from skills.base_skill import BaseSkill


class PowerControlSkill(BaseSkill):
    name = "control_power"
    description = (
        "Shut down, restart, or put the computer to sleep. This is a "
        "destructive action — ALWAYS ask the user to explicitly confirm "
        "(e.g. 'are you sure you want to shut down?') in your previous "
        "response before calling this tool. Only call this after the "
        "user has clearly confirmed yes."
    )
    parameters = {
        "action": {
            "type": "string",
            "description": "One of: 'shutdown', 'restart', 'sleep'",
        }
    }

    DELAY_SECONDS = 15  # gives a window to cancel via `shutdown /a` if triggered by mistake

    def run(self, action: str) -> str:
        if sys.platform != "win32":
            return "Power control is only implemented for Windows right now."

        action = action.lower().strip()

        try:
            if action == "shutdown":
                subprocess.run(["shutdown", "/s", "/t", str(self.DELAY_SECONDS)], check=True)
                return f"Shutting down in {self.DELAY_SECONDS} seconds. Say 'cancel shutdown' to stop it."
            if action == "restart":
                subprocess.run(["shutdown", "/r", "/t", str(self.DELAY_SECONDS)], check=True)
                return f"Restarting in {self.DELAY_SECONDS} seconds. Say 'cancel shutdown' to stop it."
            if action == "sleep":
                subprocess.run(
                    ["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"], check=True
                )
                return "Going to sleep now."
            if action == "cancel":
                subprocess.run(["shutdown", "/a"], check=True)
                return "Shutdown/restart cancelled."
        except subprocess.CalledProcessError as e:
            return f"Failed to {action}: {e}"

        return f"Unknown power action: {action}"
