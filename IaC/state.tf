/*
resource "aws_s3_bucket" "audio_curl_bot_bucket" {
  bucket = "audio-curl-bot-state-bucket"

  force_destroy = false

  tags = {
    Name        = "audio-curl-bot-state-bucket"
    Environment = "prod"
  }
}
*/
resource "aws_s3_bucket_versioning" "audio_curl_bot_bucket_versioning" {
  bucket = aws_s3_bucket.audio_curl_bot_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "audio_curl_bot_bucket_encryption" {
  bucket = aws_s3_bucket.audio_curl_bot_bucket.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "audio_curl_bot_bucket_block" {
  bucket                  = aws_s3_bucket.audio_curl_bot_bucket.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "audio_curl_bot_bucket_ownership_controls" {
  bucket = aws_s3_bucket.audio_curl_bot_bucket.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "audio_curl_bot_bucket_private_acl" {
  depends_on = [aws_s3_bucket_ownership_controls.audio_curl_bot_bucket_ownership_controls]
  bucket     = aws_s3_bucket.audio_curl_bot_bucket.id
  acl        = "private"
}