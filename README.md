# Jarvis — Setup Guide

## 1. Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com) installed
- NVIDIA GPU + CUDA drivers (you have this already)

## 2. Pull the model
```bash
ollama pull mistral:7b
```
(If tool-calling feels unreliable later, try `ollama pull llama3.1:8b` instead and
change `llm.model` in config.yaml — bigger models follow tool-use instructions better.)

## 3. Python dependencies
```bash
cd jarvis
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

## 4. Install Piper (TTS)
Download the piper binary for your OS from:
https://github.com/rhasspy/piper/releases

Place the `piper` executable somewhere on your PATH, or in the project root.

Download a voice model (e.g. `en_US-lessac-medium`) from:
https://github.com/rhasspy/piper/blob/master/VOICES.md

Put both the `.onnx` and `.onnx.json` files into:
```
jarvis/models/piper/en_US-lessac-medium.onnx
jarvis/models/piper/en_US-lessac-medium.onnx.json
```

## 5. Start Ollama (if not already running)
```bash
ollama serve
```

## 6. Run Jarvis
```bash
python main.py
```

Speak after you see "Listening..." — it'll cut off after ~1 second of silence,
transcribe, think, and reply out loud.

## Troubleshooting
- **No mic input detected**: run `python -c "import sounddevice; print(sounddevice.query_devices())"`
  to list devices, and set a specific input device in `core/stt.py` if needed.
- **CUDA errors on STT**: set `stt.device: "cpu"` and `stt.compute_type: "int8"` in config.yaml.
- **Tool calls not firing**: Mistral 7B is decent but not great at function calling.
  Try llama3.1:8b, or make skill descriptions even more explicit/example-driven.
- **Piper not found**: make sure the `piper` executable is on your system PATH,
  or edit core/tts.py to use the full path to the binary.

## Adding a new skill (this is the whole point of the architecture)
1. Create `skills/your_skill.py`:
```python
from skills.base_skill import BaseSkill

class YourSkill(BaseSkill):
    name = "your_skill"
    description = "Clear explanation of when the LLM should call this."
    parameters = {"some_arg": {"type": "string", "description": "..."}}

    def run(self, some_arg: str) -> str:
        # do the thing
        return "Result message"
```
2. Register it in `skills/__init__.py`:
```python
from skills.your_skill import YourSkill
ALL_SKILLS = [..., YourSkill()]
```
That's it. brain.py, router logic, everything else stays untouched.

## Next upgrades to consider
- **Wake word**: add `openwakeword` so Jarvis only listens after "Hey Jarvis"
  instead of always recording.
- **Streaming responses**: stream LLM tokens into TTS in chunks for lower latency.
- **iOS bridge**: run this on your PC as a small Flask/FastAPI server, then use
  an Apple Shortcut to send your voice/text to it over your home network and
  play back the response.
