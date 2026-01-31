class TranscriptBuffer:
    """
    Keeps a rolling transcript window so NLP sees context
    across chunks instead of isolated sentences.
    """
    def __init__(self, max_chars=500):
        self.text = ""
        self.max_chars = max_chars

    def add(self, chunk: str) -> str:
        if not chunk:
            return self.text

        self.text += " " + chunk
        self.text = self.text[-self.max_chars:]
        return self.text.strip()