from backend.app.core.exceptions import ConflictError, NotFoundError


class ServiceNotFoundError(NotFoundError):
    code = "SERVICE_NOT_FOUND"

class ServiceAlreadyExistsError(ConflictError):
    code = "SERVICE_ALREADY_EXISTS"
