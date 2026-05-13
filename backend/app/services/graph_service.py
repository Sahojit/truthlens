"""
Graph-Based Fake News Propagation Analysis
Builds entity relationship graphs and misinformation cluster networks.
"""

import re
from typing import Dict, Any, List, Tuple
from collections import Counter
import networkx as nx
from loguru import logger

try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except Exception:
    SPACY_AVAILABLE = False
    logger.warning("spaCy not available, using regex-based NER fallback.")


class GraphAnalysisService:

    def build_entity_graph(self, headline: str, article: str) -> Dict[str, Any]:
        """
        Extracts entities and builds a co-occurrence graph.
        Returns nodes, edges, and basic graph metrics.
        """
        text = f"{headline} {article}"
        entities = self._extract_entities(text)
        G = self._build_graph(entities, text)
        return self._serialize_graph(G, entities)

    # ── Entity Extraction ─────────────────────────────────────
    def _extract_entities(self, text: str) -> List[Tuple[str, str]]:
        if SPACY_AVAILABLE:
            return self._spacy_entities(text)
        return self._regex_entities(text)

    def _spacy_entities(self, text: str) -> List[Tuple[str, str]]:
        doc = nlp(text[:8000])
        seen = set()
        entities = []
        for ent in doc.ents:
            if ent.label_ in {"PERSON", "ORG", "GPE", "LOC", "EVENT", "NORP"}:
                key = (ent.text.strip(), ent.label_)
                if key not in seen and len(ent.text.strip()) > 1:
                    seen.add(key)
                    entities.append(key)
        return entities[:50]  # cap

    def _regex_entities(self, text: str) -> List[Tuple[str, str]]:
        """Simple proper noun extraction as fallback."""
        words = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", text)
        counts = Counter(words)
        # Keep entities mentioned more than once
        return [(w, "MISC") for w, c in counts.most_common(30) if c > 1]

    # ── Graph Construction ────────────────────────────────────
    def _build_graph(
        self,
        entities: List[Tuple[str, str]],
        text: str,
    ) -> nx.Graph:
        G = nx.Graph()
        sentences = text.split(". ")

        # Add nodes
        for ent_text, ent_label in entities:
            G.add_node(ent_text, label=ent_label)

        # Add edges: entities in the same sentence are connected
        entity_names = [e[0] for e in entities]
        for sent in sentences:
            present = [e for e in entity_names if e.lower() in sent.lower()]
            for i in range(len(present)):
                for j in range(i + 1, len(present)):
                    if G.has_edge(present[i], present[j]):
                        G[present[i]][present[j]]["weight"] += 1
                    else:
                        G.add_edge(present[i], present[j], weight=1)

        return G

    # ── Serialisation ─────────────────────────────────────────
    def _serialize_graph(
        self,
        G: nx.Graph,
        entities: List[Tuple[str, str]],
    ) -> Dict[str, Any]:
        entity_dict = {e[0]: e[1] for e in entities}

        nodes = [
            {
                "id": node,
                "label": node,
                "type": entity_dict.get(node, "MISC"),
                "degree": G.degree(node),
                "centrality": round(
                    nx.degree_centrality(G).get(node, 0), 4
                ),
            }
            for node in G.nodes()
        ]

        edges = [
            {
                "source": u,
                "target": v,
                "weight": data.get("weight", 1),
            }
            for u, v, data in G.edges(data=True)
        ]

        metrics = {
            "node_count": G.number_of_nodes(),
            "edge_count": G.number_of_edges(),
            "density": round(nx.density(G), 4) if G.number_of_nodes() > 1 else 0,
            "avg_clustering": round(nx.average_clustering(G), 4) if G.number_of_nodes() > 2 else 0,
        }

        return {
            "nodes": nodes[:40],  # cap for frontend
            "edges": edges[:80],
            "metrics": metrics,
        }
