import os, json, joblib, numpy as np

def model_fn(model_dir):
    return joblib.load(os.path.join(model_dir, "model.joblib"))

def input_fn(body, content_type):
    # JSON: {"instances":[[...], ...]} or {"inputs":[...]} or raw list
    if "json" in content_type:
        data = json.loads(body)
        arr = np.array(data.get("instances") or data.get("inputs") or data, dtype=float)
        return arr if arr.ndim == 2 else arr.reshape(1, -1)

    # CSV text: rows of comma-separated features
    if isinstance(body, (bytes, bytearray)):
        body = body.decode("utf-8")
    rows = [r.strip() for r in body.splitlines() if r.strip()]
    arr = np.array([list(map(float, r.split(","))) for r in rows], dtype=float)
    return arr if arr.ndim == 2 else arr.reshape(1, -1)

def predict_fn(data, model):
    return model.predict(data)

def output_fn(prediction, accept):
    vals = np.asarray(prediction).tolist()
    if "json" in accept or "*/*" in accept:
        return json.dumps({"predictions": vals}), "application/json"
    return ",".join(map(str, vals)), "text/csv"
