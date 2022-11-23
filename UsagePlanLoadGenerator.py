import requests
import json
import random
import boto3

#
# Replace apiKey with the API Key show value...
# Double check that the API Keys are associated with a Usage Plan and API
max_count = 1
restAPIname = "MyPublicAPI"
url = "https://w6gwd6p464.execute-api.us-east-1.amazonaws.com/Prod"

apigw_client = boto3.client("apigateway")
api_keys = apigw_client.get_api_keys()
api_key_ids = api_keys['items']
rest_api_list = apigw_client.get_rest_apis()['items']
target_api = [x for x in rest_api_list if x['name'] == restAPIname][0]
invoke_url = f"https://{target_api['idUsagePlanLoadGenerator.py']}.execute-api.us-east-1.amazonaws.com/Prod"
#
# restAPI = target_api['id']
# l = apigw_client.get_resources(restApiId=restAPI)['items']
# apiResource = [x for x in l if x['path'] == '/'][0]
#url = apigw_client.get_integration(restApiId=target_api['id'], resourceId=apiResource['id'],httpMethod='ANY')
for n in range(0, max_count):

    apiKey = random.choice(api_key_ids)
    a = apigw_client.get_api_key(apiKey=apiKey['id'], includeValue=True)

    header = {
        "x-api-key": a['value']
    }
    print(a['name'])
    print(header)

    x = requests.get(invoke_url, headers=header)
    print(x.content)