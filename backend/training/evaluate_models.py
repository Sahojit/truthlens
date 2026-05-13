"""
Evaluate all trained models and generate comparison report.
Run: python -m training.evaluate_models
"""

import sys
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report, confusion_matrix,
    roc_auc_score, roc_curve, accuracy_score
)

sys.path.insert(0, str(Path(__file__).parents[1]))
from training.train_logistic import load_data, preprocess

MODELS_DIR = Path("trained_models")
MODELS_DIR.mkdir(exist_ok=True)


def load_models():
    models = {}
    vec_path = MODELS_DIR / "tfidf_vectorizer.pkl"
    if not vec_path.exists():
        print("No trained models found. Run training scripts first.")
        return models, None
    vectorizer = joblib.load(vec_path)
    if (MODELS_DIR / "logistic_model.pkl").exists():
        models["Logistic Regression"] = joblib.load(MODELS_DIR / "logistic_model.pkl")
    if (MODELS_DIR / "xgboost_model.pkl").exists():
        models["XGBoost"] = joblib.load(MODELS_DIR / "xgboost_model.pkl")
    return models, vectorizer


def evaluate_all():
    df = load_data()
    X_raw, y, le = preprocess(df)
    _, X_test_raw, _, y_test = train_test_split(X_raw, y, test_size=0.20, random_state=42, stratify=y)

    models, vectorizer = load_models()
    if not models:
        return

    X_test_vec = vectorizer.transform(X_test_raw)

    fig, axes = plt.subplots(1, len(models) + 1, figsize=(6 * (len(models) + 1), 5))
    roc_fig, roc_ax = plt.subplots(figsize=(8, 6))

    summary = []
    for i, (name, model) in enumerate(models.items()):
        y_pred = model.predict(X_test_vec)
        y_prob = model.predict_proba(X_test_vec)[:, 1]
        acc = accuracy_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_prob)
        cm = confusion_matrix(y_test, y_pred)

        print(f"\n{'='*50}")
        print(f"{name}")
        print(f"Accuracy: {acc:.4f}  ROC-AUC: {auc:.4f}")
        print(classification_report(y_test, y_pred, target_names=le.classes_))

        # Confusion matrix
        ax = axes[i] if len(models) > 1 else axes
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                    xticklabels=le.classes_, yticklabels=le.classes_, ax=ax)
        ax.set_title(f"{name}\nAcc={acc:.3f} AUC={auc:.3f}")

        # ROC curve
        fpr, tpr, _ = roc_curve(y_test, y_prob)
        roc_ax.plot(fpr, tpr, label=f"{name} (AUC={auc:.3f})")

        summary.append({"Model": name, "Accuracy": acc, "ROC-AUC": auc})

    # Summary bar chart
    ax_summary = axes[-1]
    names = [s["Model"] for s in summary]
    accs  = [s["Accuracy"] for s in summary]
    x = np.arange(len(names))
    ax_summary.bar(x, accs, color=["#4f8ef7", "#f74f4f"])
    ax_summary.set_xticks(x)
    ax_summary.set_xticklabels(names, rotation=15)
    ax_summary.set_ylim(0.5, 1.0)
    ax_summary.set_title("Model Accuracy Comparison")
    ax_summary.set_ylabel("Accuracy")

    fig.tight_layout()
    fig.savefig(MODELS_DIR / "model_comparison.png")

    roc_ax.plot([0, 1], [0, 1], "k--", label="Random")
    roc_ax.set_xlabel("False Positive Rate")
    roc_ax.set_ylabel("True Positive Rate")
    roc_ax.set_title("ROC Curves")
    roc_ax.legend()
    roc_fig.tight_layout()
    roc_fig.savefig(MODELS_DIR / "roc_curves.png")
    plt.close("all")

    print(f"\nPlots saved to {MODELS_DIR}/")
    return summary


if __name__ == "__main__":
    evaluate_all()
