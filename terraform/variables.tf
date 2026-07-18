variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "eu-west-2"
}

variable "aws_account_id" {
  description = "AWS account ID — Terraform will refuse to apply if active credentials resolve to a different account"
  type        = string
}

variable "project" {
  description = "Short project identifier used to namespace resource names"
  type        = string
  default     = "jyjulianwong-tafr"
}
