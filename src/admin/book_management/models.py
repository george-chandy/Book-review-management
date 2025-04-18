from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql import func
from src.models import Base  # Assuming you have a database.py file with Base
from pydantic import BaseModel
from typing import List, Optional
from src.auth.models import Users

class Book(Base):
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author_id = Column(Integer, ForeignKey("authors.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    genre_id = Column(Integer, ForeignKey("genres.id"), nullable=False)
    language_id = Column(Integer, ForeignKey("languages.id"), nullable=False)
    coverimage_url = Column(String, nullable=True)
    page_count = Column(Integer, nullable=False)
    isbn = Column(String, nullable=False, unique=True, index=True)
    is_featured = Column(Boolean, default=False)
    is_published = Column(Boolean, default=False)
    average_rating = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    author = relationship("Author", back_populates="books")
    category = relationship("Category", back_populates="books")
    genre = relationship("Genre", back_populates="books")
    language = relationship("Language", back_populates="books")
    reviews = relationship("Review", back_populates="book", cascade="all, delete-orphan")

class Author(Base):
    __tablename__ = "authors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    books = relationship("Book", back_populates="author")

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    books = relationship("Book", back_populates="category")

class Genre(Base):
    __tablename__ = "genres"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    books = relationship("Book", back_populates="genre")

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    rating = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    book = relationship("Book", back_populates="reviews")
    user = relationship("User", back_populates="reviews")

class Language(Base):
    __tablename__ = "languages"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    books = relationship("Book", back_populates="language")


