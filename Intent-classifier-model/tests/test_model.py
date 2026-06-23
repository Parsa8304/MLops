"""Tests for the model layer (STAGE 3: Testing).

These run after `python model/train.py` has created the artifact.
"""

from model.intent_model import IntentModel


def test_predict_returns_expected_shape():
    model = IntentModel()
    result = model.predict("hello there")

    assert "intent" in result
    assert "probabilities" in result
    assert isinstance(result["probabilities"], dict)


def test_probabilities_sum_to_one():
    model = IntentModel()
    probs = model.predict("I want a refund")["probabilities"]

    # Probabilities across all classes should add up to ~1.0
    assert abs(sum(probs.values()) - 1.0) < 1e-6


def test_greeting_is_classified_as_greeting():
    model = IntentModel()
    assert model.predict("hi")["intent"] == "greeting"
