"""
Semantic Analysis Service
- Headline–body contradiction detection via NLI
- Semantic similarity scoring using Sentence-BERT
- Contextual consistency analysis
"""

from typing import Dict, Any, List, Optional
import numpy as np
from loguru import logger


class SemanticAnalysisService:
    """
    Uses Sentence-BERT and NLI models to detect semantic inconsistencies
    between headline and article body.
    """

    def __init__(self, sbert_model=None, nli_model=None):
        self.sbert = sbert_model
        self.nli = nli_model

    def analyze(self, headline: str, article: str) -> Dict[str, Any]:
        results = {}
        results["headline_body_similarity"] = self._compute_similarity(headline, article)
        results["contradiction_score"] = self._compute_contradiction(headline, article)
        results["semantic_consistency"] = self._semantic_consistency(article)
        results["topic_drift"] = self._topic_drift(headline, article)
        results["highlighted_embeddings"] = self._important_sentences(headline, article)
        return results

    # ── Headline–Body Cosine Similarity ───────────────────────
    def _compute_similarity(self, headline: str, article: str) -> float:
        if self.sbert is None:
            return self._fallback_similarity(headline, article)
        try:
            embs = self.sbert.encode([headline, article[:512]])
            sim = float(np.dot(embs[0], embs[1]) /
                        (np.linalg.norm(embs[0]) * np.linalg.norm(embs[1]) + 1e-9))
            return round(sim, 4)
        except Exception as e:
            logger.warning(f"SBERT similarity failed: {e}")
            return self._fallback_similarity(headline, article)

    def _fallback_similarity(self, headline: str, article: str) -> float:
        """Jaccard similarity as fallback when SBERT is unavailable."""
        h_words = set(headline.lower().split())
        a_words = set(article.lower().split()[:200])
        if not h_words or not a_words:
            return 0.5
        return round(len(h_words & a_words) / len(h_words | a_words), 4)

    # ── NLI-based Contradiction Score ─────────────────────────
    def _compute_contradiction(self, headline: str, article: str) -> float:
        """
        Uses cross-encoder NLI model.
        Returns probability of CONTRADICTION between headline and article opening.
        Labels: contradiction=0, entailment=1, neutral=2 (deberta model).
        """
        if self.nli is None:
            # Heuristic fallback: if similarity is low, assume contradiction
            sim = self._fallback_similarity(headline, article)
            return round(1.0 - sim, 4)
        try:
            # Take first 256 words of article as premise
            premise = " ".join(article.split()[:256])
            scores = self.nli.predict([(premise, headline)])
            # scores shape: (1, 3) — [contradiction, entailment, neutral]
            probs = self._softmax(scores[0])
            contradiction_prob = float(probs[0])
            return round(contradiction_prob, 4)
        except Exception as e:
            logger.warning(f"NLI contradiction failed: {e}")
            sim = self._fallback_similarity(headline, article)
            return round(1.0 - sim, 4)

    def _softmax(self, x):
        e = np.exp(x - np.max(x))
        return e / e.sum()

    # ── Internal Semantic Consistency ─────────────────────────
    def _semantic_consistency(self, article: str) -> float:
        """
        Checks consistency between the first paragraph and the rest.
        Low consistency → potential misinformation.
        """
        if self.sbert is None:
            return 0.7  # neutral default
        try:
            sentences = article.split(". ")
            if len(sentences) < 4:
                return 0.7
            intro = " ".join(sentences[:2])
            body = " ".join(sentences[2:min(10, len(sentences))])
            embs = self.sbert.encode([intro, body])
            sim = float(np.dot(embs[0], embs[1]) /
                        (np.linalg.norm(embs[0]) * np.linalg.norm(embs[1]) + 1e-9))
            return round(sim, 4)
        except Exception as e:
            logger.warning(f"Consistency check failed: {e}")
            return 0.7

    # ── Topic Drift ───────────────────────────────────────────
    def _topic_drift(self, headline: str, article: str) -> float:
        """
        Measures how much the article drifts from the headline topic.
        Returns 0 (no drift) to 1 (high drift).
        """
        sim = self._compute_similarity(headline, article)
        return round(1.0 - sim, 4)

    # ── Important Sentences (for highlighting) ────────────────
    def _important_sentences(self, headline: str, article: str) -> List[Dict[str, Any]]:
        """Returns sentences with their relevance score to the headline."""
        if self.sbert is None:
            return []
        try:
            sentences = [s.strip() for s in article.split(". ") if len(s.strip()) > 20][:15]
            if not sentences:
                return []
            headline_emb = self.sbert.encode([headline])[0]
            sent_embs = self.sbert.encode(sentences)
            results = []
            for i, (sent, emb) in enumerate(zip(sentences, sent_embs)):
                sim = float(np.dot(headline_emb, emb) /
                            (np.linalg.norm(headline_emb) * np.linalg.norm(emb) + 1e-9))
                results.append({"sentence": sent, "relevance_score": round(sim, 4), "index": i})
            results.sort(key=lambda x: x["relevance_score"])
            return results[:5]  # 5 least-relevant (suspicious) sentences
        except Exception as e:
            logger.warning(f"Sentence highlighting failed: {e}")
            return []
