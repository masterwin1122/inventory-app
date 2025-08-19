import os, glob, joblib, pandas as pd
from sklearn.linimport os
import glob
import joblib
import pandas as pd
from sklearn.linear_model import Ridge

DATA_DIR = "/opt/ml/input/data/train"
MODEL_DIR = "/opt/ml/model"
MODEL_PATH = os.path.join(MODEL_DIR, "model.joblib")


def load_training_data(data_dir: str) -> pd.DataFrame:
    csvs = sorted(glob.glob(os.path.join(data_dir, "*.csv")))
    if not csvs:
        raise RuntimeError(f"No CSV files found under {data_dir}")
    frames = []
    for p in csvs:
        df = pd.read_csv(p, header=None)
        if df.empty:
            continue
        frames.append(df)
    if not frames:
        raise RuntimeError(f"CSV files under {data_dir} were empty")
    return pd.concat(frames, ignore_index=True)


def main():
    # Load data (assumes no header; col0 = label, cols 1..n = features)
    df = load_training_data(DATA_DIR)

    y = df.iloc[:, 0].astype(float).values
    X = df.iloc[:, 1:].astype(float).values

    # Train a simple, robust baseline model
    model = Ridge(alpha=1.0)
    model.fit(X, y)

    # Persist the model for SageMaker
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    # Helpful logs
    print(f"Training samples: {X.shape[0]}, features: {X.shape[1]}")
    print(f"Saved model to {MODEL_PATH}")


if __name__ == "__main__":
    main()


