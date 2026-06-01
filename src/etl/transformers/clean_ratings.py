# bronze/ratings_raw.parquet
# ↓
# normalisation
# ↓
# silver/ratings_clean.parquet

import pandas as pd

from src.utils.logger import setup_logger
from src.utils.s3_io import (
    read_parquet_from_s3,
    write_parquet_to_s3,
)


logger = setup_logger("clean_ratings")

BRONZE_BUCKET = "bronze"
SILVER_BUCKET = "silver"

INPUT_KEY = "ratings_raw.parquet"
OUTPUT_KEY = "ratings_clean.parquet"


RATING_MAPPING = {
    "did not like it": 1,
    "it was ok": 2,
    "liked it": 3,
    "really liked it": 4,
    "it was amazing": 5,
}


def clean_ratings(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Starting ratings cleaning")

    df = df.rename(
        columns={
            "ID": "user_id",
            "Name": "title",
            "Rating": "rating_text",
        }
    )

    df = df[["user_id", "title", "rating_text"]]

    logger.info(f"Initial shape: {df.shape}")

    df["rating_text"] = (
        df["rating_text"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    df["title"] = (
        df["title"]
        .astype(str)
        .str.strip()
    )

    df = df[
        df["rating_text"] != "this user doesn't have any rating"
    ]

    df["rating"] = df["rating_text"].map(RATING_MAPPING)

    df = df[
        df["rating"].notna()
    ]

    df["user_id"] = pd.to_numeric(
        df["user_id"],
        errors="coerce"
    )

    df = df[
        df["user_id"].notna()
    ]

    df["user_id"] = df["user_id"].astype(int)
    df["rating"] = df["rating"].astype(int)

    df = df.drop_duplicates(
        subset=["user_id", "title"],
        keep="last"
    )

    df = df[
        ["user_id", "title", "rating"]
    ]

    logger.info(f"Final shape: {df.shape}")
    logger.info(f"Unique users: {df['user_id'].nunique()}")
    logger.info(f"Unique rated books: {df['title'].nunique()}")

    return df.reset_index(drop=True)


def main() -> None:
    try:
        logger.info("Loading raw ratings from bronze")

        ratings_df = read_parquet_from_s3(
            BRONZE_BUCKET,
            INPUT_KEY
        )

        logger.info(f"Input shape: {ratings_df.shape}")

        clean_df = clean_ratings(ratings_df)

        logger.info(f"Saving clean ratings to s3://{SILVER_BUCKET}/{OUTPUT_KEY}")

        write_parquet_to_s3(
            clean_df,
            SILVER_BUCKET,
            OUTPUT_KEY
        )

        logger.info("ratings_clean created successfully")

    except Exception as e:
        logger.exception(f"Error while cleaning ratings: {e}")
        raise


if __name__ == "__main__":
    main()