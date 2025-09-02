from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam,
)
from aws_cdk.aws_lambda_python_alpha import PythonFunction
from constructs import Construct


class TelegrambotBillingStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # Lambda auditor
        billing_fn = PythonFunction(
            self,
            "GetDemosLugares360",
            description="Lambda function to get demos for Lugares360",
            entry="./lambdas/notifier",
            runtime=_lambda.Runtime.PYTHON_3_13,
            index="handler.py",
            handler="lambda_handler",
            timeout=Duration.minutes(1),
            environment={
                "TELEGRAM_TOKEN": "<PON_AQUI_TU_TOKEN>",
                "CHAT_ID": "<PON_AQUI_TU_CHATID>",
            },
        )

        # Política mínima necesaria
        billing_fn.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "ce:GetCostAndUsage"
                ],
                resources=["*"]
            )
        )

        billing_fn.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                resources=["*"]
            )
        )

        rule_noon = events.Rule(
            self, "DailyAuditNoon",
            schedule=events.Schedule.cron(minute="0", hour="14")
        )
        rule_noon.add_target(targets.LambdaFunction(billing_fn))

        rule_evening = events.Rule(
            self, "DailyAuditEvening",
            schedule=events.Schedule.cron(minute="0", hour="0")
        )
        rule_evening.add_target(targets.LambdaFunction(billing_fn))
