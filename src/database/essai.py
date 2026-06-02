import pandas as pd

splits = {'train': 'data/train-00000-of-00001-1ddc9bde2cb8caf1.parquet', 'validation': 'data/validation-00000-of-00001-c69c3deb9f318ffd.parquet', 'test': 'data/test-00000-of-00001-35cf4a77f73c1e63.parquet'}
df = pd.read_parquet("hf://datasets/pszemraj/goodreads-bookgenres/" + splits["train"])

print(df)