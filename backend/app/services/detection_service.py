"""
Main Detection Orchestrator
Coordinates all sub-services and returns a unified prediction result.
"""

import time
import uuid
from typing import Optional
from loguru import logger

from app.services.ensemble_service import EnsembleService
from app.services.semantic_service import SemanticAnalysisService
from app.services.linguistic_service import LinguisticFeatureExtractor
from app.services.emotion_service import EmotionDetectionService
from app.services.credibility_service import CredibilityService
from app.services.ai_detection_service import AITextDetectionService
from app.services.graph_service import GraphAnalysisService
from app.services.explainability_service import ExplainabilityService
from app.models.request_models import PredictResponse


class DetectionService:
    """
    Orchestrates all detection services for a single prediction request.
    """

    def __init__(self, model_loader):
        self.ensemble = EnsembleService(model_loader)
        self.semantic = SemanticAnalysisService(
            sbert_model=getattr(model_loader, "sbert_model", None),
            nli_model=getattr(model_loader, "nli_model", None),
        )
        self.linguistic = LinguisticFeatureExtractor()
        self.emotion = EmotionDetectionService(
            emotion_classifier=getattr(model_loader, "emotion_classifier", None)
        )
        self.credibility = CredibilityService()
        self.ai_detector = AITextDetectionService()
        self.graph = GraphAnalysisService()
        self.explainer = ExplainabilityService(
            vectorizer=getattr(model_loader, "tfidf_vectorizer", None),
            logistic_model=getattr(model_loader, "logistic_model", None),
        )

    async def predict(
        self, headline: str, article: str, source_url: Optional[str] = None
    ) -> dict:
        t0 = time.time()
        pid = str(uuid.uuid4())
        logger.info(f"[{pid}] Starting prediction…")

        # ── Run all services ──────────────────────────────────
        ensemble_result   = self.ensemble.predict(headline, article)
        semantic_result   = self.semantic.analyze(headline, article)
        linguistic_result = self.linguistic.extract_all(headline, article)
        emotion_result    = self.emotion.analyze(f"{headline} {article}")
        cred_result       = self.credibility.score(source_url)
        ai_result         = self.ai_detector.analyze(article)
        graph_result      = self.graph.build_entity_graph(headline, article)
        explain_result    = self.explainer.shap_explain(f"{headline} {article}")

        # ── Highlighted text ──────────────────────────────────
        highlighted = self.explainer.highlight_text(
            article[:2000], explain_result.get("feature_contributions", {})
        )

        processing_ms = round((time.time() - t0) * 1000, 2)
        logger.info(f"[{pid}] Prediction complete in {processing_ms}ms")

        from datetime import datetime

        return {
            "prediction_id": pid,
            "prediction": ensemble_result["prediction"],
            "confidence": ensemble_result["confidence"],
            "fake_probability": ensemble_result["fake_probability"],
            "real_probability": ensemble_result["real_probability"],

            # Emotion
            "emotion_score": emotion_result["overall_emotion_score"],
            "manipulation_intensity": emotion_result["manipulation_intensity"],
            "emotion_breakdown": emotion_result["emotion_breakdown"],

            # Credibility
            "credibility_score": cred_result["trust_score"],
            "credibility_info": cred_result,

            # Semantic
            "contradiction_score": semantic_result["contradiction_score"],
            "headline_body_similarity": semantic_result["headline_body_similarity"],
            "semantic_consistency": semantic_result["semantic_consistency"],
            "topic_drift": semantic_result["topic_drift"],

            # AI detection
            "ai_generated_probability": ai_result["ai_generated_probability"],
            "ai_verdict": ai_result["verdict"],
            "ai_signals": ai_result["ai_signals"],

            # Linguistic
            "sentiment_polarity": linguistic_result.get("sentiment_polarity", 0),
            "subjectivity_score": linguistic_result.get("subjectivity_score", 0),
            "linguistic_features": {
                k: v for k, v in linguistic_result.items()
                if k not in ("suspicious_phrases", "sentiment_polarity", "subjectivity_score")
            },
            "suspicious_phrases": linguistic_result.get("suspicious_phrases", []),

            # Models
            "model_scores": ensemble_result["model_scores"],

            # Explainability
            "feature_importance": explain_result.get("feature_contributions", {}),
            "shap_values": explain_result.get("shap_values"),
            "highlighted_text": highlighted[:100],  # cap for response size

            # Graph
            "entity_graph": graph_result,

            # Meta
            "processing_time_ms": processing_ms,
            "created_at": datetime.utcnow(),
        }
