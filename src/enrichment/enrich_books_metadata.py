# src/enrichment/enrich_books_metadata.py

import time
import pandas as pd

from src.external.google_books_client import fetch_book_metadata
from src.utils.logger import setup_logger
from src.utils.s3_io import read_parquet_from_s3, write_parquet_to_s3


logger = setup_logger("enrich_books_metadata")

GOLD_BUCKET = "gold"
SILVER_BUCKET = "silver"

INPUT_KEY = "books_to_enrich.parquet"
OUTPUT_KEY = "books_metadata.parquet"

SLEEP_SECONDS = 3


def clean_value(value):
    if pd.isna(value):
        return None

    value = str(value).strip()

    if value == "" or value.lower() == "nan":
        return None

    return value


def enrich_books(df: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for index, row in df.iterrows():
        if index % 100 == 0:
            logger.info(f"Processed {index}/{len(df)} books")

        isbn = clean_value(row.get("isbn"))
        title = clean_value(row.get("title"))

        try:
            metadata = fetch_book_metadata(isbn=isbn, title=title, authors=row.get("authors"))
        except Exception as e:
            logger.warning(f"Metadata fetch failed for isbn={isbn}, title={title}: {e}")
            metadata = {
                "genre": None,
                "categories": None,
                "description": None,
                "google_books_id": None,
                "metadata_found": False,
            }

        rows.append({
            "book_id": row.get("book_id"),
            "isbn": isbn,
            "title": title,
            "authors": row.get("authors"),
            "publisher": row.get("publisher"),
            "genre": metadata["genre"],
            "categories": metadata["categories"],
            "description": metadata["description"],
            "google_books_id": metadata["google_books_id"],
            "metadata_found": metadata["metadata_found"],
        })

        time.sleep(SLEEP_SECONDS)

    return pd.DataFrame(rows)


def main() -> None:
    logger.info("Loading books_to_enrich")

    books_df = read_parquet_from_s3(GOLD_BUCKET, INPUT_KEY)
    logger.info(f"Input shape: {books_df.shape}")

    enriched_df = enrich_books(books_df)

    logger.info(f"Metadata found: {enriched_df['metadata_found'].sum()}")
    logger.info(f"Saving to s3://{SILVER_BUCKET}/{OUTPUT_KEY}")

    write_parquet_to_s3(enriched_df, SILVER_BUCKET, OUTPUT_KEY)

    logger.info("books_metadata created successfully")


if __name__ == "__main__":
    main()