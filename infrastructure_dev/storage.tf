resource "aws_s3_bucket" "main" {
  bucket        = "general-dumpss"
  force_destroy = true

  tags = merge({ Name = "general-dumpss" }, local.common_tags)

}

resource "aws_s3_bucket_versioning" "main_versioning" {
  bucket = aws_s3_bucket.main.id
  versioning_configuration {
    status = "Enabled"
  }
}