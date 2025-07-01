# Fetch .env and cookies.txt from AWS Secrets Manager and write to files using user_data
data "aws_secretsmanager_secret_version" "env_file" {
  secret_id = "audio-curl-bot-env"
}

data "aws_secretsmanager_secret_version" "cookies_file" {
  secret_id = "audio-curl-bot-cookies"
}
