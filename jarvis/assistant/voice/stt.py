"""Speech-to-text using faster-whisper. Auto-detects Hebrew vs English."""

import numpy as np

from ..config import WHISPER_MODEL

_model = None


def _get_model():
    global _model
    if _model is None:
        from faster_whisper import WhisperModel

        print(f"[stt] loading Whisper model '{WHISPER_MODEL}' (first run downloads it)...")
        _model = WhisperModel(WHISPER_MODEL, device="auto", compute_type="auto")
    return _model


def transcribe(audio: np.ndarray) -> tuple[str, str]:
    """Transcribe a 16 kHz float32 waveform.

    Returns (text, language_code) e.g. ("מה מזג האוויר", "he").
    """
    if audio.size < 1600:  # under 0.1s of audio
        return "", "en"

    model = _get_model()
    segments, info = model.transcribe(audio, vad_filter=True)
    text = " ".join(seg.text.strip() for seg in segments).strip()
    return text, info.language
