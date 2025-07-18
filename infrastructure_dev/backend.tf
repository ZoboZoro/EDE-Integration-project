terraform {
  backend "s3" {
    bucket = "terraform-state"
    key    = "dev/tf.state"
    region = "eu-west-1"
  }
}
