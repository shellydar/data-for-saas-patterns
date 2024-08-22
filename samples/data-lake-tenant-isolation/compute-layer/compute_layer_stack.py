from aws_cdk import (
    # Duration,
    Stack,
    aws_apigateway as apigw,
    aws_lambda as _lambda,
    aws_cognito as cognito
)
from aws_solutions_constructs.aws_cognito_apigateway_lambda import CognitoToApiGatewayToLambda


class compute_layer_stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # Overriding LambdaRestApiProps with type Any
        gateway_props = dict[Any, Any]
        # create a standard API GW that authenticates using Cognito and transfers Lambda the JWT token
        construct = CognitoToApiGatewayToLambda(self, 'test-cognito-apigateway-lambda',
                                        lambda_function_props=_lambda.FunctionProps(
                                            code=_lambda.Code.from_asset(
                                                'lambda'),
                                            runtime=_lambda.Runtime.PYTHON_3_12,
                                            handler='index.handler'
                                        ),
                                        api_gateway_props=gateway_props(
                                            proxy=False
                                        )
                                        )        
        resource = construct.api_gateway.root.add_resource('foobar')
        resource.add_method('POST')

# Mandatory to call this method to Apply the Cognito Authorizers on all API methods
        construct.add_authorizers()