import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


def plot_signal(df: pd.DataFrame, var: str, peak_idx: list = [], window: tuple = (0,0), ax = None, **kwargs):

    if ax is None:
        f, ax = plt.subplots(**kwargs)

    # Plot signal:
    sns.scatterplot(data=df,
                    x="Time [h]", y=var,
                    ax=ax,
                    s=5, color="black", edgecolor="black")
    
    # Plot peaks:
    sns.scatterplot(data=df.loc[peak_idx],
                    x="Time [h]", y=var,
                    ax=ax,
                    color="red")

    # Add window:
    if any(window):

        for peak in peak_idx:
            lower_index = peak - window[0]
            upper_index = peak + window[1]
                
            ax.axvspan(df["Time [h]"].iloc[lower_index],
                       df["Time [h]"].iloc[upper_index],
                       color="gray", alpha=0.4)
        
    return ax