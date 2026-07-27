import matplotlib.pyplot as plt
import seaborn as sns
 
from utils import save_fig

sns.set_style("whitegrid")
#____UNIVARIATE ANAYLSIS______
def plot_numerical_histograms(df,numerical_cols):
    for col in numerical_cols:
        fig,axes=plt.subplots(1,2,figsize=(12,4))
        sns.histplot(df[col], bins=50, kde=False, ax=axes[0], color="steelblue")
        axes[0].set_title(f"Histogram of {col}")
 
        sns.kdeplot(df[col], fill=True, ax=axes[1], color="darkorange")
        axes[1].set_title(f"KDE of {col}")
 
        save_fig(f"univariate_num_{col}.png")
        
def plot_trip_duration_histogram(df):
    cap = df["trip_duration_min"].quantile(0.99)
    plt.figure(figsize=(8, 5))
    sns.histplot(df[df["trip_duration_min"] <= cap]["trip_duration_min"], bins=50, color="steelblue")
    plt.title("Trip Duration Distribution (minutes, capped at 99th percentile)")
    plt.xlabel("Trip duration (minutes)")
    save_fig("trip_duration_histogram.png")

def plot_fare_distribution(df):
    cap = df["fare_amount"].quantile(0.99)
    plt.figure(figsize=(8, 5))
    sns.histplot(df[df["fare_amount"] <= cap]["fare_amount"], bins=50, kde=True, color="darkorange")
    plt.title("Fare Amount Distribution ($, capped at 99th percentile)")
    plt.xlabel("Fare amount ($)")
    save_fig("fare_distribution.png")
    
def plot_categorical_counts(df, low_cardinality_cats):
    for col in low_cardinality_cats:
        plt.figure(figsize=(6, 4))
        order = df[col].value_counts().index
        sns.countplot(x=df[col], order=order, color="teal")
        plt.title(f"Count plot of {col}")
        plt.xticks(rotation=45)
        save_fig(f"univariate_cat_{col}.png")
        
        
def plot_high_cardinality_top15(df, high_cardinality_cols):
    """Top-15 bar chart for high-cardinality columns (PULocationID, DOLocationID)."""
    for col in high_cardinality_cols:
        top15 = df[col].value_counts().nlargest(15)
        plt.figure(figsize=(8, 4))
        sns.barplot(x=top15.index.astype(str), y=top15.values, color="purple")
        plt.title(f"Top 15 most frequent {col} zones")
        plt.xlabel(col)
        plt.ylabel("Trip count")
        plt.xticks(rotation=45)
        save_fig(f"univariate_cat_{col}_top15.png")
        
def run_univariate_analysis(df,numerical_cols,low_cardinality_cats,high_cardinality_cols):
    plot_numerical_histograms(df,numerical_cols)
    plot_trip_duration_histogram(df)
    plot_fare_distribution(df)
    plot_categorical_counts(df,low_cardinality_cats)
    plot_high_cardinality_top15(df,high_cardinality_cols)

# BIVARIATE ANALYSIS
def plot_correlation_heatmap(df,numerical_cols):
    plt.figure(figsize=(10,8))
    corr=df[numerical_cols].corr()
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0)
    plt.title("Correlation Heatmap of Numerical Features")
    save_fig("bivariate_num_num_heatmap.png")
        
        
def plot_hourly_heatmap(df):
    pivot = (
        df.groupby(["pickup_dayofweek", "pickup_hour"])
        .size()
        .unstack(fill_value=0)
    )
    day_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    pivot.index = day_labels
 
    plt.figure(figsize=(12, 6))
    sns.heatmap(pivot, cmap="YlOrRd", linewidths=0.5)
    plt.title("Trip Volume by Hour of Day and Day of Week")
    plt.xlabel("Pickup Hour")
    plt.ylabel("Day of Week")
    save_fig("heatmap_hourly.png")
    
    
def plot_scatter_pairs(df, pairs):
    for x_col, y_col in pairs:
        plt.figure(figsize=(6, 5))
        sns.scatterplot(x=df[x_col], y=df[y_col], alpha=0.2, s=10)
        plt.title(f"{x_col} vs {y_col}")
        save_fig(f"bivariate_num_num_{x_col}_vs_{y_col}.png")
        
def plot_boxplots(df, pairs):
    """Boxplot of a numerical column grouped by a categorical column, for each pair."""
    for num_col, cat_col in pairs:
        plt.figure(figsize=(7, 5))
        sns.boxplot(x=df[cat_col], y=df[num_col], showfliers=False)
        plt.title(f"{num_col} Distribution Across {cat_col}")
        plt.xticks(rotation=45)
        save_fig(f"bivariate_num_cat_box_{num_col}_by_{cat_col}.png")
        
        
def plot_tip_violin(df):
    card_df=df[df["payment_type"]==1]
    plt.figure(figsize=(7,5))
    sns.violinplot(x=card_df["payment_type"],y=card_df["tip_amount"],cut=0)
    plt.title("Tip Amount Distribution for Card Payments")
    save_fig("bivariate_num_cat_violin_tip_by_payment.png")

def plot_distance_by_flag_bar(df):
    plt.figure(figsize=(6, 4))
    sns.barplot(x=df["store_and_fwd_flag"], y=df["trip_distance"], estimator="mean", errorbar="sd")
    plt.title("Average Trip Distance by store_and_fwd_flag")
    save_fig("bivariate_num_cat_bar_distance_by_flag.png")