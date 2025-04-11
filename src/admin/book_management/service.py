from sqlalchemy.orm import Session
from sqlalchemy.sql import func, select
from src.admin.book_management.schemas import AuthorBase
from sqlalchemy.ext.asyncio import AsyncSession
from src.admin.book_management.models import *
from src.admin.book_management.schemas import BookResponse
from typing import List, Optional

# Function to Get Average Rating
def get_average_rating(db: Session, book_id: int):
    avg_rating = db.query(func.avg(Review.rating)).filter(Review.book_id == book_id).scalar()
    return round(avg_rating, 2) if avg_rating else 0  # Round to 2 decimal places

# async def create_book(book:Book, db: AsyncSession):
#     db.add(book)
#     await db.commit()
#     await db.refresh(book)
#     return book

# async def get_author_by_id(db: AsyncSession, author: str):
#     stmt = select(Author).where(Author.name == author)
#     result = await db.execute(stmt)
#     return result.scalars().first()

# # ✅ Create Author
# async def create_author(db: AsyncSession, author_name: str):
#     new_author = Author(name=author_name)
#     db.add(new_author)
#     await db.commit()
#     await db.refresh(new_author)  # ✅ Refresh to get the generated ID
#     return new_author
# # ✅ Get Language by ID
# async def get_language_by_id(db: AsyncSession, language: str):
#     stmt = select(Language).where(Language.name == language)
#     result = await db.execute(stmt)
#     return result.scalars().first()

# async def create_language(db: AsyncSession, language_name: str):
#     new_language = Language(name=language_name)
#     db.add(new_language)
#     await db.commit()
#     await db.refresh(new_language)
#     return new_language
# # ✅ Get Category by ID
# async def get_category_by_id(db: AsyncSession, category: str):
#     stmt = select(Category).where(Category.name == category)
#     result = await db.execute(stmt)
#     return result.scalars().first()
# # ✅ Create Category
# async def create_category(db: AsyncSession, category_name: str):
#     new_category = Category(name=category_name)
#     db.add(new_category)
#     await db.commit()
#     await db.refresh(new_category)
#     return new_category
# # ✅ Get Genre by ID
# async def get_genre_by_id(db: AsyncSession, genre: str):
#     stmt = select(Genre).where(Genre.name == genre)
#     result = await db.execute(stmt)
#     return result.scalars().first()

# # ✅ Create Genre
# async def create_genre(db: AsyncSession, genre_name: str):
#     new_genre = Genre(name=genre_name)
#     db.add(new_genre)
#     await db.commit()
#     await db.refresh(new_genre)
#     return new_genre

# ✅ Get Author by Name
async def get_author_by_name(db: AsyncSession, author: str):
    stmt = select(Author).where(Author.name == author)
    result = await db.execute(stmt)
    return result.scalars().first()

# ✅ Create Author
async def create_author(db: AsyncSession, author_name: str):
    new_author = Author(name=author_name)
    db.add(new_author)
    await db.commit()
    await db.refresh(new_author)  # ✅ Refresh to get the generated ID
    return new_author

async def get_author_by_id(db: AsyncSession, id:int):
    stmt = select(Author).where(Author.id == id)
    result = await db.execute(stmt)
    return result.scalars().first()

# ✅ Get Language by Name
async def get_language_by_name(db: AsyncSession, language: str):
    stmt = select(Language).where(Language.name == language)
    result = await db.execute(stmt)
    return result.scalars().first()

async def create_language(db: AsyncSession, language_name: str):
    new_language = Language(name=language_name)
    db.add(new_language)
    await db.commit()
    await db.refresh(new_language)
    return new_language

async def get_language_by_id(db: AsyncSession, id:int):
    stmt = select(Language).where(Language.id == id)
    result = await db.execute(stmt)
    return result.scalars().first()


# ✅ Get Category by Name
async def get_category_by_name(db: AsyncSession, category: str):
    stmt = select(Category).where(Category.name == category)
    result = await db.execute(stmt)
    return result.scalars().first()

# ✅ Create Category
async def create_category(db: AsyncSession, category_name: str):
    new_category = Category(name=category_name)
    db.add(new_category)
    await db.commit()
    await db.refresh(new_category)
    return new_category

async def get_category_by_id(db: AsyncSession, id:int):
    stmt = select(Category).where(Category.id == id)
    result = await db.execute(stmt)
    return result.scalars().first()


# ✅ Get Genre by Name
async def get_genre_by_name(db: AsyncSession, genre: str):
    stmt = select(Genre).where(Genre.name == genre)
    result = await db.execute(stmt)
    return result.scalars().first()

# ✅ Create Genre
async def create_genre(db: AsyncSession, genre_name: str):
    new_genre = Genre(name=genre_name)
    db.add(new_genre)
    await db.commit()
    await db.refresh(new_genre)
    return new_genre

async def get_genre_by_id(db :AsyncSession, id :int):
    stmt = select(Genre).where(Genre.id == id)
    result = await db.execute(stmt)
    return result.scalars().first()

async def get_author_by_name(name: str, db: AsyncSession):
    stmt = select(Author).where(Author.name == name)
    result = await db.execute(stmt)
    return result.scalars().first()

async def get_all_books(db: AsyncSession) -> Optional[List[Book]]:
    statement = (
        select(
            Book.id,
            Book.title,
            # Author.id.label("author_id"),   # Include Author ID
            Author.name.label("author"),
            # Category.id.label("category_id"),  # Include Category ID
            Category.name.label("category"),
            # Genre.id.label("genre_id"),  # Include Genre ID
            Genre.name.label("genre"),
            # Language.id.label("language_id"),  # Include Language ID
            Language.name.label("language"),
            Book.cover_image_url,
            Book.page_count,
            Book.isbn,
            Book.is_featured,
            Book.is_published,
            Book.average_rating,
            Book.description,
            Book.created_at,
            Book.updated_at,
        )
        .join(Author, Book.author_id == Author.id)
        .join(Category, Book.category_id == Category.id)
        .join(Genre, Book.genre_id == Genre.id)
        .join(Language, Book.language_id == Language.id)
    )

    result = await db.execute(statement)
    books = result.fetchall()

    if not books:
        return None

    return [BookResponse.model_validate(dict(book._mapping)) for book in books] 

async def get_book_by_id(id: int, db: AsyncSession):
    stmt = select(Book).where(Book.id == id)
    result = await db.execute(stmt)
    book = result.scalars().first()
    return [BookResponse.model_validate(book)]