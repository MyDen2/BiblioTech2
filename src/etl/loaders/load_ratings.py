from pathlib import Path

import pandas as pd

from src.utils.logger import setup_logger
from src.utils.s3_io import (
    write_parquet_to_s3,
    list_objects,
)

logger = setup_logger("load_ratings")

BASE_DIR = Path(__file__).resolve().parents[3]

RAW_DIR = BASE_DIR / "data" / "raw"

RATINGS_PATTERN = "user_rating*.csv"

BRONZE_BUCKET = "bronze"

OUTPUT_KEY = "ratings_raw.parquet"


def load_ratings_files() -> pd.DataFrame:

    logger.info(f"Searching ratings files in {RAW_DIR}")

    files = sorted(
        RAW_DIR.glob(RATINGS_PATTERN)
    )

    if not files:
        raise FileNotFoundError(
            f"No ratings files found"
        )

    dfs = []

    for file in files:

        logger.info(f"Loading {file.name}")

        df = pd.read_csv(
            file
        )

        df["source_file"] = file.name

        logger.info(
            f"{file.name}: {df.shape}"
        )

        dfs.append(df)

    final_df = pd.concat(
        dfs,
        ignore_index=True
    )

    logger.info(
        f"Final dataset shape: {final_df.shape}"
    )

    return final_df


def save_to_bronze(df):

    logger.info(
        f"Saving ratings to s3://{BRONZE_BUCKET}/{OUTPUT_KEY}"
    )

    write_parquet_to_s3(
        df,
        BRONZE_BUCKET,
        OUTPUT_KEY
    )

    logger.info("Ratings saved")


def verify():

    objects = list_objects(
        BRONZE_BUCKET
    )

    if OUTPUT_KEY not in objects:
        raise RuntimeError(
            "Upload failed"
        )

    logger.info("Upload verified")


def main():

    try:

        df = load_ratings_files()

        save_to_bronze(
            df
        )

        verify()

        logger.info(
            "ratings loader completed"
        )

    except Exception as e:

        logger.exception(e)

        raise


if __name__ == "__main__":
    main()