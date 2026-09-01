"""
Jarvis main loop: wake word -> listen -> transcribe -> think -> speak. Repeat.
Clap detection runs independently in the background for music control.

Run with: python main.py
Press Ctrl+C to stop.
"""

import os
import sys


def _add_cuda_dll_paths():
    """
    faster-whisper (via CTranslate2) needs CUDA 12.x's cublas/cudnn DLLs.
    Rather than relying on a system-wide CUDA Toolkit install (version
    mismatches are a common headache on Windows), we point directly at
    the DLLs shipped inside the nvidia-cublas-cu12 / nvidia-cudnn-cu12
    pip packages installed in this venv. In current package versions the
    DLLs live in a `bin/` folder under the package root (no importable
    `.lib` submodule), so we find the package root and look in `bin/`.
    """
    if sys.platform != "win32":
        return

    packages = [("nvidia.cublas", "cublas"), ("nvidia.cudnn", "cudnn")]
    for package_name, label in packages:
        try:
            pkg = __import__(package_name, fromlist=["__path__"])
            for root in pkg.__path__:
                bin_dir = os.path.join(root, "bin")
                if os.path.isdir(bin_dir):
                    os.add_dll_directory(bin_dir)
                    os.environ["PATH"] = bin_dir + os.pathsep + os.environ["PATH"]
                    print(f"[CUDA] Loaded {label} DLLs from {bin_dir}")
                    break
            else:
                print(f"[WARN] No bin/ folder found under {package_name} at {list(pkg.__path__)}")
        except ImportError as e:
            print(f"[WARN] Failed to import {package_name}: {e}")
        except Exception as e:
            print(f"[WARN] Unexpected error loading {label} DLLs: {e}")


_add_cuda_dll_paths()

import yaml
from core.brain import Brain
from core.stt import STT
from core.tts import TTS
from core.wake_word import WakeWordListener
from core.clap_detector import ClapDetector
from music_player import MusicPlayer
from skills import build_registry


def load_config(path="config.yaml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def main():
    config = load_config()

    print("Initializing Jarvis...")

    music_player = MusicPlayer(config)
    tts = TTS(config)
    build_registry(
    music_player=music_player,
    tts=tts,
    llm_base_url=config["llm"]["base_url"],
    llm_model=config["llm"]["model"],
)
    brain = Brain(config)
    stt = STT(config)

    wake_word_enabled = config.get("wake_word", {}).get("enabled", True)
    wake_listener = WakeWordListener(config) if wake_word_enabled else None

    clap_enabled = config.get("clap_detection", {}).get("enabled", True)
    clap_detector = None
    if clap_enabled:
        clap_detector = ClapDetector(config, on_clap=lambda: print(f"[Clap] {music_player.toggle()}"))
        clap_detector.start()

    print(f"\n{config['jarvis']['name']} is online.")
    if wake_word_enabled:
        print("Say 'Hey Jarvis' to start a conversation. (Ctrl+C to quit)\n")
    else:
        print("Wake word disabled — listening continuously. (Ctrl+C to quit)\n")

    try:
        from core.world_monitor_manager import WorldMonitorManager
        wm_manager = WorldMonitorManager(r"C:\Users\shris\OneDrive\Desktop\worldmonitor")
        wm_manager.start()

        while True:
            if wake_listener:
                wake_listener.listen_for_wake_word()
                tts.speak("Yes?")

            user_text = stt.listen()
            if not user_text:
                continue

            print(f"[You]: {user_text}")
            reply = brain.think(user_text)
            tts.speak(reply)

    except KeyboardInterrupt:
        print("\nShutting down. Goodbye.")
        if clap_detector:
            clap_detector.stop()
        try:
            wm_manager.stop()
        except Exception:
            pass


if __name__ == "__main__":
    main()