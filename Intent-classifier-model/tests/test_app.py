"""Tests for the Flask API (STAGE 3: Testing).

Uses Flask's built-in test client, so no running server is needed.
"""

import pytest

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_predict_ok(client):
    resp = client.post("/predict", json={"text": "cancel my subscription"})
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["intent"] == "complaint"
    assert "probabilities" in body


def test_predict_missing_text_returns_400(client):
    resp = client.post("/predict", json={})
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_predict_empty_text_returns_400(client):
    resp = client.post("/predict", json={"text": "   "})
    assert resp.status_code == 400
