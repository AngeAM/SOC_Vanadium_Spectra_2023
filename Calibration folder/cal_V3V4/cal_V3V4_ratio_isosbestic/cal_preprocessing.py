
import numpy as np

from fit_gauss_spectra import FitGauss



class PreprocessingSOC:

    def __init__(self, list_spectra):

        self.list_spectra = list_spectra
        self.list_fit = []
        self.gauss_popt = []
        self.ratio = []
        self.iso = []
        for spec in self.list_spectra:
            spec.spectrum = spec.spectrum
            peak1 = spec.spectrum.loc[760:761].mean()
            peak2 = spec.spectrum.loc[607.5:608.5].mean()
            self.ratio.append(peak1 / peak2)
            self.iso.append(peak2)

        self.ratio = np.asarray(self.ratio)
        self.x = 38.26 * self.ratio - 1.91
        self.iso = np.asarray(self.iso)
        self.list_Ctotal = self.iso / 7.52

