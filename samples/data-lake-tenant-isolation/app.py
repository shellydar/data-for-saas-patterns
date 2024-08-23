#!/usr/bin/env python3
import os

import aws_cdk as cdk

from data_lake_tenant_isolation.data_lake_tenant_isolation_stack import DataLakeTenantIsolationStack
from compute_layer.compute_layer_stack import compute_layer_stack

app = cdk.App()

tag_role=compute_layer_stack(app, "ComputeLayerStack").output_role
DataLakeTenantIsolationStack(app, "DataLakeTenantIsolationStack")

app.synth()
