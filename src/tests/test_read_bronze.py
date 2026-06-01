from src.utils.logger import setup_logger
from src.utils.s3_io import read_parquet_from_s3


logger = setup_logger("test_read_bronze")


def main():

    df = read_parquet_from_s3(
        "bronze",
        "books_raw.parquet"
    )

    logger.info(df.head())

    logger.info(df.shape)


if __name__ == "__main__":
    main()