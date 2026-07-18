terraform {
  required_version = ">= 1.6"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region             = var.aws_region
  allowed_account_ids = [var.aws_account_id]
}

locals {
  global_prefix = "${var.aws_account_id}-${var.project}"
  scoped_prefix = var.project
}

# ---------------------------------------------------------------------------
# S3 — Reports bucket (public-read; PDFs are linked directly by URL)
# ---------------------------------------------------------------------------

resource "aws_s3_bucket" "reports" {
  bucket = "${local.global_prefix}-reports"
}

resource "aws_s3_bucket_public_access_block" "reports" {
  bucket                  = aws_s3_bucket.reports.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_ownership_controls" "reports" {
  bucket = aws_s3_bucket.reports.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_policy" "reports_public_read" {
  bucket = aws_s3_bucket.reports.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = ["s3:GetObject", "s3:ListBucket"]
        Resource = [
          aws_s3_bucket.reports.arn,
          "${aws_s3_bucket.reports.arn}/*",
        ]
      }
    ]
  })

  depends_on = [aws_s3_bucket_public_access_block.reports]
}
