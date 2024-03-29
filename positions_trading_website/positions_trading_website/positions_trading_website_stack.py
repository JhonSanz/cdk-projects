import os
from dotenv import load_dotenv
load_dotenv()

from constructs import Construct
from aws_cdk import (
    Stack,
    aws_iam as iam,
    aws_cloudfront as cloudfront,
    aws_s3 as s3,
    aws_certificatemanager as acm,
    aws_route53 as route53,
    aws_route53_targets as targets,
    RemovalPolicy
)

class PositionsTradingWebsiteStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.domain_certificate_arn = os.getenv("domain_certificate_arn")
        self.site_domain_name = os.getenv("site_domain_name")
        self.hosted_zone_name = os.getenv("hosted_zone_name")
        self.hosted_zone_id = os.getenv("hosted_zone_id")

        bucket = self.create_site_bucket()
        hosted_zone = self.get_hosted_zone()
        certificate = self.create_certificate(hosted_zone)
        distribution = self.create_cloudfront_distribution(bucket, certificate)
        self.create_route53_record(hosted_zone, distribution)

    def create_site_bucket(self):
        block_public_access = s3.BlockPublicAccess(
            block_public_acls=False,
            ignore_public_acls=False,
            block_public_policy=False,
            restrict_public_buckets=False
        )

        bucket = s3.Bucket(
            self,
            "site_bucket",
            bucket_name=self.site_domain_name,
            website_index_document="index.html",
            website_error_document="error.html",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            block_public_access=block_public_access
        )
        bucket_policy = iam.PolicyStatement(
            actions=["s3:GetObject"],
            resources=[bucket.arn_for_objects("*")],
            principals=[iam.AnyPrincipal()],
        )
        bucket.add_to_resource_policy(bucket_policy)
        return bucket

    def get_hosted_zone(self):
        # Obitene una zona hospedada existente en la cuenta.
        # Es mejor así poruqe a veces compramos el dominio en otra página 
        # y toca copiar las direcciones
        return route53.HostedZone.from_hosted_zone_attributes(
            self,
            "hosted_zone",
            zone_name=self.hosted_zone_name,
            hosted_zone_id=self.hosted_zone_id,
        )

    def create_route53_record(self, hosted_zone, distribution):
        # Este crea el record dentro de la zona hospedada
        route53.ARecord(
            self,
            "site-alias-record",
            record_name=self.site_domain_name,
            zone=hosted_zone,
            target=route53.RecordTarget.from_alias(
                targets.CloudFrontTarget(distribution)
            ),
        )

    def create_certificate(self, hosted_zone):
        if self.domain_certificate_arn:
            # If certificate arn is provided, import the certificate
            certificate = acm.Certificate.from_certificate_arn(
                self,
                "site_certificate",
                certificate_arn=self.domain_certificate_arn,
            )
        else:
            # If certificate arn is not provided, create a new one.
            # ACM certificates that are used with CloudFront must be in
            # the us-east-1 region.
            certificate = acm.DnsValidatedCertificate(
                self,
                "site_certificate",
                domain_name=self.site_domain_name,
                hosted_zone=hosted_zone,
                region="us-east-1",
            )
        return certificate


    def create_cloudfront_distribution(self, bucket, certificate):
        # formulario de CloudFront para orígenes
        origin_source = cloudfront.CustomOriginConfig(
            domain_name=bucket.bucket_website_domain_name,
            origin_protocol_policy=cloudfront.OriginProtocolPolicy.HTTP_ONLY,
        )

        # formualrio de CloudFront para la distribución como tal
        distribution = cloudfront.CloudFrontWebDistribution(
            self,
            "cloudfront_distribution",
            viewer_certificate = cloudfront.ViewerCertificate.from_acm_certificate(certificate,
                aliases=[self.site_domain_name],
                security_policy=cloudfront.SecurityPolicyProtocol.TLS_V1_2_2021,
                ssl_method=cloudfront.SSLMethod.SNI
            ),
            origin_configs=[
                # pueden haber varios orígenes entonces especificamos que este es el por defecto
                cloudfront.SourceConfiguration(
                    custom_origin_source=origin_source,

                    behaviors=[
                        cloudfront.Behavior(
                            is_default_behavior=True,
                        ),
                    ],
                )
            ],
            viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            price_class=cloudfront.PriceClass.PRICE_CLASS_ALL,
        )
        return distribution