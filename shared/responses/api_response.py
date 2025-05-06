"""API response models."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Error detail model."""

    loc: Optional[List[str]] = None
    msg: str
    type: str


class ErrorResponse(BaseModel):
    """Error response model."""

    status: str = "error"
    code: int
    message: str
    details: Optional[List[ErrorDetail]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        """Pydantic config."""

        schema_extra = {
            "example": {
                "status": "error",
                "code": 400,
                "message": "Bad Request",
                "details": [
                    {
                        "loc": ["body", "name"],
                        "msg": "field required",
                        "type": "value_error.missing",
                    }
                ],
                "timestamp": "2023-05-06T12:34:56.789012",
            }
        }


class APIResponse(BaseModel):
    """API response model."""

    status: str = "success"
    code: int = 200
    message: str = "OK"
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        """Pydantic config."""

        schema_extra = {
            "example": {
                "status": "success",
                "code": 200,
                "message": "OK",
                "data": {"id": 1, "name": "Example"},
                "timestamp": "2023-05-06T12:34:56.789012",
            }
        }

    @classmethod
    def success(
        cls,
        data: Any = None,
        message: str = "OK",
        code: int = 200,
    ) -> "APIResponse":
        """Create a success response."""
        return cls(
            status="success",
            code=code,
            message=message,
            data=data,
        )

    @classmethod
    def error(
        cls,
        message: str,
        code: int = 400,
        details: Optional[List[ErrorDetail]] = None,
    ) -> ErrorResponse:
        """Create an error response."""
        return ErrorResponse(
            status="error",
            code=code,
            message=message,
            details=details,
        )
