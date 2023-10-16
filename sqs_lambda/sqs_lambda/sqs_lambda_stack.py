from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    aws_sqs as sqs,
    aws_lambda as lambda_,
    aws_lambda_event_sources as lambda_event_sources
)


class SqsLambdaStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        queue = sqs.Queue(
            self, "SqsLambdaQueue",
            visibility_timeout=Duration.seconds(300),
        )
        lambda_function = lambda_.Function(
            self, "SQSLambda", handler="lambda_handler.handler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            code=lambda_.Code.from_asset("lambda"),
        )
        sqs_event_source = lambda_event_sources.SqsEventSource(queue)
        lambda_function.add_event_source(sqs_event_source)
