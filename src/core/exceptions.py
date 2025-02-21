class AppException(Exception):
    """Base exception handler for all application errors"""

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message
        super().__init__(message)


class BadActionError(AppException):
    """Raise exception for bad or invalid action"""

    def __init__(self, message: str = "Bad Request") -> None:
        super().__init__(message=message, status_code=400)


class AuthenticationError(AppException):
    """Raise exception for unauthorized action"""

    def __init__(self, message: str = "Authentication Error") -> None:
        super().__init__(message=message, status_code=403)


class PermissionDeniedError(AppException):
    """Raise exception for forbidden actions"""

    def __init__(self, message: str = "Permission Denied") -> None:
        super().__init__(message=message, status_code=403)


class NotFoundError(AppException):
    """Raise exception for not found actions"""

    def __init__(self, message: str = "Not Found") -> None:
        super().__init__(message=message, status_code=404)


class ConflictError(AppException):
    """Raise exception for conflict errors"""

    def __init__(self, message: str = "Conflict. Resource already exists") -> None:
        super().__init__(message=message, status_code=409)


class InternalServerError(AppException):
    """Raise exception for internal errors"""

    def __init__(self, message: str = "Something went wrong") -> None:
        super().__init__(message=message, status_code=500)
