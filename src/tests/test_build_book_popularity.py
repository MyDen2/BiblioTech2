from src.utils.s3_io import read_parquet_from_s3

df = read_parquet_from_s3("gold", "book_popularity.parquet")

print(df.head(10))
print(df.shape)