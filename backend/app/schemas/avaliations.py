from uuid import UUID
from pydantic import BaseModel, model_validator, Field
from typing import Optional, Union
from datetime import datetime
from app.models.company import CompanyType

class AvaliationCreate(BaseModel):
    company_uuid: UUID
    company_avaliadora_uuid: UUID
    discard_uuid: UUID
    comment: Optional[str] = None
    score: int = Field(ge=1, le=5)


class AvaliationUpdate(BaseModel):
    comment: Optional[str] = Field(default=None, min_length= 1, max_length=500, description= "comentario opcional (1-500 caracteres)")
    score: Optional[int] = Field(default=None, ge=1, le=5)


    @model_validator(mode="after")
    def validate_at_least_one_field(cls, model):
        """Ensure at least one field is provided for update"""
        if model.comment is None and model.score is None:
            raise ValueError("At least one field (comment or score) must be provided for update")
        return model

class AvaliationOut(BaseModel):
    uuid: UUID
    score: int
    comment: Optional[str] = None
    discard_uuid: UUID
    company_uuid: UUID
    company_avaliadora_uuid: UUID
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="after")
    def validate_rating(cls, model):
        if not (1 <= model.score <= 5):
            raise ValueError("Score must be between 1 and 5")
        return model

    
class CompanyAvaliationsSummary(BaseModel):
    company_uuid: UUID
    company_name: str
    company_type: CompanyType
    average_rating: Union[float, None]
    total_ratings: int
    rating_distribution: dict[int, int]  # {1: 5, 2: 3, 3: 10, 4: 7, 5: 12}

    @model_validator(mode="after")
    def validate_average_rating(cls, model):
        if model.average_rating is not None and not (1 <= model.average_rating <= 5):
            raise ValueError("Average rating must be between 1 and 5")
        return model