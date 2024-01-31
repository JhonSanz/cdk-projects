VPC_CONFIG = {
    "vpc_name": "my-awesome-project",
    "cidr": "10.6.6.0/27",
    "nat_gateways": 0,
}
SUBNETS = [
    {
        "type": "public",
        "name": "my-awesome-public-subnet",
        "cidr_block": "10.6.6.0/28",
        "availability_zone": "us-east-1a",
    },
    {
        "type": "private",
        "name": "my-awesome-private-subnet",
        "cidr_block": "10.6.6.16/28",
        "availability_zone": "us-east-1a",
    },
]