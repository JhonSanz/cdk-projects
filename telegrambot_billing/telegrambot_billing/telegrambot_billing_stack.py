from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_budgets as budgets,  # nivel L1
)
from aws_cdk.aws_lambda_python_alpha import PythonFunction
from constructs import Construct


class TelegrambotBillingStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # Lambda auditor
        billing_fn = PythonFunction(
            self,
            "TelegramBotDataGenerator",
            description="Queries bill report and send it through telegram",
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

        # -------------------------------
        # SNS Topic para alertas de Budget
        # -------------------------------
        topic = sns.Topic(
            self, "BillingAlertsTopic",
            display_name="Billing Alerts Topic"
        )

        # Agrega aquí tu correo
        topic.add_subscription(
            subs.EmailSubscription("ingjhonsanz@gmail.com")
        )

        topic.add_to_resource_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                principals=[iam.ServicePrincipal("budgets.amazonaws.com")],
                actions=["SNS:Publish"],
                resources=[topic.topic_arn],
            )
        )
        # -------------------------------
        # Crear Budgets (3, 5, 10 y 20 USD)
        # -------------------------------
        for amount in [3, 5, 10, 20]:
            budgets.CfnBudget(
                self,
                f"Budget{amount}USD",
                budget=budgets.CfnBudget.BudgetDataProperty(
                    budget_type="COST",
                    time_unit="MONTHLY",
                    budget_limit=budgets.CfnBudget.SpendProperty(
                        amount=float(amount),
                        unit="USD"
                    )
                ),
                notifications_with_subscribers=[
                    budgets.CfnBudget.NotificationWithSubscribersProperty(
                        notification=budgets.CfnBudget.NotificationProperty(
                            notification_type="ACTUAL",  # cuando el costo real excede
                            comparison_operator="GREATER_THAN",
                            threshold=float(amount),  # mismo valor que el límite
                            threshold_type="ABSOLUTE_VALUE"
                        ),
                        subscribers=[
                            budgets.CfnBudget.SubscriberProperty(
                                subscription_type="SNS",
                                address=topic.topic_arn
                            )
                        ]
                    )
                ]
            )