from typing import Any
from fastapi import HTTPException, status

class BookreviewException(HTTPException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    DETAIL = "Internal Server Error"
    
    def __init__(self, **kwargs: dict[str, Any]) -> None:
        super().__init__(status_code=self.STATUS_CODE, detail=self.DETAIL, **kwargs)

class BadRequest(BookreviewException):
    status_code = status.HTTP_400_BAD_REQUEST
    DETAIL = "Bad Request"

class Conflict(BookreviewException):
    status_code = status.HTTP_409_CONFLICT
    DETAIL = "Conflict"

class Unauthorized(BookreviewException):
    status_code = status.HTTP_401_UNAUTHORIZED
    DETAIL = "Unauthorized"

class NotFound(BookreviewException):
    status_code = status.HTTP_404_NOT_FOUND
    DETAIL = "Not Found"
    