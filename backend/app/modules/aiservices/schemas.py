from pydantic import BaseModel


class CreateServiceRequest(BaseModel):
    name: str
    service_key: str 
    description: str | None = None

class ServiceResponse(BaseModel):
    id: int
    name: str
    service_key: str 
    description: str | None = None
    is_active: bool

class UpdateServiceRequest(BaseModel):
    description: str | None = None