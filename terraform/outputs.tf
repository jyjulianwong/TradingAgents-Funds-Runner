output "reports_bucket_name" {
  description = "S3 bucket name — set as AWS_S3_REPORTS_BUCKET_NAME in .env"
  value       = aws_s3_bucket.reports.bucket
}

output "reports_bucket_url" {
  description = "Base URL for the public reports bucket"
  value       = "https://${aws_s3_bucket.reports.bucket}.s3.${var.aws_region}.amazonaws.com"
}

output "github_actions_access_key_id" {
  description = "AWS access key ID for GitHub Actions — store as GitHub secret AWS_ACCESS_KEY_ID"
  value       = aws_iam_access_key.github_actions.id
}

output "github_actions_secret_access_key" {
  description = "AWS secret access key for GitHub Actions — store as GitHub secret AWS_SECRET_ACCESS_KEY"
  value       = aws_iam_access_key.github_actions.secret
  sensitive   = true
}
