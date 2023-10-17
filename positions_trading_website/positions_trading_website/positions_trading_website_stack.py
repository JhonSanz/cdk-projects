from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    aws_iam as iam,
    aws_s3 as s3,
    aws_ssm as ssm,
    aws_certificatemanager as acm,
    aws_route53 as route53,
    RemovalPolicy
)


class PositionsTradingWebsiteStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

    # TODO: check aws Parameter Store clicking ssm import
    def __get_referer_header(self, parameter_name):
        return ssm.StringParameter.from_string_parameter_attributes(
            self, "custom_header", parameter_name=parameter_name
        ).string_value

    def create_site_bucket(self):
        """Creates a public S3 bucket for the static site construct"""
        self.bucket = s3.Bucket(
            self,
            "site_bucket",
            bucket_name=self._site_domain_name,
            website_index_document="index.html",
            website_error_document="error.html",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )
        bucket_policy = iam.PolicyStatement(
            actions=["s3:GetObject"],
            resources=[self.bucket.arn_for_objects("*")],
            principals=[iam.AnyPrincipal()],
        )
        # Con este permitimos que se acceda al bucket
        # unicamente desde una dirección específica
        bucket_policy.add_condition(
            "StringEquals",
            {"aws:Referer": self.__get_referer_header},
        )

        self.bucket.add_to_resource_policy(bucket_policy)
        return self.bucket

    def get_hosted_zone(self):
        """ Retrieves an specific hosted zone in our account """
        return route53.HostedZone.from_hosted_zone_attributes(
            self,
            "hosted_zone",
            zone_name=self.__hosted_zone_name,
            hosted_zone_id=self.__hosted_zone_id,
        )

    def create_certificate(self, hosted_zone):
        """ Gets or creates our certificate to enable HTTPS """
        if self.__domain_certificate_arn:
            # If certificate arn is provided, import the certificate
            self.certificate = acm.Certificate.from_certificate_arn(
                self,
                "site_certificate",
                certificate_arn=self.__domain_certificate_arn,
            )
        else:
            # If certificate arn is not provided, create a new one.
            # ACM certificates that are used with CloudFront must be in
            # the us-east-1 region.
            self.certificate = acm.DnsValidatedCertificate(
                self,
                "site_certificate",
                domain_name=self._site_domain_name,
                hosted_zone=hosted_zone,
                region="us-east-1",
            )

