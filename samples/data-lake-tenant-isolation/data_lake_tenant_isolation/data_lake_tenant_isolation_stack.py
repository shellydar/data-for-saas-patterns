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
from aws_cdk import aws_iam as iam

class DataLakeTenantIsolationStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        
        storage = dsf.storage.DataLakeStorage(self, "MyDataLakeStorage")

        cat = dsf.governance.DataLakeCatalog(self, "DataCatalog",
          data_lake_storage=storage
          )
        
        athenaWG=dsf.consumption.AthenaWorkGroup(self, "AthenaWorkGroupDefault",
                                               name="athena-default",
                                               result_location_prefix="athena-default-results/"
                                               )
        
        athenaWG.add_to_role_policy(PolicyStatement(
            actions=["kms:Decrypt"],
            resources=["*"]
        ))
        tenantPolicy=iam.Policy(self, "TenantPolicy",
            statements=[
                iam.PolicyStatement(
                    actions=["athena:*"],
                    resources=["*"],
                    effect=iam.Effect.ALLOW,
                    conditions={"StringEquals": {"aws:ResourceAccount": "tenantTBD"}}
                )
            ]
        )
        