from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.core.dependencies import get_current_admin_user, get_current_user
from backend.app.database.session import get_db
from backend.app.modules.aiservices.schemas import (
    CreateServiceRequest,
    PagedServices,
    ServiceResponse,
    UpdateServiceRequest,
)
from backend.app.modules.aiservices.service import (
    create_ai_service,
    delete_ai_service,
    get_services,
    set_ai_service_active,
    update_ai_service,
)

router = APIRouter()
DBSession = Annotated[Session, Depends(get_db)]


@router.get("/", dependencies=[Depends(get_current_user)])
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


@router.get(
    "/{service_key}",
    dependencies=[Depends(get_current_user)],
)
def get_service(db: DBSession, service_key: str) -> ServiceResponse:
    try:
        return get_service(db, service_key)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/", dependencies=[Depends(get_current_admin_user)], status_code=201)
def create_service(db: DBSession, request: CreateServiceRequest) -> ServiceResponse:
    try:
        return create_ai_service(
            db, request.name, request.service_key, request.description
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch(
    "/{service_key}",
    dependencies=[Depends(get_current_admin_user)],
)
def update_service(
    db: DBSession, service_key: str, request: UpdateServiceRequest
) -> ServiceResponse:
    try:
        return update_ai_service(db, service_key, request.name, request.description)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/{service_key}", dependencies=[Depends(get_current_admin_user)], status_code=204
)
def delete_service(db: DBSession, service_key: str) -> ServiceResponse:
    try:
        return delete_ai_service(db, service_key)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch(
    "/{service_key}/activate",
    dependencies=[Depends(get_current_admin_user)],
)
def activate_service(db: DBSession, service_key: str) -> ServiceResponse:
    try:
        return set_ai_service_active(db, service_key, True)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch(
    "/{service_key}/deactivate",
    dependencies=[Depends(get_current_admin_user)],
)
def deactivate_service(db: DBSession, service_key: str) -> ServiceResponse:
    try:
        return set_ai_service_active(db, service_key, False)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
