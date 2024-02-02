from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
)
from .config import BACKEND_CONFIG, VPC_CONFIG, SUBNETS


class BackendEcsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        resources = self.create_vpc()
        sec_groups = self.create_security_groups(resources["vpc"])
        self.create_private_nacl(resources["vpc"], resources["private_subnets"][0])
        self.create_cluster(
            resources["vpc"],
            resources["private_subnets"][0],
            sec_groups["private_sec_gp"],
        )

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

    def create_private_nacl(self, vpc, private_subnet):
        my_nacl = ec2.NetworkAcl(self, "MyNACL", vpc=vpc)
        my_nacl.add_entry(
            f"{VPC_CONFIG['vpc_name']}-AllowSpecificIPInbound",
            rule_number=100,
            cidr=ec2.AclCidr.ipv4(SUBNETS[0]["cidr_block"]),
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
        ec2.CfnSubnetNetworkAclAssociation(
            self,
            f"{VPC_CONFIG['vpc_name']}-MyNACLAssociation",
            subnet_id=private_subnet.subnet_id,
            network_acl_id=my_nacl.network_acl_id,
        )

    def create_vpc(self):
        resources = {
            "public_subnets": [],
            "private_subnets": [],
            "public_route_table": None,
            "private_route_table": None,
            "vpc": None,
            "all_subnets": [],
        }

        vpc = ec2.Vpc(
            self,
            VPC_CONFIG["vpc_name"],
            cidr=VPC_CONFIG["cidr"],
            nat_gateways=VPC_CONFIG["nat_gateways"],
            subnet_configuration=[],
            enable_dns_support=True,
            enable_dns_hostnames=True,
        )
        resources["vpc"] = vpc

        for subnet in SUBNETS:
            subnet_created = ec2.Subnet(
                self,
                subnet["name"],
                vpc_id=vpc.vpc_id,
                cidr_block=subnet["cidr_block"],
                availability_zone=subnet["availability_zone"],
                map_public_ip_on_launch=True,
            )
            resources[f"{subnet['type']}_subnets"].append(subnet_created)

        resources["all_subnets"] = (
            resources["public_subnets"] + resources["private_subnets"]
        )

        # internet_gateway = ec2.CfnInternetGateway(
        #     self, f"{VPC_CONFIG['vpc_name']}-internet-gateway"
        # )

        # for intex, subnet in enumerate(resources["all_subnets"]):
        #     subnet.add_route(
        #         f"{subnet.to_string()}-{intex}-{VPC_CONFIG['vpc_name']}-route",
        #         router_id=internet_gateway.ref,
        #         router_type=ec2.RouterType.GATEWAY,
        #     )

        # for type_subnet in ["public", "private"]:
        #     rt_table_created = ec2.CfnRouteTable(
        #         self,
        #         f"my-awesome-{type_subnet}-rt",
        #         vpc_id=vpc.vpc_id,
        #         tags=[
        #             {
        #                 "key": "Name",
        #                 "value": f"{VPC_CONFIG['vpc_name']}-{type_subnet}-rt",
        #             }
        #         ],
        #     )
        #     resources[f"{type_subnet}_route_table"] = rt_table_created

        #     for index, subnet in enumerate(resources[f"{type_subnet}_subnets"]):
        #         ec2.CfnSubnetRouteTableAssociation(
        #             self,
        #             f"rt-{type_subnet}-{index}-association",
        #             subnet_id=subnet.ref,
        #             route_table_id=rt_table_created.ref,
        #         )

        # internet_gateway = ec2.CfnInternetGateway(
        #     self, f"{VPC_CONFIG['vpc_name']}-internet-gateway"
        # )
        # ec2.CfnVPCGatewayAttachment(
        #     self,
        #     "internet-gateway-attachment",
        #     vpc_id=vpc.vpc_id,
        #     internet_gateway_id=internet_gateway.ref,
        # )

        # ec2.CfnRoute(
        #     self,
        #     f"my-public-route-internet",
        #     destination_cidr_block="0.0.0.0/0",
        #     gateway_id=internet_gateway.ref,
        #     route_table_id=resources["public_route_table"].ref,
        # )

        return resources

    def create_cluster(self, vpc, private_subnet, private_sec_gp):
        cluster = ecs.Cluster(self, "MyCluster", vpc=vpc)

        task_definition = ecs.FargateTaskDefinition(
            self,
            f"{VPC_CONFIG['vpc_name']}-MyFargateTaskDefinition",
            memory_limit_mib=512,  # 512 is 0.5 GB
            cpu=256,  # 256 is 0.25 vCPU
        )

        task_definition.add_container(
            f"{VPC_CONFIG['vpc_name']}-MyBackendContainer",
            image=ecs.ContainerImage.from_registry(BACKEND_CONFIG["docker_image"]),
            memory_reservation_mib=256,
        )

        service = ecs.FargateService(
            self,
            "MyService",
            cluster=cluster,
            task_definition=task_definition,
            desired_count=1,
            assign_public_ip=False,
            vpc_subnets=ec2.SubnetSelection(subnets=[private_subnet]),
            security_groups=[private_sec_gp],
        )
