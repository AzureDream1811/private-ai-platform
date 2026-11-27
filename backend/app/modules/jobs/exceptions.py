from backend.app.core.exceptions import ConflictError, NotFoundError


class JobNotFound(NotFoundError):
    code = "JOB_NOT_FOUND"


class JobResultNotFound(NotFoundError):
    code = "JOB_RESULT_NOT_FOUND"


class ResourcesAlreadyExistsError(ConflictError):
    code = "RESOURCES_ALREADY_EXISTS"
