from sqlite3 import IntegrityError

from sqlalchemy.orm import Session

from backend.app.database.models.ai_service import AIService
from backend.app.modules.ai_service.exceptions import (
    ServiceAlreadyExistsError,
    ServiceNotFoundError,
)
from backend.app.modules.ai_service.repository import (
    create_service,
    delete_service,
    get_service_by_service_key,
    get_services_with_filters,
)
from backend.app.modules.ai_service.schemas import ServiceResponse


def _get_existing_service(db: Session, service_key: str) -> AIService:
    existing = get_service_by_service_key(db, service_key)
    if not existing:
        raise ServiceNotFoundError(
            f"Service with service_key '{service_key}' does not exist."
        )

    return existing



def _commit_and_refresh(db: Session, obj: AIService) -> None:
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(obj)


def create_ai_service(
    db: Session,
    name: str,
    service_key: str,
    description: str | None = None,
) -> ServiceResponse:

    if get_service_by_service_key(db, service_key):
        raise ServiceAlreadyExistsError(
            f"Service with service_key '{service_key}' already exists."
        )

    service = AIService(name=name, service_key=service_key, description=description)
    create_service(db, service)

    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise ServiceAlreadyExistsError(service_key) from e

    db.refresh(service)
    return ServiceResponse.model_validate(service)


def update_ai_service(
    db: Session,
    service_key: str,
    name: str | None = None,
    description: str | None = None,
) -> ServiceResponse:

    existing = _get_existing_service(db, service_key)
    if name is not None:
        existing.name = name
    if description is not None:
        existing.description = description

    _commit_and_refresh(db, existing)
    return ServiceResponse.model_validate(existing)


def set_ai_service_active(
    db: Session,
    service_key: str,
    active: bool,
) -> ServiceResponse:

    service = _get_existing_service(db, service_key)
    service.is_active = active
    _commit_and_refresh(db, service)

    return ServiceResponse.model_validate(service)


def delete_ai_service(db: Session, service_key: str) -> ServiceResponse:
    service = _get_existing_service(db, service_key)

    try:
        delete_service(db, service)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return ServiceResponse.model_validate(service)


def get_services(
    db: Session,
    page: int,
    size: int,
    name: str | None = None,
    is_active: bool | None = None,
):

    return get_services_with_filters(db, page, size, name, is_active)


def get_service(db: Session, service_key: str) -> ServiceResponse:
    existing = _get_existing_service(db, service_key)

    return ServiceResponse.model_validate(existing)
