import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_parquet("data/processed/cleaned_taxi_data.parquet")

numerical_cols = df.select_dtypes(include=["int64", "float64"]).columns

for col in numerical_cols:
    plt.figure(figsize=(8,5))
    df[col].hist(bins=30)        
    plt.title(f"Histogram of {col}")
    plt.xlabel(col)
    plt.ylabel("Frequency")
    plt.show()