from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.core.dependencies import get_current_admin_user, get_current_user
from backend.app.database.models.enum import JobStatus
from backend.app.database.models.user import User
from backend.app.database.session import get_db
from backend.app.modules.jobs.schemas import (
    InferenceJobCreateRequest,
    InferenceJobResponse,
    InferenceResultResponse,
    Page,
)
from backend.app.modules.jobs.service import (
    create_job_service,
    get_all_jobs_service,
    get_job_by_id_service,
    get_job_result_service,
    get_user_jobs_service,
)

router = APIRouter()
DBSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentAdminUser = Annotated[User, Depends(get_current_admin_user)]


@router.post("/")
def create_job(
    db: DBSession,
    current_user: CurrentUser,
    request: InferenceJobCreateRequest,
) -> InferenceJobResponse:

    return create_job_service(
        db, current_user.id, 
        request.service_id, 
        request.input_file, 
        request.parameters
    )


@router.get("/")
def get_user_jobs(
    db: DBSession,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    status: Annotated[JobStatus | None, Query()] = None,
) -> Page[InferenceJobResponse]:

    return get_user_jobs_service(db, current_user.id, page, size, status)


@router.get("/{job_id}")
def get_job_by_id(
    db: DBSession,
    current_user: CurrentUser,
    job_id: int,
) -> InferenceJobResponse | None:

    return get_job_by_id_service(db, current_user.id, job_id)


@router.get("/{job_id}/result")
def get_job_result(
    db: DBSession,
    current_user: CurrentUser,
    job_id: int,
) -> InferenceResultResponse | None:

    return get_job_result_service(db, current_user.id, job_id)


@router.get("/all", dependencies=[Depends(get_current_admin_user)])
def admin_get_all_jobs(
    db: DBSession,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    status: Annotated[JobStatus | None, Query()] = None,
) -> Page[InferenceJobResponse]:

    return get_all_jobs_service(db, page, size, status)
