from typing import Annotated, Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone
from app.models.company import Company
from app.models.discard import Discard
from beanie import Document, Indexed, Link
from pydantic import Field


class Rating(Document):
    uuid: Annotated[UUID, Field(default_factory=uuid4), Indexed(unique=True)]
    score: Annotated[int, Field(ge=1, le=5)]  
    comment: Optional[str] = Field(None, max_length=500)
    
    
    discard_uuid: UUID  
    company_uuid: UUID 
    company_avaliadora_uuid: UUID  

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


    class Settings:
        name = "ratings"
        
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }