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
  cluster_identifier           = "tf-multisource-warehouse"
  database_name                = "prod_4wdhealth"
  master_username              = var.master_username
  node_type                    = "ra3.large"
  cluster_type                 = "multi-node"
  publicly_accessible          = true
  number_of_nodes              = 2
  vpc_security_group_ids       = [aws_security_group.sg1.id]
  cluster_subnet_group_name    = aws_redshift_subnet_group.subnet_group.name
  master_password              = aws_ssm_parameter.redshiftpass.value
  skip_final_snapshot          = true
  iam_roles                    = [aws_iam_role.s3_role.arn, aws_iam_role.schedule_role.arn]
  cluster_parameter_group_name = aws_redshift_parameter_group.custom.name
  apply_immediately            = true


  tags = local.common_tags
}


resource "aws_redshift_parameter_group" "custom" {
  name   = "custom-parameter-group"
  family = "redshift-2.0"

  parameter {
    name  = "require_ssl"
    value = "true"
  }

  tags = local.common_tags
}

# Attach roles to cluster
resource "aws_redshift_cluster_iam_roles" "cluster_iam_role" {
  cluster_identifier = aws_redshift_cluster.multisource_db.cluster_identifier
  iam_role_arns      = [aws_iam_role.s3_role.arn, aws_iam_role.schedule_role.arn]
}


resource "aws_redshift_scheduled_action" "pause" {
  name     = "tf-redshift-scheduled-action-pause"
  schedule = "cron(30 15 * * ? *)"
  iam_role = aws_iam_role.schedule_role.arn
  target_action {
    pause_cluster {
      cluster_identifier = aws_redshift_cluster.multisource_db.cluster_identifier
    }
  }
}

resource "aws_redshift_scheduled_action" "resume" {
  name     = "tf-redshift-scheduled-action-resume"
  schedule = "cron(00 9 * * ? *)"
  iam_role = aws_iam_role.schedule_role.arn
  target_action {
    resume_cluster {
      cluster_identifier = aws_redshift_cluster.multisource_db.cluster_identifier
    }
  }
}

resource "aws_redshift_scheduled_action" "resize" {
  name     = "tf-redshift-scheduled-action-resize"
  schedule = "cron(00 13 * * ? *)"
  iam_role = aws_iam_role.schedule_role.arn

  target_action {
    resize_cluster {
      cluster_identifier = aws_redshift_cluster.multisource_db.cluster_identifier
      cluster_type       = "multi-node"
      node_type          = "dc1.large"
      number_of_nodes    = 1
    }
  }
}


# RDS
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
  allocated_storage       = 20
  storage_type            = "gp2"
  engine                  = "postgres"
  engine_version          = "17.4"
  identifier              = "production-postgres1"
  instance_class          = "db.t4g.micro"
  db_name                 = "production4wdhealthdb"
  username                = var.db_username
  password                = aws_ssm_parameter.rdssecret.value
  db_subnet_group_name    = aws_db_subnet_group.db_subnetgroup.name
  parameter_group_name    = "default.postgres17"
  vpc_security_group_ids = [aws_security_group.sg1.id]
  publicly_accessible     = true
  skip_final_snapshot     = true
  backup_retention_period = 0
  apply_immediately       = true

  tags = local.common_tags
}
