from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.orm import Session

from app.core.db.database import async_get_db
from app.services.ingest_service import IngestService

router = APIRouter()


@router.post("/ingest")
async def ingest_file(
    file: UploadFile,
    db: Session = Depends(async_get_db),
):
    service = IngestService(db)
    response = await service.ingest(file)
    return response
