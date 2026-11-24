"""Train the optional TF-IDF + LogisticRegression scam classifier.

Usage (from project root):  python -m ml.train_model
Training data is 100% SYNTHETIC (see ml/dataset.py). The artifact is a weak
signal used alongside transparent rules, never a certainty engine.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.pipeline import Pipeline

from ml.dataset import get_examples

ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"
MODEL_PATH = ARTIFACT_DIR / "scam_classifier.joblib"
METADATA_PATH = ARTIFACT_DIR / "model_metadata.json"
VERSION = "synthetic-v1"


def build_pipeline() -> Pipeline:
    return Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    strip_accents="unicode",
                    ngram_range=(1, 2),
                    min_df=1,
                    max_features=30000,
                    sublinear_tf=True,
                ),
            ),
            (
                "clf",
                LogisticRegression(
                    max_iter=2000,
                    C=4.0,
                    class_weight="balanced",
                    random_state=42,
                ),
            ),
        ]
    )


def main() -> None:
    examples = get_examples()
    texts = [example.text for example in examples]
    labels = [example.label for example in examples]
    pipeline = build_pipeline()
    pipeline.fit(texts, labels)
    predictions = pipeline.predict(texts)

    metrics = {
        "training_accuracy": round(float(accuracy_score(labels, predictions)), 4),
        "training_precision": round(float(precision_score(labels, predictions, pos_label="scam")), 4),
        "training_recall": round(float(recall_score(labels, predictions, pos_label="scam")), 4),
        "training_f1": round(float(f1_score(labels, predictions, pos_label="scam")), 4),
    }

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    metadata = {
        "version": VERSION,
        "trained_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "dataset_size": len(examples),
        "synthetic_only": True,
        "data_source": "ml/dataset.py — invented examples only; no real user messages",
        "labels": sorted(set(labels)),
        "vectorizer": "TF-IDF word 1-2 grams",
        "classifier": "LogisticRegression (class_weight=balanced)",
        "metrics_on_training_data": metrics,
        "warning": "Indicative signal only; not validated on real scam data.",
    }
    METADATA_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print("SYNTHETIC DATA ONLY — no real messages or users were used.")
    print(f"Trained on {len(examples)} synthetic examples -> {MODEL_PATH}")
    print(json.dumps(metrics, indent=2))
    print("Run `python -m ml.evaluate` for held-out metrics.")


if __name__ == "__main__":
    main()
