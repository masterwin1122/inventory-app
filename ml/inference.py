import os, json, joblib, numpy as np

def model_fn(model_dir):
    return joblib.load(os.path.join(model_dir, "model.joblib"))

def _to_2d(x):
    arr = np.asarray(x, dtype=float)
    return arr if arr.ndim == 2 else arr.reshape(1, -1)

def input_fn(body, content_type):
    ct = (content_type or "").lower()
    if "json" in ct:
        if isinstance(body, (bytes, bytearray)):
            body = body.decode("utf-8")
        data = json.loads(body)
        if isinstance(data, dict):
            payload = data.get("instances", data.get("inputs", data))
        else:
            payload = data
        return _to_2d(payload)
    # CSV fallback
    if isinstance(body, (bytes, bytearray)):
        body = body.decode("utf-8")
    rows = [r.strip() for r in body.splitlines() if r.strip()]
    vals = [list(map(float, r.split(","))) for r in rows]
    return _to_2d(vals)

def predict_fn(data, model):
    return model.predict(data)

def output_fn(pred, accept):
    acc = (accept or "").lower()
    vals = np.asarray(pred).tolist()
    if "json" in acc or "*/*" in acc or not acc:
        return json.dumps({"predictions": vals}), "application/json"
    return ",".join(map(str, vals)), "text/csv"
