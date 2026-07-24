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

# Handling missing values
print("---Missing values for each column---")
missing=df.isnull().sum()
missing=missing[missing>0] 
print(missing)

missing_percent=(df.isnull().sum()/len(df))*100
missing_percent=missing_percent[missing_percent>0]
print(missing_percent.sort_values(ascending=False))

print(df.groupby("VendorID")["RatecodeID"].apply(lambda x: x.isna().mean()))


for col in [
    "store_and_fwd_flag",
    "congestion_surcharge",
    "Airport_fee"
]:
    print(f"\n{col}")
    print(df.groupby("VendorID")[col].apply(lambda x: x.isna().mean()))
    
# 1.passenger_count=>Already catered by median
# 2.RatecodeID=>Unknown Category
df['RatecodeID']=df['RatecodeID'].cat.add_categories(['Unknown'])
df['RatecodeID']=df['RatecodeID'].fillna("Unknown")
print("Filled missing RatecodeID with 'Unknown'.")

# 3.store_and_fwd_flag -> Unknown category
df["store_and_fwd_flag"]=df["store_and_fwd_flag"].cat.add_categories(['Unknown'])
df["store_and_fwd_flag"]=df["store_and_fwd_flag"].fillna("Unknown")
print("Filled missing store_and_fwd_flag with 'Unknown'.")

# 4.congestion_surcharge->0
df['congestion_surcharge']=df['congestion_surcharge'].fillna(0)
print("Filled missing congestion_surcharge with 0")
