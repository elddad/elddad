"""Open applications and websites on the local computer (cross-platform)."""

import platform
import shutil
import subprocess
import webbrowser

# Friendly names -> what to actually launch, per OS.
# Extend this dict with your own favourite apps.
_APP_COMMANDS = {
    "Windows": {
        "browser": ["cmd", "/c", "start", "", "https://www.google.com"],
        "chrome": ["cmd", "/c", "start", "chrome"],
        "notepad": ["notepad"],
        "calculator": ["calc"],
        "files": ["explorer"],
        "terminal": ["cmd", "/c", "start", "cmd"],
        "spotify": ["cmd", "/c", "start", "spotify:"],
        "vscode": ["cmd", "/c", "start", "", "code"],
    },
    "Darwin": {
        "browser": ["open", "https://www.google.com"],
        "chrome": ["open", "-a", "Google Chrome"],
        "notepad": ["open", "-a", "TextEdit"],
        "calculator": ["open", "-a", "Calculator"],
        "files": ["open", "-a", "Finder"],
        "terminal": ["open", "-a", "Terminal"],
        "spotify": ["open", "-a", "Spotify"],
        "vscode": ["open", "-a", "Visual Studio Code"],
    },
    "Linux": {
        "browser": ["xdg-open", "https://www.google.com"],
        "files": ["xdg-open", "."],
        "calculator": ["gnome-calculator"],
        "terminal": ["x-terminal-emulator"],
        "vscode": ["code"],
    },
}

# Spoken aliases (including Hebrew) -> canonical app key
_ALIASES = {
    "google": "browser", "internet": "browser", "דפדפן": "browser",
    "כרום": "chrome", "מחשבון": "calculator", "קבצים": "files",
    "טרמינל": "terminal", "ספוטיפיי": "spotify", "מוזיקה": "spotify",
    "code": "vscode", "vs code": "vscode",
}


def open_app(name: str) -> str:
    """Open an application by name. Returns a short status message."""
    key = name.strip().lower()
    key = _ALIASES.get(key, key)

    system = platform.system()
    commands = _APP_COMMANDS.get(system, {})
    cmd = commands.get(key)

    if cmd is None:
        available = ", ".join(sorted(commands)) or "none on this OS"
        return f"I don't know how to open '{name}'. Apps I know: {available}."

    try:
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return f"Opened {key}."
    except FileNotFoundError:
        return f"'{key}' does not seem to be installed ({cmd[0]} not found)."


def open_url(url: str) -> str:
    """Open a URL in the default browser."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    webbrowser.open(url)
    return f"Opened {url} in your browser."
