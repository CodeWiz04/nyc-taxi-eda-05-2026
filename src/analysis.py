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
    
def analyze_weekend_vs_weekday_fare(df):
    is_weekend=df["pickup_dayofweek"]>=5
    weekday_fares=df.loc[~is_weekend,"fare_amount"]
    weekend_fares=df.loc[is_weekend,"fare_amount"]
    
    weekday_mean=weekday_fares.mean()
    weekend_mean=weekend_fares.mean()
    diff=weekend_mean-weekday_mean
    pct_diff=(diff/weekday_mean)*100
    
    stat,p_value=stats.mannwhitneyu(
        weekend_fares,weekday_fares,alternative="two-sided"
    )
    statistically_significant=p_value<0.05
    
    print("\n--- 2. Weekend vs Weekday Average Fare ---")
    print(f"Weekday mean fare: ${weekday_mean:.2f} (n={len(weekday_fares):,})")
    print(f"Weekend mean fare: ${weekend_mean:.2f} (n={len(weekend_fares):,})")
    print(f"Difference (weekend - weekday): ${diff:+.2f} ({pct_diff:+.1f}%)")
    print(f"Mann-Whitney U p-value: {p_value:.4g}")
    print(f"Statistically significant (p<0.05): {statistically_significant}")
    print(
        "Caveat: with sample sizes this large, even tiny/trivial differences "
        "tend to be statistically significant. Judge practical importance "
        "from the dollar/percent difference above, not the p-value alone."
    )
 
    cap = df["fare_amount"].quantile(0.99)
    plot_df = df[df["fare_amount"] <= cap].copy()
    plot_df["day_type"] = np.where(plot_df["pickup_dayofweek"] >= 5, "Weekend", "Weekday")
 
    plt.figure(figsize=(6, 5))
    sns.boxplot(x="day_type", y="fare_amount", data=plot_df, showfliers=False)
    plt.title(f"Fare Amount: Weekend vs Weekday (diff = ${diff:+.2f}, p={p_value:.3g})")
    plt.xlabel("")
    plt.ylabel("Fare amount ($)")
    save_fig("business_weekend_vs_weekday_fare.png")
 
    return {
        "weekday_mean_fare": round(float(weekday_mean), 2),
        "weekend_mean_fare": round(float(weekend_mean), 2),
        "difference": round(float(diff), 2),
        "pct_difference": round(float(pct_diff), 2),
        "p_value": float(p_value),
        "statistically_significant": bool(statistically_significant),
    }