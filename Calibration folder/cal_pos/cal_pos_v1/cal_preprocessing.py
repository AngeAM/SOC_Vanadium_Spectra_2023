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


def return_diff(x, spectrum, wl1, wl2, e4, e45, e5, k, p):
    spectrum = spectrum.loc[wl1:wl2]
    e5 = e5.loc[wl1:wl2]
    e4 = e4.loc[wl1:wl2]
    e45 = e45.loc[wl1:wl2]
    chi = k / (k * x[0] + 1)
    C45 = (1 - np.sqrt(1 - 4 * chi ** 2 * x[1] * (1 - x[1]) * x[0] ** 2)) / 2 / chi
    diff = np.sum(
        abs(spectrum - e5*(x[0]*x[1]-C45)**p - e4.loc[wl1:wl2] * ((1-x[1])*x[0]-C45) - e45*C45 - x[2]))
    return diff




class PreprocessingSOC:

    """"Algorithm that performs deconvolution of the spectrum using epsilon 4 and epsilon 45 (the complex absorbance)"""

    def __init__(self, list_spectra, calibration_folder, skip=1, arg=None):

        self.list_spectra = list_spectra
        self.list_fit = []
        self.interval = 1
        self.e45 = pd.read_csv(calibration_folder + "/e45.csv", index_col=0)
        self.e45 = interpolation_spectrum(440, 1001, self.interval, self.e45)

        self.e4 = pd.read_csv(calibration_folder + "/e4.csv", index_col=0)
        self.e4 = interpolation_spectrum(440, 1001, self.interval, self.e4)

        self.e5 = pd.read_csv(calibration_folder + "/e5.csv", index_col=0)
        self.e5 = interpolation_spectrum(440, 1001, self.interval, self.e5)

        self.p = np.load(calibration_folder + "p.npy")
        self.k = np.load(calibration_folder + "K.npy")
        self.f_e4 = np.zeros(len(self.list_spectra))
        self.f_e5 = np.zeros(len(self.list_spectra))
        self.list_fit = []
        result = []
        self.index = []
        self.list_C5_deriv_calc = []
        self.list_C5_std = []
        self.f_e4 = np.zeros(len(self.list_spectra))
        self.f_e5 = np.zeros(len(self.list_spectra))
        wl1 = 440
        wl2 = 900
        self.w = np.linspace(0, 1, self.e4.size)
        self.w = pd.DataFrame(self.w, index=self.e4.index, columns=["Intensity"])

        method = None
        options = {"ftol": 1e-12, "maxfun": 10000}
        for i, spec in enumerate(self.list_spectra):
            if divmod(i, skip)[1] == 0:
                spectrum = interpolation_spectrum(wl1, wl2, 1, spec.spectrum)

                x = minimize(return_diff, [1, 0.5, 0], args=(spectrum, wl1, wl2, self.e4, self.e45, self.e5, self.k, self.p),
                             bounds=((0.001, 2), (0.001, 1), (-0.001, -0.001)), options=options, method=method
                             )

                print(str(i) + "/" + str(len(self.list_spectra)))
                print(x.success)
                print(x.x)
                result.append(x.x)
                self.index.append(i)
                self.list_fit.append(x)
                self.f_e5[i] = x.fun

        result = np.array(result)

        self.list_Ctotal = result[:, 0]
        self.x = result[:, 1]*100
        chi = self.k / (self.k * self.list_Ctotal + 1)
        self.list_C45 = (1 - np.sqrt(1 - 4 * chi ** 2 * self.x/100 * (1 - self.x/100) * self.list_Ctotal ** 2)) / 2 / chi
        self.list_C4 = (1-self.x/100)*self.list_Ctotal - self.list_C45
        self.list_C5 = self.x / 100 * self.list_Ctotal - self.list_C45




    def plot_fit(self, index):
        plt.plot(self.list_spectra[index].spectrum, label="data")
        plt.plot(self.e45*self.list_C45[index]+self.e4*self.list_C4[index] + self.e5*self.list_C5[index]**self.p, label="fit")
        plt.legend()
        plt.xlabel("Wavelength(nm)")

    def plot_fit_param(self, c4, c5, c45):
        plt.plot(
            self.e4*c4 + self.e5*c5**self.p + self.e45 * c45)
        plt.xlabel("Wavelength(nm)")

