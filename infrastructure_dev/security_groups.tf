
resource "aws_security_group" "sg1" {
  name        = "sg1"
  description = "Allow inbound traffic from specific ports on any network, and all outbound traffics"
  vpc_id      = aws_vpc.multisource_vpc.id

  tags = merge({ Name = "sg1" }, local.common_tags)

}

resource "aws_vpc_security_group_ingress_rule" "ingress1_https" {
  security_group_id = aws_security_group.sg1.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 443
  ip_protocol       = "tcp"
  to_port           = 443
}

resource "aws_vpc_security_group_ingress_rule" "ingress2_ssh" {
  security_group_id = aws_security_group.sg1.id
  cidr_ipv4         = aws_vpc.multisource_vpc.cidr_block
  from_port         = 22
  ip_protocol       = "tcp"
  to_port           = 22
}

resource "aws_vpc_security_group_ingress_rule" "ingress3_postgres" {
  security_group_id = aws_security_group.sg1.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 5432
  ip_protocol       = "tcp"
  to_port           = 5432
}

resource "aws_vpc_security_group_ingress_rule" "ingress4_redshift" {
  security_group_id = aws_security_group.sg1.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 5439
  ip_protocol       = "tcp"
  to_port           = 5439
}

# resource "aws_vpc_security_group_ingress_rule" "ingress5_all" {
#   security_group_id = aws_security_group.sg1.id
#   cidr_ipv4         = "0.0.0.0/0"
#   ip_protocol       = "-1"
# }

resource "aws_vpc_security_group_egress_rule" "egress1" {
  security_group_id = aws_security_group.sg1.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}
