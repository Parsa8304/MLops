"""Train the intent classifier and save the model artifact.

This is STAGE 1 of the MLops pipeline (Data + Training).

What happens here:
  1. Load labelled examples from data/intents.csv (data is kept OUT of the code).
  2. Build a scikit-learn Pipeline: text -> CountVectorizer -> MultinomialNB.
  3. Fit the pipeline and report training accuracy.
  4. Serialise ("pickle") the fitted pipeline to model/artifacts/intent_model.pkl.

Run it with:  python model/train.py   (or: make train)
"""

import csv
import os

import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

# Resolve paths relative to the project root so the script works from anywhere.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(ROOT, "data", "intents.csv")
ARTIFACT_DIR = os.path.join(ROOT, "model", "artifacts")
ARTIFACT_PATH = os.path.join(ARTIFACT_DIR, "intent_model.pkl")

# A tiny fallback dataset so training still works even if the CSV is missing.
FALLBACK = [
    ("hi", "greeting"),
    ("hello", "greeting"),
    ("how to reset password", "question"),
    ("cancel my subscription", "complaint"),
    ("great service", "praise"),
]


def load_data(path):
    """Return (texts, labels) from the CSV, or a small built-in fallback."""
    if not os.path.exists(path):
        print(f"[warn] {path} not found, using built-in fallback dataset")
        texts, labels = zip(*FALLBACK)
        return list(texts), list(labels)

    texts, labels = [], []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            texts.append(row["text"])
            labels.append(row["label"])
    return texts, labels


def main():
    X, y = load_data(DATA_PATH)
    print(f"Loaded {len(X)} examples across {len(set(y))} intents: {sorted(set(y))}")

    pipeline = Pipeline(
        [
            ("vect", CountVectorizer()),
            ("clf", MultinomialNB()),
        ]
    )
    pipeline.fit(X, y)

    # Training accuracy (on this toy dataset it will be ~1.0 — that is expected).
    accuracy = pipeline.score(X, y)
    print(f"Training accuracy: {accuracy:.2%}")

    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    joblib.dump(pipeline, ARTIFACT_PATH)
    print(f"Saved model artifact -> {ARTIFACT_PATH}")


if __name__ == "__main__":
    main()
