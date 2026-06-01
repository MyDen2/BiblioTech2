from src.utils.s3_io import read_parquet_from_s3

df = read_parquet_from_s3(
    "silver",
    "books_clean.parquet"
)

print(df.head())

print(df.shape)

print(df.dtypes)