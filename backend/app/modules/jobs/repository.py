from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.database.models.ai_service import AIService


def get_active_service_by_key(db: Session, service_key: str):
    stmt = select(AIService).where(AIService.service_key == service_key, AIService.is_active == True)
    return db.scalar(stmt)

def create_Job(db: Session, job_data: dict):
    pass

def get_job_by_id(db: Session, job_id: int):
    pass

def get_jobs_by_user_id(db: Session, user_id: int):
    pass

def create_inference_result(db: Session, inference_data: dict):
    pass