"""
Text-to-speech using Piper (fast, local, free, sounds decent).
Piper outputs raw audio which we play immediately via sounddevice.

Setup note: you need the piper executable + a voice model (.onnx + .onnx.json)
downloaded locally. See README for the one-time download step.
"""

import subprocess
import numpy as np
import sounddevice as sd


class TTS:
    def __init__(self, config: dict):
        tts_cfg = config["tts"]
        self.voice = tts_cfg["voice"]
        self.sample_rate = 22050  # standard piper output rate for most voices
        self.model_path = f"models/piper/{self.voice}.onnx"

    def speak(self, text: str):
        if not text:
            return
        print(f"[Jarvis]: {text}")

        # Run piper as a subprocess: text in via stdin, raw audio out via stdout
        proc = subprocess.run(
            ["piper\\piper.exe", "--model", self.model_path, "--output-raw"],
            input=text.encode("utf-8"),
            capture_output=True,
        )
        if proc.returncode != 0:
            print(f"[TTS] Piper error: {proc.stderr.decode()}")
            return

        audio = np.frombuffer(proc.stdout, dtype=np.int16)
        sd.play(audio, samplerate=self.sample_rate)
        sd.wait()

    def generate_audio_bytes(self, text: str) -> bytes | None:
        if not text:
            return None
        
        proc = subprocess.run(
            ["piper\\piper.exe", "--model", self.model_path, "--output-raw"],
            input=text.encode("utf-8"),
            capture_output=True,
        )
        if proc.returncode != 0:
            print(f"[TTS] Piper error: {proc.stderr.decode()}")
            return None

        # Piper outputs raw 16-bit PCM. We need to wrap it in a WAV header for the browser.
        import io
        import wave
        
        raw_audio = proc.stdout
        wav_io = io.BytesIO()
        with wave.open(wav_io, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2) # 16-bit
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(raw_audio)
            
        return wav_io.getvalue()

