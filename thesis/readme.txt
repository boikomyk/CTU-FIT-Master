Contents of USB flash drive:
|readme.txt ....................... the file with USB flash drive contents description
||__src.......................................the directory of source codes| || |__impl......................the directory of the thesis experiments source codes| || |__thesis..............the directory of LATEX source codes of the thesis|   ||   |__figures .............................. the thesis figures directory|   ||   |__*.tex .................... the LATEX source code files of the thesis||__text..........................................the thesis text directory  |  |__DP_Boiko_Mykyta.pdf ...................... the Master thesis in PDF format


Thesis experiments source codes directory structure (impl/thesis_experiments/*):
 -  cvm.ipynb - jupyter notebook experiment with the Constant Velocity Model(CVM)
 -  pgm.ipynb - jupyter notebook experiment with the Power Growth Model(PGM)
 -  prm.ipynb - jupyter notebook experiment with the Polar Radar Model(PRM)
 -  models/power_growth.py - model for trajectory generation and measurements for PGM
 -  models/trajectory.py   - model for trajectory generation and measurements for CVM
 -  models/polar_radar.py  - model for trajectory generation and measurements for PRM
 -  models/data/*       - generated model trajectories used in the experiments
 -  models/mse_finals/* - final MSE values of each of 100 runs for all models
 -  utils/* - support classes containing methods used in the experiments


To run experiments, you must have the following dependencies installed:

Predefined requirements:
 1. NumPy v.1.21.3
 2. SciPy v.1.7.1
 3. Matplotlib v.3.4.3

Author
Bc. Mykyta Boiko boikomyk@fit.cvut.cz