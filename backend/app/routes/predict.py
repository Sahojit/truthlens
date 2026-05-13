"""
POST /api/predict
Main prediction endpoint — orchestrates all AI services.
"""

from fastapi import APIRouter, Request, Depends, HTTPException
from loguru import logger

from app.models.request_models import PredictRequest
from app.services.detection_service import DetectionService
from app.database.connection import get_db
from app.utils.auth import get_current_user

router = APIRouter()


def get_detection_service(request: Request) -> DetectionService:
    loader = request.app.state.model_loader
    return DetectionService(loader)


@router.post("/")
async def predict_news(
    body: PredictRequest,
    request: Request,
    current_user: dict = Depends(get_current_user),
    service: DetectionService = Depends(get_detection_service),
):
    """
    Analyse a news article and return a comprehensive fake-news assessment.

    - **headline**: The article headline (required)
    - **article**: Full article body (min 10 words)
    - **source_url**: Optional URL for source credibility analysis
    """
    try:
        result = await service.predict(
            headline=body.headline,
            article=body.article,
            source_url=body.source_url,
        )

        # Persist to MongoDB if user is authenticated
        db = get_db()
        if db is not None:
            try:
                record = {
                    **result,
                    "user_id": current_user.get("sub") if current_user else None,
                    "headline": body.headline,
                    "article": body.article[:5000],  # truncate for storage
                    "source_url": body.source_url,
                    "entity_graph": result.get("entity_graph", {}),
                    "highlighted_text": result.get("highlighted_text", [])[:50],
                    "created_at": result["created_at"],
                }
                await db["predictions"].insert_one(record)
            except Exception as db_err:
                logger.warning(f"DB save failed (non-fatal): {db_err}")

        return result

    except Exception as e:
        logger.error(f"Prediction error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.post("/quick")
async def quick_predict(
    body: PredictRequest,
    request: Request,
    service: DetectionService = Depends(get_detection_service),
):
    """
    Lightweight prediction — only returns core scores (faster response).
    """
    try:
        result = await service.predict(body.headline, body.article, body.source_url)
        return {
            "prediction": result["prediction"],
            "confidence": result["confidence"],
            "fake_probability": result["fake_probability"],
            "real_probability": result["real_probability"],
            "emotion_score": result["emotion_score"],
            "credibility_score": result["credibility_score"],
            "contradiction_score": result["contradiction_score"],
            "ai_generated_probability": result["ai_generated_probability"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
