from fastapi import Request
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from app.core.logging import get_logger

logger = get_logger(__name__)


def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle HTTPException and return a JSON response.

    Args:
        request (Request): The incoming HTTP request.
        exc (HTTPException): The exception to handle.

    Returns:
        JSONResponse: A JSON response with the error details and trace ID.
    """
    # trace_id = set_span_error(exc)
    logger.error(
        f"HTTPException: status_code: {exc.status_code}, request: {request.url}, detail: {exc.detail}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": f"{exc.detail}, Please raise a support ticket."},
    )
