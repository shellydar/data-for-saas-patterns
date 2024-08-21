import aws_cdk as core
import aws_cdk.assertions as assertions

from data_lake_tenant_isolation.data_lake_tenant_isolation_stack import DataLakeTenantIsolationStack

# example tests. To run these tests, uncomment this file along with the example
# resource in data_lake_tenant_isolation/data_lake_tenant_isolation_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = DataLakeTenantIsolationStack(app, "data-lake-tenant-isolation")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
