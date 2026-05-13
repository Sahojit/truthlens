"""
Training Script — XGBoost Classifier
Uses TF-IDF features from the logistic training step.
Run: python -m training.train_xgboost
"""

import sys
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score, accuracy_score
from xgboost import XGBClassifier
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).parents[1]))
from training.train_logistic import load_data, preprocess

MODELS_DIR = Path("trained_models")
MODELS_DIR.mkdir(exist_ok=True)


def main():
    df = load_data()
    X, y, le = preprocess(df)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    # Load vectorizer trained in logistic step
    vec_path = MODELS_DIR / "tfidf_vectorizer.pkl"
    if not vec_path.exists():
        print("ERROR: Run train_logistic.py first to create the TF-IDF vectorizer.")
        return

    vectorizer = joblib.load(vec_path)
    X_train_vec = vectorizer.transform(X_train)
    X_test_vec  = vectorizer.transform(X_test)

    print("Training XGBoost…")
    model = XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        use_label_encoder=False,
        eval_metric="logloss",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(
        X_train_vec, y_train,
        eval_set=[(X_test_vec, y_test)],
        verbose=50,
    )

    y_pred = model.predict(X_test_vec)
    y_prob = model.predict_proba(X_test_vec)[:, 1]

    print("\n" + "="*60)
    print("XGBOOST EVALUATION")
    print("="*60)
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print(f"ROC-AUC:  {roc_auc_score(y_test, y_prob):.4f}")
    print(classification_report(y_test, y_pred, target_names=le.classes_))

    # Feature importance plot (top 20)
    fi = model.feature_importances_
    fn = vectorizer.get_feature_names_out()
    top_idx = np.argsort(fi)[-20:]
    plt.figure(figsize=(10, 6))
    plt.barh(fn[top_idx], fi[top_idx])
    plt.title("XGBoost — Top 20 Feature Importances")
    plt.tight_layout()
    plt.savefig(MODELS_DIR / "xgboost_feature_importance.png")
    plt.close()

    joblib.dump(model, MODELS_DIR / "xgboost_model.pkl")
    print(f"XGBoost model saved to {MODELS_DIR}/xgboost_model.pkl")


if __name__ == "__main__":
    main()
