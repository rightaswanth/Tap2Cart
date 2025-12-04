import boto3
from botocore.exceptions import NoCredentialsError
from fastapi import UploadFile, HTTPException
import uuid
import os
from app.config import settings

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region
        )
        self.bucket_name = settings.s3_bucket_name

    async def upload_file(self, file: UploadFile, folder: str = "products") -> str:
        """
        Upload a file to S3 and return the URL.
        """
        if not self.bucket_name:
            raise HTTPException(status_code=500, detail="S3 bucket name not configured")

        # Generate a unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{folder}/{uuid.uuid4()}{file_extension}"

        try:
            # Upload the file
            # We use file.file which is the actual Python file object
            self.s3_client.upload_fileobj(
                file.file,
                self.bucket_name,
                unique_filename,
                ExtraArgs={
                    "ContentType": file.content_type,
                    "ACL": "public-read"
                }
            )

            # Construct the URL
            # Assuming standard S3 URL format. 
            # If using a custom domain or CloudFront, this would need adjustment.
            url = f"https://{self.bucket_name}.s3.{settings.aws_region}.amazonaws.com/{unique_filename}"
            return url

        except NoCredentialsError:
            raise HTTPException(status_code=500, detail="AWS credentials not found")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to upload file to S3: {str(e)}")
