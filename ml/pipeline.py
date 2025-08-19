import os
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.steps import TrainingStep
from sagemaker.workflow.step_collections import RegisterModel
from sagemaker.workflow.parameters import ParameterString
from sagemaker.workflow.pipeline_context import PipelineSession
from sagemaker.inputs import TrainingInput
from sagemaker.sklearn.estimator import SKLearn
from sagemaker.sklearn.model import SKLearnModel

REGION = os.getenv("AWS_REGION","eu-central-1")
S3_BUCKET = os.getenv("S3_BUCKET","REPLACE_ME_BUCKET")
MODEL_PACKAGE_GROUP = os.getenv("MODEL_PACKAGE_GROUP","inventory-forecasting")
ROLE_ARN = os.getenv("SAGEMAKER_EXECUTION_ROLE_ARN","REPLACE_ME_ROLE_ARN")

pipeline_session = PipelineSession()

# Parameters (keep instance_type configurable; SKLearn must have instance_count=1)
p_train_prefix = ParameterString("TrainPrefix", default_value=f"s3://{S3_BUCKET}/inventory/output/")
p_train_instance_type = ParameterString("TrainInstanceType", default_value="ml.m5.large")

est = SKLearn(
    entry_point="train.py",
    source_dir="ml",
    framework_version="1.2-1",
    role=ROLE_ARN,
    instance_count=1,                            # <-- fixed to 1 (required by SKLearn)
    instance_type=p_train_instance_type,
    sagemaker_session=pipeline_session,
    output_path=f"s3://{S3_BUCKET}/inventory/models/",
)

train_input = TrainingInput(s3_data=p_train_prefix, content_type="text/csv")
step_train = TrainingStep(name="TrainSKLearn", estimator=est, inputs={"train": train_input})

model = SKLearnModel(
    model_data=step_train.properties.ModelArtifacts.S3ModelArtifacts,
    entry_point="inference.py",
    source_dir="ml",
    framework_version="1.2-1",
    role=ROLE_ARN,
    sagemaker_session=pipeline_session,
)

register_step = RegisterModel(
    name="RegisterInventoryModel",
    model=model,
    content_types=["text/csv","application/json"],
    response_types=["application/json"],
    inference_instances=["ml.m5.large"],
    transform_instances=["ml.m5.large"],
    model_package_group_name=MODEL_PACKAGE_GROUP,
    approval_status="PendingManualApproval",
)

pipeline = Pipeline(
    name="InventoryForecastingPipeline",
    parameters=[p_train_prefix, p_train_instance_type],
    steps=[step_train, register_step],
    sagemaker_session=pipeline_session,
)

def get_pipeline(): return pipeline
