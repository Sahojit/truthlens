"""
Pydantic models for API request/response validation.
"""

from pydantic import BaseModel, HttpUrl, validator
from typing import Optional, Dict, Any, List
from datetime import datetime


# ── Prediction ────────────────────────────────────────────────
class PredictRequest(BaseModel):
    headline: str
    article: str
    source_url: Optional[str] = None

    @validator("headline")
    def headline_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Headline cannot be empty.")
        return v.strip()

    @validator("article")
    def article_min_length(cls, v):
        if len(v.split()) < 10:
            raise ValueError("Article must contain at least 10 words.")
        return v.strip()


class EmotionBreakdown(BaseModel):
    fear: float = 0.0
    anger: float = 0.0
    joy: float = 0.0
    sadness: float = 0.0
    surprise: float = 0.0
    disgust: float = 0.0
    trust: float = 0.0
    anticipation: float = 0.0


class ModelScores(BaseModel):
    logistic_regression: float = 0.0
    xgboost: float = 0.0
    bilstm: float = 0.0
    bert: float = 0.0
    ensemble: float = 0.0


class LinguisticFeatures(BaseModel):
    word_count: int = 0
    avg_sentence_length: float = 0.0
    lexical_diversity: float = 0.0
    readability_score: float = 0.0
    exclamation_count: int = 0
    question_count: int = 0
    caps_ratio: float = 0.0
    clickbait_score: float = 0.0
    propaganda_score: float = 0.0
    urgency_score: float = 0.0
    sensationalism_score: float = 0.0


class PredictResponse(BaseModel):
    prediction_id: str
    prediction: str                      # "FAKE" | "REAL"
    confidence: float                    # 0–1
    fake_probability: float
    real_probability: float
    emotion_score: float                 # overall manipulation intensity
    credibility_score: float             # source trust
    contradiction_score: float           # headline vs body
    ai_generated_probability: float
    manipulation_intensity: float
    sentiment_polarity: float            # -1 to 1
    subjectivity_score: float            # 0 to 1
    emotion_breakdown: EmotionBreakdown
    model_scores: ModelScores
    linguistic_features: LinguisticFeatures
    feature_importance: Dict[str, float]
    suspicious_phrases: List[str]
    highlighted_text: List[Dict[str, Any]]  # [{word, score, type}]
    entity_graph: Dict[str, Any]
    shap_values: Optional[List[float]] = None
    processing_time_ms: float
    created_at: datetime


# ── Auth ──────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    email: str
    username: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


# ── Analytics ─────────────────────────────────────────────────
class AnalyticsSummary(BaseModel):
    total_predictions: int
    fake_count: int
    real_count: int
    fake_percentage: float
    avg_confidence: float
    avg_emotion_score: float
    top_suspicious_domains: List[Dict[str, Any]]
    predictions_over_time: List[Dict[str, Any]]
    emotion_distribution: Dict[str, float]
    model_accuracy_comparison: Dict[str, float]
