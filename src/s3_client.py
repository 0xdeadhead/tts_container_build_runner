import boto3
from pathlib import Path


class S3Client:
    def __init__(self, access_key_id: str, access_key_secret: str, region: str):
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=access_key_id,
            aws_secret_access_key=access_key_secret,
            region_name=region,
        )

    def upload_file(self, file_path: Path, bucket_name: str, object_key: str):
        self.s3_client.upload_file(file_path, bucket_name, object_key)

    def generate_presigned_url(
        self, object_key: str, bucket_name: str, expires_in: int = 86400
    ) -> str:
        return self.s3_client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": bucket_name, "Key": object_key},
            ExpiresIn=expires_in,
        )
