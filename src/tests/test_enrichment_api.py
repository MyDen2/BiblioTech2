from src.utils.s3_io import read_parquet_from_s3

df = read_parquet_from_s3("silver", "books_metadata.parquet")

print(df.shape)
print(df["metadata_found"].value_counts())
print(df[["title", "genre", "categories"]].head(10))