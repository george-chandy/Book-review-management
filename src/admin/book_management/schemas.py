from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

# --- Author ---
class AuthorBase(BaseModel):
    name: str

class AuthorCreate(AuthorBase):
    pass

class AuthorResponse(AuthorBase):
    id: int
    class Config:
        from_attributes = True


# --- Category ---
class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    class Config:
        from_attributes = True


# --- Genre ---
class GenreBase(BaseModel):
    name: str

class GenreCreate(GenreBase):
    pass

class GenreResponse(GenreBase):
    id: int
    class Config:
        from_attributes = True


# --- Language ---
class LanguageBase(BaseModel):
    name: str

class LanguageCreate(LanguageBase):
    pass

class LanguageResponse(LanguageBase):
    id: int
    class Config:
        from_attributes = True


# --- Review ---
class ReviewBase(BaseModel):
    book_id: int
    user_id: int
    content: str
    rating: float

class ReviewCreate(ReviewBase):
    pass

class ReviewResponse(ReviewBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True


# --- Book ---
class BookBase(BaseModel):
    title: str
    author_id: int
    category_id: int
    genre_id: int
    language_id: int
    cover_image_url: Optional[str] = None
    page_count: int
    isbn: str
    is_featured: Optional[bool] = False
    is_published: Optional[bool] = False
    average_rating: Optional[float] = 0.0
    description: Optional[str] = None

class BookCreate(BookBase):
    pass

class BookResponse(BaseModel):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    author: str
    category: str
    genre: str
    language: str
    reviews: List[ReviewResponse] = []  # Include all reviews
    class Config:
        from_attributes = True