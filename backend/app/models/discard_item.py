from typing import Annotated
from uuid import UUID, uuid4
from beanie import Document, Indexed
from pydantic import Field


class DiscardItem(Document):
    uuid: Annotated[UUID, Field(default_factory=uuid4), Indexed(unique=True)]
    
    nome: str
    quantity: int = 1
    metrics_ids: list[UUID] = []

    class Settings:
        name = "discard_items" 

    
