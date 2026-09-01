"""
Screenshot skill — captures the current screen and saves it to a
Screenshots folder, using pillow's ImageGrab (no extra Windows-specific
dependency needed beyond Pillow, which is lightweight and commonly already
installed).
"""

import os
from datetime import datetime
from skills.base_skill import BaseSkill

try:
    from PIL import ImageGrab
    _PIL_AVAILABLE = True
except ImportError:
    _PIL_AVAILABLE = False


class ScreenshotSkill(BaseSkill):
    name = "take_screenshot"
    description = (
        "Take a screenshot of the current screen and save it. Use this "
        "when the user asks to take a screenshot, capture the screen, "
        "or grab an image of what's currently displayed."
    )
    parameters = {}

    def run(self) -> str:
        if not _PIL_AVAILABLE:
            return "Screenshot isn't available — Pillow isn't installed."

        screenshots_dir = os.path.join(os.path.expanduser("~"), "Pictures", "Screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filepath = os.path.join(screenshots_dir, f"jarvis_screenshot_{timestamp}.png")

        try:
            image = ImageGrab.grab()
            image.save(filepath)
        except Exception as e:
            return f"Failed to take screenshot: {e}"

        return f"Screenshot saved to {filepath}."
