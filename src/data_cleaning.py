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

datetime_cols=[
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime"
]
for col in datetime_cols:
    df[col]=pd.to_datetime(df[col])
    
    
print(df[datetime_cols].dtypes)

# # Converting passenger_count to int
# df['passenger_count']=df['passenger_count'].astype("int64")

# print(df.dtypes)

print(df["passenger_count"].isna().sum())
# First handle missings values in passenger_count column to convert the data type of that column
df['passenger_count']=df['passenger_count'].fillna(
    df['passenger_count'].median()
)
print("After handling missing values in passenger_count column:", df["passenger_count"].isna().sum())
df['passenger_count']=df['passenger_count'].astype("int64")

print(df.dtypes)