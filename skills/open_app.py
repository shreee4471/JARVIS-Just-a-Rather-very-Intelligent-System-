import subprocess
import sys
from skills.base_skill import BaseSkill


class OpenAppSkill(BaseSkill):
    name = "open_app"
    description = (
        "Open an application on the user's computer by name, e.g. 'chrome', "
        "'notepad', 'spotify', 'vscode'. Use this whenever the user asks to "
        "open, launch, or start a program."
    )
    parameters = {
        "app_name": {
            "type": "string",
            "description": "Name of the application to open, lowercase, e.g. 'chrome'",
        }
    }

    # Map friendly names -> actual command per OS. Extend this as you add apps.
    APP_MAP = {
        "win32": {
            "chrome": "start chrome",
            "notepad": "start notepad",
            "spotify": "start spotify",
            "vscode": "code",
            "explorer": "start explorer",
        },
        "darwin": {
            "chrome": "open -a 'Google Chrome'",
            "spotify": "open -a Spotify",
            "vscode": "open -a 'Visual Studio Code'",
        },
        "linux": {
            "chrome": "google-chrome",
            "spotify": "spotify",
            "vscode": "code",
        },
    }

    def run(self, app_name: str) -> str:
        platform = sys.platform
        platform_key = "win32" if platform.startswith("win") else (
            "darwin" if platform == "darwin" else "linux"
        )
        cmd = self.APP_MAP.get(platform_key, {}).get(app_name.lower())
        if not cmd:
            return f"I don't know how to open '{app_name}' yet. Add it to OpenAppSkill.APP_MAP."
        try:
            subprocess.Popen(cmd, shell=True)
            return f"Opening {app_name}."
        except Exception as e:
            return f"Failed to open {app_name}: {e}"
