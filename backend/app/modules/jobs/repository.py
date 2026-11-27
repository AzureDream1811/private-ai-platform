from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.database.models.enum import JobStatus
from backend.app.database.models.inference_job import InferenceJob
from backend.app.database.models.inference_result import InferenceResult


def create_job(
    db: Session,
    user_id: int,
    service_id: int,
    input_file: str,
    parameters: dict | None = None,
) -> InferenceJob:
    new_job = InferenceJob(
        user_id=user_id,
        service_id=service_id,
        input_file=input_file,
        parameters=parameters,
    )
    db.add(new_job)
    db.flush()
    return new_job


def get_job_by_id(db: Session, user_id: int, job_id: int) -> InferenceJob | None:
    stmt = select(InferenceJob).where(
        InferenceJob.id == job_id, InferenceJob.user_id == user_id
    )
    result = db.execute(stmt).scalar_one_or_none()
    return result


def get_user_jobs(
    db: Session, user_id: int, page: int, size: int, status: JobStatus | None = None
) -> tuple[list[InferenceJob], int]:
    stmt = select(InferenceJob).where(InferenceJob.user_id == user_id)
    count_stmt = select(func.count()).where(InferenceJob.user_id == user_id)

    if status is not None:
        stmt = stmt.where(InferenceJob.status == status)
        count_stmt = count_stmt.where(InferenceJob.status == status)

    total = db.scalar(count_stmt) or 0
    items = db.scalars(
        stmt.order_by(InferenceJob.created_at.desc(), InferenceJob.id.desc())
        .offset((page - 1) * size)
        .limit(size)
    ).all()
    return list(items), total


def get_job_result(db: Session, user_id: int, job_id: int) -> InferenceResult | None:
    stmt = (
        select(InferenceResult)
        .join(InferenceJob, InferenceResult.job_id == InferenceJob.id)
        .where(InferenceJob.id == job_id, InferenceJob.user_id == user_id)
    )
    result = db.execute(stmt).scalar_one_or_none()
    return result
