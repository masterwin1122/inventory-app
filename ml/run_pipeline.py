import os, time, boto3
from pipeline import get_pipeline, MODEL_PACKAGE_GROUP, REGION, ROLE_ARN
AUTO_DEPLOY = os.getenv("AUTO_DEPLOY","false").lower()=="true"
AUTO_APPROVE = os.getenv("AUTO_APPROVE","false").lower()=="true"
ENDPOINT_NAME = os.getenv("ENDPOINT_NAME","inventory-forecasting-endpoint")
TRAIN_INSTANCE_TYPE = os.getenv("TRAIN_INSTANCE_TYPE","ml.m5.large")
sm = boto3.client("sagemaker", region_name=REGION)

def upsert_and_start():
    p = get_pipeline(); p.upsert(role_arn=ROLE_ARN)
    s = p.start(parameters={"TrainInstanceType": TRAIN_INSTANCE_TYPE})
    print("Started pipeline execution:", s.arn); return s.arn

def wait(arn):
    while True:
        st = sm.describe_pipeline_execution(PipelineExecutionArn=arn)["PipelineExecutionStatus"]
        print("Execution status:", st)
        if st in ("Succeeded","Failed","Stopped"): return st
        time.sleep(20)

def steps(arn):
    for s in sm.list_pipeline_execution_steps(PipelineExecutionArn=arn)["PipelineExecutionSteps"]:
        print(f"- {s['StepName']}: {s['StepStatus']} {s.get('FailureReason','')[:250]}")

def latest_pkg(status=None):
    r=sm.list_model_packages(ModelPackageGroupName=MODEL_PACKAGE_GROUP,SortBy="CreationTime",SortOrder="Descending",MaxResults=10)
    for p in r.get("ModelPackageSummaryList",[]): 
        if status is None or p.get("ModelApprovalStatus")==status: return p["ModelPackageArn"]
    return None

def approve():
    arn = latest_pkg("PendingManualApproval") or latest_pkg()
    if not arn: return None
    sm.update_model_package(ModelPackageArn=arn, ModelApprovalStatus="Approved", ApprovalDescription="Auto-approve (dev)")
    print("Approved:", arn); return arn

def cfg(name):
    c=f"inv-forecast-cfg-{int(time.time())}"
    sm.create_endpoint_config(EndpointConfigName=c, ProductionVariants=[{"VariantName":"All","ModelName":name,"InitialInstanceCount":1,"InstanceType":"ml.m5.large"}])
    return c

def deploy():
    pkg = latest_pkg("Approved")
    if not pkg: return print("No Approved model packages.")
    name=f"inv-forecast-model-{int(time.time())}"
    sm.create_model(ModelName=name, PrimaryContainer={"ModelPackageName": pkg}, ExecutionRoleArn=ROLE_ARN)
    try:
        sm.describe_endpoint(EndpointName=ENDPOINT_NAME)
        sm.update_endpoint(EndpointName=ENDPOINT_NAME, EndpointConfigName=cfg(name))
        print("Updated endpoint:", ENDPOINT_NAME)
    except sm.exceptions.ClientError:
        sm.create_endpoint(EndpointName=ENDPOINT_NAME, EndpointConfigName=cfg(name))
        print("Created endpoint:", ENDPOINT_NAME)

if __name__=="__main__":
    arn=upsert_and_start()
    if wait(arn)!="Succeeded": print("Pipeline failed; steps:"); steps(arn); raise SystemExit(1)
    if AUTO_APPROVE: approve()
    if AUTO_DEPLOY: deploy()
