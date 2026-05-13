"""
Singleton model loader — loads all ML models at startup so
individual requests don't pay the cold-start penalty.
"""

import os
import joblib
import asyncio
from pathlib import Path
from loguru import logger

MODELS_DIR = Path(os.getenv("MODELS_DIR", "./trained_models"))


class ModelLoader:
    """Holds references to all loaded models and vectorizers."""

    def __init__(self):
        self.tfidf_vectorizer = None
        self.logistic_model = None
        self.xgboost_model = None
        self.bilstm_model = None
        self.bert_tokenizer = None
        self.bert_model = None
        self.sbert_model = None
        self.nli_model = None
        self.emotion_classifier = None
        self.label_encoder = None
        self._loaded = False

    async def load_all(self):
        """Load models asynchronously (runs in thread pool to avoid blocking)."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._load_blocking)

    def _load_blocking(self):
        """Synchronous model loading — called from thread pool."""
        logger.info("Loading ML models…")

        # ── Sentence-BERT ─────────────────────────────────────
        try:
            from sentence_transformers import SentenceTransformer, CrossEncoder
            sbert_name = os.getenv("SBERT_MODEL", "all-MiniLM-L6-v2")
            logger.info(f"Loading SBERT: {sbert_name}")
            self.sbert_model = SentenceTransformer(sbert_name)
            nli_name = os.getenv("NLI_MODEL", "cross-encoder/nli-deberta-v3-base")
            logger.info(f"Loading NLI model: {nli_name}")
            self.nli_model = CrossEncoder(nli_name)
        except Exception as e:
            logger.warning(f"SBERT/NLI load failed (will use fallback): {e}")

        # ── Emotion Classifier ────────────────────────────────
        try:
            from transformers import pipeline
            logger.info("Loading emotion classifier…")
            self.emotion_classifier = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                return_all_scores=True,
                truncation=True,
                max_length=512,
            )
        except Exception as e:
            logger.warning(f"Emotion classifier load failed (will use fallback): {e}")

        # ── Classical models (only if saved files exist) ──────
        self._try_load_pkl("tfidf_vectorizer", "tfidf_vectorizer.pkl")
        self._try_load_pkl("logistic_model",   "logistic_model.pkl")
        self._try_load_pkl("xgboost_model",    "xgboost_model.pkl")
        self._try_load_pkl("label_encoder",    "label_encoder.pkl")

        # ── BiLSTM ────────────────────────────────────────────
        bilstm_path = MODELS_DIR / "bilstm_model.h5"
        if bilstm_path.exists():
            try:
                import tensorflow as tf
                self.bilstm_model = tf.keras.models.load_model(str(bilstm_path))
                logger.info("BiLSTM model loaded.")
            except Exception as e:
                logger.warning(f"BiLSTM load failed: {e}")

        # ── BERT Classifier ───────────────────────────────────
        bert_path = MODELS_DIR / "bert_classifier"
        if bert_path.exists():
            try:
                from transformers import AutoTokenizer, AutoModelForSequenceClassification
                self.bert_tokenizer = AutoTokenizer.from_pretrained(str(bert_path))
                self.bert_model = AutoModelForSequenceClassification.from_pretrained(str(bert_path))
                logger.info("BERT classifier loaded.")
            except Exception as e:
                logger.warning(f"BERT load failed: {e}")

        self._loaded = True
        logger.info("Model loading complete.")

    def _try_load_pkl(self, attr: str, filename: str):
        path = MODELS_DIR / filename
        if path.exists():
            try:
                setattr(self, attr, joblib.load(str(path)))
                logger.info(f"Loaded {filename}")
            except Exception as e:
                logger.warning(f"Could not load {filename}: {e}")

    @property
    def is_ready(self):
        return self._loaded
