# Redshift provision
resource "random_password" "mastersecret" {
    length           = 16
    special          = true
    override_special = "!#$%&*()-_=+[]{}<>:?"
}

resource "aws_ssm_parameter" "secret" {
    name  = "production/redshift/secret/master"
    type  = "SecureString"
    value = random_password.mastersecret.result
}


resource "aws_redshift_cluster" "multisource_db" {
  cluster_identifier = "tf-multisource-warehouse"
  database_name      = "production_4wdhealth_warehouse"
  master_username    = var.master_username
  node_type          = "dc1.large"
  cluster_type       = "multi-node"
  vpc_security_group_ids =  [aws_security_group.sg1.id]
  cluster_subnet_group_name = aws_subnet.public_subnet1.arn

  master_password = aws_ssm_parameter.secret.value

  tags = local.common_tags
}


# RDS provision
resource "random_password" "rdsmastersecret" {
    length           = 16
    special          = true
    override_special = "!#$%&*()-_=+[]{}<>:?"
}

resource "aws_ssm_parameter" "rdssecret" {
    name  = "production/rds/secret/master"
    type  = "SecureString"
    value = random_password.rdsmastersecret.result
}

resource "aws_db_instance" "rds" {
  allocated_storage    = 20
  storage_type         = "gp2"
  engine               = "postgres"
  engine_version       = "17.4"
  identifier           = "production-postgres1"
  instance_class       = "db.t4g.micro"
  db_name              = "production/4wdhealthdb"
  username             = var.db_username
  password             = aws_ssm_parameter.rdssecret.value
  port = 5437
  db_subnet_group_name = aws_db_subnet_group.sunbet_g1.id
  parameter_group_name = "default.postgres17"
  publicly_accessible = true

  tags = local.common_tags
}
