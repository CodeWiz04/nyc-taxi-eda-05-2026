import os
import pandas as pd
import matplotlib.pyplot as plt

IMAGES_DIR="images"

def load_cleaned_data(path="data/processed/cleaned_taxi_data.parquet"):
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