import pandas as pd

from src.database.db import get_connection
from src.utils.logger import setup_logger
from src.utils.s3_io import read_parquet_from_s3


logger = setup_logger("load_grades_to_postgres")

SILVER_BUCKET = "silver"
RATINGS_KEY = "ratings_joinable.parquet"


def clean_isbn(value):
    if pd.isna(value):
        return None

    value = str(value).strip().replace("-", "").replace(" ", "")

    if value == "" or value.lower() == "nan":
        return None

    return value[:20]


def load_grades_to_postgres(df: pd.DataFrame) -> None:
    conn = get_connection()

    inserted = 0
    skipped = 0

    try:
        with conn:
            with conn.cursor() as cur:
                logger.info("Loading grades into PostgreSQL")

                for _, row in df.iterrows():
                    isbn = clean_isbn(row["isbn"])

                    if isbn is None:
                        skipped += 1
                        continue

                    cur.execute(
                        """
                        SELECT book_id
                        FROM bibliotech.books
                        WHERE isbn = %s;
                        """,
                        (isbn,)
                    )

                    result = cur.fetchone()

                    if result is None:
                        skipped += 1
                        continue

                    book_id = result[0]
                    user_id = int(row["user_id"])
                    grade = int(row["rating"])

                    cur.execute(
                        """
                        INSERT INTO bibliotech.grades (
                            book_id,
                            user_id,
                            grade
                        )
                        VALUES (%s, %s, %s)
                        ON CONFLICT (book_id, user_id)
                        DO UPDATE SET
                            grade = EXCLUDED.grade,
                            grade_date = CURRENT_TIMESTAMP;
                        """,
                        (
                            book_id,
                            user_id,
                            grade,
                        )
                    )

                    inserted += 1

        logger.info(f"Grades loaded successfully: {inserted}")
        logger.info(f"Grades skipped: {skipped}")

    finally:
        conn.close()


def main() -> None:
    logger.info("Reading ratings_joinable from MinIO")

    ratings_df = read_parquet_from_s3(
        SILVER_BUCKET,
        RATINGS_KEY
    )

    logger.info(f"Ratings dataframe shape: {ratings_df.shape}")

    load_grades_to_postgres(ratings_df)


if __name__ == "__main__":
    main()