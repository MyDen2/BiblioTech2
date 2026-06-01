# 
# books_clean.parquet
# ↓
# INSERT books
# ON CONFLICT (isbn)
# DO UPDATE
# RETURNING book_id
# ↓
# authors
# ↓
# book_author

import pandas as pd

from src.database.db import get_connection
from src.utils.logger import setup_logger
from src.utils.s3_io import read_parquet_from_s3


logger = setup_logger("load_books_to_postgres")

SILVER_BUCKET = "silver"
BOOKS_KEY = "books_clean.parquet"


def clean_isbn(value):
    if pd.isna(value):
        return None

    value = str(value).strip()

    if value == "" or value.lower() == "nan":
        return None

    return value[:20]


def split_author_name(full_name: str) -> tuple[str, str]:
    if not full_name or full_name == "Unknown":
        return "Unknown", "Unknown"

    parts = str(full_name).strip().split()

    if len(parts) == 1:
        return parts[0][:50], "Unknown"

    first_name = " ".join(parts[:-1])
    last_name = parts[-1]

    return first_name[:50], last_name[:50]


def load_books_to_postgres(df: pd.DataFrame) -> None:
    conn = get_connection()

    try:
        with conn:
            with conn.cursor() as cur:
                logger.info("Loading books into PostgreSQL")

                for _, row in df.iterrows():
                    isbn = clean_isbn(row["isbn"])
                    title = str(row["title"])[:150]
                    summary = "No summary available"
                    release_year = int(row["release_year"]) if pd.notna(row["release_year"]) else 0
                    number_pages = int(row["number_pages"]) if pd.notna(row["number_pages"]) and row["number_pages"] > 0 else 1

                    cur.execute(
                        """
                        INSERT INTO bibliotech.books (
                            isbn,
                            title,
                            summary,
                            release_year,
                            number_pages
                        )
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (isbn)
                        DO UPDATE SET
                            title = EXCLUDED.title,
                            summary = EXCLUDED.summary,
                            release_year = EXCLUDED.release_year,
                            number_pages = EXCLUDED.number_pages
                        RETURNING book_id;
                        """,
                        (
                            isbn,
                            title,
                            summary,
                            release_year,
                            number_pages,
                        )
                    )

                    book_id = cur.fetchone()[0]

                    authors_raw = str(row["authors"]).split(",")

                    for author_name in authors_raw:
                        first_name, last_name = split_author_name(author_name)

                        cur.execute(
                            """
                            SELECT author_id
                            FROM bibliotech.authors
                            WHERE first_name = %s
                            AND last_name = %s;
                            """,
                            (
                                first_name,
                                last_name,
                            )
                        )

                        existing = cur.fetchone()

                        if existing:
                            author_id = existing[0]
                        else:
                            cur.execute(
                                """
                                INSERT INTO bibliotech.authors (
                                    first_name,
                                    last_name,
                                    birth_date,
                                    nationality
                                )
                                VALUES (%s, %s, NULL, NULL)
                                RETURNING author_id;
                                """,
                                (
                                    first_name,
                                    last_name,
                                )
                            )

                            author_id = cur.fetchone()[0]

                        cur.execute(
                            """
                            INSERT INTO bibliotech.book_author (
                                book_id,
                                author_id
                            )
                            VALUES (%s, %s)
                            ON CONFLICT DO NOTHING;
                            """,
                            (
                                book_id,
                                author_id,
                            )
                        )

        logger.info("Books loaded successfully")

    finally:
        conn.close()


def main() -> None:
    logger.info("Reading books_clean from MinIO")

    books_df = read_parquet_from_s3(
        SILVER_BUCKET,
        BOOKS_KEY
    )

    logger.info(f"Books dataframe shape: {books_df.shape}")

    load_books_to_postgres(books_df)


if __name__ == "__main__":
    main()