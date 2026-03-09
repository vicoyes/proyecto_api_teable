from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ApiMessage(BaseModel):
    message: str


class PaginationParams(BaseModel):
    skip: int = 0
    take: int = 50


class TeableRecord(BaseModel):
    id: str
    fields: dict[str, Any]
    createdTime: datetime | None = None

    model_config = ConfigDict(extra="allow")
