"""
Reminders/timers skill — sets a timer for N minutes/seconds, or a reminder
with a message, and speaks it aloud via the shared TTS instance when it
fires.
"""

import threading
from skills.base_skill import BaseSkill


class ReminderSkill(BaseSkill):
    name = "set_reminder"
    description = (
        "Set a timer or reminder that will speak a message after a delay. "
        "Use this when the user asks to be reminded of something, or to "
        "set a timer (e.g. 'remind me to check the oven in 10 minutes', "
        "'set a timer for 5 minutes')."
    )
    parameters = {
        "minutes": {
            "type": "number",
            "description": "How many minutes from now to fire the reminder (can be fractional, e.g. 0.5 for 30 seconds)",
        },
        "message": {
            "type": "string",
            "description": "What to say when the reminder fires, e.g. 'check the oven'",
        },
    }

    def __init__(self, tts):
        self.tts = tts

    def run(self, minutes, message: str) -> str:
        try:
            minutes = float(minutes)
        except (TypeError, ValueError):
            return f"Invalid minutes value: {minutes!r}"

        seconds = max(1, minutes * 60)

        def fire():
            self.tts.speak(f"Reminder: {message}")

        timer = threading.Timer(seconds, fire)
        timer.daemon = True
        timer.start()

        if minutes >= 1:
            time_desc = f"{minutes:.0f} minute(s)" if minutes == int(minutes) else f"{minutes:.1f} minutes"
        else:
            time_desc = f"{int(seconds)} seconds"

        return f"Okay, I'll remind you about '{message}' in {time_desc}."