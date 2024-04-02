import os
from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    aws_sns_subscriptions as subs,
    aws_ec2 as ec2,
    aws_events as events,
    aws_lambda as _lambda,
    aws_s3 as s3,
    aws_iam as iam,
    aws_events_targets as targets,
    RemovalPolicy,
)
from .handler_generator import generate_lambda_function


class Horariosimplev1Stack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.create_site_bucket()
        self.create_hosted_ec2_backend()

    def create_hosted_ec2_backend(self):
        vpc = ec2.Vpc(self, "HorarioSimpleVpc", max_azs=1)
        instance = ec2.Instance(
            self,
            "HorariosimpleInstance",
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T4G, ec2.InstanceSize.SMALL
            ),
            machine_image=ec2.MachineImage.latest_amazon_linux2(),
            vpc=vpc,
        )
        # generate_lambda_function(str(instance.instance_public_ip))
        # raise Exception
        current_dir = os.path.dirname(__file__)
        lambda_function = _lambda.Function(
            self,
            "HorariosimpleBackupsGenerator",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda_function.handler",
            code=_lambda.Code.from_asset(
                os.path.join(current_dir, "horarioSimpleFunction.zip")
            ),
        )
        rule = events.Rule(
            self,
            "MyScheduledRule",
            schedule=events.Schedule.cron(
                minute="0", hour="22", month="*", week_day="*", year="*"
            ),
        )
        rule.add_target(targets.LambdaFunction(lambda_function))

    def create_site_bucket(self):
        block_public_access = s3.BlockPublicAccess(
            block_public_acls=False,
            ignore_public_acls=False,
            block_public_policy=False,
            restrict_public_buckets=False,
        )

        bucket = s3.Bucket(
            self,
            "site_bucket",
            bucket_name="horario-simple-website",
            website_index_document="index.html",
            website_error_document="error.html",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            block_public_access=block_public_access,
        )
        bucket_policy = iam.PolicyStatement(
            actions=["s3:GetObject"],
            resources=[bucket.arn_for_objects("*")],
            principals=[iam.AnyPrincipal()],
        )
        bucket.add_to_resource_policy(bucket_policy)
        return bucket
