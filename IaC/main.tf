terraform {
  backend "s3" {
    bucket         = "audio-curl-bot-state-bucket"
    key            = "global/s3/terraform.tfstate"
    region         = "us-east-1"
    // dynamodb_table = "dynamoDB_to_lock_terraform_state"
    encrypt        = true
  }
}

provider aws {
  region = var.aws_region
}