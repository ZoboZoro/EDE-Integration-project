terraform {
  backend "s3" {
    bucket = "terraform-state"
    key    = "development/tf.state"
    region = "eu-west-1"
    use_lockfile = true
  }
}
