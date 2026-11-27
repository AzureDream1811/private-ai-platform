from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.core.dependencies import get_current_admin_user, get_current_user
from backend.app.database.session import get_db
from backend.app.modules.ai_service.schemas import (
    CreateServiceRequest,
    PagedServices,
    ServiceResponse,
    UpdateServiceRequest,
)
from backend.app.modules.ai_service.service import (
    create_ai_service,
    delete_ai_service,
    get_service,
    get_services,
    set_ai_service_active,
    update_ai_service,
)

router = APIRouter()
DBSession = Annotated[Session, Depends(get_db)]
public_router = APIRouter(dependencies=[Depends(get_current_user)])
admin_router = APIRouter(dependencies=[Depends(get_current_admin_user)])


@public_router.get("/")
def list_services(
    db: DBSession,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    name: str | None = None,
    is_active: bool | None = None,
) -> PagedServices:
    services, total = get_services(db, page, size, name, is_active)
    return PagedServices(
        items=[ServiceResponse.model_validate(service) for service in services],
        total=total,
        page=page,
        size=size,
    )


@public_router.get("/{service_key}")
def get_service_detail(db: DBSession, service_key: str) -> ServiceResponse:
    return get_service(db, service_key)


@admin_router.post("/", status_code=201)
def create_service(db: DBSession, request: CreateServiceRequest) -> ServiceResponse:
    return create_ai_service(db, request.name, request.service_key, request.description)


@admin_router.patch("/{service_key}")
def update_service(
    db: DBSession, service_key: str, request: UpdateServiceRequest
) -> ServiceResponse:
    return update_ai_service(db, service_key, request.name, request.description)


@admin_router.delete("/{service_key}", status_code=204)
def delete_service(db: DBSession, service_key: str) -> None:
    delete_ai_service(db, service_key)


@admin_router.patch("/{service_key}/activate")
def activate_service(db: DBSession, service_key: str) -> ServiceResponse:
    return set_ai_service_active(db, service_key, True)


@admin_router.patch("/{service_key}/deactivate")
def deactivate_service(db: DBSession, service_key: str) -> ServiceResponse:
    return set_ai_service_active(db, service_key, False)


router.include_router(public_router)
router.include_router(admin_router)
