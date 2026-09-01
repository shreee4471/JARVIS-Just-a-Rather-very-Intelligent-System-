# Jarvis — Local AI Voice Assistant

A fully local, voice-activated AI assistant built in Python, running entirely on your own machine with an NVIDIA GPU. No cloud dependency except Tavily for real-time web search. Inspired by Iron Man's J.A.R.V.I.S.

> **Built on:** Python 3.14 · Windows 11 · NVIDIA GPU · Ollama · faster-whisper · Piper TTS · openWakeWord

---

## Features

### Voice Pipeline
- **Wake word detection** — say "Hey Jarvis" to activate (openWakeWord, pre-trained model, always-on lightweight listener)
- **Speech-to-text** — faster-whisper `medium.en` running GPU-accelerated via CUDA
- **Text-to-speech** — Piper TTS (`en_US-lessac-high`), fast and natural-sounding, fully offline
- **Local LLM brain** — Llama 3.1 8B via Ollama, handles conversation + tool/function calling
- **Rolling memory** — keeps the last 8 conversation turns in context

### Clap Detection
- Single clap toggles music play/pause — runs as an independent background thread
- Resumes last played track, or picks a random one if nothing played yet
- Amplitude + sharpness validation to avoid false triggers from background noise

### Skills (Voice Commands)

| Skill | What to say |
|---|---|
| **Web search** | "Who is the current president?" / "Search for the latest iPhone" |
| **YouTube** | "Play Bohemian Rhapsody on YouTube" |
| **Open app** | "Open Chrome / Spotify / VS Code / Notepad" |
| **Play music** | "Play music" / "Pause music" / "Stop music" |
| **Volume** | "Set volume to 40 percent" / "Turn the volume up" / "Mute" |
| **Brightness** | "Set brightness to 50 percent" / "Brightness up" |
| **System info** | "What's my battery level?" / "How much RAM am I using?" |
| **File search** | "Find my resume" / "Open the games folder" |
| **Screenshot** | "Take a screenshot" |
| **Date/time** | "What time is it?" / "What's today's date?" |
| **Reminders** | "Remind me to drink water in 5 minutes" |
| **Write code** | "Open Notepad and write a Python script that prints 1 to 10" |
| **Power control** | "Shut down the computer" (always asks for confirmation first) |

### WorldMonitor Integration
Live geopolitical intelligence dashboard integrated directly into Jarvis. WorldMonitor's local sidecar API feeds real-time data — news, Country Instability Index (CII) scores, market prices, weather, conflict zones — which Jarvis can summarize and alert you about on demand or automatically.

---

## Local LLM — The Brain

