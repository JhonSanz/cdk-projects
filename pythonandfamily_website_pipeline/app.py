#!/usr/bin/env python3

import aws_cdk as cdk

from pythonandfamily_website_pipeline.pythonandfamily_website_pipeline_stack import PythonandfamilyWebsitePipelineStack


app = cdk.App()
PythonandfamilyWebsitePipelineStack(app, "PythonandfamilyWebsitePipelineStack")

app.synth()
