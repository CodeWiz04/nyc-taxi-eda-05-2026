import os
import pandas as pd
import matplotlib.pyplot as plt

IMAGES_DIR="images"

def load_cleaned_data(path="data/processed/cleaned_taxi_data.parquet"):
    '''Loads cleaned data present in data/processed'''
    df = pd.read_parquet(path)
    print(f"Loaded cleaned dataset: {df.shape[0]} rows, {df.shape[1]} columns")
    return df


def add_derived_features(df):
    df=df.copy()
    df["trip_duration_mins"]=(
        df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]
    ).dt.total_seconds() / 60
    df["pickup_hour"] = df["tpep_pickup_datetime"].dt.hour
    df["pickup_dayofweek"] = df["tpep_pickup_datetime"].dt.dayofweek
    return df

def get_column_groups(df):
    numerical_cols=df.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols=df.select_dtypes(include=["category"]).columns.tolist()
    high_cardinality_cols=[c for c in ["PULocationID","DOLocationID"] if c in categorical_cols]
    low_cardinality_cats = [c for c in categorical_cols if c not in high_cardinality_cols]
    return numerical_cols, low_cardinality_cats, high_cardinality_cols

def save_fig(filename,dpi=100):
    os.makedirs(IMAGES_DIR, exist_ok=True)
    filepath = os.path.join(IMAGES_DIR, filename)
    plt.tight_layout()
    plt.savefig(filepath, dpi=dpi)
    plt.close()
    print(f"Saved: {filepath}")
    