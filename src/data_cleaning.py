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
df['RatecodeID']=df['RatecodeID'].astype(str)
df['RatecodeID']=df['RatecodeID'].replace('nan', pd.NA)
df['RatecodeID']=df['RatecodeID'].astype("category")
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

# 5.Airport_fee->0
df['Airport_fee']=df['Airport_fee'].fillna(0)
print("Filled missing Airport_fee with 0")

print("\nFinal Data Types:")
print(df.dtypes)

#Fields with no sane imputable value (timestamps, GPS coordinates) should be dropped if missing: do not invent a pickup time or location 
critical_cols=[
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime",
    "PULocationID",
    "DOLocationID"
]
critical_missing=df[critical_cols].isna().sum()
print("\nMissing values in critical Col:")
print(critical_missing)

if critical_missing.sum()>0:
    print("Dropping rows with missing values in critical columns.")
    df=df.dropna(subset=critical_cols)
    rows_dropped=critical_missing.sum()
    
    print(f"Dropped {rows_dropped} rows due to missing timestamps or location IDs.")
else:
    print("No missing values found in critical columns. No rows dropped.")
    
# Also handle: negative fares/distances, zero-passenger trips,
# impossible timestamps (dropoff before pickup)

# ----------------------------
# Negative Fares
# ----------------------------
neg_fares = (df["fare_amount"] < 0).sum()
print("Negative fares:", neg_fares)

before_rows = len(df)
df = df[df["fare_amount"] >= 0]
after_rows = len(df)

print(f"Rows before filter: {before_rows}")
print(f"Rows after filter : {after_rows}")
print(f"Rows removed      : {before_rows - after_rows}")
print("Remaining negative fares:", (df["fare_amount"] < 0).sum())


# ----------------------------
# Negative Distances
# ----------------------------
neg_distances = (df["trip_distance"] < 0).sum()
print("\nNegative distances:", neg_distances)

before_rows = len(df)
df = df[df["trip_distance"] >= 0]
after_rows = len(df)

print(f"Rows before filter: {before_rows}")
print(f"Rows after filter : {after_rows}")
print(f"Rows removed      : {before_rows - after_rows}")
print("Remaining negative distances:", (df["trip_distance"] < 0).sum())


# ----------------------------
# Zero-passenger trips
# ----------------------------
zero_passengers = (df["passenger_count"] == 0).sum()
print("\nZero passenger trips:", zero_passengers)

before_rows = len(df)
df = df[df["passenger_count"] > 0]
after_rows = len(df)

print(f"Rows before filter: {before_rows}")
print(f"Rows after filter : {after_rows}")
print(f"Rows removed      : {before_rows - after_rows}")
print("Remaining zero passenger trips:", (df["passenger_count"] == 0).sum())


# ----------------------------
# Impossible timestamps
# ----------------------------
invalid_time = (
    df["tpep_dropoff_datetime"] <
    df["tpep_pickup_datetime"]
).sum()

print("\nDropoff before pickup:", invalid_time)

before_rows = len(df)
df = df[
    df["tpep_dropoff_datetime"] >=
    df["tpep_pickup_datetime"]
]
after_rows = len(df)

print(f"Rows before filter: {before_rows}")
print(f"Rows after filter : {after_rows}")
print(f"Rows removed      : {before_rows - after_rows}")
print(
    "Remaining dropoffs before pickups:",
    (df["tpep_dropoff_datetime"] < df["tpep_pickup_datetime"]).sum()
)

df.to_parquet("data/processed/cleaned_taxi_data.parquet", index=False)
print("Cleaned Data has been saved to data/processed/")