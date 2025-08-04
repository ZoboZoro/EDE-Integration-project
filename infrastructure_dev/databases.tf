# Redshift provision
resource "random_password" "mastersecret" {
  length           = 16
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

resource "aws_ssm_parameter" "redshiftpass" {
  name  = "/production/redshift/secret/master"
  type  = "SecureString"
  value = random_password.mastersecret.result
}


resource "aws_redshift_cluster" "multisource_db" {
  cluster_identifier        = "tf-multisource-warehouse"
  database_name             = "prod_4wdhealth"
  master_username           = var.master_username
  node_type                 = "ra3.large"
  cluster_type              = "multi-node"
  publicly_accessible       = true
  number_of_nodes           = 2
  vpc_security_group_ids    = [aws_security_group.sg1.id]
  cluster_subnet_group_name = aws_redshift_subnet_group.subnet_group.name
  iam_roles                 = []
  master_password           = aws_ssm_parameter.redshiftpass.value

  tags = local.common_tags
}

# RDS provision
resource "random_password" "rdsmastersecret" {
  length           = 16
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

resource "aws_ssm_parameter" "rdssecret" {
  name  = "/production/rds/secret/master"
  type  = "SecureString"
  value = random_password.rdsmastersecret.result
}

resource "aws_db_instance" "rds" {
  allocated_storage = 20
  storage_type      = "gp2"
  engine            = "postgres"
  engine_version    = "17.4"
  identifier        = "production-postgres1"
  instance_class    = "db.t4g.micro"
  db_name           = "production4wdhealthdb"
  username          = var.db_username
  password          = aws_ssm_parameter.rdssecret.value
  # port                 = 5439
  #db_subnet_group_name = aws_db_subnet_group.sunbet_g1.id
  parameter_group_name = "default.postgres17"
  publicly_accessible  = true

  tags = local.common_tags
}
