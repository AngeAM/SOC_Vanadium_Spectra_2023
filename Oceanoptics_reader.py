"""Class that reads the spectra measured with an Oceanoptics Spectrometer
Ange Maurice 2022"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from copy import deepcopy
plt.rcParams.update({'font.size': 16})

class SpectrumReader:

    def __init__(self, spectrum_path):

        file = open(spectrum_path)
        string = file.read()
        idx_date = string.find("Date") + 6
        string_date = string[idx_date:idx_date+29]
        self.path = spectrum_path
        try:
            self.date = datetime.strptime(string_date, '%a %b %d %H:%M:%S CEST %Y')
        except ValueError:
            self.date = datetime.strptime(string_date, '%a %b %d %H:%M:%S CET %Y\n')

        self.raw_spectrum = pd.read_csv(spectrum_path, delimiter="\t", skiprows=13, index_col=0)
        self.raw_spectrum.columns = ["Intensity"]
        self.spectrum = deepcopy(self.raw_spectrum)

    def normalize(self):
        self.spectrum = self.spectrum - self.spectrum.min()
        self.spectrum = self.spectrum/self.spectrum.max()

    def window_spectrum(self, wl1, wl2):
        self.spectrum = self.spectrum.loc[wl1:wl2]

    def offset_zero(self):
        self.spectrum = self.spectrum - self.spectrum.min()

    def offset_wl(self, wl):
        self.spectrum = self.spectrum - np.average(self.spectrum.loc[wl-5:wl + 5])

    def divide_max(self):
        self.spectrum = self.spectrum/self.spectrum.max()

    def apply_factor(self, factor):
        """Multiply the spectrum by a number, used for example to correct the concentration difference"""
        self.spectrum = self.spectrum*factor

    def get_timestamp(self):
        return self.date.timestamp()


if __name__ == "__main__":
    path = "V2V3/0_91M/1_mm_pl_0pc_Absorbance__0__17-19-27-755.txt"
    reader = SpectrumReader(path)
    reader.spectrum.plot()
