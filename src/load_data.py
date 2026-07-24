from pathlib import Path
import pandas as pd 
DATA_FILE=Path("data/raw/yellow_tripdata_2026-05.parquet")

if not DATA_FILE.exists():
    raise FileNotFoundError(f"Data file not found: {DATA_FILE}")

print("File Found!")


# File Size

file_size=DATA_FILE.stat().st_size


print("File Size in Bytes:",file_size)
size_mb=file_size/(1024*1024)
print("file size in MBs:",size_mb) 


if size_mb<1:
    raise ValueError("File appears to be empty or corrupted")

df=pd.read_parquet(DATA_FILE)

print(f"Rows: {len(df):,}")
print(f"Columns: {len(df.columns)}")
