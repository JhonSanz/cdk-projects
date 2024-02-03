from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
)
from .config import BACKEND_CONFIG, VPC_CONFIG


class BackendEcsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        vpc = self.create_vpc()
        sec_groups = self.create_security_groups(vpc)
        self.create_private_nacl(vpc)

    def create_security_groups(self, vpc):
        internet_sg = ec2.SecurityGroup(
            self, f"{VPC_CONFIG['vpc_name']}-public-sg", vpc=vpc
        )
        internet_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80))
        internet_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(22))

        internal_sg = ec2.SecurityGroup(
            self, f"{VPC_CONFIG['vpc_name']}-private-sg", vpc=vpc
        )
        internal_sg.add_ingress_rule(internet_sg, ec2.Port.all_traffic())
        return {
            "public_sec_gp": internet_sg,
            "private_sec_gp": internal_sg,
        }

    def create_private_nacl(self, vpc):
        my_nacl = ec2.NetworkAcl(
            self,
            "MyNACL",
            vpc=vpc,
            subnet_selection=ec2.SubnetSelection(subnets=vpc.isolated_subnets),
        )
        my_nacl.add_entry(
            f"{VPC_CONFIG['vpc_name']}-AllowSpecificIPInbound",
            rule_number=100,
            cidr=ec2.AclCidr.ipv4(vpc.public_subnets[0].ipv4_cidr_block),
            traffic=ec2.AclTraffic.all_traffic(),
            direction=ec2.TrafficDirection.INGRESS,
        )
        my_nacl.add_entry(
            f"{VPC_CONFIG['vpc_name']}-AllowAllOutbound",
            rule_number=200,
            cidr=ec2.AclCidr.any_ipv4(),
            traffic=ec2.AclTraffic.all_traffic(),
            direction=ec2.TrafficDirection.EGRESS,
        )

    def create_vpc(self):
        subnet_config = [
            ec2.SubnetConfiguration(
                name="PublicSubnet",
                subnet_type=ec2.SubnetType.PUBLIC,
                cidr_mask=28,
            ),
            ec2.SubnetConfiguration(
                name="VpnSubnet",
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                cidr_mask=28,
            ),
        ]

        vpc = ec2.Vpc(
            self,
            VPC_CONFIG["vpc_name"],
            cidr=VPC_CONFIG["cidr"],
            nat_gateways=VPC_CONFIG["nat_gateways"],
            subnet_configuration=subnet_config,
            enable_dns_support=True,
            enable_dns_hostnames=True,
            availability_zones=VPC_CONFIG["availability_zones"],
        )
        return vpc

    # def create_cluster(self, vpc, private_subnet, private_sec_gp):
    #     cluster = ecs.Cluster(self, "MyCluster", vpc=vpc)

    #     task_definition = ecs.FargateTaskDefinition(
    #         self,
    #         f"{VPC_CONFIG['vpc_name']}-MyFargateTaskDefinition",
    #         memory_limit_mib=512,  # 512 is 0.5 GB
    #         cpu=256,  # 256 is 0.25 vCPU
    #     )

    #     task_definition.add_container(
    #         f"{VPC_CONFIG['vpc_name']}-MyBackendContainer",
    #         image=ecs.ContainerImage.from_registry(BACKEND_CONFIG["docker_image"]),
    #         memory_reservation_mib=256,
    #     )

    #     service = ecs.FargateService(
    #         self,
    #         "MyService",
    #         cluster=cluster,
    #         task_definition=task_definition,
    #         desired_count=1,
    #         assign_public_ip=False,
    #         vpc_subnets=ec2.SubnetSelection(subnets=[private_subnet]),
    #         security_groups=[private_sec_gp],
    #     )
