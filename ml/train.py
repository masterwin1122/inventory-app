import os, glob, joblib, pandas as pd
from sklearn.linear_model import Ridge

DATA_DIR = "/opt/ml/input/data/train"
files = sorted(glob.glob(os.path.join(DATA_DIR, "*.csv")))
if not files:
    raise RuntimeError(f"No CSV found under {DATA_DIR}")
df = pd.read_csv(files[0], header=None)
y = df.iloc[:, 0].astype(float).values
X = df.iloc[:, 1:].astype(float).values

model = Ridge(alpha=1.0).fit(X, y)
os.makedirs("/opt/ml/model", exist_ok=True)
joblib.dump(model, "/opt/ml/model/model.joblib")
print("Saved model to /opt/ml/model/model.joblib")
