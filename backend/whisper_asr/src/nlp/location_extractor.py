import re

PIN_REGEX = r"\b([1-9][0-9]{5})\b"

PLACE_SUFFIXES = [
    "street", "road", "lane", "avenue", "circle", "cross",
    "mall", "hospital", "college", "school", "university",
    "station", "airport", "temple", "church", "mosque",
    "pg", "hostel", "apartment", "residency", "society",
    "habitat", "illuminar", "rv", "R.V.", "college"
]

STOPWORDS = {
    "i", "am", "the", "to", "you", "me",
    "come", "fast", "soon", "please",
    "near", "in", "on", "at", "live", "stay",
    "there", "here", "has", "have", "is", "are",
    "only", "also", "near"
}


def extract_location(text: str):
    if not text:
        return None

    original = text.strip()
    lower = original.lower()

    # --------------------------------------------------
    # 1️⃣ ACRONYM + PLACE (BDA apartments, RV college)
    # --------------------------------------------------
    acronym_pattern = re.compile(
        r"\b([A-Z]{2,5})\s+(apartment|apartments|colony|layout|society|residency|pg|hostel|college|campus|hospital|mall)\b",
        re.IGNORECASE
    )

    match = acronym_pattern.search(original)
    if match:
        return {
            "text": match.group(0).title(),
            "confidence": 0.95
        }

    # --------------------------------------------------
    # 2️⃣ Named place (Church Street, Orion Mall)
    # --------------------------------------------------
    name_pattern = re.compile(
        r"\b([a-z]{2,}(?:\s[a-z]{2,})*)\s("
        + "|".join(PLACE_SUFFIXES)
        + r")\b",
        re.IGNORECASE
    )

    match = name_pattern.search(original)
    if match:
        return {
            "text": match.group(0).title(),
            "confidence": 0.95
        }

    # --------------------------------------------------
    # 3️⃣ PIN fallback
    # --------------------------------------------------
    pin_match = re.search(PIN_REGEX, lower)
    if pin_match:
        return {
            "text": None,
            "pincode": pin_match.group(1),
            "confidence": 0.8
        }

    return None