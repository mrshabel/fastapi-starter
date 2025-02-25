import uuid
from fastapi import APIRouter, status, UploadFile, File
from fastapi.logger import logger
from src.models import file as file_models, Message
from src.api.dependencies import StorageServiceDep
from src.core.exceptions import NotFoundError, InternalServerError

router = APIRouter(
    prefix="/files",
    tags=["File Endpoints"],
    responses={
        201: {"description": "File created successfully"},
        404: {"description": "File not found"},
    },
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=file_models.FilePublicResponse,
)
async def upload_one_file(
    storage_service: StorageServiceDep,
    file: UploadFile = File(...),
):
    """
    Upload a new file
    """
    # generate file path
    file_ext = file.filename.split(".")[-1] if file.filename else ""
    unique_filename = f"{uuid.uuid4()}.{file_ext}"

    try:
        path = await storage_service.upload_file(file=file, path=unique_filename)
    except FileExistsError:
        # TODO: regenerate filename
        logger.fatal("Filename not unique")
    except Exception:
        raise InternalServerError("Failed to upload file")

    return file_models.FilePublicResponse(
        message="File uploaded successfully", data=file_models.FilePublic(path=path)
    )


@router.delete("/{id}", response_model=Message)
async def delete_one_file(
    path: str,
    storage_service: StorageServiceDep,
):
    """
    Deleted saved file
    """
    try:
        is_deleted = await storage_service.delete_file(path=path)
        if not is_deleted:
            raise NotFoundError("File not found")
    except Exception:
        raise InternalServerError("Failed to delete file")

    return Message(message="Item deleted successfully")
