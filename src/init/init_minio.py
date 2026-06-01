from src.utils.logger import setup_logger
from src.utils.s3_io import (
    create_bucket_if_not_exists,
)

logger = setup_logger("init_minio")

BUCKETS = [
    "bronze",
    "silver",
    "gold",
]


def main():

    logger.info("Initializing MinIO")

    for bucket in BUCKETS:
        create_bucket_if_not_exists(bucket)
        logger.info(f"Bucket ready: {bucket}")

    logger.info("MinIO initialization completed")


if __name__ == "__main__":
    main()