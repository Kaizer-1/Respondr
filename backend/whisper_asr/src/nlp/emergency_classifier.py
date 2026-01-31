from collections import defaultdict
from .keyword_sets import EMERGENCY_KEYWORDS, PRIORITY_KEYWORDS
from .location_extractor import extract_location
from .semantic_fallback import semantic_classify


class EmergencyClassifier:
    def classify(self, text: str):
        if not text:
            return self._empty()

        text = text.lower()
        scores = defaultdict(int)
        keywords = []

        # ------------------------------------
        # 1️⃣ Keyword-based scoring (PRIMARY)
        # ------------------------------------
        for etype, groups in EMERGENCY_KEYWORDS.items():
            for kw in groups.get("strong", []):
                if kw in text:
                    scores[etype] += 3
                    keywords.append(kw)

            for kw in groups.get("weak", []):
                if kw in text:
                    scores[etype] += 1
                    keywords.append(kw)

        location = extract_location(text)

        # ------------------------------------
        # 2️⃣ Semantic fallback (ONLY if no keywords)
        # ------------------------------------
        if not scores:
            intent, score = semantic_classify(text)

            if score > 0.6:
                return {
                    "type": intent,
                    "priority": "medium",
                    "confidence": round(score, 2),
                    "keywords": [],
                    "location": location
                }

            return self._empty()

        # ------------------------------------
        # 3️⃣ Pick best keyword-based intent
        # ------------------------------------
        etype = max(scores, key=scores.get)
        score = scores[etype]

        # ------------------------------------
        # 4️⃣ Priority detection
        # ------------------------------------
        priority = "low"
        for level, kws in PRIORITY_KEYWORDS.items():
            if any(k in text for k in kws):
                priority = level
                break

        confidence = min(0.5 + 0.1 * score, 0.95)

        return {
            "type": etype,
            "priority": priority,
            "confidence": round(confidence, 2),
            "keywords": list(set(keywords)),
            "location": location
        }

    def _empty(self):
        return {
            "type": "unknown",
            "priority": "low",
            "confidence": 0.0,
            "keywords": [],
            "location": None
        }