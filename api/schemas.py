"""
api/schemas.py
--------------
Pydantic request/response schemas for all API endpoints.
"""

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator
from typing import Optional, Literal


# ── Submit ────────────────────────────────────────────────────────

class RTISubmitRequest(BaseModel):
    name: Optional[str] = Field("Anonymous Citizen", min_length=2, max_length=100)
    email: Optional[EmailStr] = Field("citizen@rti-system.gov.in", description="Citizen email")
    address: str = Field(..., min_length=2, max_length=500, description="Applicant address")
    query_text: str = Field(..., min_length=10, max_length=2000)
    phone_number: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    pincode: Optional[str] = None
    language: Optional[Literal["en", "hi", "mr", "ta", "te", "bn", "gu", "kn", "ml", "pa"]] = "en"
    thread_id: Optional[str] = None  # Provide to continue existing conversation thread

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Akash Gaikwad",
                "email": "akash@example.com",
                "address": "Pune, Maharashtra",
                "query_text": "I want details about road construction budget in Pune for 2024-25",
                "language": "en",
            }
        }
    }


class RTISubmitResponse(BaseModel):
    request_id: str
    thread_id: str
    status: str
    message: str
    stream_url: str


# ── Approval ──────────────────────────────────────────────────────

class ApprovalRequest(BaseModel):
    decision: Literal["approved", "rejected"]
    approved_by: Optional[str] = "admin"
    edited_query: Optional[str] = None  # Human may edit the RTI draft


class ApprovalResponse(BaseModel):
    request_id: str
    tracking_id: str
    status: str
    message: str


# ── Status ────────────────────────────────────────────────────────

class RTIStatusResponse(BaseModel):
    tracking_id: str
    status: str
    department: str
    created_at: str
    updated_at: str
    approval_status: Optional[str] = None
    formal_query: Optional[str] = None
    workflow_path: Optional[list[str]] = None


# ── Thread ────────────────────────────────────────────────────────

class ThreadResponse(BaseModel):
    thread_id: str
    history: list[dict]
    active_request_id: Optional[str] = None
    created_at: str
    updated_at: str


# ── Feedback ──────────────────────────────────────────────────────

class FeedbackRequest(BaseModel):
    tracking_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=1000)
    comments: Optional[str] = Field(None, max_length=1000)
    was_helpful: Optional[bool] = True

    @model_validator(mode="before")
    @classmethod
    def populate_comments(cls, data):
        if isinstance(data, dict):
            if "comments" in data and "comment" not in data:
                data["comment"] = data["comments"]
            elif "comment" in data and "comments" not in data:
                data["comments"] = data["comment"]
        return data


class FeedbackResponse(BaseModel):
    status: str
    message: str


# ── Health ────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    services: dict[str, str]


# RAG Operations

class RAGIngestRequest(BaseModel):
    paths: Optional[list[str]] = None
    department: Optional[str] = None
    rebuild: bool = False
    document_name: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[dict] = None


class RAGScrapeRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    targets: Optional[list[str]] = None
    url: Optional[str] = None
    max_depth: Optional[int] = Field(None, ge=0, le=5)
    depth: Optional[int] = Field(None, ge=0, le=5)
    max_pages: Optional[int] = Field(None, ge=1)
    rebuild: bool = False

    @model_validator(mode="after")
    def normalize_legacy_fields(self) -> "RAGScrapeRequest":
        if self.max_depth is None and self.depth is not None:
            self.max_depth = self.depth
        return self


class RAGQueryRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    query: Optional[str] = Field(None, min_length=3, max_length=3000)
    query_text: Optional[str] = Field(None, min_length=3, max_length=3000)
    department: Optional[str] = None
    language: Optional[Literal["en", "hi", "mr"]] = None
    k: Optional[int] = Field(None, ge=1, le=20)
    top_k: Optional[int] = Field(None, ge=1, le=20)

    @model_validator(mode="after")
    def normalize_legacy_fields(self) -> "RAGQueryRequest":
        if self.query is None:
            self.query = self.query_text
        if self.k is None:
            self.k = self.top_k or 5
        if self.query is None:
            raise ValueError("query is required")
        return self


class RAGQueryResponse(BaseModel):
    query: str
    cache_hit: bool
    confidence: float
    results: list[dict]


# ── Respond ───────────────────────────────────────────────────────

class RespondRequest(BaseModel):
    response_text: str = Field(..., min_length=10, max_length=5000)


class RespondResponse(BaseModel):
    request_id: str
    tracking_id: str
    status: str
    message: str

