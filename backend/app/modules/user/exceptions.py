from backend.app.core.exceptions import BadRequestError, ConflictError, NotFoundError


class UserNotFound(NotFoundError):
    code = "USER_NOT_FOUND"

class ResourcesAlreadyExistsError(ConflictError):
    code = "RESOURCES_ALREADY_EXISTS"

class InvalidUserDataError(BadRequestError):
    code = "INVALID_USER_DATA"