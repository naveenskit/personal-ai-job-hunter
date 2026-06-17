from http import HTTPStatus
from typing import Any


class JobHunterError(Exception):
    code = "JOB_HUNTER_ERROR"
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR

    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }


class ConfigError(JobHunterError):
    code = "CONFIG_ERROR"
    status_code = HTTPStatus.INTERNAL_SERVER_ERROR


class AuthenticationError(JobHunterError):
    code = "AUTHENTICATION_ERROR"
    status_code = HTTPStatus.UNAUTHORIZED


class NotFoundError(JobHunterError):
    code = "NOT_FOUND"
    status_code = HTTPStatus.NOT_FOUND


class ValidationError(JobHunterError):
    code = "VALIDATION_ERROR"
    status_code = HTTPStatus.BAD_REQUEST


class ExternalServiceError(JobHunterError):
    code = "EXTERNAL_SERVICE_ERROR"
    status_code = HTTPStatus.BAD_GATEWAY


class RateLimitError(JobHunterError):
    code = "RATE_LIMITED"
    status_code = HTTPStatus.TOO_MANY_REQUESTS
