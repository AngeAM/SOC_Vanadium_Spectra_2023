import sys
import glob
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from copy import deepcopy
from Oceanoptics_reader import SpectrumReader
import importlib.util


def import_module(path):
    """To import the calibration module that corresponds the specified calibration path"""
    spec = importlib.util.spec_from_file_location("cal_preprocessing.PreprocessingSOC", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["cal_preprocessing.PreprocessingSOC"] = module
    spec.loader.exec_module(module)
    return module

class StateOfCharge:
    def __init__(self, spectra_path, path_ref=None, calibration_folder_list=None, path_length=None):

        self.list_spectra = []
        self.list_dates = []
        self.intensity = []
        self.list_soc = []
        self.time = []
        self.path_length = path_length
        if calibration_folder_list:
            self.calibration_folder = calibration_folder_list

        if path_ref:
            self.ref = SpectrumReader(path_ref)



        #  Opening the spectra from the path list
        for path in spectra_path:
            spec = SpectrumReader(path)
            if path_ref:
                spec.spectrum = -np.log10(spec.spectrum/self.ref.spectrum)
            if path_length:
                spec.spectrum = spec.spectrum / self.path_length

            self.list_spectra.append(spec)
            self.list_dates.append(spec.date.timestamp())
        self.time = np.array(self.list_dates) - self.list_dates[0]

    def calculate_soc(self, index_cal=0, skip=1, arg=None):
        """To calculate the soc or X, index_cal points to the corresponding calibration folder in the given list, skip is for skipping spectra, it will compute the SOC every
        "skip" spectra, arg is almost always None apart for the empirical positive calibration where it must be entered the assumed concentration"""
        preprocess = import_module(self.calibration_folder[index_cal] + "cal_preprocessing.py")
        self.preprocessing = preprocess.PreprocessingSOC(deepcopy(self.list_spectra), self.calibration_folder[index_cal], skip=skip, arg=arg)
        self.list_soc = self.preprocessing.x

    def calculate_single_wl(self, wl):
        """Calculates the intensity value at one wavelength for all spectra"""
        self.list_values = []
        for spectrum in self.list_spectra:
            self.list_values.append(np.average(spectrum.spectrum.loc[wl-1:wl+1]))
        self.intensity = pd.DataFrame(self.list_values, index=self.list_dates)

    def calculate_plot_absorbance(self, wl):
        """Calculates the intensity value at one wavelength for all spectra and plots it"""
        self.calculate_single_wl(wl)
        plt.plot(self.intensity.values)
        plt.ylabel("Intensity")

    def plot_spectra(self, skip=1):
        plt.figure()
        """Plots all the spectra, skip argument to plot every "skip" spectra"""
        for i, spectrum in enumerate(self.list_spectra):
            if divmod(i, skip)[1] == 0:
                plt.plot(spectrum.spectrum, label=i)
        plt.legend()
        plt.xlabel("Wavelength (nm)")
        plt.ylabel("Absorbance")
        plt.xlim(430, 1000)
        plt.show()


if __name__ == '__main__':
    """Example of a script opening and plotting the SOC, the spectra and the concentration"""
    import os
    path_list = glob.glob("V2V3/1_83M/*")
    path_list.sort(key=os.path.getmtime)
    path_cal_neg_deconv = "Calibration folder\cal_neg\cal_neg_deconvolution_V2/"
    path_cal_neg_empirical = "Calibration folder/cal_neg/cal_neg_ratio_isosbestic/"
    soc = StateOfCharge(path_list, path_ref=None, calibration_folder_list=[path_cal_neg_deconv, path_cal_neg_empirical], path_length=0.1)
    """The command to calculate the soc"""
    soc.calculate_soc(index_cal=0)
    """Spectra"""
    soc.plot_spectra()
    plt.figure()
    """SOC"""
    plt.plot(soc.list_soc)
    plt.figure()
    """Concentration"""
    plt.plot(soc.preprocessing.list_Ctotal)
