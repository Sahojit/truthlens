"""
Multi-Model Ensemble Prediction Service
Combines: Logistic Regression, XGBoost, BiLSTM, BERT
Weights: 0.20, 0.20, 0.25, 0.35
"""

import numpy as np
from typing import Dict, Any, Optional, Tuple
from loguru import logger


ENSEMBLE_WEIGHTS = {
    "logistic": 0.20,
    "xgboost":  0.20,
    "bilstm":   0.25,
    "bert":     0.35,
}


class EnsembleService:

    def __init__(self, model_loader):
        self.loader = model_loader

    def predict(self, headline: str, article: str) -> Dict[str, Any]:
        """
        Runs all available models and returns weighted ensemble prediction.
        Gracefully handles missing models.
        """
        full_text = f"{headline} {article}"
        model_scores = {}

        # ── Model 1: TF-IDF + Logistic Regression ────────────
        lr_score = self._predict_logistic(full_text)
        if lr_score is not None:
            model_scores["logistic"] = lr_score

        # ── Model 2: XGBoost ──────────────────────────────────
        xgb_score = self._predict_xgboost(full_text)
        if xgb_score is not None:
            model_scores["xgboost"] = xgb_score

        # ── Model 3: BiLSTM ───────────────────────────────────
        bilstm_score = self._predict_bilstm(full_text)
        if bilstm_score is not None:
            model_scores["bilstm"] = bilstm_score

        # ── Model 4: BERT ─────────────────────────────────────
        bert_score = self._predict_bert(full_text)
        if bert_score is not None:
            model_scores["bert"] = bert_score

        # ── Weighted Ensemble ─────────────────────────────────
        if not model_scores:
            # No models available — return neutral heuristic
            fake_prob = 0.5
        else:
            available_weights = {k: ENSEMBLE_WEIGHTS[k] for k in model_scores}
            total_weight = sum(available_weights.values())
            fake_prob = sum(
                model_scores[k] * available_weights[k] / total_weight
                for k in model_scores
            )

        fake_prob = float(np.clip(fake_prob, 0.0, 1.0))
        real_prob = 1.0 - fake_prob
        prediction = "FAKE" if fake_prob >= 0.5 else "REAL"
        confidence = max(fake_prob, real_prob)

        return {
            "prediction": prediction,
            "confidence": round(confidence, 4),
            "fake_probability": round(fake_prob, 4),
            "real_probability": round(real_prob, 4),
            "model_scores": {
                "logistic_regression": round(model_scores.get("logistic", -1), 4),
                "xgboost": round(model_scores.get("xgboost", -1), 4),
                "bilstm": round(model_scores.get("bilstm", -1), 4),
                "bert": round(model_scores.get("bert", -1), 4),
                "ensemble": round(fake_prob, 4),
            },
        }

    # ── Logistic Regression ───────────────────────────────────
    def _predict_logistic(self, text: str) -> Optional[float]:
        if self.loader.tfidf_vectorizer is None or self.loader.logistic_model is None:
            return self._heuristic_score(text)
        try:
            from app.services.preprocessing_service import TextPreprocessor
            cleaned = TextPreprocessor.full_pipeline(text)
            X = self.loader.tfidf_vectorizer.transform([cleaned])
            prob = self.loader.logistic_model.predict_proba(X)[0]
            # prob[1] = FAKE probability (class ordering: REAL=0, FAKE=1)
            return float(prob[1])
        except Exception as e:
            logger.warning(f"Logistic prediction failed: {e}")
            return self._heuristic_score(text)

    # ── XGBoost ───────────────────────────────────────────────
    def _predict_xgboost(self, text: str) -> Optional[float]:
        if self.loader.xgboost_model is None:
            return None
        try:
            from app.services.preprocessing_service import TextPreprocessor
            cleaned = TextPreprocessor.full_pipeline(text)
            if self.loader.tfidf_vectorizer:
                X = self.loader.tfidf_vectorizer.transform([cleaned])
                prob = self.loader.xgboost_model.predict_proba(X)[0]
                return float(prob[1])
            return None
        except Exception as e:
            logger.warning(f"XGBoost prediction failed: {e}")
            return None

    # ── BiLSTM ────────────────────────────────────────────────
    def _predict_bilstm(self, text: str) -> Optional[float]:
        if self.loader.bilstm_model is None:
            return None
        try:
            import tensorflow as tf
            from tensorflow.keras.preprocessing.sequence import pad_sequences
            # Tokenise to integers (simple hash-based approach when tokenizer absent)
            tokens = text.lower().split()[:200]
            token_ids = [hash(t) % 10000 for t in tokens]
            padded = pad_sequences([token_ids], maxlen=200, padding="post")
            prob = float(self.loader.bilstm_model.predict(padded, verbose=0)[0][0])
            return prob
        except Exception as e:
            logger.warning(f"BiLSTM prediction failed: {e}")
            return None

    # ── BERT ──────────────────────────────────────────────────
    def _predict_bert(self, text: str) -> Optional[float]:
        if self.loader.bert_model is None:
            return None
        try:
            import torch
            inputs = self.loader.bert_tokenizer(
                text[:512],
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True,
            )
            with torch.no_grad():
                outputs = self.loader.bert_model(**inputs)
            logits = outputs.logits.numpy()[0]
            probs = self._softmax(logits)
            return float(probs[1])  # class 1 = FAKE
        except Exception as e:
            logger.warning(f"BERT prediction failed: {e}")
            return None

    # ── Heuristic fallback ────────────────────────────────────
    def _heuristic_score(self, text: str) -> float:
        """
        Rule-based fake news score used when models aren't trained yet.
        Based on clickbait, emotional, and propaganda signals.
        """
        from app.services.linguistic_service import (
            CLICKBAIT_PATTERNS, PROPAGANDA_PHRASES, FEAR_WORDS
        )
        import re
        text_lower = text.lower()
        score = 0.0
        for p in CLICKBAIT_PATTERNS:
            if re.search(p, text_lower):
                score += 0.05
        for p in PROPAGANDA_PHRASES:
            if p in text_lower:
                score += 0.04
        for w in FEAR_WORDS:
            if w in text_lower:
                score += 0.02
        # Excessive caps
        cap_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        score += cap_ratio * 0.3
        return min(0.9, score)

    def _softmax(self, x):
        e = np.exp(x - np.max(x))
        return e / e.sum()
