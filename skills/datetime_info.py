"""
Date/time skill — current date, time, day of week, timezone. Pure Python
standard library, no dependencies.
"""

from datetime import datetime
from skills.base_skill import BaseSkill


class DateTimeSkill(BaseSkill):
    name = "get_datetime"
    description = (
        "Get the current date, time, day of the week, or timezone. Use "
        "this when the user asks what time it is, what day it is, or "
        "today's date."
    )
    parameters = {
        "info_type": {
            "type": "string",
            "description": "One of: 'time', 'date', 'day', 'all'",
        }
    }

    def run(self, info_type: str) -> str:
        now = datetime.now()
        info_type = info_type.lower().strip()

        if info_type == "time":
            return f"It's currently {now.strftime('%I:%M %p')}."
        if info_type == "date":
            return f"Today's date is {now.strftime('%B %d, %Y')}."
        if info_type == "day":
            return f"Today is {now.strftime('%A')}."
        if info_type == "all":
            return f"It's {now.strftime('%A, %B %d, %Y')} at {now.strftime('%I:%M %p')}."

        return f"Unknown info type: {info_type}"
