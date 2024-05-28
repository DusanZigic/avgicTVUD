# avgicTVUD

### Trento + Vishnu + Urqmd + Dreena  -  averaged initial conditions

This is a package for full heavy-ion collision simulation performed on averaged initial conditions. It contains [TRENTO](https://github.com/Duke-QCD/trento) initial conditions, [viscous hydrodynamics](https://github.com/jbernhard/osu-hydro) code, [UrQMD](https://github.com/jbernhard/urqmd-afterburner) afterburner and [DREENA-A](https://github.com/DusanZigic/DREENA-A) model for high-pT energy loss calculations, as well as [freestream](https://github.com/Duke-QCD/freestream) and [freezout](https://github.com/Duke-QCD/frzout) modules.

## <1> prerequisites and compilation

Following modules, libraries and compilers are needed:
+ Python 3.5+ with the following modules: numpy, scipy, cython, and h5py
+ C, C++, and Fortran compilers
+ CMake 3.4+
+ Boost, HDF5 and GSL (Gnu Scientific Library) C++ libraries

When running the code, check for all prerequisites is performed, as well as check for all executables. If any of the prerequisites is
not found, executions is stoped and error message is printed. If executables are not found, they are automatically compiled. Output of
compilation is printed to compile.info file and if compilation is successful, this file is deleted and execution is continued - if not,
execution is stoped and compilation errors can be seen in this file.

## <2> running simulation and parameters

Entire simulation is ran through runHIC.py (run heavy-ion collision)with:

'''
./runHIC.py
'''

or with:

'''
python3 runHIC.py
'''

All the parameters are contained within python dictionary in params.py. Details about all parameters and their values are commented in
params.py. Different configuration files needed by other modules, e.g. osu-hydro.conf are automatically generated based on the values
from this dictionary.
Parameter values can be overwritten with command line arguments when executing: ./run_hic.py --[param_name]=[param_value] (see
jobscript.slurm for more details and examples). Only parameter values that can not be overwritten with command line arguments are
options which files to save after the calculation is done. When parameter values are overwritten, dictionary values are updated, and this
updated dictionary will be saved for record keeping after the calculation is finished.

Certain parameter values depend on other parameter values and if one is changed other one is automatically changed. E.g. if freestreaming
is turned on, hydro parameters that determine whether to read initial condition as energy or entropy density and wheter or not to read
initial flow and viscous terms will be changed. Also, hydro's initial time, T0, will be changed to the value of freestreaming time.

In freestream procedure, TRENTO's grid parameters and freestreaming time were hard-code - now they are set to parameter dictionary value.
In freezout procedure, Tswitch was a parameter that was hard-coded - now it is determined by hydro's decoupling energy parameter and
equation of state (decoupling energy and/or equation of state can be changed and code would stil be consistent).
In freezout procedure and analysys script, number of oversamples was hard-coded - now it is set to parameter dictionary value.

Cross-section as a TRENTO parameter is automatically determined based on the dictionary parameter value of collision energy - ecm.