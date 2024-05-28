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

Entire simulation is ran through runHIC.py (run heavy-ion collision) with:
```
./runHIC.py
```
or with:
```
python3 runHIC.py
```

All the parameters are contained within python dictionary in *params.py*. Details about all parameters and their values are commented in
*params.py*. Different configuration files needed by other modules, e.g. osu-hydro.conf are automatically generated based on the values
from this dictionary.

Parameter values can be overwritten with command line arguments when executing:
```
./runHIC.py --paramName=paramValue
```
For example, default value of number of TRENTO events is set to 250 000, through parameter *trento_event_n*, but this value can bee changed to 100 000 with command line arguments like this:
```
./runHIC.py --trento_event_n=100000
```
Only parameter values that can not be overwritten with command line arguments are options which files to save after the calculation is done.  
When parameter values are overwritten, dictionary values are updated, and this updated dictionary will be saved as json file for record keeping after the calculation is finished.

Certain parameter values depend on other parameter values and if one is changed other one is automatically changed.  
For example, if freestreaming is turned on, hydro parameters that determine whether to read initial condition as energy or entropy density and wheter or not to read initial flow and viscous terms will be changed. Also, hydro's initial time, T0, will be changed to the value of freestreaming time.

In [script used to freestream](https://github.com/DusanZigic/freestream/blob/34633c2795a2ce3548dda89730da2950b7e2e0d4/streamIC.py) intial conditions, TRENTO's grid parameters and freestreaming time are set to parameter dictionary value.  
In [script used for freezout](https://github.com/DusanZigic/frzout/blob/de3f29ceffb78c2821e318173c7faed2352e13b5/sampleSurface.py), *Tswitch* parameter is determined by hydro's decoupling energy parameter, *Edec* and equation of state (decoupling energy and/or equation of state can be changed and code would stil be consistent).  
Number of oversamples in [freezout](https://github.com/DusanZigic/frzout/blob/de3f29ceffb78c2821e318173c7faed2352e13b5/sampleSurface.py) and [analysys](https://github.com/DusanZigic/avgicTVUD/blob/main/models/analysis/analyse.py) scripts is set to parameter dictionary value.

Cross-section as a TRENTO parameter is automatically determined based on the dictionary parameter value of collision energy - ecm, based on values from [TRENTO documentation page](http://qcd.phy.duke.edu/trento/usage.html).

## <3> outline of the algorithm

First, TRENTO is used to generate initial conditions. TRENTO parameter *trento_event_n* is used to determine number of minimum-bias events.  
These events will be generated in parallel with number of jobs determined by *num_of_trento_jobs* parameter.  
When all events are generated, they are sorted based on multiple keys: *npart*, *ncoll*, *TATB* and *b*, respectively.

Initial entropy densities from events that correspond to centrality classes specified by the user are averaged, while binary collisions from
all events in a centrality class are binned into histograms that will be used as jets' creation probabilities when calculating energy loss.  
Histogram parameters (ranges and bin widths) are determined by *x_hist* and *y_hist* parameters.  
Averaging of initial entropy densities and binning of binary collisions is done by [trentoavgc module](https://github.com/DusanZigic/avgicTVUD/tree/main/models/trentoavgc).

If freestreaming is turned on, averaged initial entropy densities are freastreamed until a time determined by *tau_freestream* dictionary parameter.  
After that, freestreaming module products are fed into hydro. If freestreaming is turned off, averaged initial entropy densities are directly fed into hydro.  
Freestreaming and hydro jobs are parallelized on centrality classes, meaning freestream and hydro evolution for all centrality classes
provided by the user will run at the same time. Same is true for particlization procedure.

Since the number of oversamples needs to be high to achieve desired statistical correctness, UrQMD is the bottle-neck of the entire algorithm.  
For this reason UrQMD jobs are parallelized on single centrality based on *num_of_urqmd_jobs* dictionary parameter, i.e. UrQMD has *num_of_urqmd_jobs* processes running in parallel for single centrality, while loop over centralities is sequential.

Once UrQMD jobs are finished, analysis jobs are performed that generate low-pT monentum distributions, identified particles multiplicities, reference flow vectors and integrated flows.  
These jobs are parallelized on centrality loop.

At the end, high-pT energy loss calculations is performed for light and heavy flavour.  
Total number of threads used by energy loss code is determined by *NUM_THREADS* dictionary parameter (see description of this parameter in *params.py*).

Once entire simulation has completed, data is moved into directory *analysis[ID]* in the same directory where runHIC.py is. ID in directory
name will depend on how many directories with analysis in their name already exist so there will be no overwriting of the data.