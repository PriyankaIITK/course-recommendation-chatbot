"""Training and inference utilities for the course recommendation chatbot."""

from __future__ import annotations

import json
import re
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "data" / "intents.json"
MODEL_FILE = ROOT / "models" / "intent_classifier.joblib"
METRICS_FILE = ROOT / "models" / "metrics.json"


def clean_text(text: str) -> str:
    """Lowercase text and keep words/numbers. TF-IDF handles tokenization."""
    text = text.lower().replace("'", "")
    return re.sub(r"[^a-z0-9+#.\s]", " ", text).strip()


def load_examples() -> tuple[list[str], list[str]]:
    with DATA_FILE.open(encoding="utf-8") as file:
        intents = json.load(file)["intents"]
    messages, labels = [], []
    for intent in intents:
        messages.extend(intent["patterns"])
        labels.extend([intent["tag"]] * len(intent["patterns"]))
    return messages, labels


def build_pipeline() -> Pipeline:
    return Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    preprocessor=clean_text,
                    ngram_range=(1, 2),
                    stop_words="english",
                    sublinear_tf=True,
                    min_df=1,
                ),
            ),
            (
                "classifier",
                LogisticRegression(max_iter=1500, class_weight="balanced", random_state=42),
            ),
        ]
    )


def train_and_save(verbose: bool = True) -> tuple[Pipeline, dict]:
    messages, labels = load_examples()
    x_train, x_test, y_train, y_test = train_test_split(
        messages, labels, test_size=0.25, random_state=42, stratify=labels
    )

    model = build_pipeline()
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)
    report = classification_report(y_test, predictions, output_dict=True, zero_division=0)
    metrics = {
        "training_samples": len(x_train),
        "test_samples": len(x_test),
        "accuracy": round(float(accuracy_score(y_test, predictions)), 4),
        "precision_weighted": round(float(report["weighted avg"]["precision"]), 4),
        "recall_weighted": round(float(report["weighted avg"]["recall"]), 4),
        "f1_weighted": round(float(report["weighted avg"]["f1-score"]), 4),
        "classification_report": report,
    }

    # Refit on every example after evaluation so the deployed model uses all data.
    model.fit(messages, labels)
    MODEL_FILE.parent.mkdir(exist_ok=True)
    joblib.dump(model, MODEL_FILE)
    METRICS_FILE.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    if verbose:
        print(f"Trained with {len(messages)} examples")
        print(f"Accuracy: {metrics['accuracy']:.2%}")
        print(f"Weighted F1: {metrics['f1_weighted']:.2%}")
        print(f"Saved model to: {MODEL_FILE}")
    return model, metrics


def load_or_train() -> Pipeline:
    if not MODEL_FILE.exists():
        return train_and_save(verbose=False)[0]
    return joblib.load(MODEL_FILE)


def predict_intent(model: Pipeline, message: str) -> tuple[str, float]:
    probabilities = model.predict_proba([message])[0]
    best_index = int(probabilities.argmax())
    return str(model.classes_[best_index]), float(probabilities[best_index])

