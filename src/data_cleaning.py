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

# ----------------------------
# Outlier Detection
# ----------------------------
# Method justification:
# fare_amount, trip_distance, total_amount and tip_amount are all heavily
# right-skewed -- most trips are short/cheap, but a real minority (airport
# runs, long crosstown trips) are legitimately large. That skew breaks the
# two most common statistical outlier methods:
#   - z-score assumes a roughly normal distribution. On skewed data the mean
#     and std are themselves pulled by the tail, so the method both misses
#     genuine errors and flags legitimate long trips.
#   - a blanket 1.5*IQR rule over-flags on right-skewed data, because the
#     "normal" upper range of fares/distances already sits close to the
#     whisker, so a large chunk of perfectly real trips get marked.
# Instead each feature uses a domain-knowledge ceiling (grounded in how NYC
# taxis actually operate, per TLC rules/typical trip geography), backed up
# by a 99.5th-percentile cutoff observed in this month's data as a
# data-driven safety net -- whichever is tighter is used. Nothing is
# silently dropped: every flagged row is either capped (winsorized), with
# the fact recorded in a boolean flag column, or -- where no safe
# replacement value exists -- kept untouched and flagged for downstream
# caution.

print("\n--- Outlier Detection ---")

outlier_summary = {}

def cap_outliers(df, col, upper_bound, label):
    """Cap values above upper_bound; report and flag, never silently drop."""
    flag_col = f"{col}_outlier_capped"
    mask = df[col] > upper_bound
    n_flagged = int(mask.sum())
    df[flag_col] = mask
    df.loc[mask, col] = upper_bound
    outlier_summary[label] = {
        "method": "domain threshold + 99.5th percentile backstop",
        "upper_bound": upper_bound,
        "rows_flagged": n_flagged,
        "action": "capped (winsorized) to upper_bound; flagged, not deleted"
    }
    print(f"{label}: {n_flagged} rows above {upper_bound:.2f} -> capped, flagged in '{flag_col}'")
    return df

# fare_amount: NYC TLC in-city fares rarely exceed ~$250 even for long
# trips; beyond that a metering/data error is far more likely than a real
# fare. Use whichever is tighter: the domain ceiling or this month's
# observed 99.5th percentile.
fare_domain_cap = 250
fare_pct_cap = df["fare_amount"].quantile(0.995)
fare_upper = min(fare_domain_cap, fare_pct_cap)
df = cap_outliers(df, "fare_amount", fare_upper, "fare_amount")

# trip_distance: the longest plausible single NYC taxi trip (e.g. Manhattan
# to a far borough edge or regional airport) is well under 100 miles.
distance_domain_cap = 100
distance_pct_cap = df["trip_distance"].quantile(0.995)
distance_upper = min(distance_domain_cap, distance_pct_cap)
df = cap_outliers(df, "trip_distance", distance_upper, "trip_distance")

# total_amount: derived from fare + surcharges + tip, so it inherits the
# same right skew. No independent domain ceiling makes sense here (it's a
# function of the other capped fields), so use the 99.5th percentile alone.
total_upper = df["total_amount"].quantile(0.995)
df = cap_outliers(df, "total_amount", total_upper, "total_amount")

# tip_amount: only meaningful for card payments (payment_type == 1), since
# cash tips aren't captured by the meter and are legitimately recorded as 0.
# A percentile cutoff computed across all payment types would treat those
# structural zeros as part of the distribution and distort the threshold, so
# the percentile is computed within card payments only.
card_mask = df["payment_type"] == 1
tip_upper = df.loc[card_mask, "tip_amount"].quantile(0.995)
tip_outlier_mask = card_mask & (df["tip_amount"] > tip_upper)
n_tip_flagged = int(tip_outlier_mask.sum())
df["tip_amount_outlier_capped"] = tip_outlier_mask
df.loc[tip_outlier_mask, "tip_amount"] = tip_upper
outlier_summary["tip_amount"] = {
    "method": "99.5th percentile within card-payment trips only",
    "upper_bound": tip_upper,
    "rows_flagged": n_tip_flagged,
    "action": "capped (winsorized) to upper_bound; flagged, not deleted"
}
print(f"tip_amount (card payments only): {n_tip_flagged} rows above {tip_upper:.2f} -> capped, flagged in 'tip_amount_outlier_capped'")

# passenger_count: NYC TLC licenses taxis for a maximum of 6 passengers.
# Values above that are almost certainly data-entry errors, but unlike the
# monetary/distance features there's no sane value to cap them *to* --
# capping to 6 would fabricate a plausible-looking but unverifiable number.
# So these rows are left untouched and only flagged, with the caveat that
# downstream analysis should treat them with caution (or filter on the flag
# if a stricter view is needed).
passenger_domain_cap = 6
passenger_outlier_mask = df["passenger_count"] > passenger_domain_cap
n_passenger_flagged = int(passenger_outlier_mask.sum())
df["passenger_count_outlier"] = passenger_outlier_mask
outlier_summary["passenger_count"] = {
    "method": "domain threshold (TLC max licensed capacity = 6)",
    "upper_bound": passenger_domain_cap,
    "rows_flagged": n_passenger_flagged,
    "action": "kept as-is; flagged in 'passenger_count_outlier' (no removal, no safe substitute value)"
}
print(f"passenger_count: {n_passenger_flagged} rows above {passenger_domain_cap} -> kept, flagged in 'passenger_count_outlier' (not removed)")

print("\n--- Outlier Detection Summary ---")
for feature, info in outlier_summary.items():
    print(f"{feature}: {info['rows_flagged']} rows flagged | method: {info['method']} | action: {info['action']}")

df.to_parquet("data/processed/cleaned_taxi_data.parquet", index=False)
print("Cleaned Data has been saved to data/processed/")