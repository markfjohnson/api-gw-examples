import unittest
import boto3
import requests


class MyTestCase(unittest.TestCase):
    apigw_client = boto3.client("apigateway")

    def get_invoke_url(self, apiName):
        rest_api_list = self.apigw_client.get_rest_apis()['items']
        target_api = [x for x in rest_api_list if x['name'] == apiName][0]
        invoke_url = f"https://{target_api['id']}.execute-api.us-east-1.amazonaws.com/Prod"
        return(invoke_url)


    def test_parameters_validation_present(self):
        url = self.get_invoke_url("PetStore")

        # Check that api gateway gets the parameter
        try:
            url_param = f"{url}?param1=1"
            x = requests.get(url_param)
            self.assertEqual(x['status_code'], 200)  # add assertion here
        except Exception as ex:
            print(ex)
            self.assertEqual(True, False)

    def test_parameters_param_validation_not_present(self):
        url = self.get_invoke_url("PetStore")

        # Check that api gateway throws an error if the parameter is missing
        try:
            x = requests.get(url)
            self.assertEqual(x['response_code'], 400)  # add assertion here
        except Exception as ex:
            print(ex)
            self.assertEqual(True, False)



if __name__ == '__main__':
    unittest.main()
