"""Text-to-speech using free Microsoft Edge voices, with Hebrew support."""

import asyncio
import os
import re
import tempfile

import edge_tts

from ..config import VOICE_ENGLISH, VOICE_HEBREW

_HEBREW_RE = re.compile(r"[֐-׿]")

_mixer_ready = False


def _pick_voice(text: str) -> str:
    return VOICE_HEBREW if _HEBREW_RE.search(text) else VOICE_ENGLISH


def _play_mp3(path: str) -> None:
    global _mixer_ready
    os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
    import pygame

    if not _mixer_ready:
        pygame.mixer.init()
        _mixer_ready = True
    pygame.mixer.music.load(path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.wait(100)
    pygame.mixer.music.unload()


async def speak(text: str) -> None:
    """Synthesize `text` (Hebrew or English, auto-detected) and play it aloud."""
    text = text.strip()
    if not text:
        return

    voice = _pick_voice(text)
    fd, path = tempfile.mkstemp(suffix=".mp3")
    os.close(fd)
    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(path)
        # Playback is blocking; run it off the event loop so reminders keep ticking.
        await asyncio.get_running_loop().run_in_executor(None, _play_mp3, path)
    finally:
        try:
            os.remove(path)
        except OSError:
            pass
