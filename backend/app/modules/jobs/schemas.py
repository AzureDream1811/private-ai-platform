from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel

from backend.app.database.models.enum import JobStatus

T = TypeVar("T")


class InferenceJobCreateRequest(BaseModel):
    service_id: int
    input_file: str
    parameters: dict | None = None

class InferenceJobResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    service_id: int
    input_file: str
    parameters: dict | None
    status: JobStatus
    created_at: datetime


class InferenceResultResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    result: dict | None
    error_message: str | None
    created_at: datetime


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int
