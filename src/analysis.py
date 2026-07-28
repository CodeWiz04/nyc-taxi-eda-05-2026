import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

from src.utils import load_cleaned_data,add_derived_features,save_fig

sns.set_style("whitegrid")
DAY_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
PAYMENT_TYPE_LABELS = {
    1: "Credit card",
    2: "Cash",
    3: "No charge",
    4: "Dispute",
    5: "Unknown",
    6: "Voided trip",
}

#Peak demand hour vs. slowest hour
def analyze_peak_vs_slow_hour(df):
    hourly_counts=df.groupby("pickup_hour").size().sort_index()
    peak_hour=hourly_counts.idxmax()
    slow_hour=hourly_counts.idxmin()
    peak_count=int(hourly_counts.max())
    slow_count=int(hourly_counts.min())
    ratio=peak_count/slow_count
    print("\n--- 1. Peak vs Trough Hour ---")
    print(f"Peak hour: {peak_hour}:00 ({peak_count:,} trips)")
    print(f"Slowest hour: {slow_hour}:00 ({slow_count:,} trips)")
    print(f"Peak is {ratio:.1f}x the trough")
 
    colors = [
        "crimson" if h == peak_hour else "gray" if h == slow_hour else "steelblue"
        for h in hourly_counts.index
    ]
    plt.figure(figsize=(10, 5))
    sns.barplot(x=hourly_counts.index, y=hourly_counts.values, palette=colors)
    plt.title(f"Trip Volume by Pickup Hour (peak is {ratio:.1f}x the trough)")
    plt.xlabel("Hour of day")
    plt.ylabel("Trip count")
    save_fig("business_peak_vs_trough_hour.png")
 
    return {
        "peak_hour": int(peak_hour),
        "trough_hour": int(slow_hour),
        "peak_count": peak_count,
        "trough_count": slow_count,
        "ratio": round(ratio, 2),
    }