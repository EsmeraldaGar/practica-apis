from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    aws_s3 as s3,
    aws_lambda as lambda_,
    CfnOutput
)
from constructs import Construct
from aws_cdk.aws_lambda_python_alpha import PythonFunction
import os
 
class PracticaStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
 
        bucket = s3.Bucket(
            self, "SnapshotsBucket",
            bucket_name="esmeralda-practica-snapshots",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )
 
        lambda_fn = lambda_.Function(
            self, "ClimaApiFunction",
            runtime=lambda_.Runtime.PYTHON_3_13,
            handler="handler.handler",   # archivo.handler
            code=lambda_.Code.from_asset("../src/lambda_function"),
            timeout=Duration.seconds(15),
            environment={
                "API_KEY": os.environ["API_KEY"],
                "SNAPSHOTS_BUCKET": bucket.bucket_name
            }
        )
 
        bucket.grant_read_write(lambda_fn)
 
        fn_url = lambda_fn.add_function_url(
            auth_type=lambda_.FunctionUrlAuthType.NONE
        )
 
        CfnOutput(self, "FunctionUrl", value=fn_url.url)
        CfnOutput(self, "BucketName", value=bucket.bucket_name)
 