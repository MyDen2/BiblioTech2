import pandas as pd
import re

from src.utils.logger import setup_logger
from src.utils.s3_io import (
    read_parquet_from_s3,
    write_parquet_to_s3,
)


logger = setup_logger("clean_books")

BRONZE_BUCKET = "bronze"
SILVER_BUCKET = "silver"

INPUT_KEY = "books_raw.parquet"
OUTPUT_KEY = "books_clean.parquet"


COLUMN_MAPPING = {
    "Id": "book_id",
    "Name": "title",
    "Authors": "authors",
    "ISBN": "isbn",
    "Rating": "average_rating",
    "PublishYear": "release_year",
    "Publisher": "publisher",
    "Language": "language",
    "pagesNumber": "number_pages",
}

def normalize_key(value):

    if pd.isna(value):
        return None

    value = str(value)

    value = value.strip()

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.lower()

def clean_text(value):
    if pd.isna(value):
        return None

    value = str(value).strip()
    value = re.sub(r"\s+", " ", value)

    if value == "" or value.lower() == "nan":
        return None

    return value


def clean_isbn(value):
    if pd.isna(value):
        return None

    value = str(value).strip().replace("-", "").replace(" ", "")

    if value == "" or value.lower() == "nan":
        return None

    return value[:20]

def clean_books(df: pd.DataFrame) -> pd.DataFrame:

    logger.info("Starting books cleaning")

    df = df.rename(columns=COLUMN_MAPPING)

    columns_to_keep = list(COLUMN_MAPPING.values())
    df = df[columns_to_keep]

    logger.info("Cleaning text columns")

    df["title"] = df["title"].apply(clean_text)
    df["authors"] = df["authors"].apply(clean_text)
    df["publisher"] = df["publisher"].apply(clean_text)
    df["language"] = df["language"].apply(clean_text)
    df["isbn"] = df["isbn"].apply(clean_isbn)

    logger.info("Handling missing values")

    df["title"] = df["title"].fillna("Unknown")
    df["authors"] = df["authors"].fillna("Unknown")
    df["publisher"] = df["publisher"].fillna("Unknown")
    df["language"] = df["language"].fillna("unknown")

    df["average_rating"] = (
        pd.to_numeric(df["average_rating"], errors="coerce")
        .fillna(0)
    )

    df["release_year"] = pd.to_numeric(
        df["release_year"],
        errors="coerce"
    )

    df = df[
    (df["release_year"].isna())
    |
    (
        (df["release_year"] >= 1400)
        &
        (df["release_year"] <= 2030)
    )
    ]

    df["number_pages"] = pd.to_numeric(
        df["number_pages"],
        errors="coerce"
    )

    logger.info("Filtering invalid rows")

    df = df[df["title"] != "Unknown"]
    df = df[df["number_pages"] > 0]

    df["title_key"] = (
        df["title"]
        .apply(normalize_key)
    )

    df["authors_key"] = (
        df["authors"]
        .apply(normalize_key)
    )

    logger.info("Removing duplicates")

    df_with_isbn = df[df["isbn"].notna()].drop_duplicates(
        subset=["isbn"],
        keep="last"
    )

    df_without_isbn = (
        df[
            df["isbn"].isna()
        ]
        .drop_duplicates(
            subset=[
                "title_key",
                "authors_key",
                "release_year"
            ],
            keep="last"
        )
    )

    df = pd.concat(
        [df_with_isbn, df_without_isbn],
        ignore_index=True
    )

    df = df.drop(
        columns=[
            "title_key",
            "authors_key"
        ],
        errors="ignore"
    )

    logger.info(f"Final shape: {df.shape}")

    return df.reset_index(drop=True)

def main():

    logger.info("Loading bronze data")

    books_df = read_parquet_from_s3(
        BRONZE_BUCKET,
        INPUT_KEY
    )

    logger.info(f"Input shape: {books_df.shape}")

    cleaned_df = clean_books(
        books_df
    )

    logger.info("Saving silver data")

    write_parquet_to_s3(
        cleaned_df,
        SILVER_BUCKET,
        OUTPUT_KEY
    )

    logger.info("books_clean created")


if __name__ == "__main__":
    main()