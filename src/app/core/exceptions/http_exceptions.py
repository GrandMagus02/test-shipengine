# ruff: noqa
from fastcrud.exceptions.http_exceptions import (
    CustomException,
    BadRequestException,
    NotFoundException,
    ForbiddenException,
    UnauthorizedException,
    UnprocessableEntityException,
    DuplicateValueException,
    RateLimitException,
)


class ServiceUnavailableException(CustomException):
    def __init__(self, detail: str = "Service unavailable") -> None:
        super().__init__(status_code=503, detail=detail)
