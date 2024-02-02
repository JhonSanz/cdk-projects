from aws_cdk import aws_ec2 as ec2

BACKEND_CONFIG = {
    "docker_image": "nginx:latest"
}

VPC_CONFIG = {
    "vpc_name": "my-awesome-project",
    "cidr": "10.6.6.0/24",
    "nat_gateways": 0,
}
SUBNETS = [
    {
        "type": "public",
        "type_ec2": ec2.SubnetType.PUBLIC,
        "name": "my-awesome-public-subnet",
        "availability_zone": "us-east-1a",
        "cidr_block": "10.6.6.0/28",
    },
    {
        "type": "private",
        "type_ec2": ec2.SubnetType.PRIVATE_ISOLATED,
        "name": "my-awesome-private-subnet",
        "availability_zone": "us-east-1a",
        "cidr_block": "10.6.6.16/28",
    },
]