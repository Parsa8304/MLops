"""Load the trained model artifact and expose a simple predict() method.

This is the bridge between STAGE 1 (training) and STAGE 2 (serving): the API
layer in app.py never touches scikit-learn directly, it only talks to this class.
"""

import os

import joblib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_PATH = os.path.join(ROOT, "model", "artifacts", "intent_model.pkl")


class IntentModel:
    def __init__(self, path=DEFAULT_PATH):
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Model artifact not found at {path}. "
                "Train it first with: python model/train.py"
            )
        self.pipeline = joblib.load(path)
        # The class labels the model was trained on, e.g. ["complaint", ...].
        self.labels = list(self.pipeline.classes_)

    def predict(self, text):
        """Return the predicted intent plus per-class probabilities."""
        intent = self.pipeline.predict([text])[0]
        probabilities = self.pipeline.predict_proba([text])[0]
        return {
            "intent": intent,
            "probabilities": {
                label: round(float(p), 4)
                for label, p in zip(self.labels, probabilities)
            },
        }
