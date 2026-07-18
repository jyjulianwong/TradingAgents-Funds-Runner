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

# ---------------------------------------------------------------------------
# IAM — GitHub Actions user (Terraform plan + apply)
# ---------------------------------------------------------------------------

resource "aws_iam_user" "github_actions" {
  name = "${local.scoped_prefix}-github-actions-user"
}

data "aws_iam_policy_document" "github_actions" {
  statement {
    sid    = "TerraformState"
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject",
      "s3:ListBucket",
    ]
    resources = [
      "arn:aws:s3:::${local.global_prefix}-terraform-state",
      "arn:aws:s3:::${local.global_prefix}-terraform-state/*",
    ]
  }

  statement {
    sid    = "TerraformLock"
    effect = "Allow"
    actions = [
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:DeleteItem",
    ]
    resources = ["arn:aws:dynamodb:${var.aws_region}:*:table/${local.scoped_prefix}-terraform-lock"]
  }

  statement {
    sid    = "TerraformApply"
    effect = "Allow"
    actions = ["s3:*", "iam:*"]
    resources = ["*"]
    condition {
      test     = "StringLike"
      variable = "aws:RequestedRegion"
      values   = [var.aws_region]
    }
  }

  # IAM is a global service — no aws:RequestedRegion condition applies.
  statement {
    sid       = "TerraformApplyIAM"
    effect    = "Allow"
    actions   = ["iam:*"]
    resources = ["*"]
  }
}

resource "aws_iam_user_policy" "github_actions" {
  name   = "${local.scoped_prefix}-github-actions-user-policy"
  user   = aws_iam_user.github_actions.name
  policy = data.aws_iam_policy_document.github_actions.json
}

resource "aws_iam_access_key" "github_actions" {
  user = aws_iam_user.github_actions.name
}

resource "aws_s3_bucket_cors_configuration" "reports" {
  bucket = aws_s3_bucket.reports.id
  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "HEAD"]
    allowed_origins = ["*"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}
