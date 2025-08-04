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
  master_password           = aws_ssm_parameter.redshiftpass.value

  tags = local.common_tags
}

# Attach roles to cluster
resource "aws_redshift_cluster_iam_roles" "cluster_iam_role" {
  cluster_identifier = aws_redshift_cluster.multisource_db.cluster_identifier
  iam_role_arns      = [aws_iam_role.s3_role.arn, aws_iam_role.schedule_role.arn]
}

# resource "aws_redshift_parameter_group" "parameter_group1" {
#   name   = "parameter-group1-terraform" #"default.redshift-2.0"
#   family = "redshift-2.0"

#   parameter {
#     name  = "require_ssl"
#     value = "false"
#   }
# }


resource "aws_redshift_scheduled_action" "pause" {
  name     = "tf-redshift-scheduled-action-pause"
  schedule = "cron(30 16 * * ? *)"
  iam_role = aws_iam_role.schedule_role.arn
  target_action {
    pause_cluster {
      cluster_identifier = aws_redshift_cluster.multisource_db.cluster_identifier
    }
  }
}

resource "aws_redshift_scheduled_action" "resume" {
  name     = "tf-redshift-scheduled-action-resume"
  schedule = "cron(30 10 * * ? *)"
  iam_role = aws_iam_role.schedule_role.arn
  target_action {
    resume_cluster {
      cluster_identifier = aws_redshift_cluster.multisource_db.cluster_identifier
    }
  }
}

resource "aws_redshift_scheduled_action" "resize" {
  name     = "tf-redshift-scheduled-action-resize"
  schedule = "cron(00 15 * * ? *)"
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
