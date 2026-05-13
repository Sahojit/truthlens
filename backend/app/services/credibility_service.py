"""
Source Credibility Service
Scores domains based on historical fake-news data and trust metrics.
"""

import re
from typing import Optional, Dict, Any
from urllib.parse import urlparse
from loguru import logger


# Pre-seeded credibility database (domain → trust_score 0-1)
CREDIBILITY_DB: Dict[str, Dict[str, Any]] = {
    # Highly trusted
    "reuters.com":       {"trust": 0.95, "bias": "center", "category": "wire"},
    "apnews.com":        {"trust": 0.94, "bias": "center", "category": "wire"},
    "bbc.com":           {"trust": 0.90, "bias": "center-left", "category": "broadcast"},
    "bbc.co.uk":         {"trust": 0.90, "bias": "center-left", "category": "broadcast"},
    "theguardian.com":   {"trust": 0.85, "bias": "left", "category": "print"},
    "nytimes.com":       {"trust": 0.82, "bias": "left", "category": "print"},
    "washingtonpost.com":{"trust": 0.82, "bias": "left", "category": "print"},
    "wsj.com":           {"trust": 0.83, "bias": "right", "category": "print"},
    "economist.com":     {"trust": 0.88, "bias": "center", "category": "magazine"},
    "nature.com":        {"trust": 0.97, "bias": "center", "category": "scientific"},
    "sciencemag.org":    {"trust": 0.97, "bias": "center", "category": "scientific"},
    "who.int":           {"trust": 0.92, "bias": "center", "category": "official"},
    "cdc.gov":           {"trust": 0.91, "bias": "center", "category": "official"},
    # Moderate
    "foxnews.com":       {"trust": 0.55, "bias": "right", "category": "broadcast"},
    "msnbc.com":         {"trust": 0.58, "bias": "left", "category": "broadcast"},
    "huffpost.com":      {"trust": 0.60, "bias": "left", "category": "digital"},
    "dailymail.co.uk":   {"trust": 0.45, "bias": "right", "category": "tabloid"},
    "nypost.com":        {"trust": 0.50, "bias": "right", "category": "tabloid"},
    "breitbart.com":     {"trust": 0.20, "bias": "far-right", "category": "partisan"},
    # Known misinformation sources
    "naturalnews.com":   {"trust": 0.05, "bias": "far-right", "category": "conspiracy"},
    "infowars.com":      {"trust": 0.04, "bias": "far-right", "category": "conspiracy"},
    "beforeitsnews.com": {"trust": 0.06, "bias": "conspiracy", "category": "conspiracy"},
    "worldnewsdailyreport.com": {"trust": 0.03, "bias": "satire/fake", "category": "fake"},
    "thenewsnerd.com":   {"trust": 0.03, "bias": "satire/fake", "category": "fake"},
}

SUSPICIOUS_TLD = [".xyz", ".click", ".buzz", ".info", ".biz"]
CREDIBLE_TLD = [".gov", ".edu", ".org"]


class CredibilityService:

    def score(self, url: Optional[str]) -> Dict[str, Any]:
        if not url:
            return self._unknown_source()

        domain = self._extract_domain(url)
        if not domain:
            return self._unknown_source()

        # Exact match
        if domain in CREDIBILITY_DB:
            entry = CREDIBILITY_DB[domain]
            return {
                "domain": domain,
                "trust_score": entry["trust"],
                "political_bias": entry["bias"],
                "category": entry["category"],
                "source_known": True,
                "credibility_label": self._label(entry["trust"]),
            }

        # TLD heuristics
        tld_score = 0.5
        for tld in SUSPICIOUS_TLD:
            if domain.endswith(tld):
                tld_score = 0.25
                break
        for tld in CREDIBLE_TLD:
            if domain.endswith(tld):
                tld_score = 0.75
                break

        # Known substring patterns
        if any(s in domain for s in ["fake", "satire", "clickbait", "hoax"]):
            tld_score = 0.05

        return {
            "domain": domain,
            "trust_score": tld_score,
            "political_bias": "unknown",
            "category": "unknown",
            "source_known": False,
            "credibility_label": self._label(tld_score),
        }

    def _extract_domain(self, url: str) -> Optional[str]:
        try:
            if not url.startswith("http"):
                url = "http://" + url
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            domain = re.sub(r"^www\.", "", domain)
            return domain or None
        except Exception:
            return None

    def _unknown_source(self) -> Dict[str, Any]:
        return {
            "domain": "unknown",
            "trust_score": 0.5,
            "political_bias": "unknown",
            "category": "unknown",
            "source_known": False,
            "credibility_label": "Unverified",
        }

    def _label(self, score: float) -> str:
        if score >= 0.85:
            return "Highly Trusted"
        if score >= 0.65:
            return "Generally Reliable"
        if score >= 0.45:
            return "Mixed Reliability"
        if score >= 0.25:
            return "Low Credibility"
        return "Known Misinformation Source"
