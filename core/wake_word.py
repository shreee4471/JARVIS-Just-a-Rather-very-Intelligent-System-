"""
Wake word detection using openWakeWord's pre-trained "hey jarvis" model.
Runs a lightweight continuous listener on the mic; only when the wake
phrase is detected does this hand control back to the main loop (which
then triggers the heavier Whisper transcription + LLM pipeline).

This keeps Jarvis idle/cheap most of the time — Whisper and the LLM are
only invoked after the wake word fires, not continuously.
"""

import numpy as np
import sounddevice as sd
import openwakeword
from openwakeword.model import Model


class WakeWordListener:
    def __init__(self, config: dict):
        ww_cfg = config.get("wake_word", {})
        self.sample_rate = 16000
        self.chunk_size = 1280
        self.threshold = ww_cfg.get("threshold", 0.5)
        self.model_name = ww_cfg.get("model", "hey_jarvis_v0.1")

        print("[WakeWord] Checking for required model files...")
        openwakeword.utils.download_models()

        print(f"[WakeWord] Loading model '{self.model_name}'...")
        self.model = Model(wakeword_models=[self.model_name], inference_framework="onnx")
        print("[WakeWord] Ready, listening for 'Hey Jarvis'...")

    def listen_for_wake_word(self) -> bool:
        """
        Blocks until the wake word is detected, then returns True.
        Runs continuously in small audio chunks to stay lightweight.
        """
        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="int16",
            blocksize=self.chunk_size,
        ) as stream:
            while True:
                audio_chunk, _ = stream.read(self.chunk_size)
                audio_chunk = audio_chunk.flatten()

                prediction = self.model.predict(audio_chunk)
                score = prediction.get(self.model_name, 0.0)

                if score > self.threshold:
                    print(f"[WakeWord] Detected! (score={score:.2f})")
                    self.model.reset()  # clear internal state before next listen cycle
                    return True
