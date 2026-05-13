"""
Training Script — BERT Fine-tuned Classifier
Uses HuggingFace Transformers + PyTorch
Run: python -m training.train_bert
NOTE: Requires GPU for reasonable training time.
"""

import sys
import torch
import numpy as np
import pandas as pd
from pathlib import Path
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    AdamW, get_linear_schedule_with_warmup
)
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).parents[1]))
from training.train_logistic import load_data, preprocess

MODELS_DIR = Path("trained_models")
MODELS_DIR.mkdir(exist_ok=True)

MODEL_NAME  = "distilbert-base-uncased"  # Faster than bert-base for training
MAX_LEN     = 256
BATCH_SIZE  = 16
EPOCHS      = 3
LR          = 2e-5
DEVICE      = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class NewsDataset(Dataset):
    def __init__(self, texts, labels, tokenizer):
        self.encodings = tokenizer(
            list(texts),
            truncation=True,
            padding=True,
            max_length=MAX_LEN,
            return_tensors="pt",
        )
        self.labels = torch.tensor(labels, dtype=torch.long)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return {
            "input_ids":      self.encodings["input_ids"][idx],
            "attention_mask": self.encodings["attention_mask"][idx],
            "labels":         self.labels[idx],
        }


def train_epoch(model, loader, optimizer, scheduler):
    model.train()
    total_loss, correct, total = 0, 0, 0
    for batch in tqdm(loader, desc="Train"):
        optimizer.zero_grad()
        out = model(
            input_ids=batch["input_ids"].to(DEVICE),
            attention_mask=batch["attention_mask"].to(DEVICE),
            labels=batch["labels"].to(DEVICE),
        )
        out.loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()
        total_loss += out.loss.item()
        preds = out.logits.argmax(dim=1)
        correct += (preds == batch["labels"].to(DEVICE)).sum().item()
        total += len(batch["labels"])
    return total_loss / len(loader), correct / total


@torch.no_grad()
def eval_epoch(model, loader):
    model.eval()
    all_preds, all_probs, all_labels = [], [], []
    for batch in tqdm(loader, desc="Eval"):
        out = model(
            input_ids=batch["input_ids"].to(DEVICE),
            attention_mask=batch["attention_mask"].to(DEVICE),
        )
        probs = torch.softmax(out.logits, dim=1)[:, 1].cpu().numpy()
        preds = out.logits.argmax(dim=1).cpu().numpy()
        all_probs.extend(probs)
        all_preds.extend(preds)
        all_labels.extend(batch["labels"].numpy())
    return np.array(all_preds), np.array(all_probs), np.array(all_labels)


def main():
    print(f"Device: {DEVICE}")
    df = load_data()
    X_raw, y, le = preprocess(df)
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        X_raw, y, test_size=0.20, random_state=42, stratify=y
    )

    # Cap training size for speed
    if len(X_train_raw) > 20000:
        X_train_raw = X_train_raw[:20000]
        y_train = y_train[:20000]

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)
    model.to(DEVICE)

    train_ds = NewsDataset(X_train_raw, y_train, tokenizer)
    test_ds  = NewsDataset(X_test_raw,  y_test,  tokenizer)
    train_dl = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
    test_dl  = DataLoader(test_ds,  batch_size=BATCH_SIZE, num_workers=0)

    optimizer = AdamW(model.parameters(), lr=LR, weight_decay=0.01)
    total_steps = len(train_dl) * EPOCHS
    scheduler = get_linear_schedule_with_warmup(
        optimizer, num_warmup_steps=total_steps // 10, num_training_steps=total_steps
    )

    best_auc = 0
    for epoch in range(1, EPOCHS + 1):
        loss, acc = train_epoch(model, train_dl, optimizer, scheduler)
        y_pred, y_prob, y_true = eval_epoch(model, test_dl)
        auc = roc_auc_score(y_true, y_prob)
        print(f"Epoch {epoch}: loss={loss:.4f} train_acc={acc:.4f} val_auc={auc:.4f}")
        if auc > best_auc:
            best_auc = auc
            model.save_pretrained(str(MODELS_DIR / "bert_classifier"))
            tokenizer.save_pretrained(str(MODELS_DIR / "bert_classifier"))
            print(f"  Best model saved (AUC={best_auc:.4f})")

    # Final evaluation with best model
    y_pred, y_prob, y_true = eval_epoch(model, test_dl)
    print("\n" + "="*60)
    print("BERT EVALUATION")
    print("="*60)
    print(classification_report(y_true, y_pred, target_names=le.classes_))
    print(f"ROC-AUC: {roc_auc_score(y_true, y_prob):.4f}")


if __name__ == "__main__":
    main()
