"""
Music player controller — plays/pauses/resumes tracks from a user-specified
folder using pygame's mixer. Designed to be driven by the clap detector
(single clap = toggle play/pause) but also usable as a normal Jarvis skill
("play music", "pause music") via voice.

State (which track was last playing) persists only for the current run —
if Jarvis restarts, it picks a fresh random track on first play, same as
the "no last-played track" case.
"""

import os
import random
import pygame


class MusicPlayer:
    def __init__(self, config: dict):
        music_cfg = config.get("music", {})
        self.music_folder = music_cfg.get("folder")
        self.supported_extensions = (".mp3", ".wav", ".ogg")

        pygame.mixer.init()
        self._current_track = None  # absolute path of the last-loaded track
        self._is_loaded = False

    def _get_track_list(self) -> list[str]:
        if not self.music_folder or not os.path.isdir(self.music_folder):
            return []
        return [
            os.path.join(self.music_folder, f)
            for f in os.listdir(self.music_folder)
            if f.lower().endswith(self.supported_extensions)
        ]

    def toggle(self) -> str:
        """
        Single entry point for clap-triggered behavior:
        - If music is currently playing -> pause it
        - If paused -> resume it
        - If nothing loaded yet -> pick last played (none yet, so random) and play
        Returns a short status string for logging/speech.
        """
        if self._is_loaded and pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            return "Music paused."

        if self._is_loaded and not pygame.mixer.music.get_busy():
            pygame.mixer.music.unpause()
            return "Resuming music."

        # Nothing loaded yet this session — pick a track and start fresh
        return self.play_random_or_resume()

    def play_random_or_resume(self) -> str:
        tracks = self._get_track_list()
        if not tracks:
            return f"No music files found in {self.music_folder or '(no folder configured)'}."

        track = self._current_track if self._current_track in tracks else random.choice(tracks)
        self._current_track = track
        pygame.mixer.music.load(track)
        pygame.mixer.music.play()
        self._is_loaded = True
        return f"Playing {os.path.basename(track)}."

    def stop(self) -> str:
        pygame.mixer.music.stop()
        self._is_loaded = False
        return "Music stopped."
