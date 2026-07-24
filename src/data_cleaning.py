import pandas as pd
#  Load Data
df=pd.read_parquet("data/raw/yellow_tripdata_2026-05.parquet")

#  Duplicates Removal
duplicate_count=df.duplicated().sum()
print(f"Duplicate rows:{duplicate_count}")

df=df.drop_duplicates()

# Check for data types
print(df.dtypes)

categorical_cols=[
    "VendorID",
    "RatecodeID",
    "store_and_fwd_flag",
    "payment_type",
    "PULocationID",
    "DOLocationID"
]

for col in categorical_cols:
    df[col]=df[col].astype("category")
    
print(df[categorical_cols].dtypes)
print(df.dtypes)