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

def return_diff(x, spectrum, wl1, wl2, e3, e2):
    diff = np.sum(abs(spectrum.loc[wl1:wl2] - (e3.loc[wl1:wl2]*(100-x[0])/100*x[1] + e2.loc[wl1:wl2]*x[0]/100*x[1])-x[2]))
    return diff

class PreprocessingSOC:

    """"Algorithm that performs deconvolution of the spectrum using epsilon 4 and epsilon 45 (the complex absorbance)"""

    def __init__(self, list_spectra, calibration_folder, skip=1, arg=None):

        self.list_spectra = list_spectra
        self.list_fit = []

        self.e2 = pd.read_csv(calibration_folder + "/e2.csv", index_col=0)
        self.e2 = interpolation_spectrum(420, 1001, 1, self.e2)

        self.e3 = pd.read_csv(calibration_folder + "/e3.csv", index_col=0)
        self.e3 = interpolation_spectrum(420, 1001, 1, self.e3)

        wl1 = 450
        wl2 = 1000
        x0 = np.array([1, 1, 0])
        self.list_fit = []
        result = []
        self.index = []
        self.result_detailed = []
        for i, spec in enumerate(self.list_spectra):
            if divmod(i, skip)[1] == 0:
                spectrum = interpolation_spectrum(420, 1001, 1, spec.spectrum)


                x = minimize(return_diff, np.array([50, 1, 0]), args=(spectrum, wl1, wl2, self.e3, self.e2),
                             bounds=((0, 100), (0, 2.5), (-0.001, 0.001)), options={"maxiter": 2000})

                print(str(i) + "/" + str(len(self.list_spectra)))
                print(x.success)
                print(x.x)
                self.result_detailed.append(x)
                result.append(x.x)
                self.index.append(i)
                self.list_fit.append(x)

        result = np.array(result)

        self.list_y = result[:, 2]
        self.list_Ctotal = result[:, 1]
        self.x = result[:, 0]

    def plot_fit(self, index):
        plt.plot(self.list_spectra[index].spectrum, label="data")
        plt.plot(self.e3*(100-self.x[index])/100*self.list_Ctotal[index]+self.e2*self.x[index]/100*self.list_Ctotal[index] + self.list_y[index], label="fit")
        plt.legend()
        plt.xlabel("Wavelength(nm)")
        plt.xlim(420, 1100)

    def plot_fit_param(self, c3, c2):
        plt.plot(
            self.e3 * 0.01 * c3 + self.e2 * 0.01 *
            c2)
        plt.xlabel("Wavelength(nm)")