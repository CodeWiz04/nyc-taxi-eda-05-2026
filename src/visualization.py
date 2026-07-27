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
        
