# whisper_asr/src/streaming/live_pipeline.py

import time

from src.asr_service import WhisperASRService
from src.nlp.emergency_classifier import EmergencyClassifier

from .audio_chunker import chunk_wav
from .audio_utils import ensure_pcm_wav
from .state import EmergencyState
from src.streaming.transcript_buffer import TranscriptBuffer
from src.normalizer import normalize_text

# 🔥 NEW: metadata + fusion
from src.location.metadata_provider import get_caller_metadata
from src.location.location_fusion import resolve_location


def run_live_simulation(wav_path: str):
    """
    Simulate a live emergency call with streaming ASR + NLP.

    Fully automated pipeline:
    - Streaming ASR (English decoding)
    - Rolling transcript buffer
    - NLP emergency classification
    - Location fusion (speech hints + caller metadata)
    - No follow-up questions required
    """

    # --------------------------------------------------
    # Initialize services
    # --------------------------------------------------
    asr = WhisperASRService()
    clf = EmergencyClassifier()
    state = EmergencyState()

    # --------------------------------------------------
    # Ensure PCM WAV (16kHz, mono)
    # --------------------------------------------------
    pcm_path = wav_path.replace(".wav", "_pcm.wav")
    wav_path = ensure_pcm_wav(wav_path, pcm_path)

    # --------------------------------------------------
    # Chunk audio for streaming simulation
    # --------------------------------------------------
    chunks = chunk_wav(wav_path)

    print("🚨 Live call started\n")

    # --------------------------------------------------
    # Rolling transcript buffer
    # --------------------------------------------------
    buffer = TranscriptBuffer(max_chars=500)

    # --------------------------------------------------
    # Streaming loop
    # --------------------------------------------------
    for i, chunk in enumerate(chunks):
        # 1️⃣ ASR
        clean_text, detected_lang, raw_text = asr.transcribe(chunk)

        # 2️⃣ Update rolling buffer
        full_text = buffer.add(clean_text)

        # 3️⃣ Normalize text (noop for English, safe for mixed input)
        normalized_text = normalize_text(full_text)

        # 4️⃣ NLP classification (on full context)
        nlp_result = clf.classify(normalized_text)

        # 5️⃣ Location fusion (NO PIN DEPENDENCY)
        metadata = get_caller_metadata()
        final_location = resolve_location(
            nlp_result.get("location"),
            metadata
        )

        # 6️⃣ Merge final location into NLP result
        nlp_result_with_location = {
            **nlp_result,
            "final_location": final_location
        }

        # 7️⃣ Update global emergency state
        state.update(clean_text, nlp_result_with_location)

        # --------------------------------------------------
        # Logs (debug / demo)
        # --------------------------------------------------
        print(f"⏱️  Chunk {i}")
        print("ASR (chunk):", clean_text)
        print("ASR (buffered):", full_text)
        print("ASR (normalized):", normalized_text)
        print("NLP:", nlp_result_with_location)
        print("STATE:", state.snapshot())
        print("-" * 60)

        time.sleep(1.5)

    print("\n✅ Call ended")
    return state.snapshot()