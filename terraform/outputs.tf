output "reports_bucket_name" {
  description = "S3 bucket name — set as AWS_S3_REPORTS_BUCKET_NAME in .env"
  value       = aws_s3_bucket.reports.bucket
}

output "reports_bucket_url" {
  description = "Base URL for the public reports bucket"
  value       = "https://${aws_s3_bucket.reports.bucket}.s3.${var.aws_region}.amazonaws.com"
}
