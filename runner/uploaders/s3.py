import os
from pathlib import Path
from urllib.parse import urlparse

import boto3

from runner.uploaders.base import BaseUploader


def _parse_bucket_name(value: str) -> str:
    """Accept either a bare bucket name or an S3 URL; always return the bucket name."""
    if value.startswith("https://") or value.startswith("http://"):
        # e.g. https://my-bucket.s3.eu-west-2.amazonaws.com
        return urlparse(value).hostname.split(".")[0]
    return value


class S3Uploader(BaseUploader):
    def __init__(self, bucket: str, region: str | None = None):
        self.bucket = _parse_bucket_name(bucket)
        self.region = region or os.environ.get("AWS_DEFAULT_REGION", "eu-west-2")
        self._client = boto3.client("s3", region_name=self.region)

    def upload(self, local_path: Path, remote_key: str) -> str:
        self._client.upload_file(
            str(local_path),
            self.bucket,
            remote_key,
            ExtraArgs={"ContentType": "application/pdf"},
        )
        return f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{remote_key}"
