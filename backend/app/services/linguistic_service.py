"""
Linguistic Feature Extraction Service
Extracts 20+ features: clickbait, propaganda, sentiment, readability, etc.
"""

import re
import math
from typing import Dict, Any, List, Tuple
from collections import Counter

import nltk
from textblob import TextBlob
from nltk.tokenize import word_tokenize, sent_tokenize

# ── Lexicons ──────────────────────────────────────────────────
CLICKBAIT_PATTERNS = [
    r"\byou won'?t believe\b", r"\bshocking\b", r"\bmind-?blowing\b",
    r"\bbreaking\b", r"\bexclusive\b", r"\burgent\b", r"\bwow\b",
    r"\bincredible\b", r"\bamazing truth\b", r"\bsecret revealed\b",
    r"\bthey don'?t want you to know\b", r"\bmust see\b", r"\bviral\b",
    r"\btrending\b", r"\bwhat happened next\b", r"\bnumber \d+ will shock\b",
]

PROPAGANDA_PHRASES = [
    "mainstream media", "deep state", "globalist", "fake news",
    "they don't want you", "wake up sheeple", "the truth is",
    "elites", "new world order", "agenda", "cover-up", "false flag",
    "government conspiracy", "big pharma", "controlled narrative",
    "psychological operation", "shadow government",
]

FEAR_WORDS = [
    "terror", "threat", "danger", "attack", "catastrophe", "disaster",
    "crisis", "emergency", "panic", "horror", "destroy", "collapse",
    "annihilate", "massacre", "extinction", "chaos", "apocalypse",
]

ANGER_WORDS = [
    "outrage", "furious", "disgusting", "unacceptable", "scandal",
    "corrupt", "traitor", "betray", "hypocrite", "fraud", "lie", "liar",
]

URGENCY_PHRASES = [
    r"\bright now\b", r"\bbreaking\b", r"\bimmediately\b", r"\burgent\b",
    r"\blast chance\b", r"\btime is running out\b", r"\bact now\b",
    r"\bdo it today\b", r"\bbefore it'?s too late\b",
]

SENSATIONAL_WORDS = [
    "bombshell", "explosive", "jaw-dropping", "earth-shattering",
    "unprecedented", "historic", "massive", "enormous", "stunning",
    "spectacular", "breathtaking", "sensational",
]


