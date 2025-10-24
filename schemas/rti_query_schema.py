from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal
from datetime import datetime


class RTIRequestSchema(BaseModel):
    """
    Schema representing an incoming RTI query from a user.
    Ensures all required fields are properly validated.
    """

    user_id: Optional[str] = Field(None, description="Unique ID of the user submitting the RTI query.")
    name: str = Field(..., description="Full name of the citizen.")
    gender: Optional[str] = Field(None, description="Gender of the citizen.")
    address: str = Field(..., description="Full postal address.")
    pincode: Optional[str] = Field(None, description="Postal code of the location.")
    country: Optional[str] = Field("India", description="Country of residence.")
    state: Optional[str] = Field(None, description="State of residence.")
    district: Optional[str] = Field(None, description="District of residence.")
    tehsil: Optional[str] = Field(None, description="Tehsil or sub-district.")
    village: Optional[str] = Field(None, description="Village name (if applicable).")
    location_type: Optional[Literal["urban", "rural"]] = Field(None, description="Type of location.")
    education_status: Optional[Literal["literate", "illiterate"]] = Field(None, description="Education status.")
    phone_number: Optional[str] = Field(None, description="Contact phone number.")
    email: EmailStr = Field(..., description="Valid email address of the citizen.")
    query_text: str = Field(..., description="The main RTI query text provided by the citizen.")
    language: Literal["en", "hi", "mr", "ta", "te", "bn", "gu", "kn", "ml", "pa"] = Field(
        "en", description="Language code of the query (default is English)."
    )
    submission_time: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of query submission.")
    category: Optional[str] = Field(None, description="Predicted or user-defined category of the query.")
    department: Optional[str] = Field(None, description="Department predicted by the classifier agent.")
    formatted_query: Optional[str] = Field(None, description="LLM formatted RTI query for submission.")
    status: Literal["pending", "classified", "submitted", "in_progress", "resolved", "rejected"] = Field(
        "pending", description="Current processing status of the RTI query."
    )

    class Config:
        schema_extra = {
            "example": {
                "name": "Akash Gaikwad",
                "gender": "male",
                "address": "Pune, Maharashtra",
                "pincode": "411001",
                "country": "India",
                "state": "Maharashtra",
                "district": "Pune",
                "tehsil": "Haveli",
                "location_type": "urban",
                "education_status": "literate",
                "phone_number": "9876543210",
                "email": "akash@example.com",
                "query_text": "I want details about local agriculture schemes",
                "language": "en"
            }
        }
