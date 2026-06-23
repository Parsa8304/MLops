"""Flask API that serves predictions from the trained intent model.

This is STAGE 2 of the MLops pipeline (Serving / Inference).

Endpoints:
  GET  /         -> tiny landing page describing the API
  GET  /health   -> health check used by load balancers / orchestrators
  POST /predict  -> {"text": "..."} -> {"intent": "...", "probabilities": {...}}

Run it with:  python app.py   (or: make run)
"""

from flask import Flask, jsonify, request

from model.intent_model import IntentModel

app = Flask(__name__)

# Load the model once at startup, not on every request (much faster).
model = IntentModel()


@app.route("/")
def index():
    return jsonify(
        {
            "service": "intent-classifier",
            "endpoints": {
                "GET /health": "health check",
                "POST /predict": 'send {"text": "..."} to get the predicted intent',
            },
        }
    )


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True) or {}
    text = data.get("text")

    # Validate the input before handing it to the model.
    if not isinstance(text, str) or not text.strip():
        return jsonify({"error": "Request body must include a non-empty 'text' field"}), 400

    return jsonify(model.predict(text))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000)
