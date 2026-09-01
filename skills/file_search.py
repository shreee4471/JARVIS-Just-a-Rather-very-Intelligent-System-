"""
File/folder search skill — checks common user folders first (fast), and
only falls back to a full C: drive scan (slower) if nothing's found there.
Can also open the best match directly.
"""

import os
import sys
import subprocess
from skills.base_skill import BaseSkill


class FileSearchSkill(BaseSkill):
    name = "search_files"
    description = (
        "Search for a file or folder by name on the user's computer, and "
        "optionally open it. Use this when the user asks to find, locate, "
        "search for, or open a file or folder by name."
    )
    parameters = {
        "filename": {
            "type": "string",
            "description": "Name or partial name of the file/folder to search for, e.g. 'resume' or 'games'",
        },
        "open_it": {
            "type": "boolean",
            "description": "Set to true if the user wants the file/folder opened, not just located",
        },
    }

    MAX_RESULTS = 10
    MAX_SEARCH_DEPTH = 6

    COMMON_FOLDERS = ["Desktop", "Documents", "Downloads", "Pictures", "Music", "Videos"]

    SKIP_DIR_NAMES = {
        "Windows", "Program Files", "Program Files (x86)", "ProgramData",
        "$Recycle.Bin", "System Volume Information", "node_modules",
        "AppData", ".git", "venv", "__pycache__",
    }

    def _search_folder(self, query: str, root: str, max_depth: int = None) -> list[str]:
        matches = []
        if not os.path.isdir(root):
            return matches

        root_depth = root.rstrip("\\/").count(os.sep)
        for current_root, dirs, files in os.walk(root, topdown=True):
            if max_depth is not None:
                depth = current_root.rstrip("\\/").count(os.sep) - root_depth
                if depth >= max_depth:
                    dirs[:] = []
                    continue

            dirs[:] = [d for d in dirs if d not in self.SKIP_DIR_NAMES]

            for name in files + dirs:
                if query in name.lower():
                    matches.append(os.path.join(current_root, name))
                    if len(matches) >= self.MAX_RESULTS:
                        return matches

        return matches

    def _search(self, query: str) -> list[str]:
        home = os.path.expanduser("~")
        matches = []
        for folder_name in self.COMMON_FOLDERS:
            folder_path = os.path.join(home, folder_name)
            matches.extend(self._search_folder(query, folder_path))
            if len(matches) >= self.MAX_RESULTS:
                return matches[: self.MAX_RESULTS]

        if matches:
            return matches

        return self._search_folder(query, "C:\\", max_depth=self.MAX_SEARCH_DEPTH)

    def run(self, filename: str, open_it: bool = False) -> str:
        query = filename.lower()
        matches = self._search(query)

        if not matches:
            return f"No files or folders found matching '{filename}'."

        if open_it:
            best_match = matches[0]
            try:
                if sys.platform == "win32":
                    os.startfile(best_match)
                else:
                    subprocess.run(["open" if sys.platform == "darwin" else "xdg-open", best_match])
                return f"Opening {best_match}."
            except Exception as e:
                return f"Found {best_match} but couldn't open it: {e}"

        result_lines = [f"Found {len(matches)} match(es) for '{filename}':"]
        result_lines.extend(f"- {path}" for path in matches)
        return "\n".join(result_lines)