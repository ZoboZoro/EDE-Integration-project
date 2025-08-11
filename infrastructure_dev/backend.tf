terraform {
  backend "s3" {
    bucket       = "terraformbackend-infra"
    key          = "ede-multisource-project/development/tf.state"
    region       = "eu-central-1"
    use_lockfile = false
  }
}
