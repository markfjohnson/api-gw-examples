from aws_cdk import (
    # Duration,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_cognito as cognito,
    aws_logs as logs,
    Stack,
    # aws_sqs as sqs,
)
from constructs import Construct

class ApiGwExamplesStack(Stack):

    def defineCognito(self, poolName):
        up = cognito.UserPool(poolName, user_pool_name=poolName, self_sign_up_enabled=True)
        up.add_client("app-client",
                        o_auth=cognito.OAuthSettings(
                            flows=cognito.OAuthFlows(
                                authorization_code_grant=True
                            ),
                            scopes=[cognito.OAuthScope.OPENID],
                            callback_urls=["https://my-app-domain.com/welcome"],
                            logout_urls=["https://my-app-domain.com/signin"]
                        )
                        )
        return up


    def defineFunction(self, functionName):
        lambda_func = _lambda.Function(
            self, functionName,
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.from_asset('lambda'),
            handler='hello.handler',
        )
        return(lambda_func)

    def defineApiGateway(self, apiName, description, myFunction=None, apikey_required=False):
        # log_group = logs.LogGroup(self, f"{apiName}-{stageName}Logs")
        # deploy_options = apigateway.StageOptions(stage_name=stageName, description="CDK Sample Prod Stage Option",
        #                                          logging_level=apigateway.MethodLoggingLevel.INFO
        #                                          )
        request_params = []
        method_option = apigateway.MethodOptions(api_key_required=apikey_required, request_parameters=request_params)
        if myFunction is not None:
            lambda_proxy = True
        else:
            lambda_proxy = False

        api = apigateway.RestApi(
            self, apiName,
            proxy=lambda_proxy,
            description=description,
            # deploy_options=deploy_options,
            deploy=True,
            handler=myFunction,
            default_method_options=method_option
        )

        return api

    def defineUsagePlan(self, usagePlanName, api):
        plan = api.add_usage_plan(usagePlanName, name=usagePlanName,
                                  throttle=apigateway.ThrottleSettings(
                                      rate_limit=10,
                                      burst_limit=2
                                  )
                                  )
        return(plan)

    def addApiKey(self, apiKeyName, usagePlan, api):
        key = api.add_api_key(apiKeyName)
        usagePlan.add_api_key(key)
        return key

    def setPrivateEndpointIntegration(self, apigw, vpc):
        # endpoint_configuration = api.EndpointConfiguration(
        #     types=[api.EndpointType.PRIVATE],
        #     vpc_endpoints=[some_endpoint]
        #
        return None

    def addStageToApi(self, apigw, stageName, deploymentName, cacheEnabled=False, tacingEnabled=True,
                      retainDeployment=False, stageVariables=None):
        #log_group = logs.LogGroup(self, f"{stageName}-StageLogs")
        deployment = apigateway.Deployment(self, deploymentName, api=apigw, retain_deployments=retainDeployment)
        new_stage = apigateway.Stage(self, stageName, description=f"{stageName} - an additional stage",
                         deployment=deployment, stage_name=stageName, tracing_enabled=tacingEnabled,
                                     caching_enabled=cacheEnabled, variables=stageVariables
                         )
        return new_stage
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        func = self.defineFunction("APIGwTestFunction")

        #Setup the public API Gateway
        # Setup the private API Gateway
        public_stage_variables = {
            "year": "2022"
        }
        api_gw = self.defineApiGateway("UsagePlan", "This is a test API Gateway with Lambda Integration", func)
        stage = self.addStageToApi(api_gw, "Produ", "deployment2", cacheEnabled=True, retainDeployment=True)
        plan = self.defineUsagePlan("TestUsagePlan", api_gw)
        new_key = self.addApiKey("Customer1", plan, api_gw)
        new_key = self.addApiKey("Customer2", plan, api_gw)
        new_key = self.addApiKey("Customer3", plan, api_gw)


        public_stage_variables = {

        }
        pri_api_gw = self.defineApiGateway("PublicParams", "This is a test API Gateway with Lambda Integration", func)
        stage = self.addStageToApi(api_gw, "Prod", "deployment1", cacheEnabled=True, retainDeployment=True, stageVariables=public_stage_variables)

