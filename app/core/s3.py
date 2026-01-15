import aioboto3
from dotenv import load_dotenv
from fastapi import UploadFile
import os
import uuid  # Для уникальных имен файлов

load_dotenv()

ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL", "http://localhost:9000")
ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
SECRET_KEY = os.getenv("S3_SECRET_KEY")
BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "blog-images")


async def upload_image_to_s3(file: UploadFile) -> str:
    session = aioboto3.Session()
    async with session.client(
        "s3",
        endpoint_url=ENDPOINT_URL,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
    ) as s3:
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = f"articles/{unique_filename}"

        file_content = await file.read()

        await s3.put_object(
            Bucket=BUCKET_NAME,
            Key=file_path,
            Body=file_content,
            ContentType=file.content_type,
        )

        return f"http://localhost:9000/{BUCKET_NAME}/{file_path}"
