from src.external.google_books_client import (
    fetch_book_metadata
)

print(
    fetch_book_metadata(
        isbn="0439358078",
        title="Harry Potter",
        authors="J.K. Rowling"
    )
)