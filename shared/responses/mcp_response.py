"""MCP response models."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class MCPResponse(BaseModel):
    """MCP response model."""

    success: bool = True
    data: Optional[Any] = None
    error: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        """Pydantic config."""

        schema_extra = {
            "example": {
                "success": True,
                "data": {"result": 42},
                "error": None,
                "error_details": None,
                "timestamp": "2023-05-06T12:34:56.789012",
            }
        }

    @classmethod
    def success_response(cls, data: Any = None) -> Dict[str, Any]:
        """Create a success response."""
        response = cls(
            success=True,
            data=data,
            error=None,
            error_details=None,
        )
        # Convert to dict and remove None values
        response_dict = response.dict(exclude_none=True)
        # Convert datetime to ISO format string
        response_dict["timestamp"] = response_dict["timestamp"].isoformat()
        return response_dict

    @classmethod
    def error_response(
        cls, error: str, error_details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create an error response."""
        response = cls(
            success=False,
            data=None,
            error=error,
            error_details=error_details,
        )
        # Convert to dict and remove None values
        response_dict = response.dict(exclude_none=True)
        # Convert datetime to ISO format string
        response_dict["timestamp"] = response_dict["timestamp"].isoformat()
        return response_dict
