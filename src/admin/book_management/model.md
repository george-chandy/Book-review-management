# from sqlalchemy import (
#     Column, Integer, String, ForeignKey, Boolean, DateTime, Text, DECIMAL)
# from sqlalchemy.orm import relationship
# from sqlalchemy.sql import func
# from src.models import Base
# from src.auth.models import Users

# class Book(Base):
#     __tablename__ = "books"
    
#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String, nullable=False)
#     author_id = Column(Integer, ForeignKey("authors.id", ondelete="CASCADE"), nullable=False)
#     category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
#     genre_id = Column(Integer, ForeignKey("genres.id", ondelete="CASCADE"), nullable=False)
#     language_id = Column(Integer, ForeignKey("languages.id", ondelete="CASCADE"), nullable=False)
#     coverimage_url = Column(String, nullable=True)
#     page_count = Column(Integer, nullable=False)
#     isbn = Column(String, nullable=False, unique=True, index=True)
#     is_featured = Column(Boolean, default=False)
#     is_published = Column(Boolean, default=False)
#     average_rating = Column(DECIMAL(2, 1), default=0.0)  # ✅ Use DECIMAL for consistent rounding
#     created_at = Column(DateTime(timezone=True), server_default=func.now())  # ✅ DB-level timestamp
#     description = Column(Text, nullable=True)

#     # Relationships
#     author = relationship("Author", back_populates="books")
#     category = relationship("Category", back_populates="books")
#     genre = relationship("Genre", back_populates="books")
#     language = relationship("Language", back_populates="books")
#     reviews = relationship("Review", back_populates="book", cascade="all, delete-orphan")

# class Author(Base):
#     __tablename__ = "authors"
    
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, nullable=False)
#     books = relationship("Book", back_populates="author", cascade="all, delete-orphan")

# class Category(Base):
#     __tablename__ = "categories"
    
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, nullable=False, unique=True)
#     books = relationship("Book", back_populates="category", cascade="all, delete-orphan")

# class Genre(Base):
#     __tablename__ = "genres"
    
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, nullable=False, unique=True)
#     books = relationship("Book", back_populates="genre", cascade="all, delete-orphan")

# class Review(Base):
#     __tablename__ = "reviews"
    
#     id = Column(Integer, primary_key=True, index=True)
#     book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
#     user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
#     content = Column(Text, nullable=False)
#     rating = Column(DECIMAL(2, 1), nullable=False)  # ✅ Use DECIMAL for consistent rounding
#     created_at = Column(DateTime(timezone=True), server_default=func.now())

#     # Relationships
#     book = relationship("Book", back_populates="reviews")
#     user = relationship("Users", back_populates="reviews")  # ✅ Fixed User relationship

# class Language(Base):
#     __tablename__ = "languages"
    
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, nullable=False, unique=True)
#     books = relationship("Book", back_populates="language", cascade="all, delete-orphan")

from sqlalchemy import (
    Column, Integer, String, ForeignKey, Boolean, DateTime, Text, Float
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.models import Base

class Book(Base):
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author_id = Column(Integer, ForeignKey("authors.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    genre_id = Column(Integer, ForeignKey("genres.id", ondelete="CASCADE"), nullable=False)
    language_id = Column(Integer, ForeignKey("languages.id", ondelete="CASCADE"), nullable=False)
    coverimage_url = Column(String, nullable=True)
    page_count = Column(Integer, nullable=False)
    isbn = Column(String, nullable=False, unique=True, index=True)
    is_featured = Column(Boolean, default=False)
    is_published = Column(Boolean, default=False)
    average_rating = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    description = Column(Text, nullable=True)

    # Relationships
    author = relationship("Author", back_populates="books")
    category = relationship("Category", back_populates="books")
    genre = relationship("Genre", back_populates="books")
    language = relationship("Language", back_populates="books")
    reviews = relationship("Review", back_populates="book", cascade="all, delete-orphan")


class Author(Base):
    __tablename__ = "authors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    
    books = relationship("Book", back_populates="author", cascade="all, delete-orphan")


class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    
    books = relationship("Book", back_populates="category", cascade="all, delete-orphan")


class Genre(Base):
    __tablename__ = "genres"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    
    books = relationship("Book", back_populates="genre", cascade="all, delete-orphan")


class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)  # ✅ Reference to users table
    content = Column(Text, nullable=False)
    rating = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # ✅ Use a string reference for Users to avoid circular import
    book = relationship("Book", back_populates="reviews")
    user = relationship("Users", back_populates="reviews")


class Language(Base):
    __tablename__ = "languages"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    
    books = relationship("Book", back_populates="language", cascade="all, delete-orphan")