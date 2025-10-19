# schema.py 
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, Literal
import uuid


class RTIRequest(BaseModel):
    # Personal Details
    name: str
    gender: Literal["male", "female", "other"]
    address: str
    pincode: str
    country: str
    state: str
    district: str
    tehsil: str
    village: str
    location_type: Literal["rural", "urban"]
    education_status: Literal["literate", "illiterate"]
    phone_number: str
    email: EmailStr

    # Query fields
    raw_query: str = Field(..., description="User’s original informal query")
    formatted_query: Optional[str] = Field(None, description="AI-processed formal query")

    # AI processing metadata
    department: Optional[str] = Field(None, description="Predicted department by AI")
    status: str = Field(default="pending", description="Current RTI request status")

    # Tracking and audit info
    tracking_id: str = Field(default_factory=lambda: f"RTI-{uuid.uuid4().hex[:8].upper()}")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        json_schema_extra = {
            "example": {
                "name": "Akash Gaikwad",
                "gender": "male",
                "address": "MG Road, Pune",
                "pincode": "411001",
                "country": "India",
                "state": "Maharashtra",
                "district": "Pune",
                "tehsil": "Haveli",
                "village": "Koregaon Park",
                "location_type": "urban",
                "education_status": "literate",
                "phone_number": "9876543210",
                "email": "akash@example.com",
                "raw_query": "मला माझ्या गावातील जलसंपदा प्रकल्पाविषयी माहिती हवी आहे",
            }
        }
