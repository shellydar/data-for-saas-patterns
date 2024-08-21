from aws_cdk import (
    # Duration,
    Stack,
    aws_lakeformation as LakeFormation,  
    CfnOutput
    aws_s3 as S3,
    aws_lambda as _lambda
)
from constructs import Construct

class DataLakeTenantIsolationStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # create lambda function
        lambda_function_new_tenant = _lambda.Function(self, "LambdaFunction",
                                    runtime=_lambda.Runtime.PYTHON_3_12,
                                    handler="lambda_function.lambda_handler",
                                    code=_lambda.Code.from_asset("lambda/new_tenant"))
        
        # create s3 bucket
        s3 = S3(self, "S3")
        s3.create_s3_bucket()
        s3.add_s3_bucket_policy()
        s3.add_s3_bucket_public_access_block()
        s3.add_s3_bucket_encryption()
        

        # lakeformation 
        lf = LakeFormation(self, "LakeFormation")
        lf.add_lake_formation_permissions()
        lf.add_lake_formation_tags()
        lf.add_lake_formation_resource()
        
        # The code that defines your stack goes here

        # example resource
        # queue = sqs.Queue(
        #     self, "DataLakeTenantIsolationQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )
