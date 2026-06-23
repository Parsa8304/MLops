import pandas as pd


def load_data(path):
    """Load CSV and ensure 'quality' column exists."""
    df = pd.read_csv(path)
    if "quality" not in df.columns:
        raise ValueError("CSV must contain a 'quality' column.")
    return df


def features_and_target(df):
    """Return X (features) and y (target)."""
    X = df.drop(columns=["quality"])
    y = df["quality"]
    return X, y
