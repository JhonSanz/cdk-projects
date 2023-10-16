#!/usr/bin/env python3

import aws_cdk as cdk

from sqs_lambda.sqs_lambda_stack import SqsLambdaStack


app = cdk.App()
SqsLambdaStack(app, "SqsLambdaStack")

app.synth()
