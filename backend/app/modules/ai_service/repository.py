from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.database.models.ai_service import AIService


def get_service(db: Session, id: int):
    stmt = select(AIService).where(AIService.id == id)
    return db.scalars(stmt).first()


def get_service_by_id(db: Session, id: int):
    stmt = select(AIService).where(AIService.id == id)
    return db.scalars(stmt).first()


def get_service_by_service_key(db: Session, service_key: str):
    stmt = select(AIService).where(AIService.service_key == service_key)
    return db.scalars(stmt).first()


def get_services_with_filters(db: Session, page, size, name=None, is_active=None) -> tuple[list[AIService], int]:
    stmt = select(AIService)

    if name:
        stmt = stmt.where(AIService.name.ilike(f"%{name}%"))
    if is_active is not None:
        stmt = stmt.where(AIService.is_active == is_active)

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    items = db.scalars(
        stmt.order_by(AIService.id).offset((page - 1) * size).limit(size)
    ).all()

    return list(items), total


def create_service(db: Session, service: AIService) -> None:
    db.add(service)
    db.flush()


def delete_service(db: Session, service: AIService) -> None:
    db.delete(service)
    db.flush()
