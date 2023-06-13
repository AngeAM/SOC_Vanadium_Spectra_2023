import numpy as np

class PreprocessingSOC:

    def __init__(self, list_spectra, cal_folder, skip, arg):

        self.list_spectra = list_spectra
        self.list_fit = []
        self.gauss_popt = []
        self.ratio = []
        self.iso = []
        self.list_Ctotal = []
        for spec in self.list_spectra:
            spec.spectrum = spec.spectrum
            peak1 = spec.spectrum.loc[723:724].mean()
            peak2 = spec.spectrum.loc[849:851].mean()
            self.ratio.append(peak2 / peak1)
            self.iso.append(peak1)
            self.list_Ctotal.append(1/1.36*peak1)

        self.ratio = np.asarray(self.ratio)
        self.x = 40.512 * self.ratio
        self.max = []
        self.peak_area = []
        self.peak_area = np.array(self.peak_area)


