from pydantic import BaseModel
from typing import Optional


class ErrorResponse(BaseModel):
    """
    Schema for error responses.
    """
    detail: str
    error_code: Optional[str] = None
    timestamp: Optional[str] = None


class ValidationErrorResponse(BaseModel):
    """
    Schema for validation error responses.
    """
    detail: list
    error_code: str = "VALIDATION_ERROR"