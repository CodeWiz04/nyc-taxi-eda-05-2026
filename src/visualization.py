import matplotlib.pyplot as plt
import seaborn as sns
 
from src.utils import save_fig

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
        
