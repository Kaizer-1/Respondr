from src.pipeline.process_call import CallProcessor


def run_analysis(wav_path: str):
    """
    Core analysis entrypoint.
    Used by both local testing and Twilio.
    """
    processor = CallProcessor()
    return processor.process(wav_path)


def analyze_call_audio(wav_path: str):
    """
    Wrapper for Twilio calls.
    Twilio should ONLY call this function.
    """
    return run_analysis(wav_path)


# --------------------------------------------------
# Local testing ONLY
# --------------------------------------------------
if __name__ == "__main__":
    result = run_analysis("test_audio/sample8.wav")

    print("\n🚨 FINAL RESULT")
    print("Language:", result["language"])
    print("Transcript:", result["transcript"])
    print("Analysis:", result["analysis"])