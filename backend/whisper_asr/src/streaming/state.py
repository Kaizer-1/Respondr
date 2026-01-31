class EmergencyState:
    """
    Holds evolving state of an emergency call.
    This class stores results — it does NOT compute them.
    """

    def __init__(self):
        self.transcript = ""
        self.type = "unknown"
        self.priority = "low"
        self.keywords = []
        self.location = None
        self._location_locked = False

    def update(self, new_text: str, nlp_result: dict):
        # Append transcript
        if new_text:
            self.transcript += " " + new_text

        # Update emergency info
        self.type = nlp_result.get("type", self.type)
        self.priority = nlp_result.get("priority", self.priority)
        self.keywords = nlp_result.get("keywords", self.keywords)

        # Update location (lock once confident)
        new_location = nlp_result.get("location")
        if new_location and not self._location_locked:
            self.location = new_location

            if new_location.get("confidence", 0) >= 0.9:
                self._location_locked = True

    def snapshot(self):
        return {
            "transcript": self.transcript.strip(),
            "type": self.type,
            "priority": self.priority,
            "keywords": self.keywords,
            "location": self.location
        }