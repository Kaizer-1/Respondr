import whisper

class OfflineASR:
    """
    Offline, high-accuracy ASR using Whisper Large.
    """

    def __init__(self, model_name="large-v2", device="cpu"):
        print(f"🔊 Loading Whisper model: {model_name}")
        self.model = whisper.load_model(model_name, device=device)
        print("✅ Whisper model loaded")

    def transcribe(self, audio_path: str) -> dict:
        """
        Returns:
        {
            text: full transcript,
            language: detected language,
            segments: whisper segments
        }
        """
        result = self.model.transcribe(
            audio_path,
            task="transcribe",
            fp16=False
        )

        return {
            "text": result.get("text", "").strip(),
            "language": result.get("language", "unknown"),
            "segments": result.get("segments", [])
        }