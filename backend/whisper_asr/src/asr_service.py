# whisper_asr/src/asr_service.py

import whisper
from .normalizer import normalize_text

# 🔒 HARD-LOCK SAFE MODEL CONFIG (Mac-friendly)
WHISPER_MODEL_NAME = "medium"   # ← was large-v2 (too heavy)
DEVICE = "cpu"


class WhisperASRService:
    """
    Production-ready ASR service wrapper around OpenAI Whisper.

    - CPU-only (stable on Mac)
    - English decoding (romanized output)
    - Multilingual input (Hindi / Kannada / English)
    - Safe for streaming usage
    """

    def __init__(self):
        print(f"🔊 Loading Whisper model: {WHISPER_MODEL_NAME} ({DEVICE})")

        # Load model once (NO reloads)
        self.model = whisper.load_model(
            WHISPER_MODEL_NAME,
            device=DEVICE
        )

        print("✅ Whisper model loaded")

    def transcribe(self, audio_path: str):
        """
        Transcribe an audio chunk.

        Returns:
            clean_text (str): normalized text (romanized if Hindi)
            detected_language (str)
            raw_text (str): raw Whisper output
        """

        result = self.model.transcribe(
            audio_path,
            task="transcribe",
            language="en",   # 🔒 Force English decoding
            fp16=False       # 🔒 CPU-safe
        )

        raw_text = result.get("text", "").strip()
        detected_language = result.get("language", "unknown")

        # Normalize ONCE (Hindi → Romanized English)
        clean_text = normalize_text(raw_text)

        return clean_text, detected_language, raw_text
