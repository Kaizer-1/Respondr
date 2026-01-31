def resolve_location(speech_location: dict | None, metadata: dict):
    """
    Industry-grade location resolution.

    Rules:
    1. If speech gives a valid PIN → trust it
    2. Else if speech gives place text → use it WITH metadata
    3. Else → fallback to metadata region
    """

    # 1️⃣ PIN code is strongest
    if speech_location and speech_location.get("pincode"):
        return {
            "level": "precise",
            "pincode": speech_location["pincode"],
            "text": speech_location.get("text"),
            "confidence": speech_location.get("confidence", 0.8)
        }

    # 2️⃣ Place name but no PIN
    if speech_location and speech_location.get("text"):
        return {
            "level": "approx",
            "area": speech_location["text"],
            "city": metadata.get("city"),
            "confidence": 0.6
        }

    # 3️⃣ Hard fallback (THIS IS REAL WORLD)
    return {
        "level": "region",
        "region": metadata.get("region"),
        "city": metadata.get("city"),
        "confidence": 0.4
    }