"""
Prediction History Routes
"""

from fastapi import APIRouter, Depends, Query
from app.database.connection import get_db
from app.utils.auth import get_current_user

router = APIRouter()


@router.get("/")
async def get_history(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    db = get_db()
    if db is None:
        return {"items": [], "total": 0, "page": page}

    query = {}
    if current_user:
        query["user_id"] = current_user.get("sub")

    skip = (page - 1) * limit
    total = await db["predictions"].count_documents(query)
    cursor = db["predictions"].find(query).sort("created_at", -1).skip(skip).limit(limit)
    items = await cursor.to_list(length=limit)

    for item in items:
        item["_id"] = str(item["_id"])
        # Remove heavy fields from list view
        item.pop("shap_values", None)
        item.pop("highlighted_text", None)
        item.pop("entity_graph", None)

    return {"items": items, "total": total, "page": page, "limit": limit}


@router.get("/{prediction_id}")
async def get_prediction(prediction_id: str):
    db = get_db()
    if db is None:
        return {"error": "Database unavailable"}
    item = await db["predictions"].find_one({"prediction_id": prediction_id})
    if not item:
        return {"error": "Not found"}
    item["_id"] = str(item["_id"])
    return item


@router.delete("/{prediction_id}")
async def delete_prediction(
    prediction_id: str,
    current_user: dict = Depends(get_current_user),
):
    if not current_user:
        return {"error": "Authentication required"}
    db = get_db()
    if db:
        result = await db["predictions"].delete_one({
            "prediction_id": prediction_id,
            "user_id": current_user.get("sub"),
        })
        return {"deleted": result.deleted_count}
    return {"error": "Database unavailable"}