Jarvis runs a **fully local Large Language Model** via [Ollama](https://ollama.com) — no OpenAI, no Anthropic, no cloud API calls for the core intelligence. Everything stays on your machine.

### Model: Llama 3.1 8B
- Runs entirely on your NVIDIA GPU via Ollama
- Handles natural conversation, intent understanding, and tool/function calling
- Keeps a rolling context window of the last 8 conversation turns (configurable)
- Chosen for its strong tool-calling reliability among open-weight 8B models

### How the LLM fits into the pipeline
Every voice command goes through the LLM — it decides whether to:
- **Just chat** — answer directly from its own knowledge (timeless facts, greetings, general questions)
- **Call a skill** — invoke one of the 13+ registered skills (web search, volume control, open app, etc.) using Ollama's native function-calling API
- **Search first, then answer** — trigger the web_search skill for anything time-sensitive, then synthesize the real results into a spoken reply

### Why local?
- **Privacy** — your voice, commands, and system data never leave your machine
- **Free** — no API costs, no rate limits on the core intelligence
- **Offline capable** — works without internet (except Tavily web search, which is optional)
- **Customizable** — swap in any Ollama-compatible model by changing one line in `config.yaml`

### Swapping models
Any model pulled via `ollama pull` works — just update `config.yaml`:
```yaml
llm:
  model: "llama3.1:8b"    # change this to any ollama model
```
Models worth trying:
- `llama3.1:8b` — recommended, best tool-calling balance for the size
- `llama3.1:70b` — significantly better reasoning, needs a powerful GPU
- `mistral:7b` — lighter, faster, slightly less reliable at tool calling
- `gemma2:9b` — good alternative if Llama isn't available

### Code generation (write_code skill)
The LLM also powers the `write_code` skill — when you ask Jarvis to write code, it makes a dedicated second LLM call with a focused code-generation prompt (low temperature, raw output only), then types the result live into Notepad or VS Code using pywinauto.

```
You speak
    ↓
Wake Word ("Hey Jarvis") — openWakeWord, lightweight always-on listener
    ↓
Speech-to-Text — faster-whisper medium.en, GPU-accelerated
    ↓
Brain — Llama 3.1 8B via Ollama, decides: chat or call a skill?
    ↓
Skill Router — executes the right skill and returns the result
    ↓
Text-to-Speech — Piper speaks the reply out loud
    ↓
You hear the response

Running independently in background:
Clap Detector → toggles music play/pause from your Music folder
WorldMonitor Sidecar → feeds real-time global intelligence data
```

### Project Structure

```
jarvis/
├── main.py                    # Entry point — boots everything, runs the main loop
├── config.yaml                # All settings in one place — never hardcode anything
│
├── core/
│   ├── brain.py               # LLM calls, conversation memory, tool/function calling
│   ├── stt.py                 # Mic recording + faster-whisper transcription (GPU)
│   ├── tts.py                 # Piper TTS — speaks replies out loud
│   ├── wake_word.py           # Always-on openWakeWord listener
│   └── clap_detector.py       # Background clap detection for music control
│
├── music_player/
│   └── __init__.py            # pygame-ce music player — shared state between
│                              #   clap detector and voice skill
│
├── skills/
│   ├── base_skill.py          # Abstract base class all skills inherit from
│   ├── __init__.py            # Central skill registry — build_registry() wires
│   │                          #   everything at startup. New skill = one file.
│   ├── open_app.py            # Opens apps by name
│   ├── web_search.py          # Tavily real-time web search
│   ├── youtube_play.py        # Opens top YouTube result in browser
│   ├── play_music.py          # Voice-controlled music (shared with clap detector)
│   ├── volume_control.py      # System volume via pycaw
│   ├── brightness_control.py  # Screen brightness via screen-brightness-control
│   ├── system_info.py         # Battery, RAM, disk via psutil
│   ├── file_search.py         # File/folder search across C: drive
│   ├── screenshot.py          # Screen capture via Pillow
│   ├── datetime_info.py       # Current time/date/day (stdlib only)
│   ├── reminders.py           # Timed reminders spoken aloud via TTS
│   ├── power_control.py       # Shutdown/restart/sleep with confirmation
│   └── write_code.py          # LLM-generated code typed into Notepad/VS Code
│
└── models/
    └── piper/                 # Piper voice model files (.onnx + .onnx.json)
```

---

## Prerequisites

- Python 3.10+ (tested on 3.14)
- Windows 10/11 (64-bit)
- NVIDIA GPU with CUDA drivers
- [Ollama](https://ollama.com) installed
- [Piper](https://github.com/rhasspy/piper/releases) executable on PATH
- [WorldMonitor Desktop App](https://worldmonitor.app) installed (for WorldMonitor integration)

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/jarvis.git
cd jarvis
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 3. Fix CUDA DLLs for faster-whisper (Windows)

The CUDA libraries ship inside pip packages on Windows — no system-wide CUDA Toolkit needed:

```bash
pip install nvidia-cublas-cu12 nvidia-cudnn-cu12
```

This is handled automatically at startup by `_add_cuda_dll_paths()` in `main.py`.

### 4. Pull the LLM model

```bash
ollama pull llama3.1:8b
```

### 5. Install Piper TTS

Download the Piper binary for Windows from:
https://github.com/rhasspy/piper/releases

Download the voice model files from:
https://github.com/rhasspy/piper/blob/master/VOICES.md

Recommended: `en_US-lessac-high`

Place both `.onnx` and `.onnx.json` files into:
```
jarvis/models/piper/en_US-lessac-high.onnx
jarvis/models/piper/en_US-lessac-high.onnx.json
```

### 6. Set your Tavily API key

Sign up free at https://tavily.com (1,000 searches/month, no card required), then:

```powershell
[System.Environment]::SetEnvironmentVariable("TAVILY_API_KEY", "tvly-your-key-here", "User")
```

### 7. Configure `config.yaml`

Key settings to check/update:

```yaml
jarvis:
  name: "Jarvis"

llm:
  model: "llama3.1:8b"          # must match your ollama pull

music:
  folder: "C:\\Users\\YourName\\Music"   # your actual music folder

clap_detection:
  amplitude_threshold: 10000    # tune up if too sensitive, down if not triggering
  quiet_threshold: 6000
```

### 8. Windows-specific: disable Notepad App Execution Alias

For the `write_code` skill to type into Notepad, disable the UWP wrapper:

**Settings → Apps → Advanced app settings → App execution aliases → Notepad → Off**

### 9. Start Ollama

```bash
ollama serve
```

### 10. Run Jarvis

```bash
python main.py
```

Say **"Hey Jarvis"** — wait for "Yes?" — then give your command.

---

## Configuration Reference

```yaml
jarvis:
  name: "Jarvis"                # Name used in system prompt and greetings

wake_word:
  model: "hey_jarvis_v0.1"      # openWakeWord model name
  threshold: 0.5                # Detection confidence threshold (0.0–1.0)
  enabled: true                 # Set false to listen continuously without wake word

llm:
  provider: "ollama"
  model: "llama3.1:8b"          # Any model pulled via `ollama pull`
  base_url: "http://localhost:11434"
  temperature: 0.6
  context_window: 8             # Number of past conversation turns to remember

stt:
  model_size: "medium.en"       # tiny/base/small/medium/large-v3
  device: "cuda"                # "cpu" if no GPU
  compute_type: "float16"       # "int8" on CPU

tts:
  voice: "en_US-lessac-high"    # Must match your downloaded .onnx filename
  speed: 1.0

clap_detection:
  enabled: true
  amplitude_threshold: 10000    # Tune based on your mic sensitivity
  quiet_threshold: 6000         # Must be quiet just before a real clap
  min_gap_seconds: 0.5          # Debounce — minimum time between clap triggers
  debug: false                  # true prints peak values to terminal for tuning

music:
  folder: "C:\\Users\\YourName\\Music"

audio:
  silence_threshold: 500        # Mic sensitivity for end-of-speech detection
  silence_duration: 1.0         # Seconds of silence before STT cuts off
```

---

## Adding a New Skill

The skill system is designed so adding a new action never touches any existing files except the registry.

**1. Create `skills/your_skill.py`:**

```python
from skills.base_skill import BaseSkill

class YourSkill(BaseSkill):
    name = "your_skill"
    description = "Clear explanation of when the LLM should call this."
    parameters = {
        "some_arg": {"type": "string", "description": "What this arg is for"}
    }

    def run(self, some_arg: str) -> str:
        # do the thing
        return "Result message Jarvis will speak"
```

**2. Register it in `skills/__init__.py`:**

```python
from skills.your_skill import YourSkill

# inside build_registry():
skills.append(YourSkill())
```

That's it. `brain.py`, the main loop, nothing else needs changing.

---

## Dependencies

```
faster-whisper       # GPU-accelerated Whisper STT
openwakeword         # Wake word detection
pyyaml               # Config file parsing
numpy                # Audio processing
sounddevice          # Mic input
requests             # HTTP calls (Tavily, Ollama API)
beautifulsoup4       # HTML parsing (YouTube skill)
pygame-ce            # Music playback
pycaw                # Windows volume control
comtypes             # COM interface (required by pycaw)
screen-brightness-control  # Screen brightness
psutil               # System info (battery, RAM, disk)
pillow               # Screenshot capture
pywinauto            # GUI automation (write_code skill)
nvidia-cublas-cu12   # CUDA cuBLAS DLLs for faster-whisper
nvidia-cudnn-cu12    # CUDA cuDNN DLLs for faster-whisper
```

---

## Troubleshooting

**`cublas64_12.dll not found`**
Run: `pip install nvidia-cublas-cu12 nvidia-cudnn-cu12`
These are handled automatically at startup — if you still see this, check that `main.py` has the `_add_cuda_dll_paths()` function at the top.

**Wake word not triggering**
First run downloads the model files automatically. If it still doesn't trigger, try lowering `wake_word.threshold` in `config.yaml` (e.g. `0.3`).

**Clap detector firing on its own**
You're likely using speakers instead of headphones — mic picks up the music. Use headphones, or raise `clap_detection.amplitude_threshold`.

**`[TTS] Piper error:`**
Check that the `piper` executable is on PATH (`where piper` in PowerShell), and that both `.onnx` and `.onnx.json` files exist in `models/piper/` and match the voice name in `config.yaml`.

**Tool calls not firing / Jarvis answers from memory instead of searching**
Llama 3.1 8B occasionally skips tool calls. Try rephrasing with explicit trigger words: "search the web for...", "look up...", "what is the *current*...".

**`write_code` skill times out on Notepad**
Disable the Windows 11 UWP Notepad alias: Settings → Apps → Advanced app settings → App execution aliases → Notepad → Off.

**File search takes 10-15 seconds**
Normal for files outside Desktop/Documents/Downloads/Pictures/Music/Videos — those trigger a full C: drive scan. Common folders resolve instantly.

---

## Roadmap

- [ ] Auto-start on system boot
- [ ] iOS bridge (Flask/FastAPI server + Apple Shortcuts)
- [ ] Streaming LLM responses into TTS for lower latency
- [ ] WorldMonitor continuous background monitoring with automatic alerts
- [ ] More skills: Spotify control, email, calendar

---

## License & Open Source

This project is fully open source under the **MIT License** — you are free to use, modify, distribute, and build on it however you like, for personal or commercial purposes.

**Contributions are welcome.** If you add a new skill, fix a bug, improve the architecture, or build something cool on top of this, feel free to open a pull request. The skill system is specifically designed to make adding new features easy — a new skill is just one file and one registry line, no deep knowledge of the rest of the codebase needed.

Some ideas for community contributions:
- New skills (Spotify control, Gmail, calendar, smart home)
- Wake word alternatives or custom trained models
- iOS/Android bridge
- Streaming LLM responses for lower latency
- Better tool-calling reliability with different local models
- Linux/macOS compatibility improvements

---

*Built entirely in one conversation with Claude. Started as a fresh Python project, evolved into a full voice assistant with 13 skills, wake word detection, clap-controlled music, real-time web search, and WorldMonitor integration.*
