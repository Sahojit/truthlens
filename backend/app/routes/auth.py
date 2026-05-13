"""
Authentication Routes: register, login, profile
"""

from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime

from app.models.request_models import RegisterRequest, LoginRequest, TokenResponse
from app.database.connection import get_db
from app.utils.auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter()


@router.post("/register", status_code=201)
async def register(body: RegisterRequest):
    db = get_db()
    if db is None:
        raise HTTPException(503, "Database unavailable")

    existing = await db["users"].find_one({"email": body.email})
    if existing:
        raise HTTPException(409, "Email already registered")

    user = {
        "email": body.email,
        "username": body.username,
        "hashed_password": hash_password(body.password),
        "is_active": True,
        "created_at": datetime.utcnow(),
        "total_predictions": 0,
    }
    result = await db["users"].insert_one(user)
    token = create_access_token({"sub": str(result.inserted_id), "email": body.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": str(result.inserted_id), "email": body.email, "username": body.username},
    }


@router.post("/login")
async def login(body: LoginRequest):
    db = get_db()
    if db is None:
        raise HTTPException(503, "Database unavailable")

    user = await db["users"].find_one({"email": body.email})
    if not user or not verify_password(body.password, user["hashed_password"]):
        raise HTTPException(401, "Invalid credentials")

    token = create_access_token({"sub": str(user["_id"]), "email": user["email"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": str(user["_id"]),
            "email": user["email"],
            "username": user["username"],
            "total_predictions": user.get("total_predictions", 0),
        },
    }


@router.get("/me")
async def get_profile(current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(401, "Not authenticated")
    db = get_db()
    if db:
        from bson import ObjectId
        user = await db["users"].find_one({"_id": ObjectId(current_user["sub"])})
        if user:
            return {
                "id": str(user["_id"]),
                "email": user["email"],
                "username": user["username"],
                "total_predictions": user.get("total_predictions", 0),
                "created_at": user.get("created_at"),
            }
    return current_user
