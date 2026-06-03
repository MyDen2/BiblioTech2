import time
import requests
import os 
from pathlib import Path
from dotenv import load_dotenv



BASE_DIR = Path(__file__).resolve().parents[2]

ENV_PATH = BASE_DIR / "config" / ".env"

load_dotenv(dotenv_path=ENV_PATH)

GOOGLE_BOOKS_API_KEY = os.getenv(
    "GOOGLE_BOOKS_API_KEY"
)

print(
    "KEY FOUND:",
    GOOGLE_BOOKS_API_KEY is not None
)

GOOGLE_BOOKS_URL = "https://www.googleapis.com/books/v1/volumes"


def empty_metadata() -> dict:
    return {
        "genre": None,
        "categories": None,
        "description": None,
        "google_books_id": None,
        "metadata_found": False,
    }


def build_query(isbn, title, authors):
    if isbn:
        return f"isbn:{isbn}"

    query = ""

    if title:
        query += f'intitle:"{title}" '

    if authors:
        first_author = str(authors).split(",")[0].strip()
        query += f'inauthor:"{first_author}"'

    return query.strip()


def fetch_book_metadata(
    isbn: str | None,
    title: str | None,
    authors: str | None
) -> dict:
    query = build_query(isbn, title, authors)

    if not query:
        return empty_metadata()

    params = {
        "q": query,
        "maxResults": 1,
        "printType": "books",
    }

    if GOOGLE_BOOKS_API_KEY:
        params["key"] = GOOGLE_BOOKS_API_KEY

    for attempt in range(3):
        response = requests.get(
            GOOGLE_BOOKS_URL,
            params=params,
            timeout=10,
        )

        if response.status_code != 429:
            break

        time.sleep(30 * (attempt + 1))

    response.raise_for_status()

    data = response.json()
    items = data.get("items", [])

    if not items:
        return empty_metadata()

    volume = items[0]
    volume_info = volume.get("volumeInfo", {})

    categories = volume_info.get("categories", [])
    description = volume_info.get("description")

    return {
        "genre": categories[0] if categories else None,
        "categories": ", ".join(categories) if categories else None,
        "description": description,
        "google_books_id": volume.get("id"),
        "metadata_found": True,
    }