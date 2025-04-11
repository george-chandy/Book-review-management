from typing import List
from fastapi import APIRouter, FastAPI, Depends
from fastapi.responses import JSONResponse
from src.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

from src.admin.book_management.schemas import(
     AuthorBase,
     AuthorCreate,
     BookCreate, 
     BookBase,
     BookResponse,
     GenreCreate,
     LanguageCreate)
from src.admin.book_management import models

from src.admin.book_management.exceptions import( 
    AuthorIdRequiredException,
    AuthorNotFoundException,
    DescriptionRequiredException,
    ISBNRequiredException,
    TitleRequiredException,)

from src.admin.book_management.service import(
    
    get_all_books,
    get_author_by_id,
    create_author,
    get_author_by_name,
    get_book_by_id,
    get_language_by_id,
    create_language,
    get_category_by_id,
    create_category,
    get_genre_by_id,
    create_genre,
    )

router = APIRouter(prefix="/book", tags=["Book"], default_response_class=JSONResponse)

@router.post("/books")
async def add_book(book: BookCreate, db: AsyncSession = Depends(get_db)) -> BookBase:
    if not book.title:
        raise TitleRequiredException()
    if not book.isbn:
        raise ISBNRequiredException()
    if not book.description:
        raise DescriptionRequiredException()
    
    # ✅ Fetch or Create Author
    author = await get_author_by_id(db, book.author_id)
    if not author:
        author = await create_author(db, book.author_id)

    # ✅ Fetch or Create Language
    book_language = await get_language_by_id(db, book.language_id)
    if not book_language:
        book_language = await create_language(db, book.language_id)

    # ✅ Fetch or Create Category
    book_category = await get_category_by_id(db, book.category_id)
    if not book_category:
        book_category = await create_category(db, book.category_id)

    # ✅ Fetch or Create Genre
    book_genre = await get_genre_by_id(db, book.genre_id)
    if not book_genre:
        book_genre = await create_genre(db, book.genre_id)

    # ✅ Create new Book instance
    book_model = models.Book(
        title=book.title,
        isbn=book.isbn,
        average_rating=book.average_rating,
        description=book.description,
        author_id=author.id,
        category_id=book_category.id,
        genre_id=book_genre.id,
        language_id=book_language.id,
        cover_image_url=book.cover_image_url,
        page_count=book.page_count,
        is_featured=False,
        is_published=False
    )

    # ✅ Save Book to DB
    db.add(book_model)
    await db.commit()
    await db.refresh(book_model)  # Refresh to get the generated ID

    return book

@router.get("/books")
async def fetch_books(db: AsyncSession = Depends(get_db)) -> List[BookResponse]:
    books = await get_all_books(db)
    return books

@router.get("/book/{id}", response_model=BookResponse)
async def fetch_book_by_id(id : int, db : AsyncSession = Depends(get_db)):
    book = await get_book_by_id(id, db)
    return book

@router.post("/author")
async def add_author(author:AuthorCreate, db :AsyncSession = Depends(get_db)):
    author = await create_author(db, author.name)
    return author

@router.get("/author/", response_model=AuthorBase)
async def fetch_author_by_name(name:str, db: AsyncSession = Depends(get_db)):
    author = await get_author_by_name(name, db)
    return author

@router.post("/language")
async def add_language(language: LanguageCreate, db: AsyncSession = Depends(get_db)):
    language = await create_language(db, language.name)
    return language

@router.post("/genre")
async def add_genre(genre:GenreCreate, db :AsyncSession = Depends(get_db)):
    genre = await create_genre(db, genre.name)
    return genre

