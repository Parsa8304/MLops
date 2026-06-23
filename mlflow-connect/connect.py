"""Minimal example: connect to an MLflow tracking server and log one run.

Start a server first (see ../mlflow-basic-install), then run:

    python connect.py

Override the server address with an env var if needed:

    MLFLOW_TRACKING_URI=http://localhost:5000 python connect.py
"""

import os

import mlflow

# Point at the tracking server. Default matches `mlflow server ... --port 5000`.
tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
mlflow.set_tracking_uri(tracking_uri)
mlflow.set_experiment("hello-mlflow")

print(f"Connecting to MLflow at {tracking_uri}")

with mlflow.start_run(run_name="first-run") as run:
    # Log a parameter, a metric, and a tiny artifact.
    mlflow.log_param("learning_rate", 0.01)
    mlflow.log_metric("accuracy", 0.95)
    mlflow.set_tag("stage", "demo")
    print(f"Logged run {run.info.run_id} — refresh the MLflow UI to see it.")
