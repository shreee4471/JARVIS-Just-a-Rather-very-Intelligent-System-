import subprocess
import time
import os
import urllib.request
import urllib.error

class WorldMonitorManager:
    def __init__(self, wm_dir: str):
        self.wm_dir = wm_dir
        self.process = None

    def start(self):
        print("\n[World Monitor] Starting background server...")
        try:
            # Start World Monitor via npm run dev in the background
            # We use shell=True and CREATE_NEW_PROCESS_GROUP to ensure it doesn't block
            # and can be killed properly later. We redirect stdout/stderr to DEVNULL 
            # to avoid cluttering Jarvis's terminal.
            self.process = subprocess.Popen(
                "npm run dev",
                cwd=self.wm_dir,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
            
            # Wait for it to be ready
            self._wait_for_ready()
            
        except Exception as e:
            print(f"[World Monitor] Failed to start: {e}")

    def _wait_for_ready(self, timeout: int = 30):
        print("[World Monitor] Waiting for API to come online", end="", flush=True)
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # The root /api/health endpoint or just / should respond when ready
                req = urllib.request.Request("http://localhost:3000/")
                with urllib.request.urlopen(req, timeout=2):
                    print("\n[World Monitor] STATUS: CONNECTED and gathering data.")
                    return
            except urllib.error.URLError:
                pass
            except Exception:
                pass
                
            print(".", end="", flush=True)
            time.time()
            time.sleep(2)
            
        print("\n[World Monitor] STATUS: TIMEOUT waiting for connection. Skills may not work.")

    def stop(self):
        if self.process:
            print("\n[World Monitor] Shutting down...")
            # Kill the process tree (since shell=True spawns a cmd.exe which spawns node)
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(self.process.pid)], 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.process = None