class LinguisticFeatureExtractor:
    """Extracts a rich set of linguistic features from news text."""

    def extract_all(self, headline: str, article: str) -> Dict[str, Any]:
        full_text = f"{headline} {article}"

        features = {}
        features.update(self._basic_stats(full_text))
        features.update(self._readability(full_text))
        features.update(self._sentiment(full_text))
        features.update(self._clickbait(headline, full_text))
        features.update(self._propaganda(full_text))
        features.update(self._emotional_language(full_text))
        features.update(self._punctuation_abuse(full_text))
        features.update(self._caps_analysis(full_text))
        features.update(self._lexical_diversity(full_text))
        features.update(self._burstiness(article))
        features["suspicious_phrases"] = self._find_suspicious_phrases(full_text)
        return features

    # ── Basic Stats ───────────────────────────────────────────
    def _basic_stats(self, text: str) -> Dict[str, Any]:
        words = word_tokenize(text.lower())
        sentences = sent_tokenize(text)
        word_count = len([w for w in words if w.isalpha()])
        sent_count = max(len(sentences), 1)
        return {
            "word_count": word_count,
            "sentence_count": sent_count,
            "avg_sentence_length": round(word_count / sent_count, 2),
            "avg_word_length": round(
                sum(len(w) for w in words if w.isalpha()) / max(word_count, 1), 2
            ),
        }

    # ── Flesch Reading Ease ───────────────────────────────────
    def _readability(self, text: str) -> Dict[str, float]:
        words = [w for w in word_tokenize(text) if w.isalpha()]
        sentences = sent_tokenize(text)
        syllables = sum(self._count_syllables(w) for w in words)
        word_count = max(len(words), 1)
        sent_count = max(len(sentences), 1)
        flesch = (
            206.835
            - 1.015 * (word_count / sent_count)
            - 84.6 * (syllables / word_count)
        )
        return {"readability_score": round(max(0, min(100, flesch)), 2)}

    def _count_syllables(self, word: str) -> int:
        word = word.lower()
        count = len(re.findall(r"[aeiouy]+", word))
        if word.endswith("e"):
            count -= 1
        return max(1, count)

    # ── Sentiment ─────────────────────────────────────────────
    def _sentiment(self, text: str) -> Dict[str, float]:
        blob = TextBlob(text[:3000])
        return {
            "sentiment_polarity": round(blob.sentiment.polarity, 4),
            "subjectivity_score": round(blob.sentiment.subjectivity, 4),
        }

    # ── Clickbait ─────────────────────────────────────────────
    def _clickbait(self, headline: str, full_text: str) -> Dict[str, float]:
        text_lower = full_text.lower()
        matches = sum(
            1 for p in CLICKBAIT_PATTERNS if re.search(p, text_lower, re.IGNORECASE)
        )
        score = min(1.0, matches / max(len(CLICKBAIT_PATTERNS) * 0.3, 1))
        return {"clickbait_score": round(score, 4)}

    # ── Propaganda ────────────────────────────────────────────
    def _propaganda(self, text: str) -> Dict[str, float]:
        text_lower = text.lower()
        matches = sum(1 for p in PROPAGANDA_PHRASES if p in text_lower)
        score = min(1.0, matches / max(len(PROPAGANDA_PHRASES) * 0.2, 1))
        return {"propaganda_score": round(score, 4)}

    # ── Emotional Language ────────────────────────────────────
    def _emotional_language(self, text: str) -> Dict[str, float]:
        text_lower = text.lower()
        words = word_tokenize(text_lower)
        word_set = set(words)
        fear_hits = sum(1 for w in FEAR_WORDS if w in word_set)
        anger_hits = sum(1 for w in ANGER_WORDS if w in word_set)
        urgency_hits = sum(
            1 for p in URGENCY_PHRASES if re.search(p, text_lower, re.IGNORECASE)
        )
        sensational_hits = sum(1 for w in SENSATIONAL_WORDS if w in word_set)
        total = fear_hits + anger_hits + urgency_hits + sensational_hits
        return {
            "fear_word_count": fear_hits,
            "anger_word_count": anger_hits,
            "urgency_score": round(min(1.0, urgency_hits / 3), 4),
            "sensationalism_score": round(min(1.0, sensational_hits / 4), 4),
            "emotional_intensity": round(min(1.0, total / 10), 4),
        }

    # ── Punctuation ───────────────────────────────────────────
    def _punctuation_abuse(self, text: str) -> Dict[str, int]:
        return {
            "exclamation_count": text.count("!"),
            "question_count": text.count("?"),
            "ellipsis_count": text.count("..."),
            "all_caps_words": len(re.findall(r"\b[A-Z]{2,}\b", text)),
        }

    # ── CAPS Ratio ────────────────────────────────────────────
    def _caps_analysis(self, text: str) -> Dict[str, float]:
        alpha_chars = [c for c in text if c.isalpha()]
        if not alpha_chars:
            return {"caps_ratio": 0.0}
        caps_ratio = sum(1 for c in alpha_chars if c.isupper()) / len(alpha_chars)
        return {"caps_ratio": round(caps_ratio, 4)}

    # ── Lexical Diversity ─────────────────────────────────────
    def _lexical_diversity(self, text: str) -> Dict[str, float]:
        words = [w.lower() for w in word_tokenize(text) if w.isalpha()]
        if not words:
            return {"lexical_diversity": 0.0}
        return {"lexical_diversity": round(len(set(words)) / len(words), 4)}

    # ── Burstiness (variance in sentence lengths → AI-gen indicator) ──
    def _burstiness(self, text: str) -> Dict[str, float]:
        sentences = sent_tokenize(text)
        if len(sentences) < 2:
            return {"burstiness": 0.0}
        lengths = [len(s.split()) for s in sentences]
        mean = sum(lengths) / len(lengths)
        variance = sum((l - mean) ** 2 for l in lengths) / len(lengths)
        std = math.sqrt(variance)
        burstiness = (std - mean) / (std + mean + 1e-9)
        return {"burstiness": round(burstiness, 4)}

    # ── Suspicious Phrase Collector ───────────────────────────
    def _find_suspicious_phrases(self, text: str) -> List[str]:
        found = []
        text_lower = text.lower()
        for phrase in PROPAGANDA_PHRASES:
            if phrase in text_lower:
                found.append(phrase)
        for pattern in CLICKBAIT_PATTERNS:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                found.append(match.group(0))
        return list(set(found))[:20]  # cap at 20
