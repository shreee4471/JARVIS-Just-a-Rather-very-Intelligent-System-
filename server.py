import os
import sys

def _add_cuda_dll_paths():
    """
    faster-whisper (via CTranslate2) needs CUDA 12.x's cublas/cudnn DLLs.
    We point directly at the DLLs shipped inside the pip packages.
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
        except ImportError:
            pass

_add_cuda_dll_paths()

import yaml
import base64
from fastapi import FastAPI, UploadFile, File, Form

from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from core.brain import Brain
from core.stt import STT
from core.tts import TTS
from music_player import MusicPlayer
from skills import build_registry
from core.world_monitor_manager import WorldMonitorManager

def load_config(path="config.yaml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)

print("Initializing Jarvis API Server...")
config = load_config()

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

wm_manager = WorldMonitorManager(r"C:\Users\shris\OneDrive\Desktop\worldmonitor")
wm_manager.start()

app = FastAPI(title="Jarvis API")

# Ensure public directory exists
os.makedirs("public", exist_ok=True)
app.mount("/public", StaticFiles(directory="public"), name="public")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("public/index.html", "r") as f:
        return f.read()

@app.post("/api/chat")
async def chat(audio: UploadFile = File(None), text: str = Form(None)):
    user_text = ""
    
    if audio:
        print("[API] Received audio file")
        import tempfile
        import shutil
        
        # Save to a temporary file so faster-whisper (via ffmpeg) can parse the webm container
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_audio:
            shutil.copyfileobj(audio.file, temp_audio)
            temp_audio_path = temp_audio.name
            
        try:
            # Transcribe directly using the file path
            segments, _ = stt.model.transcribe(temp_audio_path, language="en")
            user_text = " ".join(seg.text.strip() for seg in segments).strip()
        except Exception as e:
            print(f"[API] STT Error: {e}")
            return JSONResponse(status_code=500, content={"error": "Transcription failed"})
        finally:
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
    elif text:
        user_text = text
    
    if not user_text:
        return JSONResponse(status_code=400, content={"error": "No audio or text provided"})
        
    print(f"[API] User: {user_text}")
    
    try:
        reply_text = brain.think(user_text)
        print(f"[API] Jarvis: {reply_text}")
        
        audio_bytes = tts.generate_audio_bytes(reply_text)
        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8") if audio_bytes else None
        
        return {
            "text": reply_text,
            "audio_base64": audio_base64
        }
    except Exception as e:
        print(f"[API] Brain/TTS Error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.on_event("shutdown")
def shutdown_event():
    print("Shutting down API server...")
    wm_manager.stop()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False)
