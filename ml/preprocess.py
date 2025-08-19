import argparse
import os
import boto3
import pandas as pd
from io import StringIO

def parse_s3_uri(uri):
    assert uri.startswith("s3://")
    parts = uri[5:].split("/", 1)
    bucket = parts[0]
    prefix = parts[1] if len(parts) > 1 else ""
    return bucket, prefix

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_s3", required=True)
    parser.add_argument("--output_s3", required=True)
    args = parser.parse_args()

    s3 = boto3.client("s3")
    in_bucket, in_prefix = parse_s3_uri(args.input_s3)
    out_bucket, out_prefix = parse_s3_uri(args.output_s3)

    # List CSVs under input prefix
    resp = s3.list_objects_v2(Bucket=in_bucket, Prefix=in_prefix)
    frames = []
    for obj in resp.get("Contents", []):
        if obj["Key"].endswith(".csv"):
            body = s3.get_object(Bucket=in_bucket, Key=obj["Key"])["Body"].read().decode("utf-8")
            df = pd.read_csv(StringIO(body))
            # Expect: date, sku, qty_sold
            df = df[["date", "sku", "qty_sold"]].dropna()
            frames.append(df)

    if not frames:
        # minimal synthetic example if no data present
        df = pd.DataFrame({"date": pd.date_range("2024-01-01", periods=30, freq="D"),
                           "sku": ["SKU_DEMO"]*30,
                           "qty_sold": [10]*30})
    else:
        df = pd.concat(frames, ignore_index=True)

    # Aggregate to daily totals (demo)
    agg = df.groupby("date")["qty_sold"].sum().reset_index()

    # For XGBoost csv: label first, simple dummy feature
    train = pd.DataFrame({
        "label": agg["qty_sold"].astype(float),
        "feat_dummy": 1.0,
    })

    csv_buf = StringIO()
    train.to_csv(csv_buf, index=False, header=False)
    key = os.path.join(out_prefix.rstrip("/"), "train.csv")
    s3.put_object(Bucket=out_bucket, Key=key, Body=csv_buf.getvalue().encode("utf-8"))
    print(f"Wrote training CSV to s3://{out_bucket}/{key}")

if __name__ == "__main__":
    main()
