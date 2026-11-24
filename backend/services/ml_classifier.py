"""Loads the optional TF-IDF + LogisticRegression artifact produced by ml/.

The model is trained ONLY on clearly synthetic examples (see ml/dataset.py).
If the artifact is missing or unreadable, the backend honestly falls back to
rules only. No claim is ever made that the model was trained on real data.
"""

from __future__ import annotations

import json
import logging
import threading
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ARTIFACT_DIR = PROJECT_ROOT / "ml" / "artifacts"
MODEL_PATH = ARTIFACT_DIR / "scam_classifier.joblib"
METADATA_PATH = ARTIFACT_DIR / "model_metadata.json"

_lock = threading.Lock()
_loaded = False
_pipeline: Any | None = None
_metadata: dict[str, Any] = {}


def _load() -> None:
    global _loaded, _pipeline, _metadata
    if _loaded:
        return
    with _lock:
        if _loaded:
            return
        _loaded = True
        if not MODEL_PATH.exists():
            logger.info("ML artifact not found at %s; using rules only.", MODEL_PATH)
            return
        try:
            import joblib

            _pipeline = joblib.load(MODEL_PATH)
            if METADATA_PATH.exists():
                _metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
            logger.info("Loaded synthetic-data scam classifier (version %s).", _metadata.get("version", "unknown"))
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Could not load ML artifact (%s); using rules only.", type(exc).__name__)
            _pipeline = None
            _metadata = {}


def is_available() -> bool:
    _load()
    return _pipeline is not None


def metadata() -> dict[str, Any]:
    _load()
    return dict(_metadata)


def scam_probability(text: str) -> float | None:
    """Probability (0-1) that the text resembles a scam, or None if unavailable."""
    _load()
    if _pipeline is None or not text:
        return None
    try:
        probabilities = _pipeline.predict_proba([text])[0]
        classes = list(_pipeline.classes_)
        index = classes.index("scam")
        return float(probabilities[index])
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("ML inference failed (%s); ignoring ML signal.", type(exc).__name__)
        return None
