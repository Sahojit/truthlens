"""
Text preprocessing pipeline:
cleaning → tokenisation → lemmatisation → stopword removal → normalisation
"""

import re
import string
import unicodedata
from typing import List, Tuple

import nltk
import spacy
from textblob import TextBlob

# Download NLTK data at import time (no-op if already present)
for pkg in ["punkt", "stopwords", "wordnet", "averaged_perceptron_tagger"]:
    try:
        nltk.download(pkg, quiet=True)
    except Exception:
        pass

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize, sent_tokenize

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import subprocess, sys
    subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

STOP_WORDS = set(stopwords.words("english"))
LEMMATIZER = WordNetLemmatizer()


class TextPreprocessor:
    """All preprocessing steps for raw news text."""

    @staticmethod
    def clean(text: str) -> str:
        """Basic cleaning: unicode → HTML tags → URLs → extra whitespace."""
        text = unicodedata.normalize("NFKD", text)
        text = re.sub(r"<[^>]+>", " ", text)              # strip HTML
        text = re.sub(r"http\S+|www\.\S+", " URL ", text)  # mask URLs
        text = re.sub(r"\S+@\S+", " EMAIL ", text)         # mask emails
        text = re.sub(r"\d{10,}", " PHONE ", text)          # mask phone numbers
        text = re.sub(r"[^\x00-\x7F]+", " ", text)         # remove non-ASCII
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @staticmethod
    def normalize_case(text: str) -> str:
        return text.lower()

    @staticmethod
    def remove_punctuation(text: str) -> str:
        return text.translate(str.maketrans("", "", string.punctuation))

    @staticmethod
    def tokenize(text: str) -> List[str]:
        return word_tokenize(text)

    @staticmethod
    def remove_stopwords(tokens: List[str]) -> List[str]:
        return [t for t in tokens if t not in STOP_WORDS and len(t) > 1]

    @staticmethod
    def lemmatize(tokens: List[str]) -> List[str]:
        return [LEMMATIZER.lemmatize(t) for t in tokens]

    @staticmethod
    def full_pipeline(text: str) -> str:
        """Returns cleaned, lemmatized, stopword-free text (for TF-IDF / classical ML)."""
        text = TextPreprocessor.clean(text)
        text = TextPreprocessor.normalize_case(text)
        text = TextPreprocessor.remove_punctuation(text)
        tokens = TextPreprocessor.tokenize(text)
        tokens = TextPreprocessor.remove_stopwords(tokens)
        tokens = TextPreprocessor.lemmatize(tokens)
        return " ".join(tokens)

    @staticmethod
    def get_sentences(text: str) -> List[str]:
        return sent_tokenize(text)

    @staticmethod
    def extract_entities(text: str) -> List[Tuple[str, str]]:
        """Return (entity_text, entity_label) pairs using spaCy NER."""
        doc = nlp(text[:10000])  # cap length for speed
        return [(ent.text, ent.label_) for ent in doc.ents]

    @staticmethod
    def pos_tag(text: str) -> List[Tuple[str, str]]:
        doc = nlp(text[:5000])
        return [(token.text, token.pos_) for token in doc]

    @staticmethod
    def get_noun_chunks(text: str) -> List[str]:
        doc = nlp(text[:5000])
        return [chunk.text for chunk in doc.noun_chunks]
