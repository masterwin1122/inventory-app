import os, json
from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3

APP_REGION = os.getenv("AWS_REGION", "eu-central-1")
EP_NAME    = os.getenv("SAGEMAKER_ENDPOINT_NAME", "inventory-forecasting-endpoint")

rt = boto3.client("sagemaker-runtime", region_name=APP_REGION)
app = FastAPI(title="inventory-api", version="1.0")

class ForecastIn(BaseModel):
    features: List[float]

@app.get("/health")
def health():
    return {"status": "ok", "endpoint": EP_NAME, "region": APP_REGION}

@app.post("/forecast")
def forecast(inp: ForecastIn):
    try:
        body = json.dumps({"instances": [inp.features]})
        resp = rt.invoke_endpoint(
            EndpointName=EP_NAME,
            ContentType="application/json",
            Accept="application/json",
            Body=body,
        )
        pred = json.loads(resp["Body"].read().decode())["predictions"]
        return {"prediction": pred[0], "features": inp.features}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"invoke failed: {e}")
