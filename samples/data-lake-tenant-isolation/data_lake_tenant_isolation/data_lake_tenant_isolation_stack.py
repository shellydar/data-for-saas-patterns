from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
)
from constructs import Construct
import cdklabs.aws_data_solutions_framework as dsf
from aws_cdk.aws_s3 import Bucket
from aws_cdk import Stack, RemovalPolicy, CfnOutput
from aws_cdk.aws_iam import Policy, PolicyStatement
from aws_cdk.aws_kms import Key  

class DataLakeTenantIsolationStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        
        storage = dsf.storage.AnalyticsBucket(
            self, "DataLakeStorage", 
            removal_policy=RemovalPolicy.DESTROY,
            encryption_key= Key(self, "StorageEncryptionKey",
                removal_policy=RemovalPolicy.DESTROY,
                enable_key_rotation=True
            )
        )
        # The code that defines your stack goes here

        # example resource
        # queue = sqs.Queue(
        #     self, "DataLakeTenantIsolationQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )
