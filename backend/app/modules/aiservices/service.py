from sqlalchemy.orm import Session

from backend.app.database.models.ai_service import AIService
from backend.app.modules.aiservices.repository import (
    create_service,
    get_service_by_service_key,
    get_services_with_filters,
)
from backend.app.modules.aiservices.schemas import ServiceResponse


def get_services(
    db: Session,
    page: int,
    size: int,
    name: str | None = None,
    is_active: bool | None = None,
):
    return get_services_with_filters(db, page, size, name, is_active)


def create_ai_service(
    db: Session,
    name: str,
    service_key: str,
    description: str | None = None,
) -> ServiceResponse:

    existing = get_service_by_service_key(db, service_key)
    if existing:
        raise ValueError(f"Service with service_key '{service_key}' already exists.")

    try:
        new_service = AIService(
            name=name, service_key=service_key, description=description
        )

        create_service(db, new_service)

        db.commit()
        db.refresh(new_service)

        return ServiceResponse.model_validate(
            {
                "id": new_service.id,
                "name": new_service.name,
                "service_key": new_service.service_key,
                "description": new_service.description,
                "is_active": new_service.is_active,
            }
        )

    except Exception:
        db.rollback()
        raise

def update_ai_service(
    db: Session,
    service_key: str,
    description: str | None = None,
) -> ServiceResponse:

    existing = get_service_by_service_key(db, service_key)
    if not existing:
        raise ValueError(f"Service with service_key '{service_key}' does not exist.")

    try:
        if description is not None:
            existing.description = description

        db.commit()
        db.refresh(existing)

        return ServiceResponse.model_validate(
            {
                "id": existing.id,
                "name": existing.name,
                "service_key": existing.service_key,
                "description": existing.description,
                "is_active": existing.is_active,
            }
        )

    except Exception:
        db.rollback()
        raise

def disable_ai_service(
    db: Session,
    service_key: str,
) -> ServiceResponse:

    existing = get_service_by_service_key(db, service_key)
    if not existing:
        raise ValueError(f"Service with service_key '{service_key}' does not exist.")

    try:
        existing.is_active = False

        db.commit()
        db.refresh(existing)

        return ServiceResponse.model_validate(
            {
                "id": existing.id,
                "name": existing.name,
                "service_key": existing.service_key,
                "description": existing.description,
                "is_active": existing.is_active,
            }
        )

    except Exception:
        db.rollback()
        raise
