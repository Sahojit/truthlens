"""
Training Script — TF-IDF + Logistic Regression
Dataset: ISOT Fake News Dataset (or Kaggle)
Run: python -m training.train_logistic
"""

import os
import sys
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score, accuracy_score
)
from sklearn.preprocessing import LabelEncoder
from imblearn.over_sampling import SMOTE
import matplotlib.pyplot as plt
import seaborn as sns

# Add project root to path
sys.path.insert(0, str(Path(__file__).parents[1]))
from app.services.preprocessing_service import TextPreprocessor

MODELS_DIR = Path("trained_models")
MODELS_DIR.mkdir(exist_ok=True)
DATA_DIR = Path("datasets")


def load_data() -> pd.DataFrame:
    """Load and merge datasets. Falls back to generating synthetic data for demo."""
    frames = []

    # Try ISOT dataset
    for fname, label in [("True.csv", "REAL"), ("Fake.csv", "FAKE")]:
        fpath = DATA_DIR / fname
        if fpath.exists():
            df = pd.read_csv(fpath)
            df["label"] = label
            frames.append(df[["title", "text", "label"]])
            print(f"Loaded {len(df)} samples from {fname}")

    # Try Kaggle dataset
    kaggle_path = DATA_DIR / "news.csv"
    if kaggle_path.exists():
        df = pd.read_csv(kaggle_path)
        if "label" in df.columns:
            df = df[["title", "text", "label"]].dropna()
            frames.append(df)
            print(f"Loaded {len(df)} samples from news.csv")

    if not frames:
        print("WARNING: No dataset files found. Generating synthetic demo data.")
        return _generate_synthetic_data()

    combined = pd.concat(frames, ignore_index=True)
    combined = combined.dropna(subset=["text", "label"])
    combined["text"] = combined["title"].fillna("") + " " + combined["text"].fillna("")
    return combined[["text", "label"]]


def _generate_synthetic_data(n=2000) -> pd.DataFrame:
    """Generate synthetic data for demonstration when no real dataset is available."""
    np.random.seed(42)
    fake_templates = [
        "BREAKING: Shocking conspiracy reveals {topic} is hiding {claim}! You won't believe this!!!",
        "EXCLUSIVE: Deep state exposed! {topic} secretly planning {claim}. Share before deleted!",
        "URGENT: {topic} announces {claim}. Mainstream media won't report this truth!",
    ]
    real_templates = [
        "{topic} released a statement regarding {claim} following the recent developments.",
        "According to official sources, {topic} confirmed {claim} in a press conference.",
        "Researchers at {topic} published findings showing {claim} in peer-reviewed journal.",
    ]
    topics = ["government", "scientists", "officials", "researchers", "experts"]
    claims = ["new policy", "latest findings", "recent changes", "updated guidelines", "new data"]

    import random
    rows = []
    for _ in range(n // 2):
        t = random.choice(topics)
        c = random.choice(claims)
        rows.append({"text": random.choice(fake_templates).format(topic=t, claim=c), "label": "FAKE"})
        rows.append({"text": random.choice(real_templates).format(topic=t, claim=c), "label": "REAL"})
    return pd.DataFrame(rows)


def preprocess(df: pd.DataFrame) -> tuple:
    print("Preprocessing texts…")
    preprocessor = TextPreprocessor()
    df["clean_text"] = df["text"].apply(
        lambda x: preprocessor.full_pipeline(str(x)[:5000])
    )
    le = LabelEncoder()
    y = le.fit_transform(df["label"])  # FAKE=0, REAL=1 (or vice versa)
    print(f"Label encoding: {dict(zip(le.classes_, le.transform(le.classes_)))}")
    return df["clean_text"].values, y, le


def train(X_train, y_train):
    print("Training TF-IDF + Logistic Regression…")
    vectorizer = TfidfVectorizer(
        max_features=50000,
        ngram_range=(1, 2),
        sublinear_tf=True,
        min_df=2,
        max_df=0.95,
    )
    X_train_vec = vectorizer.fit_transform(X_train)

    # Apply SMOTE to balance classes
    try:
        smote = SMOTE(random_state=42)
        X_balanced, y_balanced = smote.fit_resample(X_train_vec, y_train)
        print(f"After SMOTE: {X_balanced.shape}")
    except Exception as e:
        print(f"SMOTE failed ({e}), using original data")
        X_balanced, y_balanced = X_train_vec, y_train

    model = LogisticRegression(
        max_iter=1000,
        C=1.0,
        solver="lbfgs",
        class_weight="balanced",
        random_state=42,
    )
    model.fit(X_balanced, y_balanced)
    return vectorizer, model


def evaluate(model, vectorizer, X_test, y_test, le):
    X_test_vec = vectorizer.transform(X_test)
    y_pred = model.predict(X_test_vec)
    y_prob = model.predict_proba(X_test_vec)[:, 1]

    print("\n" + "="*60)
    print("LOGISTIC REGRESSION EVALUATION")
    print("="*60)
    print(f"Accuracy:  {accuracy_score(y_test, y_pred):.4f}")
    print(f"ROC-AUC:   {roc_auc_score(y_test, y_prob):.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=le.classes_))

    # Confusion matrix plot
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=le.classes_, yticklabels=le.classes_)
    plt.title("Logistic Regression — Confusion Matrix")
    plt.ylabel("True Label")
    plt.xlabel("Predicted Label")
    plt.tight_layout()
    plt.savefig(MODELS_DIR / "logistic_confusion_matrix.png")
    plt.close()
    print(f"Confusion matrix saved.")


def main():
    df = load_data()
    print(f"Total samples: {len(df)}, label distribution:\n{df['label'].value_counts()}")

    X, y, le = preprocess(df)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    vectorizer, model = train(X_train, y_train)
    evaluate(model, vectorizer, X_test, y_test, le)

    # Save
    joblib.dump(vectorizer, MODELS_DIR / "tfidf_vectorizer.pkl")
    joblib.dump(model,      MODELS_DIR / "logistic_model.pkl")
    joblib.dump(le,         MODELS_DIR / "label_encoder.pkl")
    print(f"\nModels saved to {MODELS_DIR}/")


if __name__ == "__main__":
    main()
