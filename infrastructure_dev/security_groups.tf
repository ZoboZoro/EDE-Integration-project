
resource "aws_security_group" "sg1" {
  name        = "sg1"
  description = "Allow inbound traffic from specific ports on any network, and all outbound traffic"
  vpc_id      = aws_vpc.multisource_vpc.id

  tags = concat({Name = "sg1"}, local.common_tags)

}

resource "aws_vpc_security_group_ingress_rule" "ingress1" {
  security_group_id = aws_security_group.sg1.id
  cidr_ipv4         = "0.0.0.0/0" 
  from_port         = 443
  ip_protocol       = "tcp"
  to_port           = 443
}

resource "aws_vpc_security_group_ingress_rule" "ingress2" {
  security_group_id = "0.0.0.0/0"  #aws_security_group.sg1.id
  cidr_ipv4         = aws_vpc.multisource_vpc.cidr_block 
  from_port         = 22
  ip_protocol       = "tcp"
  to_port           = 22
}

resource "aws_vpc_security_group_egress_rule" "egress1" {
  security_group_id = aws_security_group.sg1.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1" # semantically equivalent to all ports
}
