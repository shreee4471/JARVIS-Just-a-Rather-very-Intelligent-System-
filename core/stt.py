"""
Speech-to-text using faster-whisper. Records from mic until silence is detected,
then transcribes. Runs on GPU (cuda) if available, falls back to CPU.
"""

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel


class STT:
    def __init__(self, config: dict):
        stt_cfg = config["stt"]
        audio_cfg = config["audio"]
        self.sample_rate = audio_cfg["sample_rate"]
        self.silence_threshold = audio_cfg["silence_threshold"]
        self.silence_duration = audio_cfg["silence_duration"]

        print(f"[STT] Loading faster-whisper ({stt_cfg['model_size']}) on {stt_cfg['device']}...")
        self.model = WhisperModel(
            stt_cfg["model_size"],
            device=stt_cfg["device"],
            compute_type=stt_cfg["compute_type"],
        )
        print("[STT] Ready.")

    def record_until_silence(self) -> np.ndarray:
        """Records audio from the default mic until silence_duration seconds of quiet."""
        block_duration = 0.1  # seconds per chunk
        block_size = int(self.sample_rate * block_duration)
        silence_blocks_needed = int(self.silence_duration / block_duration)

        buffer = []
        silent_blocks = 0
        started_talking = False

        print("[STT] Listening...")
        with sd.InputStream(samplerate=self.sample_rate, channels=1, dtype="int16") as stream:
            while True:
                block, _ = stream.read(block_size)
                volume = np.abs(block).mean()
                buffer.append(block)

                if volume > self.silence_threshold:
                    started_talking = True
                    silent_blocks = 0
                elif started_talking:
                    silent_blocks += 1
                    if silent_blocks >= silence_blocks_needed:
                        break

        audio = np.concatenate(buffer, axis=0).flatten().astype(np.float32) / 32768.0
        return audio

    def transcribe(self, audio: np.ndarray) -> str:
        segments, _ = self.model.transcribe(audio, language="en")
        text = " ".join(seg.text.strip() for seg in segments)
        return text.strip()

    def transcribe_bytes(self, wav_bytes: bytes) -> str:
        import io
        
        # faster-whisper accepts file-like objects directly
        audio_io = io.BytesIO(wav_bytes)
        segments, _ = self.model.transcribe(audio_io, language="en")
        text = " ".join(seg.text.strip() for seg in segments)
        return text.strip()

    def listen(self) -> str:
        audio = self.record_until_silence()
        return self.transcribe(audio)
