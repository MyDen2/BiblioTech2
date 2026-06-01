# Objectif : 

# ratings_joinable
# +
# books_clean
# ↓
# user_profiles

import pandas as pd

from src.utils.logger import setup_logger
from src.utils.s3_io import (
    read_parquet_from_s3,
    write_parquet_to_s3,
)

logger = setup_logger("build_user_profiles")

SILVER_BUCKET = "silver"
GOLD_BUCKET = "gold"

BOOKS_KEY = "books_clean.parquet"
RATINGS_KEY = "ratings_joinable.parquet"

OUTPUT_KEY = "user_profiles.parquet"


def get_favorite_author(df: pd.DataFrame) -> pd.Series:

    favorite = (
        df.groupby(
            ["user_id", "authors"]
        )
        .size()
        .reset_index(name="count")
        .sort_values(
            ["user_id", "count"],
            ascending=[True, False]
        )
        .drop_duplicates(
            subset=["user_id"]
        )
    )

    return favorite.set_index(
        "user_id"
    )["authors"]


def build_profiles(
    books_df: pd.DataFrame,
    ratings_df: pd.DataFrame
) -> pd.DataFrame:

    logger.info("Joining ratings and books")

    books_cols = [
        "book_id",
        "authors",
        "release_year",
        "number_pages",
    ]

    books = books_df[
        books_cols
    ]

    merged = ratings_df.merge(
        books,
        on="book_id",
        how="left"
    )

    logger.info(f"Merged shape: {merged.shape}")

    profiles = (
        merged
        .groupby("user_id")
        .agg(
            books_count=(
                "book_id",
                "nunique"
            ),
            average_given_rating=(
                "rating",
                "mean"
            ),
            authors_count=(
                "authors",
                "nunique"
            ),
            average_release_year=(
                "release_year",
                "mean"
            ),
            average_pages=(
                "number_pages",
                "mean"
            ),
        )
        .reset_index()
    )

    profiles["favorite_author"] = (
        profiles["user_id"]
        .map(
            get_favorite_author(
                merged
            )
        )
    )

    profiles["average_given_rating"] = (
        profiles["average_given_rating"]
        .round(2)
    )

    profiles["average_release_year"] = (
        profiles["average_release_year"]
        .round()
    )

    profiles["average_pages"] = (
        profiles["average_pages"]
        .round()
    )

    logger.info(
        f"Profiles created: {profiles.shape}"
    )

    return profiles


def main():

    try:

        logger.info(
            "Loading books"
        )

        books_df = read_parquet_from_s3(
            SILVER_BUCKET,
            BOOKS_KEY
        )

        logger.info(
            "Loading ratings"
        )

        ratings_df = read_parquet_from_s3(
            SILVER_BUCKET,
            RATINGS_KEY
        )

        profiles = build_profiles(
            books_df,
            ratings_df
        )

        logger.info(
            f"Saving to {GOLD_BUCKET}/{OUTPUT_KEY}"
        )

        write_parquet_to_s3(
            profiles,
            GOLD_BUCKET,
            OUTPUT_KEY
        )

        logger.info(
            "user_profiles created"
        )

    except Exception as e:

        logger.exception(e)

        raise


if __name__ == "__main__":
    main()