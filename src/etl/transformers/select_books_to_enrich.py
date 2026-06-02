# prendre les livres les plus intéressants depuis : gold/book_popularity.parquet
# création de : gold/books_to_enrich.parquet

from src.utils.logger import setup_logger
from src.utils.s3_io import read_parquet_from_s3, write_parquet_to_s3


logger = setup_logger("select_books_to_enrich")

GOLD_BUCKET = "gold"

INPUT_KEY = "book_popularity.parquet"
OUTPUT_KEY = "books_to_enrich.parquet"

TOP_N = 5000


def main() -> None:
    logger.info("Loading book popularity")

    df = read_parquet_from_s3(
        GOLD_BUCKET,
        INPUT_KEY
    )

    logger.info(f"Input shape: {df.shape}")

    selected = (
        df[df["isbn"].notna()]
        .sort_values(
            by=["weighted_score", "ratings_count"],
            ascending=[False, False]
        )
        .head(TOP_N)
        .reset_index(drop=True)
    )

    logger.info(f"Selected books: {selected.shape}")

    write_parquet_to_s3(
        selected,
        GOLD_BUCKET,
        OUTPUT_KEY
    )

    logger.info(f"Created gold/{OUTPUT_KEY}")


if __name__ == "__main__":
    main()

