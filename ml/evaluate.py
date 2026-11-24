"""Held-out evaluation of the synthetic-data classifier.

Usage (from project root):  python -m ml.evaluate
Reports metrics on a stratified split of the synthetic dataset. These numbers
are NOT an estimate of real-world performance.
"""

from __future__ import annotations

from pathlib import Path

import joblib
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split

from ml.dataset import get_examples
from ml.train_model import MODEL_PATH, build_pipeline

METADATA_PATH = Path(__file__).resolve().parent / "artifacts" / "model_metadata.json"


def main() -> None:
    examples = get_examples()
    texts = [example.text for example in examples]
    labels = [example.label for example in examples]

    train_x, test_x, train_y, test_y = train_test_split(
        texts, labels, test_size=0.25, random_state=42, stratify=labels
    )
    model = build_pipeline()
    model.fit(train_x, train_y)
    predictions = model.predict(test_x)

    print("SYNTHETIC DATA ONLY — metrics below are not real-world accuracy.")
    print(f"Examples: {len(examples)} (train {len(train_x)}, test {len(test_x)})")
    print(f"Accuracy : {accuracy_score(test_y, predictions):.4f}")
    print(f"Precision: {precision_score(test_y, predictions, pos_label='scam'):.4f}")
    print(f"Recall   : {recall_score(test_y, predictions, pos_label='scam'):.4f}")
    print(f"F1       : {f1_score(test_y, predictions, pos_label='scam'):.4f}")
    print("Confusion matrix (rows=true safe/scam, cols=predicted safe/scam):")
    print(confusion_matrix(test_y, predictions, labels=["safe", "scam"]))
    print(classification_report(test_y, predictions, digits=3))

    if MODEL_PATH.exists():
        saved = joblib.load(MODEL_PATH)
        sample = "Share your OTP immediately or your bank account will be blocked."
        probability = float(saved.predict_proba([sample])[0][list(saved.classes_).index("scam")])
        print(f"Saved artifact smoke-test scam probability: {probability:.4f}")
    else:
        print(f"Artifact not found at {MODEL_PATH}; run `python -m ml.train_model` first.")
    if METADATA_PATH.exists():
        print(f"Artifact metadata: {METADATA_PATH}")


if __name__ == "__main__":
    main()
