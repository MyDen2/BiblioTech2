# # Objectif : 

# books_clean
# +
# ratings_clean
# ↓
# ratings_joinable

# Car actuellelent :

# ratings_clean
# user_id
# title
# rating

# Mais le moteur IA a besoin de : 

# user_id
# book_id
# isbn
# rating

# Donc, nous faisons : JOIN ratings.title = books.title


import pandas as pd

from src.utils.logger import setup_logger
from src.utils.s3_io import (
    read_parquet_from_s3,
    write_parquet_to_s3,
)


logger = setup_logger("build_ratings_joinable")

SILVER_BUCKET = "silver"

BOOKS_KEY = "books_clean.parquet"
RATINGS_KEY = "ratings_clean.parquet"
OUTPUT_KEY = "ratings_joinable.parquet"


def normalize_title(series: pd.Series) -> pd.Series:
    return (
        series
        .astype(str)
        .str.strip()
        .str.lower()
    )


def build_ratings_joinable(
    books_df: pd.DataFrame,
    ratings_df: pd.DataFrame
) -> pd.DataFrame:

    logger.info("Building ratings_joinable")

    books = books_df.copy()
    ratings = ratings_df.copy()

    books["title_join"] = normalize_title(books["title"])
    ratings["title_join"] = normalize_title(ratings["title"])

    books_join = books[
        ["book_id", "isbn", "title", "title_join"]
    ].drop_duplicates(
        subset=["title_join"]
    )

    logger.info(f"Books available for join: {books_join.shape}")
    logger.info(f"Ratings before join: {ratings.shape}")

    joined = ratings.merge(
        books_join,
        on="title_join",
        how="inner",
        suffixes=("_rating", "_book")
    )

    logger.info(f"Ratings after join: {joined.shape}")

    result = joined[
        [
            "user_id",
            "book_id",
            "isbn",
            "title_book",
            "rating",
        ]
    ].rename(
        columns={
            "title_book": "title"
        }
    )

    result = result.drop_duplicates(
        subset=["user_id", "book_id"],
        keep="last"
    )

    result["user_id"] = result["user_id"].astype(int)
    result["book_id"] = result["book_id"].astype(int)
    result["rating"] = result["rating"].astype(int)

    logger.info(f"Final joinable shape: {result.shape}")
    logger.info(f"Unique users: {result['user_id'].nunique()}")
    logger.info(f"Unique books rated: {result['book_id'].nunique()}")

    return result.reset_index(drop=True)


def main() -> None:
    try:
        logger.info("Loading silver books")

        books_df = read_parquet_from_s3(
            SILVER_BUCKET,
            BOOKS_KEY
        )

        logger.info("Loading silver ratings")

        ratings_df = read_parquet_from_s3(
            SILVER_BUCKET,
            RATINGS_KEY
        )

        joinable_df = build_ratings_joinable(
            books_df,
            ratings_df
        )

        logger.info(f"Saving to s3://{SILVER_BUCKET}/{OUTPUT_KEY}")

        write_parquet_to_s3(
            joinable_df,
            SILVER_BUCKET,
            OUTPUT_KEY
        )

        logger.info("ratings_joinable created successfully")

    except Exception as e:
        logger.exception(f"Error while building ratings_joinable: {e}")
        raise


if __name__ == "__main__":
    main()