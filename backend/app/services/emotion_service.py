"""
Emotion Manipulation Detection Service
Detects fear, anger, urgency, propaganda, and outrage language.
"""

import re
from typing import Dict, Any
from loguru import logger


EMOTION_LEXICON = {
    "fear": [
        "terror", "terrifying", "horrifying", "deadly", "lethal", "killer",
        "catastrophe", "annihilation", "apocalypse", "extinction", "doom",
        "nightmare", "panic", "peril", "threat", "imminent danger",
    ],
    "anger": [
        "outrage", "furious", "enraged", "disgrace", "unacceptable", "corrupt",
        "criminal", "traitor", "betrayal", "scandal", "shameful", "despicable",
        "hypocrite", "liar", "fraud", "crook",
    ],
    "disgust": [
        "disgusting", "revolting", "sickening", "nauseating", "vile", "filthy",
        "perverted", "abhorrent", "repulsive",
    ],
    "sadness": [
        "devastating", "heartbreaking", "tragic", "mourning", "grief",
        "suffering", "misery", "despair", "hopeless",
    ],
    "surprise": [
        "shocking", "unbelievable", "jaw-dropping", "stunning", "astonishing",
        "bombshell", "explosive", "incredible",
    ],
    "joy": [
        "wonderful", "amazing", "fantastic", "brilliant", "glorious",
        "triumphant", "celebrating", "victory",
    ],
    "trust": [
        "reliable", "credible", "trustworthy", "verified", "confirmed",
        "official", "authentic", "legitimate",
    ],
    "anticipation": [
        "breaking", "soon", "upcoming", "imminent", "watch out",
        "prepare", "brace", "expect",
    ],
}

MANIPULATION_AMPLIFIERS = [
    "!!!",
    r"\b[A-Z]{5,}\b",           # shouting caps
    r"\?\?\?",
    r"WAKE UP",
    r"THEY ARE HIDING",
    r"YOU NEED TO SEE THIS",
    r"SHARE BEFORE IT'S DELETED",
    r"MUST WATCH",
]


class EmotionDetectionService:
    """
    Detects emotional manipulation patterns using:
    1. Transformer emotion classifier (preferred)
    2. Lexicon-based fallback
    """

    def __init__(self, emotion_classifier=None):
        self.classifier = emotion_classifier

    def analyze(self, text: str) -> Dict[str, Any]:
        emotion_scores = self._get_emotion_scores(text)
        manipulation_intensity = self._calc_manipulation_intensity(text, emotion_scores)
        dominant = max(emotion_scores, key=emotion_scores.get)
        amplifier_hits = self._detect_amplifiers(text)
        return {
            "emotion_breakdown": emotion_scores,
            "dominant_emotion": dominant,
            "manipulation_intensity": round(manipulation_intensity, 4),
            "amplifier_count": amplifier_hits,
            "overall_emotion_score": round(
                (emotion_scores.get("fear", 0) * 0.3 +
                 emotion_scores.get("anger", 0) * 0.25 +
                 emotion_scores.get("disgust", 0) * 0.15 +
                 emotion_scores.get("surprise", 0) * 0.1 +
                 manipulation_intensity * 0.2),
                4,
            ),
        }

    # ── Emotion Scoring ───────────────────────────────────────
    def _get_emotion_scores(self, text: str) -> Dict[str, float]:
        if self.classifier:
            return self._transformer_scores(text)
        return self._lexicon_scores(text)

    def _transformer_scores(self, text: str) -> Dict[str, float]:
        try:
            result = self.classifier(text[:512])
            # result = [[{"label": "fear", "score": 0.8}, ...]]
            raw = result[0] if isinstance(result[0], list) else result
            scores = {item["label"].lower(): round(item["score"], 4) for item in raw}
            # Ensure all 8 keys exist
            defaults = {k: 0.0 for k in EMOTION_LEXICON}
            defaults.update(scores)
            return defaults
        except Exception as e:
            logger.warning(f"Transformer emotion failed, using lexicon: {e}")
            return self._lexicon_scores(text)

    def _lexicon_scores(self, text: str) -> Dict[str, float]:
        text_lower = text.lower()
        words = set(text_lower.split())
        scores = {}
        for emotion, lexicon in EMOTION_LEXICON.items():
            hits = sum(1 for word in lexicon if word in text_lower)
            scores[emotion] = round(min(1.0, hits / max(len(lexicon) * 0.15, 1)), 4)
        return scores

    # ── Manipulation Intensity ────────────────────────────────
    def _calc_manipulation_intensity(self, text: str, emotion_scores: Dict) -> float:
        amplifiers = self._detect_amplifiers(text)
        amp_score = min(1.0, amplifiers / 3.0)
        negative_emotions = (
            emotion_scores.get("fear", 0) +
            emotion_scores.get("anger", 0) +
            emotion_scores.get("disgust", 0)
        ) / 3.0
        return (negative_emotions * 0.7 + amp_score * 0.3)

    def _detect_amplifiers(self, text: str) -> int:
        count = 0
        for pattern in MANIPULATION_AMPLIFIERS:
            if re.search(pattern, text, re.IGNORECASE):
                count += 1
        return count
