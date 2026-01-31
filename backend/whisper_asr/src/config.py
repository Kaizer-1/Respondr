# whisper_asr/src/config.py

WHISPER_MODEL_NAME = "large-v2"
DEVICE = "cpu"          # locked to CPU for stability
DECODE_LANGUAGE = "en"  # English decoding → romanized output
FP16 = False            # CPU-safe