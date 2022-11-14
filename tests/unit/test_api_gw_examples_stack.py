import aws_cdk as core
import aws_cdk.assertions as assertions

from api_gw_examples.api_gw_examples_stack import ApiGwExamplesStack

# example tests. To run these tests, uncomment this file along with the example
# resource in api_gw_examples/api_gw_examples_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = ApiGwExamplesStack(app, "api-gw-examples")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
