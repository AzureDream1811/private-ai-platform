from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.database.models.ai_service import AIService


def get_service_by_service_key(db: Session, service_key: str):
    stmt = select(AIService).where(AIService.service_key == service_key)
    return db.scalars(stmt).first()


def get_services_with_filters(db: Session, page, size, name=None, is_active=None):
    stmt = select(AIService)

    if name:
        stmt = stmt.where(AIService.name.ilike(f"%{name}%"))

    if is_active is not None:
        stmt = stmt.where(AIService.is_active == is_active)

    stmt = stmt.offset((page - 1) * size).limit(size)

    return db.scalars(stmt).all()


def create_service(db: Session, service: AIService) -> None:
    db.add(service)
    db.flush()

def update_service(db: Session, service: AIService) -> None:
    db.add(service)
    db.flush()

def disable_service(db: Session, service: AIService) -> None:
    service.is_active = False
    db.add(service)
    db.flush()
