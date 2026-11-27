from sqlalchemy.orm import Session

from backend.app.database.models.enum import JobStatus
from backend.app.database.models.inference_job import InferenceJob
from backend.app.modules.jobs.repository import (
    create_job,
    get_job_by_id,
    get_job_result,
    get_user_jobs,
)
from backend.app.modules.jobs.schemas import (
    InferenceJobResponse,
    InferenceResultResponse,
)


def _commit_and_refresh(db: Session, obj: InferenceJob) -> None:
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(obj)


def create_job_service(
    db: Session,
    user_id: int,
    service_id: int,
    input_file: str,
    parameters: dict | None = None,
) -> InferenceJobResponse:
    created_job = create_job(db, user_id, service_id, input_file, parameters)
    _commit_and_refresh(db, created_job)
    return InferenceJobResponse.model_validate(created_job)


def get_job_by_id_service(
    db: Session, user_id: int, job_id: int
) -> InferenceJobResponse | None:
    job = get_job_by_id(db, user_id, job_id)
    if job is None:
        return None
    return InferenceJobResponse.model_validate(job)


def get_job_result_service(
    db: Session, user_id: int, job_id: int
) -> InferenceResultResponse | None:
    job_result = get_job_result(db, user_id, job_id)
    if job_result is None:
        return None
    return InferenceResultResponse.model_validate(job_result)


def get_user_jobs_service(
    db: Session, user_id: int, page: int, size: int, status: JobStatus | None = None
) -> tuple[list[InferenceJobResponse], int]:
    jobs, total = get_user_jobs(db, user_id, page, size, status)
    job_responses = [InferenceJobResponse.model_validate(job) for job in jobs]
    return job_responses, total
