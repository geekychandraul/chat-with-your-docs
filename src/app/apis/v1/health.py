from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db.database import async_get_db
from app.core.health import check_database_health
from app.core.logging import get_logger
from app.schemas.health import HealthCheck

router = APIRouter(tags=["health"])

STATUS_HEALTHY = "healthy"
STATUS_UNHEALTHY = "unhealthy"

logger = get_logger(__name__)


@router.get("/health", response_model=HealthCheck)
async def health(db: Annotated[AsyncSession, Depends(async_get_db)]):
    database_status = await check_database_health(db=db)
    logger.info(f"Health check initiated. Database status: {database_status}")
    http_status, res_status = (
        (status.HTTP_200_OK, STATUS_HEALTHY)
        if database_status
        else (status.HTTP_503_SERVICE_UNAVAILABLE, STATUS_UNHEALTHY)
    )

    response = {
        "status": res_status,
        "environment": settings.ENVIRONMENT.value,
        "version": settings.APP_VERSION,
        "timestamp": datetime.now(UTC).isoformat(timespec="seconds"),
    }

    return JSONResponse(status_code=http_status, content=response)
