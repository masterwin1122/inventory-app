import os, sys, json, boto3
features = list(map(float, sys.argv[1:])) if len(sys.argv) > 1 else [1.0]
endpoint = os.getenv("SAGEMAKER_ENDPOINT_NAME", "inventory-forecasting-endpoint")
region   = os.getenv("AWS_REGION", "eu-central-1")

rt = boto3.client("sagemaker-runtime", region_name=region)
body = json.dumps({"instances": [features]}).encode("utf-8")

resp = rt.invoke_endpoint(
    EndpointName=endpoint,
    ContentType="application/json",
    Accept="application/json",
    Body=body,
)
print(resp["Body"].read().decode())
