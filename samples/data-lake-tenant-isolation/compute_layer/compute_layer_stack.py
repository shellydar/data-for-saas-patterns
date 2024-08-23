from aws_cdk import (
    # Duration,
    Stack,
    aws_apigateway as apigw,
    aws_lambda as _lambda,
    aws_cognito as cognito,
    CfnOutput
)
from aws_solutions_constructs.aws_cognito_apigateway_lambda import CognitoToApiGatewayToLambda
from aws_solutions_constructs.aws_apigateway_lambda import ApiGatewayToLambda
from constructs import Construct
from typing import Any
from aws_cdk import aws_iam as iam
from aws_cdk import aws_iam as iam


class compute_layer_stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # Overriding LambdaRestApiProps with type Any
        gateway_props = dict[Any, Any]
        # create a standard API GW that authenticates using Cognito and transfers Lambda the JWT token
        construct = CognitoToApiGatewayToLambda(self, 'test-cognito-apigateway-lambda',
                                        lambda_function_props=_lambda.FunctionProps(
                                            code=_lambda.Code.from_asset(
                                                'compute_layer/lambda/getTenantData'),
                                            runtime=_lambda.Runtime.PYTHON_3_12,
                                            handler='getTenantData.handler'
                                        ),
                                        api_gateway_props=gateway_props(
                                            proxy=False
                                        )
                                        )        
        resource = construct.api_gateway.root.add_resource('getTenantData')
        resource.add_method('POST')
# Mandatory to call this method to Apply the Cognito Authorizers on all API methods
        construct.add_authorizers()
        addTenantLambdacont=ApiGatewayToLambda(self, 'ApiGatewayToLambdaPattern',
            lambda_function_props=_lambda.FunctionProps(
                runtime=_lambda.Runtime.PYTHON_3_12,
                handler='addTenant.handler',
                code=_lambda.Code.from_asset('compute_layer/lambda/addTenant')
            )
            )
        addTenantLambdacont.api_gateway.root.add_resource('addTenant').add_method('POST')
        addTenantLambdacont.api_gateway_cloud_watch_role.add_to_policy(
            iam.PolicyStatement(
                actions=["lakeformation:AddLFTagsToResource",
                         "lakeformation:RemoveLFTagsFromResource",
                         "lakeformation:GetResourceLFTags",
                         "lakeformation:ListLFTags",
                         "lakeformation:CreateLFTag",
                         "lakeformation:GetLFTag",
                         "lakeformation:UpdateLFTag",
                         "lakeformation:DeleteLFTag",
                         "lakeformation:SearchTablesByLFTags",
                         "lakeformation:SearchDatabasesByLFTags"
                         ],
                effect=iam.Effect.ALLOW,
                resources=["*"]
            )
        )
        self.LF_create_tag_role=addTenantLambdacont.api_gateway_cloud_watch_role
        CfnOutput(self, 'LF_Tag_creator_role', value=self.LF_create_tag_role.role_arn)       
    
    def get_role(self):
        return self.LF_create_tag_role 
