"""
Clap detection using volume-spike pattern matching with basic shape
validation — no ML model needed. A real clap is a short, sharp transient:
loud for one chunk, then dropping off quickly. Sustained loud noise
(echoes, shouting, doors) lingers across multiple consecutive chunks and
is filtered out by requiring the chunk right before the peak to be quiet.

Runs as a lightweight background thread, independent of the wake-word
listener and the main conversation loop, so clapping works at any time
regardless of what else Jarvis is doing.
"""

import threading
import time
from collections import deque
import numpy as np
import sounddevice as sd


class ClapDetector:
    def __init__(self, config: dict, on_clap):
        """
        on_clap: a callable invoked (with no args) each time a single clap
                 is detected. Runs in the detector's own background thread,
                 so on_clap should be quick or hand off work elsewhere
                 (e.g. queue it) rather than blocking this thread.
        """
        clap_cfg = config.get("clap_detection", {})
        self.sample_rate = 16000
        self.chunk_size = 512
        self.amplitude_threshold = clap_cfg.get("amplitude_threshold", 10000)
        self.quiet_threshold = clap_cfg.get("quiet_threshold", 6000)
        self.min_gap_seconds = clap_cfg.get("min_gap_seconds", 0.5)
        self.debug = clap_cfg.get("debug", True)
        self.on_clap = on_clap
        self._stop_event = threading.Event()
        self._thread = None

    def start(self):
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        print("[Clap] Listening for claps in the background...")

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2)

    def _run(self):
        last_clap_time = 0.0
        recent_peaks = deque(maxlen=2)

        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="int16",
            blocksize=self.chunk_size,
        ) as stream:
            while not self._stop_event.is_set():
                chunk, _ = stream.read(self.chunk_size)
                peak = np.abs(chunk).max()

                if self.debug and peak > 3000:
                    print(f"[Clap][DEBUG] peak={peak}")

                now = time.time()
                is_loud_enough = peak > self.amplitude_threshold
                was_quiet_just_before = (
                    len(recent_peaks) > 0 and recent_peaks[-1] < self.quiet_threshold
                )
                debounce_ok = (now - last_clap_time) > self.min_gap_seconds

                if is_loud_enough and was_quiet_just_before and debounce_ok:
                    last_clap_time = now
                    try:
                        self.on_clap()
                    except Exception as e:
                        print(f"[Clap] Error in on_clap handler: {e}")

                recent_peaks.append(peak)