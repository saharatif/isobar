"""v0.1 upload endpoint — direct multipart upload to local disk.

Replaces the presigned-S3 flow until object storage lands (v0.5). File keys
are server-generated UUIDs, so client input never influences the stored path.
"""
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from app.config import ALLOWED_MIME_TYPES, Settings
from app.deps import get_settings
from app.schemas.candidate import UploadOut

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post("", response_model=UploadOut, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile, settings: Settings = Depends(get_settings)
) -> UploadOut:
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"unsupported content type: {file.content_type}",
        )

    content = await file.read()
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"file exceeds {settings.max_upload_bytes} bytes",
        )
    if not content:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="file is empty"
        )

    file_key = str(uuid.uuid4())
    settings.storage_dir.mkdir(parents=True, exist_ok=True)
    (settings.storage_dir / file_key).write_bytes(content)

    logger.info(
        "resume uploaded",
        extra={"ctx": {"file_key": file_key, "bytes": len(content)}},
    )
    return UploadOut(
        file_key=file_key,
        filename=file.filename or "resume",
        size_bytes=len(content),
        mime_type=file.content_type,
    )
