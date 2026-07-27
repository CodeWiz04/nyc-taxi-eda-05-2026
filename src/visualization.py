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
        
