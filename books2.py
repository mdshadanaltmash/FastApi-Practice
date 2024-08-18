import datetime

from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from starlette import status

app = FastAPI()


class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int
    published_date: int

    def __init__(self, id, title, author, description, rating, published_date):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date


class BookRequest(BaseModel):
    id: Optional[int] = Field(default=None, title='id is not needed!')
    title: str = Field(min_length=3)
    author: str = Field(min_length=3)
    description: str = Field(min_length=3)
    rating: int = Field(gt=0, lt=6)
    published_date: int = Field(ge=1000, le=int(datetime.date.today().year))

    class Config:
        json_schema_extra = {
            'example': {
                'title': 'A new book',
                'author': 'Shadan',
                'description': 'A book description',
                'rating': 5,
                'published_date': 2000
            }
        }


BOOKS = [
    Book(1, 'Computer Science Pro', 'Shadan', 'A very nice book!', 5, 2016),
    Book(2, 'Be Fast with FastAPI', 'Shadan', 'A great book!', 5, 2018),
    Book(3, 'Master Endpoints', 'Shadan', 'An awesome book!', 5, 2010),
    Book(4, 'HP1', 'Author 1', 'Book Description', 2, 1997),
    Book(5, 'HP2', 'Author 2', 'Book Description', 3, 1800),
    Book(6, 'HP3', 'Author 3', 'Book Description', 1, 1857)
]


@app.get("/books", status_code=status.HTTP_200_OK)
async def read_all_books():
    return BOOKS


@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def read_book(book_id: int = Path(gt=0)):
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail='Item not found!')


@app.get("/books/", status_code=status.HTTP_200_OK)
async def read_book_by_rating(rating: int = Query(gt=0, lt=6)):
    books_to_return = []
    for book in BOOKS:
        if book.rating == rating:
            books_to_return.append(book)
    return books_to_return


@app.get("/books/publish/", status_code=status.HTTP_200_OK)
async def read_book_by_publish_date(published_date: int = Query(ge=1000, le=int(datetime.date.today().year))):
    books_to_return = []
    for book in BOOKS:
        if book.published_date == published_date:
            books_to_return.append(book)
    return books_to_return


@app.post("/create_book", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest):
    new_book = Book(**book_request.dict())
    BOOKS.append(get_book_id(new_book))


def get_book_id(book):
    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
    return book


@app.put("/books/update_book", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book: BookRequest):
    book_changed = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book.id:
            BOOKS[i] = book
            book_changed = True
    if not book_changed:
        raise HTTPException(status_code=404, detail='Item not found!')


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int = Path(gt=0)):
    book_changed = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.pop(i)
            book_changed = True
            break
    if not book_changed:
        raise HTTPException(status_code=404, detail='Item not found!')