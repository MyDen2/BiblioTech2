from src.utils.s3_io import read_parquet_from_s3

df = read_parquet_from_s3(
    "gold",
    "user_profiles.parquet"
)

print(df.head())
print(df.shape)