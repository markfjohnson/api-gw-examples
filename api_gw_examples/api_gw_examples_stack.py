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

    def defineApiGateway(self, apiName, description, myFunction=None, apikey_required=False, integrationType=None, endpointType=None):

        # request_params = []
        # method_option = apigateway.MethodOptions(api_key_required=apikey_required, request_parameters=request_params)
        # if myFunction is not None:
        #     lambda_proxy = True
        # else:
        #     lambda_proxy = False

        api = apigateway.RestApi(
            self, apiName,
            rest_api_name=apiName,
            description=description,
            default_integration=integrationType,
            endpoint_configuration=endpointType,
        )

        return api

    def defineMethods(self, api, integrationType):
        v1 = api.root.add_resource("v1")
        echo = v1.add_resource("echo")
        echo_method = echo.add_method("GET", integrationType, api_key_required=True)

    def defineUsagePlan(self, api, usagePlanName, integrationType=None):

        plan = api.add_usage_plan(usagePlanName,
                                  name=usagePlanName,
                                  throttle=apigateway.ThrottleSettings(
                                      rate_limit=10,
                                      burst_limit=2
                                  )
                                  )

        key = api.add_api_key("ApiKey")
        plan.add_api_key(key)

        return(plan)

    def addApiKey(self, apiKeyName, usagePlan, api):
        key = api.add_api_key(apiKeyName, api_key_name=apiKeyName)
        usagePlan.add_api_key(key)
        return key

    def setPrivateEndpointIntegration(self, apigw, vpc):
        # endpoint_configuration = api.EndpointConfiguration(
        #     types=[api.EndpointType.PRIVATE],
        #     vpc_endpoints=[some_endpoint]
        #
        return None

    # def addStageToApi(self, apigw, stageName, deploymentName, cacheEnabled=False, tacingEnabled=True,
    #                   retainDeployment=False, stageVariables=None):
    #     #log_group = logs.LogGroup(self, f"{stageName}-StageLogs")
    #     deployment = apigateway.Deployment(self, deploymentName, api=apigw, retain_deployments=retainDeployment)
    #     new_stage = apigateway.Stage(self, stageName, description=f"{stageName} - an additional stage",
    #                      deployment=deployment, stage_name=stageName, tracing_enabled=tacingEnabled,
    #                                  caching_enabled=cacheEnabled, variables=stageVariables
    #                      )
    #     return new_stage


    #
    ##
    ###
    #   Example functions

    def ex_regional_usageplan(self):
        api_gw = self.defineApiGateway("UsagePlan", "This is a test API Gateway with Lambda Integration")
        self.defineMethods(api_gw, integrationType=None)
        #stage = self.addStageToApi(api_gw, "Prod", "deployment2", cacheEnabled=True, retainDeployment=True)
        plan = self.defineUsagePlan(api_gw, "TestUsagePlan")
        new_key = self.addApiKey("Customer1", plan, api_gw)
        new_key = self.addApiKey("Customer2", plan, api_gw)
        new_key = self.addApiKey("Customer3", plan, api_gw)
        return api_gw

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        func = self.defineFunction("APIGwTestFunction")

        #Setup the public API Gateway
        # Setup the private API Gateway
        public_stage_variables = {
            "year": "2022"
        }
        api_gw = self.ex_regional_usageplan()




