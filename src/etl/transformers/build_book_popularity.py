# Objectif : 

# silver/ratings_joinable
# +
# silver/books_clean
# ↓
# gold/book_popularity.parquet

import pandas as pd

from src.utils.logger import setup_logger
from src.utils.s3_io import (
    read_parquet_from_s3,
    write_parquet_to_s3,
)


logger = setup_logger("build_book_popularity")

SILVER_BUCKET = "silver"
GOLD_BUCKET = "gold"

BOOKS_KEY = "books_clean.parquet"
RATINGS_KEY = "ratings_joinable.parquet"

OUTPUT_KEY = "book_popularity.parquet"


def build_book_popularity(
    books_df: pd.DataFrame,
    ratings_df: pd.DataFrame
) -> pd.DataFrame:

    logger.info("Building book popularity gold table")

    ratings_agg = (
        ratings_df
        .groupby("book_id", as_index=False)
        .agg(
            ratings_count=("rating", "count"),
            average_rating=("rating", "mean")
        )
    )

    logger.info(f"Aggregated ratings shape: {ratings_agg.shape}")

    books_cols = [
        "book_id",
        "title",
        "authors",
        "isbn",
        "publisher",
        "release_year",
        "number_pages",
    ]

    books_light = books_df[books_cols].drop_duplicates(
        subset=["book_id"]
    )

    gold_df = books_light.merge(
        ratings_agg,
        on="book_id",
        how="inner"
    )

    logger.info(f"Gold table shape after join: {gold_df.shape}")

    gold_df["average_rating"] = (
        gold_df["average_rating"]
        .round(2)
    )

    global_mean = gold_df["average_rating"].mean()

    min_votes = 10

    gold_df["weighted_score"] = (
        (
            gold_df["ratings_count"]
            / (gold_df["ratings_count"] + min_votes)
        )
        * gold_df["average_rating"]
        +
        (
            min_votes
            / (gold_df["ratings_count"] + min_votes)
        )
        * global_mean
    ).round(2)

    gold_df = gold_df.sort_values(
        by=[
            "weighted_score",
            "ratings_count"
        ],
        ascending=[
            False,
            False
        ]
    ).reset_index(drop=True)

    logger.info(f"Final gold table shape: {gold_df.shape}")
    logger.info(f"Books with ratings: {gold_df['book_id'].nunique()}")

    return gold_df


def main() -> None:
    try:
        logger.info("Loading silver books")

        books_df = read_parquet_from_s3(
            SILVER_BUCKET,
            BOOKS_KEY
        )

        logger.info(f"Books shape: {books_df.shape}")

        logger.info("Loading ratings_joinable")

        ratings_df = read_parquet_from_s3(
            SILVER_BUCKET,
            RATINGS_KEY
        )

        logger.info(f"Ratings shape: {ratings_df.shape}")

        gold_df = build_book_popularity(
            books_df,
            ratings_df
        )

        logger.info(f"Saving to s3://{GOLD_BUCKET}/{OUTPUT_KEY}")

        write_parquet_to_s3(
            gold_df,
            GOLD_BUCKET,
            OUTPUT_KEY
        )

        logger.info("book_popularity created successfully")

    except Exception as e:
        logger.exception(f"Error while building book popularity: {e}")
        raise


if __name__ == "__main__":
    main()