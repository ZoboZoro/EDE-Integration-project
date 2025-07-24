terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }

    random = {
      source  = "hashicorp/random"
      version = "3.7.2"
    }
  }
}

# Configure Providers
provider "aws" {
  profile = "taofeecoh"
  region  = "eu-central-1"
}

provider "random" {

}