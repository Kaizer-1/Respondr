# src/pipeline/process_call.py

from src.asr_service import WhisperASRService
from src.nlp.emergency_classifier import EmergencyClassifier
from src.normalizer import normalize_text
from src.location.geocoder import geocode_location

class CallProcessor:
    """
    Orchestrates the full offline call analysis pipeline.

    Steps:
    1. Transcribe full audio (NO chunking)
    2. Normalize language (Hindi/English safe)
    3. Classify emergency + extract location
    """

    def __init__(self):
        self.asr = WhisperASRService()
        self.classifier = EmergencyClassifier()

    def process(self, wav_path: str):
        """
        Main entry point for:
        - run_call_analysis.py
        - Flask / Twilio webhook

        Returns a structured dict safe for dashboards / DB.
        """

        # -----------------------------
        # 1️⃣ Speech-to-text (FULL AUDIO)
        # -----------------------------
        text, detected_lang, raw_text = self.asr.transcribe(wav_path)

        # -----------------------------
        # 2️⃣ Normalize text
        # -----------------------------
        normalized_text = normalize_text(text)

        # 🔥 🔥 🔥 PRINT TRANSCRIPTION HERE 🔥 🔥 🔥
        print("\n📝 TRANSCRIPTION =========================")
        print(normalized_text)
        print("=========================================\n")

        # -----------------------------
        # 3️⃣ NLP analysis
        # -----------------------------
        analysis = self.classifier.classify(normalized_text)

        # 📍 Enhance location with Google Maps
        raw_location = analysis.get("location")

        if raw_location and raw_location.get("text"):
            query = raw_location["text"] + ", Bangalore, India"
            geo = geocode_location(query)
        else:
            geo = None

        analysis["geo"] = geo

        # -----------------------------
        # 4️⃣ Final structured output
        # -----------------------------
        return {
            "language": detected_lang,
            "transcript": normalized_text,
            "analysis": analysis
        }
