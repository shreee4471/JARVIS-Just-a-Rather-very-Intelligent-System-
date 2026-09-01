"""
System volume control using pycaw (Windows Core Audio API wrapper).
"""

from skills.base_skill import BaseSkill

try:
    from pycaw.pycaw import AudioUtilities
    _PYCAW_AVAILABLE = True
except ImportError:
    _PYCAW_AVAILABLE = False


class VolumeControlSkill(BaseSkill):
    name = "control_volume"
    description = (
        "Control the system volume. Use this when the user asks to change "
        "volume — set it to a percentage, turn it up, turn it down, mute, "
        "or unmute."
    )
    parameters = {
        "action": {
            "type": "string",
            "description": "One of: 'set', 'up', 'down', 'mute', 'unmute'",
        },
        "percent": {
            "type": "integer",
            "description": "Volume percentage 0-100, only used when action is 'set'",
        },
    }

    STEP = 10

    def _get_volume_interface(self):
        device = AudioUtilities.GetSpeakers()
        return device.EndpointVolume

    def run(self, action: str, percent=None) -> str:
        if not _PYCAW_AVAILABLE:
            return "Volume control isn't available — pycaw isn't installed."

        if percent is not None:
            try:
                percent = int(percent)
            except (TypeError, ValueError):
                return f"Invalid percent value: {percent!r}"

        try:
            volume = self._get_volume_interface()
        except Exception as e:
            return f"Couldn't access the system volume interface: {e}"

        action = action.lower().strip()

        if action == "mute":
            volume.SetMute(1, None)
            return "Muted."
        if action == "unmute":
            volume.SetMute(0, None)
            return "Unmuted."

        current_scalar = volume.GetMasterVolumeLevelScalar()
        current_percent = round(current_scalar * 100)

        if action == "set":
            if percent is None:
                return "No percentage given for 'set' action."
            new_percent = max(0, min(100, percent))
        elif action == "up":
            new_percent = min(100, current_percent + self.STEP)
        elif action == "down":
            new_percent = max(0, current_percent - self.STEP)
        else:
            return f"Unknown volume action: {action}"

        volume.SetMasterVolumeLevelScalar(new_percent / 100.0, None)
        return f"Volume set to {new_percent}%."