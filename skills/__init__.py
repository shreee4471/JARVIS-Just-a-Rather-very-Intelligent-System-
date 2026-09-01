"""
Central skill registry.
"""

from skills.open_app import OpenAppSkill
from skills.web_search import WebSearchSkill
from skills.play_music import PlayMusicSkill
from skills.youtube_play import YouTubePlaySkill
from skills.volume_control import VolumeControlSkill
from skills.brightness_control import BrightnessControlSkill
from skills.system_info import SystemInfoSkill
from skills.file_search import FileSearchSkill
from skills.screenshot import ScreenshotSkill
from skills.datetime_info import DateTimeSkill
from skills.reminders import ReminderSkill
from skills.power_control import PowerControlSkill
from skills.write_code import WriteCodeSkill

# World Monitor integration skills
from skills.world_news import WorldNewsSkill
from skills.world_markets import WorldMarketsSkill
from skills.world_earthquakes import WorldEarthquakesSkill
from skills.world_conflicts import WorldConflictsSkill
from skills.world_cyber import WorldCyberSkill
from skills.world_wildfire import WorldWildfireSkill

_ALL_SKILLS = []
_SKILLS_BY_NAME = {}


def build_registry(music_player=None, tts=None, llm_base_url=None, llm_model=None):
    global _ALL_SKILLS, _SKILLS_BY_NAME

    skills = [
        OpenAppSkill(),
        WebSearchSkill(),
        YouTubePlaySkill(),
        VolumeControlSkill(),
        BrightnessControlSkill(),
        SystemInfoSkill(),
        FileSearchSkill(),
        ScreenshotSkill(),
        DateTimeSkill(),
        PowerControlSkill(),
        # World Monitor skills
        WorldNewsSkill(),
        WorldMarketsSkill(),
        WorldEarthquakesSkill(),
        WorldConflictsSkill(),
        WorldCyberSkill(),
        WorldWildfireSkill(),
    ]

    if music_player is not None:
        skills.append(PlayMusicSkill(music_player))
    if tts is not None:
        skills.append(ReminderSkill(tts))
    if llm_base_url and llm_model:
        skills.append(WriteCodeSkill(llm_base_url, llm_model))

    _ALL_SKILLS = skills
    _SKILLS_BY_NAME = {skill.name: skill for skill in skills}


def get_tool_schemas() -> list[dict]:
    return [skill.to_tool_schema() for skill in _ALL_SKILLS]


def run_skill(name: str, **kwargs) -> str:
    skill = _SKILLS_BY_NAME.get(name)
    if not skill:
        return f"Unknown skill: {name}"
    return skill.run(**kwargs)