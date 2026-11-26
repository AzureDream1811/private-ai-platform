from pydantic import BaseModel, ConfigDict


class CreateServiceRequest(BaseModel):
    name: str
    service_key: str 
    description: str | None = None

class ServiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    description: str | None = None
    service_key: str
    is_active: bool

class UpdateServiceRequest(BaseModel):
    name: str | None = None
    description: str | None = None

class PagedServices(BaseModel):
    items: list[ServiceResponse]
    total: int
    page: int
    size: int