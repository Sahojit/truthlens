"""
Train Logistic Regression + XGBoost on the ISOT Fake News Dataset.
Fake.csv + True.csv  →  trained_models/
"""

import sys, os, joblib, warnings
from pathlib import Path

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score, f1_score, roc_auc_score,
    classification_report, confusion_matrix, roc_curve,
)
from xgboost import XGBClassifier
import nltk, re, string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

for pkg in ["punkt", "punkt_tab", "stopwords", "wordnet", "averaged_perceptron_tagger"]:
    nltk.download(pkg, quiet=True)

MODELS_DIR = ROOT / "trained_models"
MODELS_DIR.mkdir(exist_ok=True)

# ── 1. Load ISOT dataset ──────────────────────────────────────────────────────
DATASET_DIR = ROOT.parent / "News_Dataset"
print("Loading ISOT dataset…")
fake = pd.read_csv(DATASET_DIR / "Fake.csv")
true = pd.read_csv(DATASET_DIR / "True.csv")

fake["label"] = "FAKE"
true["label"] = "REAL"

df = pd.concat([fake, true], ignore_index=True)
df["content"] = (df["title"].fillna("") + " " + df["text"].fillna("")).str.strip()
df = df[df["content"].str.split().str.len() > 10].reset_index(drop=True)
df = df.sample(frac=0.5, random_state=42).reset_index(drop=True)  # 50% sample

print(f"  Total articles : {len(df):,}")
print(f"  FAKE           : {(df.label=='FAKE').sum():,}")
print(f"  REAL           : {(df.label=='REAL').sum():,}")

# ── 2. Preprocessing ──────────────────────────────────────────────────────────
STOP = set(stopwords.words("english"))
LEM  = WordNetLemmatizer()

def preprocess(text):
    text = text.lower()
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    tokens = word_tokenize(text)
    tokens = [LEM.lemmatize(t) for t in tokens if t not in STOP and len(t) > 1]
    return " ".join(tokens)

print("Preprocessing text (this takes ~2 min)…")
df["clean"] = df["content"].apply(preprocess)

# ── 3. Train / test split ─────────────────────────────────────────────────────
le = LabelEncoder()
y  = le.fit_transform(df["label"])   # FAKE=0, REAL=1
X  = df["clean"].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"  Train: {len(X_train):,}  |  Test: {len(X_test):,}")

# ── 4. TF-IDF ─────────────────────────────────────────────────────────────────
print("Fitting TF-IDF vectorizer…")
vectorizer = TfidfVectorizer(
    max_features=50_000,
    ngram_range=(1, 2),
    sublinear_tf=True,
    min_df=3,
    max_df=0.95,
)
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec  = vectorizer.transform(X_test)
print(f"  Vocab size: {len(vectorizer.vocabulary_):,}")

# ── 5. Logistic Regression ────────────────────────────────────────────────────
print("\nTraining Logistic Regression…")
lr = LogisticRegression(max_iter=300, C=1.0, class_weight="balanced", random_state=42, n_jobs=-1)
lr.fit(X_train_vec, y_train)

y_pred_lr = lr.predict(X_test_vec)
y_prob_lr = lr.predict_proba(X_test_vec)[:, 1]
acc_lr  = accuracy_score(y_test, y_pred_lr)
f1_lr   = f1_score(y_test, y_pred_lr)
auc_lr  = roc_auc_score(y_test, y_prob_lr)
print(f"  Accuracy: {acc_lr:.4f}  |  F1: {f1_lr:.4f}  |  AUC: {auc_lr:.4f}")
print(classification_report(y_test, y_pred_lr, target_names=le.classes_))

joblib.dump(vectorizer, MODELS_DIR / "tfidf_vectorizer.pkl")
joblib.dump(lr,         MODELS_DIR / "logistic_model.pkl")
joblib.dump(le,         MODELS_DIR / "label_encoder.pkl")
print("  Saved: tfidf_vectorizer.pkl, logistic_model.pkl, label_encoder.pkl")

# ── 6. XGBoost ────────────────────────────────────────────────────────────────
print("\nTraining XGBoost…")
xgb = XGBClassifier(
    n_estimators=150,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric="logloss",
    random_state=42,
    n_jobs=-1,
    verbosity=0,
)
xgb.fit(
    X_train_vec, y_train,
    eval_set=[(X_test_vec, y_test)],
    verbose=False,
)

y_pred_xgb = xgb.predict(X_test_vec)
y_prob_xgb = xgb.predict_proba(X_test_vec)[:, 1]
acc_xgb = accuracy_score(y_test, y_pred_xgb)
f1_xgb  = f1_score(y_test, y_pred_xgb)
auc_xgb = roc_auc_score(y_test, y_prob_xgb)
print(f"  Accuracy: {acc_xgb:.4f}  |  F1: {f1_xgb:.4f}  |  AUC: {auc_xgb:.4f}")
print(classification_report(y_test, y_pred_xgb, target_names=le.classes_))

joblib.dump(xgb, MODELS_DIR / "xgboost_model.pkl")
print("  Saved: xgboost_model.pkl")

# ── 7. Plots ──────────────────────────────────────────────────────────────────
plt.style.use("dark_background")
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle("ISOT Training Results — TruthLens", color="#6366f1", fontsize=14)

# Confusion matrices
for ax, name, y_pred in [
    (axes[0], f"Logistic Regression\nAcc={acc_lr:.3f}", y_pred_lr),
    (axes[1], f"XGBoost\nAcc={acc_xgb:.3f}",            y_pred_xgb),
]:
    cm = confusion_matrix(y_test, y_pred)
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks([0,1]); ax.set_yticks([0,1])
    ax.set_xticklabels(le.classes_); ax.set_yticklabels(le.classes_)
    for i in range(2):
        for j in range(2):
            ax.text(j, i, cm[i,j], ha="center", va="center",
                    color="white" if cm[i,j] < cm.max()/2 else "black", fontsize=14, fontweight="bold")
    ax.set_title(name, color="#e2e8f0")
    ax.set_xlabel("Predicted"); ax.set_ylabel("True")

# ROC curves
for name, probs, color in [
    ("Logistic Regression", y_prob_lr,  "#6366f1"),
    ("XGBoost",             y_prob_xgb, "#22d3ee"),
]:
    fpr, tpr, _ = roc_curve(y_test, probs)
    axes[2].plot(fpr, tpr, linewidth=2, color=color,
                 label=f"{name} (AUC={roc_auc_score(y_test,probs):.3f})")
axes[2].plot([0,1],[0,1],"--", color="#64748b", linewidth=1)
axes[2].set_xlabel("FPR"); axes[2].set_ylabel("TPR")
axes[2].set_title("ROC Curves", color="#e2e8f0")
axes[2].legend(fontsize=9)
axes[2].set_facecolor("#0f0f1a")

plt.tight_layout()
plot_path = MODELS_DIR / "isot_training_results.png"
plt.savefig(plot_path, dpi=120, bbox_inches="tight")
print(f"\nPlot saved: {plot_path}")

# ── 8. Summary ────────────────────────────────────────────────────────────────
print("\n" + "="*55)
print("  ISOT TRAINING COMPLETE")
print("="*55)
print(f"  Dataset        : {len(df):,} articles (ISOT)")
print(f"  LR   Acc={acc_lr:.4f}  F1={f1_lr:.4f}  AUC={auc_lr:.4f}")
print(f"  XGB  Acc={acc_xgb:.4f}  F1={f1_xgb:.4f}  AUC={auc_xgb:.4f}")
print(f"  Models saved to: {MODELS_DIR}")
print("="*55)
