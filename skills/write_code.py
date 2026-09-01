"""
Code-writing skill — generates code from a natural-language description
(using the same LLM Jarvis already runs locally) and types it live into
a fresh, blank Notepad window or a new VS Code window, using pywinauto
for reliable window/control targeting.

NOTEPAD NOTE: relies on classic Win32 Notepad (App execution alias for
Notepad must be OFF in Windows Settings).

VS CODE NOTE: "-n" forces a brand new empty window each time; clicks the
center of the window before typing to ensure focus lands in the editor.
"""

import time
import requests
from skills.base_skill import BaseSkill

try:
    from pywinauto.application import Application
    _PYWINAUTO_AVAILABLE = True
except ImportError:
    _PYWINAUTO_AVAILABLE = False


class WriteCodeSkill(BaseSkill):
    name = "write_code"
    description = (
        "Generate code based on a description and type it into a fresh, "
        "new file in a code editor (Notepad or VS Code). Use this when "
        "the user asks to write code, write a script, or write a program, "
        "and specifies an editor (e.g. 'open notepad and write a python "
        "script that...', 'open vs code and write code for...'). If no "
        "editor is specified, default to 'vscode'."
    )
    parameters = {
        "description": {
            "type": "string",
            "description": "What the code should do, e.g. 'a Python script that prints the Fibonacci sequence'",
        },
        "editor": {
            "type": "string",
            "description": "One of: 'notepad', 'vscode'",
        },
    }

    def __init__(self, llm_base_url: str, llm_model: str):
        self.llm_base_url = llm_base_url
        self.llm_model = llm_model

    def _generate_code(self, description: str) -> str:
        prompt = (
            f"Write code for the following request: {description}\n\n"
            "Output ONLY the raw code itself. No explanations, no markdown "
            "code fences (no ```), no commentary before or after — just the "
            "plain code text exactly as it should appear in a file."
        )
        resp = requests.post(
            f"{self.llm_base_url}/api/chat",
            json={
                "model": self.llm_model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "options": {"temperature": 0.3},
            },
            timeout=120,
        )
        resp.raise_for_status()
        code = resp.json().get("message", {}).get("content", "")

        code = code.strip()
        if code.startswith("```"):
            lines = code.split("\n")
            lines = lines[1:]
            if lines and lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            code = "\n".join(lines)
        return code.strip()

    def _type_into_notepad(self, code: str) -> str:
        app = Application(backend="uia").start("notepad.exe")
        window = app.window(title_re=".*Notepad.*")
        window.wait("ready", timeout=15)
        window.set_focus()
        time.sleep(0.5)

        window.type_keys(code, with_spaces=True, with_newlines=True, with_tabs=True)
        return "Code written into a new Notepad file."

    def _type_into_vscode(self, code: str) -> str:
        app = Application(backend="uia").start("code.exe -n")
        window = app.window(title_re=".*Visual Studio Code.*")
        window.wait("ready", timeout=20)
        window.set_focus()
        time.sleep(2)

        rect = window.rectangle()
        center_x = (rect.left + rect.right) // 2
        center_y = (rect.top + rect.bottom) // 2
        window.click_input(coords=(center_x - rect.left, center_y - rect.top))
        time.sleep(0.3)

        window.type_keys(code, with_spaces=True, with_newlines=True, with_tabs=True)
        return "Code written into a new VS Code file."

    def run(self, description: str, editor: str = "vscode") -> str:
        if not _PYWINAUTO_AVAILABLE:
            return "Code writing isn't available — pywinauto isn't installed."

        editor = editor.lower().strip()
        try:
            code = self._generate_code(description)
        except Exception as e:
            return f"Failed to generate the code: {e}"

        if not code:
            return "The code generation came back empty — try rephrasing the request."

        try:
            if editor == "notepad":
                self._type_into_notepad(code)
            elif editor == "vscode":
                self._type_into_vscode(code)
            else:
                return f"Unknown editor: {editor}. Use 'notepad' or 'vscode'."
        except Exception as e:
            return f"Generated the code, but failed to type it into {editor}: {e}"

        return (
            f"Successfully wrote this exact code into {editor}:\n{code}\n"
            f"Confirm to the user that this code is now in {editor}, and you "
            f"may briefly describe what it does, but do not invent different code."
        )