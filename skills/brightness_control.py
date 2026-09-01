"""
Screen brightness control using screen-brightness-control.
"""

from skills.base_skill import BaseSkill

try:
    import screen_brightness_control as sbc
    _SBC_AVAILABLE = True
except ImportError:
    _SBC_AVAILABLE = False


class BrightnessControlSkill(BaseSkill):
    name = "control_brightness"
    description = (
        "Control the screen brightness. Use this when the user asks to "
        "change brightness — set it to a percentage, increase it, or "
        "decrease it."
    )
    parameters = {
        "action": {
            "type": "string",
            "description": "One of: 'set', 'up', 'down'",
        },
        "percent": {
            "type": "integer",
            "description": "Brightness percentage 0-100, only used when action is 'set'",
        },
    }

    STEP = 10

    def run(self, action: str, percent=None) -> str:
        if not _SBC_AVAILABLE:
            return "Brightness control isn't available — screen_brightness_control isn't installed."

        action = action.lower().strip()

        if percent is not None:
            try:
                percent = int(percent)
            except (ValueError, TypeError):
                return f"Invalid percent value: {percent!r}"

        try:
            current = sbc.get_brightness(display=0)
            current = current[0] if isinstance(current, list) else current
        except Exception as e:
            return f"Couldn't read current brightness: {e}"

        if action == "set":
            if percent is None:
                return "No percentage given for 'set' action."
            new_value = max(0, min(100, percent))
        elif action == "up":
            new_value = min(100, current + self.STEP)
        elif action == "down":
            new_value = max(0, current - self.STEP)
        else:
            return f"Unknown brightness action: {action}"

        try:
            sbc.set_brightness(new_value)
        except Exception as e:
            return f"Couldn't set brightness: {e}"

        return f"Brightness set to {new_value}%."