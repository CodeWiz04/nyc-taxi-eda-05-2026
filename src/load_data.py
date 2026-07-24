from pathlib import Path
DATA_FILE=Path("data/raw/yellow_tripdata_2026-05.parquet")

if not DATA_FILE.exists():
    raise FileNotFoundError(f"Data file not found: {DATA_FILE}")

print("File Found!")


# File Size

file_size=DATA_FILE.stat().st_size


print("File Size in Bytes:",file_size)

