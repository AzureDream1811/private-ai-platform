from datetime import datetime

from pydantic import BaseModel

from backend.app.database.models.enum import JobStatus


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

