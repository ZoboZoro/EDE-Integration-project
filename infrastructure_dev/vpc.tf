
# Create VPC
resource "aws_vpc" "multisource_vpc" {
  cidr_block           = "98.16.0.0/16"
  instance_tenancy     = "default"
  enable_dns_hostnames = true

  tags = merge({ Name = "multi_vpc" }, local.common_tags)
}


# Internet gateway
resource "aws_internet_gateway" "multisource_gw" {
  vpc_id = aws_vpc.multisource_vpc.id

  tags = local.common_tags
}


# Subnet
resource "aws_subnet" "public_subnet1" {
  vpc_id            = aws_vpc.multisource_vpc.id
  cidr_block        = "98.16.0.0/24"
  availability_zone = "eu-central-1b"

  tags = merge({ Name = "public_subnet1" }, local.common_tags)

}

resource "aws_subnet" "public_subnet2" {
  vpc_id            = aws_vpc.multisource_vpc.id
  cidr_block        = "98.16.1.0/24"
  availability_zone = "eu-central-1a"

  tags = merge({ Name = "public_subnet2" }, local.common_tags)

}



# Route table and route
resource "aws_route_table" "multisource_rtb" {
  vpc_id = aws_vpc.multisource_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.multisource_gw.id
  }

  tags = merge({ Name = "public_rtb" }, local.common_tags)
}

# Associate route table
resource "aws_route_table_association" "multisource_rtb" {
  subnet_id      = aws_subnet.public_subnet1.id
  route_table_id = aws_route_table.multisource_rtb.id
}

resource "aws_route_table_association" "rtb_association2" {
  subnet_id      = aws_subnet.public_subnet2.id
  route_table_id = aws_route_table.multisource_rtb.id
}


resource "aws_redshift_subnet_group" "subnet_group" {
  name        = "redshift-cluster-subnet-group"
  description = "My Redshift cluster subnet group"
  subnet_ids  = [aws_subnet.public_subnet1.id, aws_subnet.public_subnet2.id]

  tags = merge({ Name = "redshift-cluster-subnet-group" }, local.common_tags)
}

resource "aws_db_subnet_group" "db_subnetgroup" {
  name       = "db-subnet-group"
  subnet_ids = [aws_subnet.public_subnet1.id, aws_subnet.public_subnet2.id]

  tags = merge({ Name = "db-subnet-group" }, local.common_tags)

}
