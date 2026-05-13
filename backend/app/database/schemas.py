"""
MongoDB document schemas (Pydantic models for DB layer).
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_encoder__(cls):
        return str


# ── Users ─────────────────────────────────────────────────────
class UserDB(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    email: str
    username: str
    hashed_password: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    total_predictions: int = 0

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


# ── Prediction Record ─────────────────────────────────────────
class PredictionDB(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: Optional[str] = None
    headline: str
    article: str
    source_url: Optional[str] = None
    prediction: str                # "FAKE" | "REAL"
    confidence: float
    emotion_score: float
    credibility_score: float
    contradiction_score: float
    ai_generated_probability: float
    manipulation_intensity: float
    sentiment_polarity: float
    subjectivity_score: float
    linguistic_features: Dict[str, Any] = {}
    emotion_breakdown: Dict[str, float] = {}
    feature_importance: Dict[str, float] = {}
    suspicious_phrases: List[str] = []
    entity_graph: Dict[str, Any] = {}
    model_scores: Dict[str, float] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


# ── Source Credibility ────────────────────────────────────────
class SourceCredibilityDB(BaseModel):
    domain: str
    trust_score: float = 0.5        # 0 = untrusted, 1 = highly trusted
    political_bias: str = "center"  # left | center | right
    fake_news_count: int = 0
    total_articles_checked: int = 0
    categories: List[str] = []
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


# ── Analytics Snapshot ────────────────────────────────────────
class AnalyticsDB(BaseModel):
    date: datetime = Field(default_factory=datetime.utcnow)
    total_predictions: int = 0
    fake_count: int = 0
    real_count: int = 0
    avg_confidence: float = 0.0
    top_domains: List[str] = []
    emotion_distribution: Dict[str, float] = {}
