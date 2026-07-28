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
    
def analyze_tip_rate_by_payment_type(df):
    valid=df[df["fare_amount"]>0].copy()
    valid["tip_rate"]=valid["tip_amount"]/valid["fare_amount"]
    
    grouped=valid.groupby("payment_type",observed=True).agg(
        avg_tip_rate=("tip_rate","mean"),n_trips=("tip_rate","size")
        
    )
    grouped["share_of_trips_pct"]=grouped["n_trips"]/grouped["n_trips"].sum()*100
    grouped=grouped.sort_values("avg_tip_rate",ascending=False)
    top_type = grouped.index[0]
    top_label = PAYMENT_TYPE_LABELS.get(top_type, str(top_type))
    top_rate = grouped.loc[top_type, "avg_tip_rate"]
    top_share = grouped.loc[top_type, "share_of_trips_pct"]
    print("\n--- 3. Payment Type with Highest Avg Tip Rate ---")
    print(
        "Caveat: cash tips are not captured by the TLC meter and are "
        "recorded as $0, so cash will structurally show ~0% tip rate here "
        "regardless of what riders actually tip in cash."
    )
    print(f"Highest avg tip rate: {top_label} at {top_rate*100:.1f}% of fare")
    print(f"{top_label} share of total trips: {top_share:.1f}%")
 
    grouped_display = grouped.copy()
    grouped_display.index = [PAYMENT_TYPE_LABELS.get(i, str(i)) for i in grouped_display.index]
 
    plt.figure(figsize=(7, 5))
    sns.barplot(x=grouped_display.index, y=grouped_display["avg_tip_rate"] * 100, color="darkorange")
    plt.title(f"Avg Tip Rate by Payment Type (top: {top_label} = {top_rate*100:.1f}%)")
    plt.xlabel("Payment type")
    plt.ylabel("Average tip rate (% of fare)")
    plt.xticks(rotation=30)
    save_fig("business_tip_rate_by_payment_type.png")
 
    return {
        "top_payment_type": top_label,
        "top_avg_tip_rate_pct": round(float(top_rate * 100), 2),
        "top_share_of_trips_pct": round(float(top_share), 2),
    }
    
# ----------------------------------------------------------------------
# 4. Average trip duration by day of week
# ------------------------------------------------------------------
def analyze_duration_by_dayofweek(df):
    grouped=df.groupby("pickup_dayofweek")["trip_duration_mins"].mean().sort_index()
    grouped.index=DAY_LABELS
    print("\n--- 4. Average Trip Duration by Day of Week ---")
    for day, mins in grouped.items():
        print(f"{day}: {mins:.1f} min")
 
    plt.figure(figsize=(8, 5))
    sns.barplot(x=grouped.index, y=grouped.values, color="teal")
    plt.title("Average Trip Duration by Day of Week")
    plt.xlabel("Day of week")
    plt.ylabel("Average trip duration (minutes)")
    save_fig("business_avg_duration_by_day.png")
 
    return {day: round(float(mins), 2) for day, mins in grouped.items()}
 
 
# ----------------------------------------------------------------------
# 5. Share of trips under 2 miles + fare-per-mile comparison
# ----------------------------------------------------------------------
def analyze_short_trip_fare_per_mile(df):
    valid=df[df["trip_distance"]>0].copy()
    valid["fare_per_mile"]=valid["fare_amount"]/valid["trip_distance"]
    
    short=valid[valid["trip_distance"]<2]
    longer=valid[valid["trip_distance"]>=2]
    
    share_short_pct=len(short)/len(valid)*100
    fpm_short=short["fare_per_mile"].mean()
    fpm_long=longer["fare_per_mile"].mean()
    fpm_ratio=fpm_short/fpm_long
    
    print("\n--- 5. Short Trips (<2mi) Share & Fare-per-Mile ---")
    print(f"Share of trips under 2 miles: {share_short_pct:.1f}% (n={len(short):,} of {len(valid):,})")
    print(f"Avg fare/mile, trips <2mi:  ${fpm_short:.2f}")
    print(f"Avg fare/mile, trips >=2mi: ${fpm_long:.2f}")
    print(f"Short trips cost {fpm_ratio:.1f}x more per mile than longer trips")
 
    cap = valid["fare_per_mile"].quantile(0.99)
    plot_df = valid[valid["fare_per_mile"] <= cap].copy()
    plot_df["trip_group"] = np.where(plot_df["trip_distance"] < 2, "<2 miles", ">=2 miles")
 
    plt.figure(figsize=(6, 5))
    sns.barplot(x="trip_group", y="fare_per_mile", data=plot_df, estimator="mean", errorbar="sd", color="purple")
    plt.title(f"Fare per Mile: <2mi vs >=2mi ({fpm_ratio:.1f}x higher for short trips)")
    plt.xlabel("")
    plt.ylabel("Fare per mile ($)")
    save_fig("business_short_trip_fare_per_mile.png")
 
    return {
        "share_under_2mi_pct": round(float(share_short_pct), 2),
        "avg_fare_per_mile_under_2mi": round(float(fpm_short), 2),
        "avg_fare_per_mile_2mi_plus": round(float(fpm_long), 2),
        "ratio": round(float(fpm_ratio), 2),
    }
    
def run_business_analysis(df):
    results = {
        "peak_vs_trough_hour": analyze_peak_vs_slow_hour(df),
        "weekend_vs_weekday_fare": analyze_weekend_vs_weekday_fare(df),
        "tip_rate_by_payment_type": analyze_tip_rate_by_payment_type(df),
        "avg_duration_by_dayofweek": analyze_duration_by_dayofweek(df),
        "short_trip_fare_per_mile": analyze_short_trip_fare_per_mile(df),
    }
    return results


def main():
    df = load_cleaned_data()
    df = add_derived_features(df)
 
    results = run_business_analysis(df)
 
    with open("business_analysis_summary.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nSaved numeric summary to business_analysis_summary.json")
    print("Charts saved to images/")
 
 
if __name__ == "__main__":
    main()