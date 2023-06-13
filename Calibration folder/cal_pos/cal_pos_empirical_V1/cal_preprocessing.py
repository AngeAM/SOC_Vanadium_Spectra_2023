import matplotlib.pyplot as plt
import numpy as np
import pandas as pd






def interpolation_spectrum(wl_min, wl_max, interv, spectrum):
    wl = np.arange(wl_min, wl_max, interv)
    x = spectrum.index
    y = spectrum.to_numpy()
    y = np.reshape(y, y.size)
    return pd.DataFrame({"Intensity": np.interp(wl, x, y)}, index=wl)

class PreprocessingSOC:


    def __init__(self, list_spectra, calibration_folder, skip=1, arg=1.8):

        self.list_spectra = list_spectra
        self.list_fit = []
        self.interval = 1
        self.C = arg


        self.a_660 = [62.12582418,  41.82603462, -42.62927574, -50.64582894]
        self.a_630 = [55.7845021,  41.310616, -42.0117017, -46.67109954]
        self.a_760 = [71.28762836,  33.62134457, -34.56110137, -51.71450803]
        self.a_860 = [60.80198867,  37.99696038, -38.39797234, -52.23007702]
        self.param = [self.a_660, self.a_760]
        list_wl = [660, 760]
        self.x_full = np.zeros((len(list_wl), len(list_spectra), 2))
        self.x = []
        list_spectra.reverse()
        for i, wl in enumerate(list_wl):
            p = self.param[i]
            a = p[2] * self.C ** 2 + p[3] * self.C
            b = p[0] * self.C + p[1]*self.C**2
            for j, spec in enumerate(list_spectra):
                c = -spec.spectrum.loc[wl-1:wl+1].mean()
                x_1 = (-b - np.sqrt(b ** 2 - 4 * a * c)) / 2 / a
                x_2 = (-b + np.sqrt(b ** 2 - 4 * a * c)) / 2 / a
                self.x_full[i, j, 0] = x_1
                self.x_full[i, j, 1] = x_2

        for i in range(self.x_full.shape[1]):
            val = self.x_full[:, i, :]
            diff1 = abs(val[0, 0]-val[1, 0])
            diff2 = abs(val[0, 1] - val[1, 1])
            if diff1 < diff2:
                self.x.append(np.average(val[:, 0]))
            else:
                self.x.append(np.average(val[:, 1]))

        self.x = np.asarray(self.x) * 100
