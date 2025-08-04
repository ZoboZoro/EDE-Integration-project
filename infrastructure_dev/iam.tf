
# IAM Roles for Redshift
resource "aws_iam_role" "s3_role" {
  name = "redshift_s3_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Sid    = ""
      Principal = {
        Service = "redshift.amazonaws.com"
      }
    }]
  })

  tags = local.common_tags
}

resource "aws_iam_role" "schedule_role" {
  name = "schedule_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "scheduler.redshift.amazonaws.com"
        }
      },
    ]
  })

  tags = local.common_tags
}


# Access Policies
resource "aws_iam_policy" "redshift_s3_access_policy" {
  name        = "redshift-s3-access-policy"
  description = "Policy to allow Redshift to read from a specific S3 bucket"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:ListAllMyBuckets"
        ]
        Resource = [
          "*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:*"
        ]
        Resource = [
          "arn:aws:s3:::general-dumpss/*"
        ]
      },
    ]
  })
}


resource "aws_iam_policy" "schedule_policy" {
  name        = "redshift-schedule-policy"
  description = "Policy to allow Redshift scheduler to pause and resume cluster"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "redshift:PauseCluster",
          "redshift:ResumeCluster"
        ],
        Resource = "arn:aws:redshift:eu-central-1:517819573047:cluster/*"
        #"arn:aws:redshift:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:cluster/*"
      }
    ]
  })
}


# Attach access Policies to the IAM Roles
resource "aws_iam_role_policy_attachment" "redshift_s3_policy_attachment" {
  role       = aws_iam_role.s3_role.name
  policy_arn = aws_iam_policy.redshift_s3_access_policy.arn
}

resource "aws_iam_role_policy_attachment" "schedule_policy_attachment" {
  role       = aws_iam_role.schedule_role.name
  policy_arn = aws_iam_policy.schedule_policy.arn
}
