"""
Explainable AI Service
SHAP + LIME explanations for the classical ML pipeline.
Token-level highlighting for attention-based models.
"""

import numpy as np
from typing import Dict, Any, List, Optional
from loguru import logger


class ExplainabilityService:

    def __init__(self, vectorizer=None, logistic_model=None):
        self.vectorizer = vectorizer
        self.logistic_model = logistic_model

    # ── SHAP Explanation ─────────────────────────────────────
    def shap_explain(self, text: str) -> Dict[str, Any]:
        """
        Uses SHAP to compute feature importance for the TF-IDF + Logistic pipeline.
        Falls back to coefficient-based explanation if SHAP unavailable.
        """
        if self.vectorizer is None or self.logistic_model is None:
            return self._coeff_explanation(text)

        try:
            import shap
            def predict_proba(texts):
                X = self.vectorizer.transform(texts)
                return self.logistic_model.predict_proba(X)

            explainer = shap.Explainer(predict_proba, shap.maskers.Text())
            shap_values = explainer([text])

            # Extract top features
            values = shap_values.values[0]
            tokens = shap_values.data[0]
            top_indices = np.argsort(np.abs(values[:, 1]))[-20:][::-1]
            feature_contributions = {
                tokens[i]: round(float(values[i, 1]), 4)
                for i in top_indices
                if len(tokens[i].strip()) > 1
            }
            return {
                "method": "SHAP",
                "feature_contributions": feature_contributions,
                "shap_values": [round(float(v), 4) for v in values[:50, 1].tolist()],
            }
        except Exception as e:
            logger.warning(f"SHAP failed: {e}")
            return self._coeff_explanation(text)

    # ── LIME Explanation ──────────────────────────────────────
    def lime_explain(self, text: str, num_features: int = 15) -> Dict[str, Any]:
        if self.vectorizer is None or self.logistic_model is None:
            return {"method": "unavailable", "feature_contributions": {}}

        try:
            from lime.lime_text import LimeTextExplainer

            def predict_fn(texts):
                X = self.vectorizer.transform(texts)
                return self.logistic_model.predict_proba(X)

            explainer = LimeTextExplainer(class_names=["REAL", "FAKE"])
            exp = explainer.explain_instance(
                text, predict_fn, num_features=num_features, num_samples=500
            )
            contributions = {word: round(weight, 4) for word, weight in exp.as_list()}
            return {
                "method": "LIME",
                "feature_contributions": contributions,
                "prediction_local": exp.predict_proba.tolist(),
            }
        except Exception as e:
            logger.warning(f"LIME failed: {e}")
            return {"method": "unavailable", "feature_contributions": {}}

    # ── Coefficient-Based Explanation (no extra deps) ─────────
    def _coeff_explanation(self, text: str) -> Dict[str, Any]:
        if self.vectorizer is None or self.logistic_model is None:
            return {
                "method": "heuristic",
                "feature_contributions": self._heuristic_contributions(text),
            }
        try:
            X = self.vectorizer.transform([text])
            feature_names = self.vectorizer.get_feature_names_out()
            coefficients = self.logistic_model.coef_[0]
            # Get non-zero features for this text
            _, non_zero_cols = X.nonzero()
            contributions = {}
            for col in non_zero_cols:
                word = feature_names[col]
                coeff = float(coefficients[col])
                tf_val = float(X[0, col])
                contributions[word] = round(coeff * tf_val, 4)
            # Sort by absolute contribution
            sorted_contribs = dict(
                sorted(contributions.items(), key=lambda x: abs(x[1]), reverse=True)[:20]
            )
            return {"method": "coefficients", "feature_contributions": sorted_contribs}
        except Exception as e:
            logger.warning(f"Coefficient explanation failed: {e}")
            return {
                "method": "heuristic",
                "feature_contributions": self._heuristic_contributions(text),
            }

    # ── Heuristic Contributions ───────────────────────────────
    def _heuristic_contributions(self, text: str) -> Dict[str, float]:
        """Assigns scores based on known suspicious word patterns."""
        from app.services.linguistic_service import (
            CLICKBAIT_PATTERNS, PROPAGANDA_PHRASES, FEAR_WORDS, ANGER_WORDS
        )
        import re
        words = text.lower().split()
        contributions = {}
        suspicious = set(FEAR_WORDS + ANGER_WORDS + PROPAGANDA_PHRASES)
        for word in words:
            clean = re.sub(r"[^a-z]", "", word)
            if clean in suspicious and clean not in contributions:
                contributions[clean] = 0.6
        return dict(list(contributions.items())[:20])

    # ── Word-Level Highlighting ───────────────────────────────
    def highlight_text(
        self, text: str, feature_contributions: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """
        Returns a list of {word, score, type} dicts for frontend highlighting.
        Positive score → fake indicator. Negative → real indicator.
        """
        words = text.split()
        highlighted = []
        for word in words:
            clean = re.sub(r"[^a-zA-Z0-9]", "", word).lower()
            score = feature_contributions.get(clean, 0.0)
            highlighted.append({
                "word": word,
                "score": score,
                "type": "fake_indicator" if score > 0.1 else (
                    "real_indicator" if score < -0.1 else "neutral"
                ),
            })
        return highlighted


import re  # ensure re is imported at module level for highlight_text
