# Database_vanadium_calibration-2023
This repository contains the database and the calibration method related to the study.

The spectra are provided raw, in txt format.
The name is given as
PL_mm_pl_Xpc_Absorbance_hour-min-second.txt
Where PL is the path length, can be 0_1mm: 0.1mm or 1_mm: 1mm
and X is: 
$X_2$ or negative SOC for V2V3
X4 or fraction of V4 for V3V4
X5 or positive SOC for V4V5

Oceanoptics_reader.py: contains the class used to read the spectra from ocean optics spectrometers.
StateOfCharge_v1.py: contains the class that reads a list of spectra and calculate the state of charge and concentration based on the provided calibration folder.
An example of script is given at the end of the file.

