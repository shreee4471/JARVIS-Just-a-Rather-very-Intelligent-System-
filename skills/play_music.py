"""
Voice-triggered music control skill — wraps the same MusicPlayer instance
used by clap detection, so "play music" / "pause music" via voice and a
clap both control the same playback state consistently.
"""

from skills.base_skill import BaseSkill


class PlayMusicSkill(BaseSkill):
    name = "play_music"
    description = (
        "Play, pause, resume, or stop music from the user's local music folder. "
        "Use this when the user asks to play music, pause music, resume music, "
        "or stop the music."
    )
    parameters = {
        "action": {
            "type": "string",
            "description": "One of: 'play', 'pause', 'resume', 'stop'",
        }
    }

    def __init__(self, music_player):
        self.music_player = music_player

    def run(self, action: str) -> str:
        action = action.lower().strip()
        if action in ("play", "resume"):
            return self.music_player.play_random_or_resume()
        if action == "pause":
            return self.music_player.toggle()  # toggle handles pause if playing
        if action == "stop":
            return self.music_player.stop()
        return f"Unknown music action: {action}"
