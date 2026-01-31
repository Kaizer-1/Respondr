# whisper_asr/src/nlp/keyword_sets.py

EMERGENCY_KEYWORDS = {
    "ambulance": {
        "strong": [
            "bleeding", "unconscious", "heart attack", "breathless",
            "accident", "collapsed", "seizure", "injured", "burn", "dying"
        ],
        "weak": [
            "pain", "hurt", "fell", "fever", "vomiting", "blood"
        ]
    },
    "fire": {
        "strong": [
            "fire", "smoke", "blast", "explosion", "burning"
        ],
        "weak": [
            "gas", "leak", "short circuit"
        ]
    },
    "police": {
        "strong": [
            "theft", "robbery", "murder", "attack", "knife",
            "gun", "assault", "threat"
        ],
        "weak": [
            "fight", "stolen", "missing", "argument"
        ]
    }
}

PRIORITY_KEYWORDS = {
    "critical": [
        "bleeding", "unconscious", "not breathing",
        "heart attack", "fire", "explosion", "gun"
    ],
    "high": [
        "accident", "injured", "burn", "attack"
    ],
    "medium": [
        "pain", "fell", "fight", "stolen"
    ]
}