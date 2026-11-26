class AppException(Exception):
    status_code: int = 500
    code: str = "INTERNAL_ERROR"

    def __init__(self, message: str | None = None):
        self.message = message or self.__class__.__name__
        super().__init__(self.message)


class BadRequestError(AppException):
    status_code = 400
    code = "BAD_REQUEST"


class UnauthorizedError(AppException):
    status_code = 401
    code = "UNAUTHORIZED"


class NotFoundError(AppException):
    status_code = 404
    code = "NOT_FOUND"


class ConflictError(AppException):
    status_code = 409
    code = "CONFLICT"


class ForbiddenError(AppException):
    status_code = 403
    code = "FORBIDDEN"
