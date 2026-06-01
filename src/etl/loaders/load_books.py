from pathlib import Path

import pandas as pd

from src.utils.logger import setup_logger
from src.utils.s3_io import write_parquet_to_s3, list_objects


logger = setup_logger("load_books")

BASE_DIR = Path(__file__).resolve().parents[3]
RAW_DIR = BASE_DIR / "data" / "raw"

BOOKS_PATTERN = "book*.csv"

BRONZE_BUCKET = "bronze"
OUTPUT_KEY = "books_raw.parquet"


def load_books_csv_files() -> pd.DataFrame:
    logger.info(f"Searching books files in {RAW_DIR}")

    files = sorted(RAW_DIR.glob(BOOKS_PATTERN))

    if not files:
        raise FileNotFoundError(f"No files found with pattern: {BOOKS_PATTERN} in {RAW_DIR}")

    dataframes = []

    for file in files:
        logger.info(f"Loading file: {file.name}")

        df = pd.read_csv(file)

        logger.info(f"{file.name}: {df.shape[0]} rows, {df.shape[1]} columns")

        df["source_file"] = file.name
        dataframes.append(df)

    books_df = pd.concat(dataframes, ignore_index=True)

    logger.info(f"Total rows loaded: {books_df.shape[0]}")
    logger.info(f"Columns: {list(books_df.columns)}")

    return books_df


def save_to_bronze(df: pd.DataFrame) -> None:
    logger.info(f"Saving books to s3://{BRONZE_BUCKET}/{OUTPUT_KEY}")

    write_parquet_to_s3(
        df=df,
        bucket=BRONZE_BUCKET,
        key=OUTPUT_KEY
    )

    logger.info("Books saved successfully")


def verify_upload() -> None:
    objects = list_objects(BRONZE_BUCKET)

    if OUTPUT_KEY not in objects:
        raise RuntimeError(f"Upload failed: {OUTPUT_KEY} not found in bucket {BRONZE_BUCKET}")

    logger.info(f"Upload verified: {OUTPUT_KEY}")


def main() -> None:
    try:
        books_df = load_books_csv_files()
        save_to_bronze(books_df)
        verify_upload()

        logger.info("load_books pipeline completed successfully")

    except Exception as e:
        logger.error(f"Error in load_books pipeline: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()