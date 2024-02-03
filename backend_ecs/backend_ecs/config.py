from aws_cdk import aws_ec2 as ec2

BACKEND_CONFIG = {
    "docker_image": "nginx:latest"
}

VPC_CONFIG = {
    "vpc_name": "my-awesome-project",
    "cidr": "10.6.6.0/24",
    "nat_gateways": 0,
    "availability_zones": ["us-east-1a"],
}
