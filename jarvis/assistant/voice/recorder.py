"""Microphone recording: push-to-talk style (Enter to start, Enter to stop)."""

import queue

import numpy as np
import sounddevice as sd

from ..config import SAMPLE_RATE


def record_until_enter() -> np.ndarray:
    """Record from the default microphone until the user presses Enter.

    Returns a float32 mono waveform at 16 kHz, ready for Whisper.
    """
    frames: queue.Queue[np.ndarray] = queue.Queue()

    def callback(indata, _frames, _time, status):
        if status:
            print(f"[mic] {status}")
        frames.put(indata.copy())

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
        callback=callback,
    ):
        input()  # recording continues until Enter is pressed

    chunks = []
    while not frames.empty():
        chunks.append(frames.get())
    if not chunks:
        return np.zeros(0, dtype=np.float32)
    return np.concatenate(chunks).flatten()
