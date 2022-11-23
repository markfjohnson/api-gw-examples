from aws_cdk import (
    # Duration,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_cognito as cognito,
    aws_logs as logs,
    aws_iam as iam,
    aws_ec2 as ec2,
    Stack, Duration
    # aws_sqs as sqs,
)
from constructs import Construct
import json


class ApiGwExamplesStack(Stack):

    def defineNetworkStuff(self, vpcName, projectTag):
        log_group = logs.LogGroup(self, f"{vpcName}VPCLogGroup", retention=logs.RetentionDays.THREE_DAYS)
        flowIAM = iam.Role(self, f"{vpcName}FlowRole", assumed_by=iam.ServicePrincipal("vpc-flow-logs.amazonaws.com"))

        # VPC
        pubSubnet = ec2.SubnetConfiguration(name=f"{vpcName}public1", subnet_type=ec2.SubnetType.PUBLIC)
        subnets = []
        subnets.append(pubSubnet)
        pubSubnet = ec2.SubnetConfiguration(name=f"{vpcName}public2", subnet_type=ec2.SubnetType.PUBLIC)
        subnets = []
        subnets.append(pubSubnet)
        privateSubnet1 = ec2.SubnetConfiguration(name=f"{vpcName}private1", subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT)
        subnets.append(privateSubnet1)
        privateSubnet2 = ec2.SubnetConfiguration(name=f"{vpcName}private2", subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT)
        subnets.append(privateSubnet2)
        vpc = ec2.Vpc(self, f"{vpcName}VPC", max_azs=3,
                      subnet_configuration=subnets)
        ec2.FlowLog(self, f"{vpcName}FlowLog",
                    resource_type=ec2.FlowLogResourceType.from_vpc(vpc),
                    destination=ec2.FlowLogDestination.to_cloud_watch_logs(log_group, flowIAM))

        vpcEndpoint = None
        # apigwService = ec2.IInterfaceVpcEndpointService(name="*.execute-api.us-east-1.amazonaws.com", port=443)
        #
        # vpcEndpoint = ec2.InterfaceVpcEndpoint(self, "API Gateway VPC Endpoint",
        #                                        vpc=vpc,
        #                                        service=apigwService,
        #                                        subnets=ec2.SubnetSelection(
        #                                            subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT
        #                                        ),
        #                                        private_dns_enabled=True
        #                                        )

        return (vpc, vpcEndpoint)

    def defineCognito(self, poolName):
        up = cognito.UserPool(poolName, user_pool_name=poolName, self_sign_up_enabled=True)
        up.add_client(f"{poolName}app-client",
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

    def defineFunction(self, functionName, vpc=None, env_vars=None):
        if vpc is not None:
            lambda_func = self.definePrivateLambda(functionName, vpc, env_vars)
        else:
            lambda_func = self.definePublicLambda(functionName, env_vars)
        return (lambda_func)

    def definePublicLambda(self, functionName, env_vars=None):
        lambda_func = _lambda.Function(
            self, functionName,
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('lambda'),
            timeout=Duration.seconds(5),
            environment=env_vars,
            handler=f"{functionName}.handler")
        return lambda_func

    def definePrivateLambda(self, functionName, vpc, env_vars=None):
        lambda_role = iam.Role(self, f"{functionName}_lambda_role", assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
                               role_name=f"{functionName}_lambda_role"
                               )
        iam.ManagedPolicy(self, f"{functionName}_managed_policy",
                          statements=[
                              iam.PolicyStatement(
                                  effect=iam.Effect.ALLOW,
                                  actions=["ec2:CreateNetworkInterface",
                                           "ec2:DescribeNetworkInterfaces",
                                           "ec2:DeleteNetworkInterface",
                                           "ec2:AssignPrivateIpAddresses",
                                           "ec2:UnassignPrivateIpAddresses"],
                                  resources=["*"]
                              )
                          ],
                          roles=[lambda_role]
                          )
        lambda_func = _lambda.Function(
            self, functionName,
            runtime=_lambda.Runtime.PYTHON_3_9,
            vpc=vpc,
            code=_lambda.Code.from_asset('lambda'),
            timeout=Duration.seconds(5),
            handler=f"{functionName}.handler",
            environment=env_vars,
            role=lambda_role
        )
        return lambda_func

    def defineApiGateway(self, apiName, description, myFunction=None, apikey_required=False, integrationType=None,
                         endpointType=None, policyDocuments=None, env=None):

        api = apigateway.RestApi(
            self, apiName,
            rest_api_name=apiName,
            description=description,
            default_integration=integrationType,
            endpoint_configuration=endpointType,
            policy=policyDocuments,
        )

        return api

    def defineMethods(self, api, integrationType, apiKeyRequired=False):
        v1 = api.root.add_resource("v1")
        echo = v1.add_resource("echo")
        echo_method = echo.add_method("GET", integrationType, api_key_required=apiKeyRequired, )

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

        return (plan)

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
        endPointConfig = apigateway.EndpointConfiguration(
            types=[apigateway.EndpointType.REGIONAL]
        )
        api_gw = self.defineApiGateway("UsagePlan", "This is a test API Gateway with UsagePlans",
                                       endpointType=endPointConfig)
        url = api_gw.url
        # print(url)
        env_vars = {
            "URL": url,
            "CALL_COUNT": 500

        }
        edgeLambdaIntegration = self.defineFunction("UsageMethodFunction")
        edgeCaller = self.defineFunction("UsageCaller", env_vars=env_vars)
        self.defineMethods(api_gw, integrationType=None, apiKeyRequired=True)
        plan = self.defineUsagePlan(api_gw, "TestUsagePlan")
        new_key = self.addApiKey("Customer1", plan, api_gw)
        new_key = self.addApiKey("Customer2", plan, api_gw)
        new_key = self.addApiKey("Customer3", plan, api_gw)
        return api_gw

    def ex_apigw_edge(self):

        endPointConfig = apigateway.EndpointConfiguration(
            types=[apigateway.EndpointType.EDGE]
        )

        api_gw = self.defineApiGateway("edgeoptimized", "This is a test API Gateway with Edge Optimized Endpoint",
                                       endpointType=endPointConfig )
        url = api_gw.url
        # print(url)
        env_vars = {
            "URL": url

        }
        edgeLambdaIntegration = self.defineFunction("PublicEdgeMethodFunction")
        edgeCaller = self.defineFunction("PublicEdgeCaller", env_vars=env_vars)
        self.defineMethods(api_gw, integrationType=apigateway.LambdaIntegration(edgeLambdaIntegration))

        return api_gw

    def ex_apigw_private(self):
        tn = "API-GW-EXAMPLES"
        (vpc, vpcEndpoint) = self.defineNetworkStuff(tn, tn)
        self.defineFunction("PrivateAPIgwFunction", vpc)
        self.defineFunction("PrivateCaller", vpc)
        self.defineFunction("PublicAPIgwFunction")
        self.defineFunction("PublicCaller")
        endPointConfig = apigateway.EndpointConfiguration(
            types=[apigateway.EndpointType.PRIVATE]
        )
        denyStmt = iam.PolicyStatement(actions=['execute-api:Invoke'],
                                       principals=[iam.AnyPrincipal()],
                                       resources=['execute-api:/*'], effect=iam.Effect.DENY,
                                       conditions={
                                           "StringNotEquals": {
                                               "aws:SourceVpce": "vpce-0f89b943aa0627f24"
                                           }
                                       })

        allowStmt = iam.PolicyStatement(actions=['execute-api:Invoke'],
                                        resources=['execute-api:/*'], effect=iam.Effect.ALLOW,
                                        principals=[iam.AnyPrincipal()])

        policyDocuments = iam.PolicyDocument(statements=[denyStmt,allowStmt])

        api_gw = self.defineApiGateway("privateapi", "This is a test API Gateway with PRIVATE Endpoint within a VPC.",
                                        endpointType=endPointConfig, policyDocuments=policyDocuments)
        self.defineMethods(api_gw, integrationType=None)

        return api_gw

    def ex_cognito_apigw_authorizer(self):
        pass


    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        # TODO Fix the gap where the Usage plan does not map to the API, STAGE
        self.ex_regional_usageplan()
        self.ex_apigw_edge()
        #self.ex_apigw_private()
        #self.ex_cognito_apigw_authorizer()
