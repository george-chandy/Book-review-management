from src.exceptions import BadRequest, NotFound
from src.admin.book_management.constants import Errorcode

class TitleRequiredException(BadRequest):
    DETAIL = Errorcode.TITLE_REQUIRED

class AuthorIdRequiredException(BadRequest):
    DETAIL = Errorcode.AUTHOR_ID_REQUIRED

class AuthorNotFoundException(NotFound):
    DETAIL = Errorcode.AUTHOR_NOT_FOUND

class ISBNRequiredException(BadRequest):
    DETAIL = Errorcode.ISBN_REQUIRED

class LanguageRequiredException(BadRequest):
    DETAIL = Errorcode.LANGUAGE_ID_REQUIRED

class DescriptionRequiredException(BadRequest):
    DETAIL = Errorcode.DESCRIPTION_REQUIRED