import os
from pathlib import Path

import boto3

from runner.uploaders.base import BaseUploader


class S3Uploader(BaseUploader):
    def __init__(self, bucket: str, region: str | None = None):
        self.bucket = bucket
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
