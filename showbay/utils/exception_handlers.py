from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from showbay.utils.exceptions import ExternalAPIException
import logging

# Set up logging
logger = logging.getLogger(__name__)


async def external_api_exception_handler(request: Request, exc: ExternalAPIException):
    """
    Handle ExternalAPIException.
    
    Args:
        request: The incoming request
        exc: The ExternalAPIException that was raised
        
    Returns:
        JSONResponse with error details
    """
    logger.error(f"External API error: {exc.message} (Status: {exc.status_code})")
    
    return JSONResponse(
        status_code=exc.status_code or status.HTTP_502_BAD_GATEWAY,
        content={
            "detail": exc.message,
            "error_code": "EXTERNAL_API_ERROR",
            "timestamp": request.scope.get("start_time") if hasattr(request.scope, "start_time") else None
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle RequestValidationError from Pydantic.
    
    Args:
        request: The incoming request
        exc: The RequestValidationError that was raised
        
    Returns:
        JSONResponse with validation error details
    """
    logger.warning(f"Validation error: {exc}")
    
    errors = []
    for error in exc.errors():
        errors.append({
            "loc": error["loc"],
            "msg": error["msg"],
            "type": error["type"],
            "input": error.get("input", "N/A")
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": errors,
            "error_code": "VALIDATION_ERROR"
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle general exceptions.
    
    Args:
        request: The incoming request
        exc: The exception that was raised
        
    Returns:
        JSONResponse with error details
    """
    logger.error(f"General error: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal server error occurred",
            "error_code": "INTERNAL_ERROR"
        }
    )