
# Create VPC
resource "aws_vpc" "multisource_vpc" {
  cidr_block           = "98.16.0.0/16"
  instance_tenancy     = "default"
  enable_dns_hostnames = true

  tags = local.common_tags
}


# Create internet gateway
resource "aws_internet_gateway" "multisource_gw" {
  vpc_id = aws_vpc.multisource_vpc.id

  tags = local.common_tags
}

# resource "aws_internet_gateway_attachment" "multisource_gw_attachment" {
#   internet_gateway_id = aws_internet_gateway.multisource_gw.id
#   vpc_id              = aws_vpc.multisource_vpc.id
# }


# Create Subnets
resource "aws_subnet" "public_subnet1" {
  vpc_id                  = aws_vpc.multisource_vpc.id
  cidr_block              = "98.16.0.0/24"
  map_public_ip_on_launch = true

  tags = local.common_tags

}

resource "aws_subnet" "private_subnet1" {
  vpc_id     = aws_vpc.multisource_vpc.id
  cidr_block = "98.16.1.0/24"

  tags = local.common_tags
}


# Route table and routes
resource "aws_route_table" "multisource_rtb" {
  vpc_id = aws_vpc.multisource_vpc.id

  tags = local.common_tags
}

resource "aws_route" "multisource_route_toInternetgw" {
  route_table_id         = aws_route_table.multisource_rtb.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.multisource_gw.id
}

# resource "aws_route" "multisource_route_toNatgw" {
#   route_table_id         = aws_route_table.multisource_rtb.id
#   destination_cidr_block = "98.16.1.0/24"
#   gateway_id             = aws_internet_gateway.multisource_gw.id
# }


# Associate route table
resource "aws_route_table_association" "multisource_rtb" {
  subnet_id      = aws_subnet.public_subnet1.id
  route_table_id = aws_route_table.multisource_rtb.id
}


# Subnet group
# resource "aws_db_subnet_group" "subnet_g1" {
#   name       = "db_subnetgroup1"
#   subnet_ids = [aws_subnet.public_subnet1.id, aws_subnet.private_subnet1.id]

#   tags =merge({Name = "db_subnetgroup1"}, local.common_tags)
# }
