"""
AI-Generated Text Detection Service
Uses stylometric analysis, burstiness, perplexity proxies, and
repetition patterns to estimate if an article was machine-generated.
"""

import re
import math
from typing import Dict, Any
from collections import Counter
from nltk.tokenize import word_tokenize, sent_tokenize


class AITextDetectionService:
    """
    Detects AI-generated news using:
    - Burstiness (variance in sentence lengths — AI text is unusually uniform)
    - Type-Token Ratio (lexical diversity)
    - Repetition patterns
    - Average sentence complexity
    - Perplexity proxy (using bigram entropy)
    """

    def analyze(self, article: str) -> Dict[str, Any]:
        signals = {}
        signals["burstiness"] = self._burstiness(article)
        signals["ttr"] = self._type_token_ratio(article)
        signals["repetition_score"] = self._repetition(article)
        signals["avg_sentence_length"] = self._avg_sent_len(article)
        signals["bigram_entropy"] = self._bigram_entropy(article)
        signals["paragraph_similarity"] = self._paragraph_similarity(article)

        probability = self._compute_probability(signals)
        return {
            "ai_generated_probability": round(probability, 4),
            "ai_signals": signals,
            "verdict": self._verdict(probability),
        }

    # ── Burstiness ────────────────────────────────────────────
    def _burstiness(self, text: str) -> float:
        """
        Real human writing has high burstiness (mixed short/long sentences).
        AI text tends to have uniform sentence lengths → low burstiness.
        Returns value closer to -1 for AI-like uniformity.
        """
        sentences = sent_tokenize(text)
        if len(sentences) < 4:
            return 0.0
        lengths = [len(s.split()) for s in sentences]
        mean = sum(lengths) / len(lengths)
        std = math.sqrt(sum((l - mean) ** 2 for l in lengths) / len(lengths))
        burstiness = (std - mean) / (std + mean + 1e-9)
        return round(burstiness, 4)

    # ── Type-Token Ratio ──────────────────────────────────────
    def _type_token_ratio(self, text: str) -> float:
        tokens = [w.lower() for w in word_tokenize(text) if w.isalpha()]
        if not tokens:
            return 1.0
        return round(len(set(tokens)) / len(tokens), 4)

    # ── Repetition Score ──────────────────────────────────────
    def _repetition(self, text: str) -> float:
        """Fraction of bigrams that appear more than once — higher = more repetitive."""
        words = [w.lower() for w in word_tokenize(text) if w.isalpha()]
        if len(words) < 4:
            return 0.0
        bigrams = [(words[i], words[i + 1]) for i in range(len(words) - 1)]
        counts = Counter(bigrams)
        repeated = sum(1 for c in counts.values() if c > 1)
        return round(repeated / max(len(counts), 1), 4)

    # ── Average Sentence Length ───────────────────────────────
    def _avg_sent_len(self, text: str) -> float:
        sentences = sent_tokenize(text)
        if not sentences:
            return 0.0
        return round(sum(len(s.split()) for s in sentences) / len(sentences), 2)

    # ── Bigram Entropy (perplexity proxy) ─────────────────────
    def _bigram_entropy(self, text: str) -> float:
        """
        Higher entropy = more unpredictable text (human-like).
        Lower entropy = repetitive, predictable (AI-like).
        """
        words = [w.lower() for w in word_tokenize(text) if w.isalpha()]
        if len(words) < 4:
            return 3.0
        bigrams = [(words[i], words[i + 1]) for i in range(len(words) - 1)]
        counts = Counter(bigrams)
        total = sum(counts.values())
        entropy = -sum(
            (c / total) * math.log2(c / total + 1e-9)
            for c in counts.values()
        )
        return round(entropy, 4)

    # ── Paragraph Similarity ──────────────────────────────────
    def _paragraph_similarity(self, text: str) -> float:
        """AI text often has very similar paragraph structures."""
        paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 50]
        if len(paragraphs) < 2:
            return 0.0
        lengths = [len(p.split()) for p in paragraphs]
        mean = sum(lengths) / len(lengths)
        std = math.sqrt(sum((l - mean) ** 2 for l in lengths) / len(lengths))
        cv = std / (mean + 1e-9)  # coefficient of variation — low = AI-like
        return round(max(0, 1 - cv), 4)

    # ── Probability Computation ───────────────────────────────
    def _compute_probability(self, signals: Dict) -> float:
        """
        Combines signals into a single AI probability score.
        Weights tuned empirically.
        """
        burstiness = signals["burstiness"]
        ttr = signals["ttr"]
        repetition = signals["repetition_score"]
        entropy = signals["bigram_entropy"]
        para_sim = signals["paragraph_similarity"]
        avg_len = signals["avg_sentence_length"]

        # Low burstiness → AI-like
        burst_signal = max(0, -burstiness)  # range 0-1

        # Lower TTR → less diverse → more AI-like
        ttr_signal = max(0, 0.85 - ttr)  # AI text often has TTR < 0.85

        # Higher repetition → AI
        rep_signal = repetition

        # Low entropy → AI
        entropy_signal = max(0, (5 - entropy) / 5)

        # High paragraph similarity → AI
        para_signal = para_sim

        # Very uniform sentence length (avg close to 20-25 words) → AI
        len_signal = max(0, 1 - abs(avg_len - 22) / 22)

        score = (
            burst_signal  * 0.25 +
            ttr_signal    * 0.20 +
            rep_signal    * 0.20 +
            entropy_signal* 0.15 +
            para_signal   * 0.10 +
            len_signal    * 0.10
        )
        return min(1.0, score)

    def _verdict(self, probability: float) -> str:
        if probability >= 0.7:
            return "Likely AI-Generated"
        if probability >= 0.4:
            return "Possibly AI-Assisted"
        return "Likely Human-Written"
