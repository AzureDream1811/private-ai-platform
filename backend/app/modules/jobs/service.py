from sqlalchemy.orm import Session

from backend.app.database.models.enum import JobStatus
from backend.app.database.models.inference_job import InferenceJob
from backend.app.modules.ai_service.exceptions import ServiceNotFoundError
from backend.app.modules.jobs.exceptions import (
    InvalidInputFileError,
    JobNotFound,
    JobResultNotFound,
    JobStatusUpdateError,
)
from backend.app.modules.jobs.repository import (
    create_job,
    get_all_jobs,
    get_job_by_id,
    get_job_result,
    get_user_jobs,
    is_service_exists_and_active,
)
from backend.app.modules.jobs.schemas import (
    JobResponse,
    Page,
    ResultResponse,
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
) -> JobResponse:

    if is_service_exists_and_active(db, service_id) is False:
        raise ServiceNotFoundError("Service not found or inactive.")

    input_file = input_file.strip()
    if not input_file:
        raise InvalidInputFileError("Input file cannot be empty.")

    created_job = create_job(db, user_id, service_id, input_file, parameters)
    _commit_and_refresh(db, created_job)
    return JobResponse.model_validate(created_job)


def get_job_by_id_service(db: Session, user_id: int, job_id: int) -> JobResponse:
    job = _get_job(db, user_id, job_id)
    return JobResponse.model_validate(job)


def get_job_result_service(db: Session, user_id: int, job_id: int) -> ResultResponse:
    job_result = get_job_result(db, user_id, job_id)
    if job_result is None:
        raise JobResultNotFound("Job result not found.")
    return ResultResponse.model_validate(job_result)


def get_user_jobs_service(
    db: Session, user_id: int, page: int, size: int, status: JobStatus | None = None
) -> Page[JobResponse]:
    jobs, total = get_user_jobs(db, user_id, page, size, status)
    job_responses = [JobResponse.model_validate(job) for job in jobs]
    return Page[JobResponse](
        items=job_responses, total=total, page=page, size=size, pages=-(-total // size)
    )


def get_all_jobs_service(
    db: Session, page: int, size: int, status: JobStatus | None = None
) -> Page[JobResponse]:
    jobs, total = get_all_jobs(db, page, size, status)
    job_responses = [JobResponse.model_validate(job) for job in jobs]
    return Page[JobResponse](
        items=job_responses, total=total, page=page, size=size, pages=-(-total // size)
    )


def update_job_status_service(
    db: Session, user_id: int, job_id: int, new_status: JobStatus
) -> JobResponse:
    job = _get_job(db, user_id, job_id)

    if job.status == new_status:
        raise JobStatusUpdateError(f"Job is already in status {new_status}.")

    job.status = new_status
    _commit_and_refresh(db, job)
    return JobResponse.model_validate(job)


def _get_job(db, user_id, job_id):
    job = get_job_by_id(db, user_id=user_id, job_id=job_id)
    if job is None:
        raise JobNotFound("Job not found.")
    return job
