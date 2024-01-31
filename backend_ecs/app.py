#!/usr/bin/env python3

import aws_cdk as cdk

from backend_ecs.backend_ecs_stack import BackendEcsStack


app = cdk.App()
BackendEcsStack(app, "BackendEcsStack")

app.synth()
