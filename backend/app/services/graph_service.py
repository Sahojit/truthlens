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
        """Regex-based NER fallback — no spaCy required."""
        # Common words that are capitalised but are not entities
        SKIP = {
            "The","A","An","In","On","At","By","For","Of","To","And","But","Or",
            "Its","It","He","She","They","We","You","This","That","These","Those",
            "Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday",
            "January","February","March","April","May","June","July","August",
            "September","October","November","December","Reuters","AP","said",
            "According","However","Meanwhile","Although","Despite","When","After",
            "Before","During","Since","Breaking","Share","Read","Watch","Click",
        }

        # Known org/location keywords to help classify
        ORG_HINTS  = {"Inc","Corp","Ltd","LLC","Co","Bank","Fund","Agency","Institute",
                      "University","College","Department","Ministry","Committee","Council",
                      "Association","Foundation","Organization","Group","Party","Union"}
        GPE_HINTS  = {"City","State","County","Republic","Kingdom","Province","District",
                      "Washington","London","Moscow","Beijing","Paris","Berlin","Tokyo",
                      "New York","Los Angeles","Chicago","United States","European Union"}

        # Extract capitalised proper noun phrases (1–4 words)
        pattern = r"\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){0,3})\b"
        candidates = re.findall(pattern, text)
        counts = Counter()
        for c in candidates:
            first = c.split()[0]
            if first not in SKIP and len(c) > 2:
                counts[c] += 1

        # Classify and collect — include even single-mention entities
        entities = []
        seen = set()
        for phrase, _ in counts.most_common(40):
            if phrase in seen:
                continue
            seen.add(phrase)
            words = phrase.split()
            if any(w in ORG_HINTS for w in words):
                label = "ORG"
            elif phrase in GPE_HINTS or any(w in GPE_HINTS for w in words):
                label = "GPE"
            elif len(words) >= 2 and all(w[0].isupper() for w in words):
                label = "PERSON"
            else:
                label = "MISC"
            entities.append((phrase, label))

        return entities[:35]

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
