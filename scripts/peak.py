import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from scripts import utils


class Peak:
    def __init__(self, peak_index, df, start_peak_index, end_peak_index, neighborhood_window):
        self._peak_index = peak_index
        self._start_peak_index = start_peak_index
        self._end_peak_index = end_peak_index
        self._neighborhood_window = neighborhood_window
        self._data = df
        
    @property
    def peak_index(self):
        return self._peak_index

    @property
    def start_peak_index(self):
        return self._start_peak_index
    
    @property
    def end_peak_index(self):
        return self._end_peak_index
    
    @property
    def data(self):
        return self._data
    
    @property
    def neighborhood_window(self):
        return self._neighborhood_window
    
    @property
    def peak_vertex(self):
        return self.data.iloc[self.peak_index]
    
    @property
    def peak_all(self):
        index1 = self.start_peak_index
        index2 = self.end_peak_index
        return self.data.iloc[index1:index2]
    
    @property
    def peak_ramp_up(self):
        index1 = self.start_peak_index
        index2 = self.peak_index + 1
        return self.data.iloc[index1:index2]
    
    @property
    def peak_ramp_down(self):
        index1 = self.peak_index + 1
        index2 = self.end_peak_index
        return self.data.iloc[index1:index2]
    
    @property
    def neighborhood(self):
        index1 = self.start_peak_index - self.neighborhood_window
        index2 = self.start_peak_index
        index3 = self.end_peak_index
        index4 = self.end_peak_index + self.neighborhood_window
        return self.data.iloc[index1:index4].drop(self.data[index2:index3].index)
    
    def interpolate_across_ramp(self):
        neigh = self.neighborhood
        t_neigh = neigh["Time [h]"]
        y_neigh = neigh["lnCO2"]
        slope, intercept, r, p, _ = stats.linregress(t_neigh, y_neigh)
        
        pk = self.peak_ramp_up
        t_peak = pk["Time [h]"]    
        y_peak_interp = slope*t_peak + intercept
        return t_peak, y_peak_interp
    
    def correct_peak_ramp(self):
        pk = self.peak_ramp_up
        t_peak = pk["Time [h]"]
        y_peak = pk["lnCO2"]
        _, pk_interp = self.interpolate_across_ramp()
        
        difference = y_peak - pk_interp
        y_peak_corr = y_peak.iloc[0] + difference
    
        return t_peak, y_peak_corr
        
    def compute_slope(self, which="uncorrected"):
        if which == "uncorrected":
            pk = self.peak_ramp_up
            
            lny = pk["lnCO2"]
            y = np.exp(lny)
            t = pk["Time [h]"]
            
            slope, _, _, _, _ = stats.linregress(t, y)
            return slope
        
        elif which == "corrected":
            t, lny = self.correct_peak_ramp()
            y = np.exp(lny)
            slope, _, _, _, _ = stats.linregress(t, y)
            return slope
        
        else:
            print("unknown input")
            return None
        
    def plot_ctr_correction(self):
        f, ax = plt.subplots(figsize=(6,5))

        # Display neighborhood of peak:
        neigh = self.neighborhood
        t = neigh["Time [h]"]
        y = neigh["lnCO2"]
        ax.scatter(t, np.exp(y), label="Neighborhood", color="black")
        
        # Display left side of the peak:
        pk = self.peak_ramp_up
        t = pk["Time [h]"]
        y = pk["lnCO2"]
        slope, inter, _, _, _ = stats.linregress(t, np.exp(y))
        ax.scatter(t, np.exp(y), label=rf"Uncorrected (CTR = {utils.convert_slope_to_CTR(slope) :.2} mmol$CO_2$/L/h)")
        ax.plot(t, slope*t + inter, color="black", linestyle="--")

        # Display left side of the peak, corrected for changing baseline:
        t, y_corr = self.correct_peak_ramp()
        slope, inter, _, _, _ = stats.linregress(t, np.exp(y_corr))
        ax.scatter(t, np.exp(y_corr), label=rf"Corrected (CTR = {utils.convert_slope_to_CTR(slope) :.2} mmol$CO_2$/L/h)")
        ax.plot(t, slope*t + inter, color="black", linestyle="--")
        
        # Display baseline:
        t, y = self.interpolate_across_ramp()
        slope, inter, _, _, _ = stats.linregress(t, np.exp(y))
        ax.scatter(t, np.exp(y), label="Interpolated baseline")
        ax.plot(t, slope*t + inter, color="black", linestyle="--")

        ax.set_ylabel(r"$CO_2$ $[\%]$")
        ax.set_xlabel("Time [h]")
        ax.legend(fontsize="x-small")
        
        return ax