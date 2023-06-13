import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import minimize

def interpolation_spectrum(wl_min, wl_max, interv, spectrum):
    wl = np.arange(wl_min, wl_max, interv)
    x = spectrum.index
    y = spectrum.to_numpy()
    y = np.reshape(y, y.size)
    return pd.DataFrame({"Intensity": np.interp(wl, x, y)}, index=wl)

def return_diff(x, spectrum, wl1, wl2, e4, e3):
    diff = np.sum(abs(spectrum.loc[wl1:wl2] - (e3.loc[wl1:wl2]*(100-x[0])/100*x[1] + e4.loc[wl1:wl2]*x[0]/100*x[1])-x[2]))
    return diff


class PreprocessingSOC:

    """"Algorithm that performs deconvolution of the spectrum using epsilon 4 and epsilon 45 (the complex absorbance)"""

    def __init__(self, list_spectra, calibration_folder, skip=1, arg=None):

        self.list_spectra = list_spectra
        self.list_fit = []

        self.int = 1
        self.e4 = pd.read_csv(calibration_folder + "/e4.csv", index_col=0)
        self.e4 = interpolation_spectrum(420, 1001, self.int, self.e4)

        self.e3 = pd.read_csv(calibration_folder + "/e3.csv", index_col=0)
        self.e3 = interpolation_spectrum(420, 1001, self.int, self.e3)

        wl1 = 440
        wl2 = 900

        self.list_fit = []
        result = []
        self.index = []
        for i, spec in enumerate(self.list_spectra):
            if divmod(i, skip)[1] == 0:
                spectrum = interpolation_spectrum(440, 1001, self.int, spec.spectrum)

                x = minimize(return_diff, np.array([50, 1, 0]), args=(spectrum, wl1, wl2, self.e4, self.e3),
                             bounds=((0, 100), (0, 5), (-5, 5)))

                print(str(i) + "/" + str(len(self.list_spectra)))
                print(x.success)
                print(x.x)
                result.append(x.x)
                self.index.append(i)
                self.list_fit.append(x)

        result = np.array(result)
        self.list_y = result[:, 2]
        self.list_Ctotal = result[:, 1]
        self.x = result[:, 0]

    def plot_fit(self, index):
        plt.plot(self.list_spectra[index].spectrum, label="data")
        plt.plot(self.list_Ctotal[index]*(self.e4*self.x[index]/100+self.e3*(100-self.x[index])/100) + self.list_y[index], label="fit")
        plt.legend()
        plt.xlabel("Wavelength(nm)")

    def plot_fit_param(self, X, C,y):
        plt.plot(
            C*(self.e3 * (100-X)/100 + self.e4*X/100)+y)
        plt.xlabel("Wavelength(nm)")