from __future__ import annotations
import os
import argparse
import math
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import mlflow
import mlflow.sklearn

def parse_args():
    p = argparse.ArgumentParser("Simple MLflow demo (wine prediction)")
    p.add_argument("--csv", default="data/wine_sample.csv", help="Path to CSV (default: data/wine_sample.csv)")
    p.add_argument("--target", default="quality", help="Target column name (default: quality)")
    p.add_argument("--experiment", default="wine-prediction", help="MLflow experiment name")
    p.add_argument("--run", default="run-2", help="MLflow run name")
    p.add_argument("--n-estimators", type=int, default=50, help="RandomForest n_estimators (default: 50)")
    p.add_argument("--max-depth", type=int, default=5, help="RandomForest max_depth (default: 5)")
    p.add_argument("--test-size", type=float, default=0.2, help="Test split fraction (default: 0.3)")
    p.add_argument("--random-state", type=int, default=42, help="Random seed (default: 42)")
    return p.parse_args()

def main():
    args = parse_args()

    # Use a tracking server if MLFLOW_TRACKING_URI is set, otherwise fall back
    # to a local ./mlruns file store so the script works out of the box.
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "file:./mlruns")
    mlflow.set_tracking_uri(tracking_uri)
    print(f"MLflow tracking URI: {tracking_uri}")
    mlflow.set_experiment(args.experiment)

    # Load CSV
    if not os.path.exists(args.csv):
        raise SystemExit(f"CSV not found: {args.csv}. Create or copy wine_sample.csv next to this script.")
    df = pd.read_csv(args.csv)

    if args.target not in df.columns:
        raise SystemExit(f"Target column '{args.target}' not found in CSV. Columns: {list(df.columns)}")

    # Prepare data
    X = df.drop(columns=[args.target])
    y = df[args.target]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=args.random_state
    )

    # Train and log with MLflow
    with mlflow.start_run(run_name=args.run) as run:
        # Log simple params
        mlflow.log_param("n_estimators", args.n_estimators)
        mlflow.log_param("max_depth", args.max_depth)
        mlflow.log_param("test_size", args.test_size)
        mlflow.log_param("random_state", args.random_state)
        mlflow.log_param("train_rows", len(X_train))
        mlflow.log_param("test_rows", len(X_test))

        # Train model
        model = RandomForestRegressor(
            n_estimators=args.n_estimators,
            max_depth=args.max_depth,
            random_state=args.random_state,
        )
        model.fit(X_train, y_train)

        # Predict + metrics
        preds = model.predict(X_test)
        mse = mean_squared_error(y_test, preds)          # MSE is stable across sklearn versions
        rmse = float(math.sqrt(mse))                     # avoid `squared=` kw argument issues
        r2 = float(r2_score(y_test, preds))

        # Log metrics
        mlflow.log_metric("mse", float(mse))
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("r2", r2)

        # Also log the trained model as an artifact.
        mlflow.sklearn.log_model(model, name="model")

        print(f"Logged run {run.info.run_id} | rmse={rmse:.4f} r2={r2:.4f}")

if __name__ == "__main__":
    main()

