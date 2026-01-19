from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.orm import Session

from app.apis.v1.auth import manager
from app.core.db.database import async_get_db
from app.services.ingest_service import IngestService

router = APIRouter()


@router.post("/ingest")
async def ingest_file(
    file: UploadFile, db: Session = Depends(async_get_db), user=Depends(manager)
):
    service = IngestService(db)
    response = await service.ingest(file, user_id=user.uuid)
    return response
