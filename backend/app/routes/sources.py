"""
Source Credibility Routes
"""

from fastapi import APIRouter
from app.services.credibility_service import CredibilityService, CREDIBILITY_DB

router = APIRouter()
svc = CredibilityService()


@router.get("/check")
async def check_source(url: str):
    return svc.score(url)


@router.get("/leaderboard")
async def credibility_leaderboard():
    """Returns top trusted and least trusted sources."""
    entries = [
        {"domain": domain, **info}
        for domain, info in CREDIBILITY_DB.items()
    ]
    entries.sort(key=lambda x: x["trust"], reverse=True)
    return {
        "most_trusted": entries[:10],
        "least_trusted": entries[-10:][::-1],
    }


@router.get("/all")
async def all_sources():
    return [
        {"domain": domain, **info}
        for domain, info in CREDIBILITY_DB.items()
    ]
