"""
Text normalization utilities.

- Converts Hindi (Devanagari) → Romanized English (ITRANS)
- Leaves English text unchanged
- Safe to use on mixed-language input
"""

from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate


def normalize_text(text: str) -> str:
    """
    Normalize text for downstream NLP.

    Hindi (देवनागरी) → romanized English
    English → unchanged
    """
    if not text or not isinstance(text, str):
        return text

    try:
        # If text contains Devanagari, transliterate it
        return transliterate(text, sanscript.DEVANAGARI, sanscript.ITRANS)
    except Exception:
        # If anything fails, return original text safely
        return text