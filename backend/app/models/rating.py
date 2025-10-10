from typing import Annotated
from uuid import UUID, uuid4
from datetime import datetime, timezone
from app.models.company import Company
from app.models.discard import Discard
from beanie import Document, Indexed, Link
from pydantic import Field


class Rating(Document):
    uuid: Annotated[UUID, Field(default_factory=uuid4), Indexed(unique=True)]
    score: Annotated[int, Field(ge=1, le=5)]  
    comment: str | None = None
    discard_uuid: Link[Discard]  
    company_uuid: Link[Company]  
    company_avaliadora_uuid: Link[Company]  
    created_at: datetime = Field(default_factory=datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=datetime.now(timezone.utc))