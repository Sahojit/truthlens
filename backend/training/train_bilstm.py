"""
Training Script — Bidirectional LSTM (TensorFlow/Keras)
Run: python -m training.train_bilstm
"""

import sys
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score

sys.path.insert(0, str(Path(__file__).parents[1]))
from training.train_logistic import load_data, preprocess

MODELS_DIR = Path("trained_models")
MODELS_DIR.mkdir(exist_ok=True)

MAX_VOCAB  = 30000
MAX_LEN    = 300
EMBED_DIM  = 128
BATCH_SIZE = 64
EPOCHS     = 10


def build_model(vocab_size: int, embed_dim: int, max_len: int):
    import tensorflow as tf
    from tensorflow.keras import layers, Model

    inp = layers.Input(shape=(max_len,), name="input_ids")
    x = layers.Embedding(vocab_size, embed_dim, mask_zero=True)(inp)
    x = layers.SpatialDropout1D(0.3)(x)
    x = layers.Bidirectional(layers.LSTM(128, return_sequences=True))(x)
    x = layers.Bidirectional(layers.LSTM(64))(x)
    x = layers.Dense(128, activation="relu")(x)
    x = layers.Dropout(0.4)(x)
    x = layers.Dense(64, activation="relu")(x)
    out = layers.Dense(1, activation="sigmoid", name="output")(x)

    model = Model(inp, out)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="binary_crossentropy",
        metrics=["accuracy", tf.keras.metrics.AUC(name="auc")],
    )
    return model


def tokenize_texts(texts, max_vocab=MAX_VOCAB, max_len=MAX_LEN):
    from tensorflow.keras.preprocessing.text import Tokenizer
    from tensorflow.keras.preprocessing.sequence import pad_sequences
    import joblib

    tokenizer = Tokenizer(num_words=max_vocab, oov_token="<OOV>")
    tokenizer.fit_on_texts(texts)
    sequences = tokenizer.texts_to_sequences(texts)
    padded = pad_sequences(sequences, maxlen=max_len, padding="post", truncating="post")
    joblib.dump(tokenizer, MODELS_DIR / "bilstm_tokenizer.pkl")
    return padded, tokenizer


def main():
    import tensorflow as tf
    from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau

    df = load_data()
    X_raw, y, le = preprocess(df)
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        X_raw, y, test_size=0.20, random_state=42, stratify=y
    )

    print("Tokenising…")
    X_train_pad, tokenizer = tokenize_texts(X_train_raw)
    from tensorflow.keras.preprocessing.sequence import pad_sequences
    X_test_pad = pad_sequences(
        tokenizer.texts_to_sequences(X_test_raw),
        maxlen=MAX_LEN, padding="post", truncating="post"
    )

    vocab_size = min(MAX_VOCAB, len(tokenizer.word_index) + 1)
    print(f"Vocab size: {vocab_size}")

    model = build_model(vocab_size, EMBED_DIM, MAX_LEN)
    model.summary()

    callbacks = [
        EarlyStopping(patience=3, restore_best_weights=True, monitor="val_auc", mode="max"),
        ModelCheckpoint(
            str(MODELS_DIR / "bilstm_model.h5"),
            save_best_only=True, monitor="val_auc", mode="max"
        ),
        ReduceLROnPlateau(patience=2, factor=0.5, monitor="val_loss"),
    ]

    history = model.fit(
        X_train_pad, y_train,
        validation_split=0.1,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        callbacks=callbacks,
    )

    # Evaluate
    y_prob = model.predict(X_test_pad, verbose=0).ravel()
    y_pred = (y_prob >= 0.5).astype(int)
    print("\n" + "="*60)
    print("BiLSTM EVALUATION")
    print("="*60)
    print(classification_report(y_test, y_pred, target_names=le.classes_))
    print(f"ROC-AUC: {roc_auc_score(y_test, y_prob):.4f}")

    # Plot training history
    import matplotlib.pyplot as plt
    plt.figure(figsize=(12, 4))
    plt.subplot(1, 2, 1)
    plt.plot(history.history["accuracy"], label="Train")
    plt.plot(history.history["val_accuracy"], label="Val")
    plt.title("BiLSTM Accuracy")
    plt.legend()
    plt.subplot(1, 2, 2)
    plt.plot(history.history["loss"], label="Train")
    plt.plot(history.history["val_loss"], label="Val")
    plt.title("BiLSTM Loss")
    plt.legend()
    plt.tight_layout()
    plt.savefig(MODELS_DIR / "bilstm_training_history.png")
    plt.close()
    print(f"BiLSTM model saved to {MODELS_DIR}/bilstm_model.h5")


if __name__ == "__main__":
    main()
