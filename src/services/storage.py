import boto3
from io import BytesIO
from fastapi import UploadFile
from pathlib import Path
from typing import BinaryIO, Optional
from src.core.config import AppConfig
from abc import ABC, abstractmethod


class BaseStorageService(ABC):
    """Base storage class for all file storage processing"""

    @abstractmethod
    async def upload_file(
        self, file: BinaryIO | UploadFile, path: str, content_type: Optional[str] = None
    ) -> str:
        pass

    @abstractmethod
    async def download_file(self, path: str) -> BinaryIO:
        pass

    @abstractmethod
    async def delete_file(self, path: str) -> bool:
        pass

    # async def validate_file(self, file: UploadFile | BytesIO) -> str:
    #     """
    #     Check if a file has the required properties

    #     Args:
    #         `file (UploadFile | BytesIO)`: the file to be validated

    #     Returns:
    #         `extension (str)`: the file extension
    #     """
    #     # check if file type if valid
    #     if not file.file or not file.filename:
    #         raise BadActionError("File is not valid")
    #     extension = file.filename.split(".")[-1]

    #     if extension not in AppConfig.ALLOWED_FILE_FORMATS:
    #         raise BadActionError("Unsupported file format")

    #     return extension


class LocalStorageService(BaseStorageService):
    """Storage class for storing files locally in development"""

    def __init__(self):
        self.root_path = Path(AppConfig.LOCAL_STORAGE_PATH)
        # ensure root path exists
        self.root_path.mkdir(parents=True, exist_ok=True)

    async def upload_file(
        self,
        file: BinaryIO | UploadFile,
        path: str,
        content_type: str | None = None,
    ) -> str:
        """Save a file to disk"""
        file_path = self.root_path / path

        # ensure the parent path exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # read contents of file
        if isinstance(file, BytesIO):
            content = file.read()
        else:
            content = await file.read()  # type: ignore

        with open(file_path, "wb") as fs:
            fs.write(content)

        # convert to public path
        # secured path should be placed in secured directory to restrict access
        public_path = self._convert_local_path_to_public(path=str(file_path))
        return public_path

    async def download_file(self, path: str) -> BinaryIO:
        """Download or Read the contents of a file in bytes"""
        file_path = self.root_path / path
        return open(file_path, "rb")

    async def delete_file(self, path: str) -> bool:
        """Delete a file if it exists"""
        file_path = self.root_path / path
        # check if path exists
        if not file_path.exists():
            return False

        # delete file from storage
        file_path.unlink()
        return True

    def _convert_local_path_to_public(self, path: str):
        """Convert local application path to public path to improve security"""
        # secured path should be placed in secured directory to restrict access
        public_path: str = path.split(AppConfig.LOCAL_STORAGE_PATH)[1]

        return "/public" + public_path


class S3StorageService(BaseStorageService):
    """Storage class for storing files remotely on AWS S3"""

    def __init__(self):
        self.bucket_name = AppConfig.AWS_BUCKET_NAME
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=AppConfig.AWS_ACCESS_KEY,
            aws_secret_access_key=AppConfig.AWS_SECRET_KEY,
            region_name=AppConfig.AWS_REGION,
        )

    async def upload_file(
        self, file: BinaryIO | UploadFile, path: str, content_type: str | None = None
    ) -> str:
        # get the file
        if isinstance(file, UploadFile):
            file = file.file

        # define content type
        extra_args = {"ContentType": content_type} if content_type else {}

        self.s3_client.upload_fileobj(
            file, self.bucket_name, path, ExtraArgs=extra_args
        )
        return f"s3://{self.bucket_name}/{path}"

    async def download_file(self, path: str) -> BinaryIO:
        file_obj = BytesIO()
        self.s3_client.download_fileobj(self.bucket_name, path, file_obj)
        file_obj.seek(0)
        return file_obj

    async def delete_file(self, path: str) -> bool:
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=path)
            return True
        except Exception:
            return False
