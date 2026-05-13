"""
Graph Analysis Routes
"""

from fastapi import APIRouter
from pydantic import BaseModel
from app.services.graph_service import GraphAnalysisService

router = APIRouter()
svc = GraphAnalysisService()


class GraphRequest(BaseModel):
    headline: str
    article: str


@router.post("/entity-graph")
async def entity_graph(body: GraphRequest):
    return svc.build_entity_graph(body.headline, body.article)


@router.get("/sample")
async def sample_graph():
    """Returns a sample propagation graph for demo purposes."""
    return {
        "nodes": [
            {"id": "CNN",         "label": "CNN",         "type": "ORG",    "degree": 4},
            {"id": "Joe Biden",   "label": "Joe Biden",   "type": "PERSON", "degree": 3},
            {"id": "Washington",  "label": "Washington",  "type": "GPE",    "degree": 5},
            {"id": "White House", "label": "White House", "type": "ORG",    "degree": 3},
            {"id": "Congress",    "label": "Congress",    "type": "ORG",    "degree": 4},
            {"id": "Russia",      "label": "Russia",      "type": "GPE",    "degree": 2},
        ],
        "edges": [
            {"source": "CNN",        "target": "Joe Biden",  "weight": 3},
            {"source": "Joe Biden",  "target": "Washington", "weight": 2},
            {"source": "Washington", "target": "White House","weight": 4},
            {"source": "White House","target": "Congress",   "weight": 2},
            {"source": "Congress",   "target": "Russia",     "weight": 1},
        ],
        "metrics": {"node_count": 6, "edge_count": 5, "density": 0.33, "avg_clustering": 0.25},
    }
