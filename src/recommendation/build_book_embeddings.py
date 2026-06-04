import pandas as pd

from src.database.db import get_connection
from src.external.transformers_client import encode_text
from src.utils.logger import setup_logger
from src.utils.s3_io import read_parquet_from_s3


logger = setup_logger("build_book_embeddings")

SILVER_BUCKET = "silver"
METADATA_KEY = "books_metadata.parquet"


def clean_value(value):
    if pd.isna(value):
        return ""

    return str(value).strip()


def build_embedding_text(row) -> str:
    return f"""
Title: {clean_value(row.get("title"))}
Authors: {clean_value(row.get("authors"))}
Publisher: {clean_value(row.get("publisher"))}
Genre: {clean_value(row.get("genre"))}
Categories: {clean_value(row.get("categories"))}
Description: {clean_value(row.get("description"))}
""".strip()


def vector_to_pgvector(vector: list[float]) -> str:
    return "[" + ",".join(str(x) for x in vector) + "]"


def get_postgres_book_id(cur, isbn: str):
    cur.execute(
        """
        SELECT book_id
        FROM bibliotech.books
        WHERE isbn = %s;
        """,
        (isbn,)
    )

    result = cur.fetchone()

    if result:
        return result[0]

    return None


def build_book_embeddings(df: pd.DataFrame) -> None:
    conn = get_connection()

    inserted = 0
    skipped = 0

    try:
        with conn:
            with conn.cursor() as cur:
                for index, row in df.iterrows():
                    if index % 50 == 0:
                        logger.info(f"Processed {index}/{len(df)} books")

                    isbn = clean_value(row.get("isbn"))

                    if not isbn:
                        skipped += 1
                        continue

                    book_id = get_postgres_book_id(cur, isbn)

                    if book_id is None:
                        skipped += 1
                        continue

                    embedding_text = build_embedding_text(row)
                    vector = encode_text(embedding_text)
                    pg_vector = vector_to_pgvector(vector)

                    cur.execute(
                        """
                        INSERT INTO bibliotech.book_embeddings (
                            book_id,
                            vector,
                            updated_at
                        )
                        VALUES (%s, %s, CURRENT_TIMESTAMP)
                        ON CONFLICT (book_id)
                        DO UPDATE SET
                            vector = EXCLUDED.vector,
                            updated_at = CURRENT_TIMESTAMP;
                        """,
                        (
                            book_id,
                            pg_vector,
                        )
                    )

                    inserted += 1

        logger.info(f"Book embeddings inserted: {inserted}")
        logger.info(f"Book embeddings skipped: {skipped}")

    finally:
        conn.close()


def main() -> None:
    logger.info("Loading books metadata")

    metadata_df = read_parquet_from_s3(
        SILVER_BUCKET,
        METADATA_KEY
    )

    logger.info(f"Metadata shape: {metadata_df.shape}")

    metadata_df = metadata_df[
        metadata_df["metadata_found"] == True
    ].reset_index(drop=True)

    logger.info(f"Books with metadata: {metadata_df.shape}")

    build_book_embeddings(metadata_df)

    logger.info("book_embeddings completed")


if __name__ == "__main__":
    main()