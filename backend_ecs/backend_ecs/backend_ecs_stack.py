from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
)
from .config import VPC_CONFIG, SUBNETS


class BackendEcsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(
            self,
            VPC_CONFIG["vpc_name"],
            cidr=VPC_CONFIG["cidr"],
            nat_gateways=VPC_CONFIG["nat_gateways"],
            subnet_configuration=[],
            enable_dns_support=True,
            enable_dns_hostnames=True,
        )

        resources = {
            "public_subnets": [],
            "private_subnets": [],
            "public_route_table": None,
            "private_route_table": None,
        }

        for subnet in SUBNETS:
            subnet_created = ec2.CfnSubnet(
                self,
                subnet["name"],
                vpc_id=vpc.vpc_id,
                cidr_block=subnet["cidr_block"],
                availability_zone=subnet["availability_zone"],
                tags=[{"key": "Name", "value": subnet["name"]}],
                map_public_ip_on_launch=True,
            )
            resources[f"{subnet['type']}_subnets"].append(subnet_created)

        for type_subnet in ["public", "private"]:
            rt_table_created = ec2.CfnRouteTable(
                self,
                f"my-awesome-{type_subnet}-rt",
                vpc_id=vpc.vpc_id,
                tags=[{"key": "Name", "value": f"my-awesome-{type_subnet}-rt"}],
            )
            resources[f"{type_subnet}_route_table"] = rt_table_created

            for index, subnet in enumerate(resources[f"{type_subnet}_subnets"]):
                ec2.CfnSubnetRouteTableAssociation(
                    self,
                    f"rt-{type_subnet}-{index}-association",
                    subnet_id=subnet.ref,
                    route_table_id=rt_table_created.ref,
                )

        internet_gateway = ec2.CfnInternetGateway(self, "my-awesome-internet-gateway")
        ec2.CfnVPCGatewayAttachment(
            self,
            "internet-gateway-attachment",
            vpc_id=vpc.vpc_id,
            internet_gateway_id=internet_gateway.ref,
        )

        ec2.CfnRoute(
            self,
            f"my-public-route-internet",
            destination_cidr_block="0.0.0.0/0",
            gateway_id=internet_gateway.ref,
            route_table_id=resources["public_route_table"].ref
        )

        # cluster = ecs.Cluster(self, "Cluster", vpc=vpc)

        # # Crea una tarea (task) de ECS
        # task_definition = ecs.FargateTaskDefinition(self, "MyTaskDefinition")

        # # Define un contenedor en la tarea
        # container = task_definition.add_container(
        #     "MyContainer",
        #     image=ecs.ContainerImage.from_registry("nginx"),
        #     memory_limit_mib=512,
        # )

        # # Crea un servicio de ECS en el clúster
        # ecs_patterns.ApplicationLoadBalancedFargateService(
        #     self,
        #     "MyFargateService",
        #     cluster=cluster,
        #     task_definition=task_definition,
        #     public_load_balancer=True,  # Usa un balanceador de carga público
        # )
