# schemas/agent_response_schema.py

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class AgentResponse(BaseModel):
    """
    Standard response format returned by all agents in the RTI Agent system.
    """

    agent_name: str = Field(..., description="Name of the agent producing this response.")
    success: bool = Field(..., description="Indicates if the agent successfully completed its task.")
    message: Optional[str] = Field(None, description="Human-readable message describing the outcome.")
    data: Optional[Dict[str, Any]] = Field(None, description="Structured data output from the agent.")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the response was created.")
    error: Optional[str] = Field(None, description="Error message, if any, encountered during processing.")

    class Config:
        schema_extra = {
            "example": {
                "agent_name": "classifier_agent",
                "success": True,
                "message": "Department classified successfully.",
                "data": {"department": "Ministry of Rural Development"},
                "timestamp": "2025-10-21T12:00:00Z",
            }
        }
